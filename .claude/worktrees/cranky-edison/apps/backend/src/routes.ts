import { type NextFunction, type Request, type Response, Router } from "express";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { z } from "zod";
import { requireAuth, signAccessToken, type AuthenticatedRequest } from "./auth";
import type { Plan, UserRepository } from "./store/types";

const analyzeBody = z.object({
  matches: z.array(
    z.object({
      home: z.string().min(1),
      away: z.string().min(1),
    })
  ),
});

const devLoginBody = z.object({
  email: z.string().email(),
  plan: z.enum(["free", "premium"]).default("free"),
});

const authExchangeBody = z.object({
  provider: z.enum(["supabase"]).default("supabase"),
  accessToken: z.string().min(1),
});

const revenueCatWebhookBody = z.object({
  event: z.object({
    type: z.string().optional(),
    app_user_id: z.string(),
    entitlement_ids: z.array(z.string()).optional(),
    aliases: z.array(z.string()).optional(),
  }),
});

function getWebhookAuthToken(rawAuthHeader: string | undefined): string | null {
  if (!rawAuthHeader) {
    return null;
  }
  if (rawAuthHeader.startsWith("Bearer ")) {
    return rawAuthHeader.slice("Bearer ".length).trim();
  }
  return rawAuthHeader.trim();
}

function isPremiumEvent(type: string, entitlements: string[]): boolean {
  const premiumTypes = new Set([
    "INITIAL_PURCHASE",
    "RENEWAL",
    "NON_RENEWING_PURCHASE",
    "PRODUCT_CHANGE",
    "UNCANCELLATION",
  ]);
  return entitlements.includes("premium") || premiumTypes.has(type);
}

function isFreeEvent(type: string): boolean {
  const freeTypes = new Set(["CANCELLATION", "EXPIRATION", "BILLING_ISSUE"]);
  return freeTypes.has(type);
}

function asyncHandler(
  handler: (req: Request, res: Response, next: NextFunction) => Promise<void | Response>
) {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(handler(req, res, next)).catch(next);
  };
}

function createSupabaseAuthClient(): SupabaseClient | null {
  const url = process.env.SUPABASE_URL;
  const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !serviceRoleKey) {
    return null;
  }
  return createClient(url, serviceRoleKey, {
    auth: { persistSession: false },
  });
}

export function buildRoutes(userRepository: UserRepository): Router {
  const router = Router();
  const authRequired = requireAuth(userRepository);
  const isProd = (process.env.NODE_ENV ?? "").toLowerCase() === "production";
  const allowDevLogin = (process.env.ALLOW_DEV_LOGIN ?? "").toLowerCase() === "true";
  const supabaseAuthClient = createSupabaseAuthClient();

  router.post("/auth/exchange", asyncHandler(async (req, res) => {
    const parsed = authExchangeBody.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ error: "invalid_request", detail: parsed.error.flatten() });
    }
    if (parsed.data.provider !== "supabase") {
      return res.status(400).json({ error: "invalid_request", detail: "unsupported_provider" });
    }
    if (!supabaseAuthClient) {
      return res.status(500).json({ error: "server_misconfigured", detail: "supabase_env_missing" });
    }

    const { data, error } = await supabaseAuthClient.auth.getUser(parsed.data.accessToken);
    if (error || !data.user || !data.user.email) {
      return res.status(401).json({ error: "unauthorized", detail: "invalid_provider_token" });
    }

    const user = await userRepository.getOrCreateByEmail(data.user.email, "free");
    const accessToken = signAccessToken(user.id, user.email);
    return res.json({
      accessToken,
      user: {
        id: user.id,
        email: user.email,
        plan: user.plan,
      },
    });
  }));

  router.post("/auth/dev-login", asyncHandler(async (req, res) => {
    if (isProd && !allowDevLogin) {
      return res.status(403).json({ error: "forbidden", detail: "dev_login_disabled" });
    }

    const parsed = devLoginBody.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ error: "invalid_request", detail: parsed.error.flatten() });
    }

    const user = await userRepository.getOrCreateByEmail(parsed.data.email, parsed.data.plan);
    const accessToken = signAccessToken(user.id, user.email);
    return res.json({
      accessToken,
      user: {
        id: user.id,
        email: user.email,
        plan: user.plan,
      },
    });
  }));

  router.post("/webhooks/revenuecat", asyncHandler(async (req, res) => {
    const expectedSecret = process.env.REVENUECAT_WEBHOOK_SECRET;
    if (expectedSecret) {
      const incoming = getWebhookAuthToken(req.header("authorization"));
      if (!incoming || incoming !== expectedSecret) {
        return res.status(401).json({ error: "unauthorized", detail: "invalid_webhook_secret" });
      }
    }

    const parsed = revenueCatWebhookBody.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ error: "invalid_request", detail: parsed.error.flatten() });
    }

    const type = String(parsed.data.event.type ?? "UNKNOWN");
    const entitlementIds = parsed.data.event.entitlement_ids ?? [];
    const targetPlan: Plan = isPremiumEvent(type, entitlementIds)
      ? "premium"
      : isFreeEvent(type)
        ? "free"
        : "free";

    const identifiers = [parsed.data.event.app_user_id, ...(parsed.data.event.aliases ?? [])];
    let updatedUser = null;
    for (const identifier of identifiers) {
      updatedUser = await userRepository.setUserPlanByIdentifier(identifier, targetPlan);
      if (updatedUser) {
        break;
      }
    }

    return res.json({
      ok: true,
      eventType: type,
      plan: targetPlan,
      userFound: Boolean(updatedUser),
      userId: updatedUser?.id ?? null,
    });
  }));

  router.get("/me/plan", authRequired, (req: AuthenticatedRequest, res) => {
    return res.json({
      userId: req.auth!.userId,
      email: req.auth!.email,
      plan: req.auth!.plan,
    });
  });

  router.post("/analyze", authRequired, (req: AuthenticatedRequest, res) => {
    const parsed = analyzeBody.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ error: "invalid_request", detail: parsed.error.flatten() });
    }

    const plan = req.auth!.plan;
    const { matches } = parsed.data;
    const scopedMatches = plan === "free" ? matches.slice(0, 3) : matches;

    const responseMatches = scopedMatches.map((m, index) => ({
      id: index + 1,
      home: m.home,
      away: m.away,
      prediction: index % 2 === 0 ? "1" : "1X",
      xgHome: 1.35 + index * 0.08,
      xgAway: 0.92 + index * 0.06,
    }));

    const coupons = plan === "premium"
      ? ["Alt-1", "Alt-2", "Alt-3", "Alt-4"]
      : ["Alt-1", "Alt-2"];

    return res.json({
      plan,
      userId: req.auth!.userId,
      matches: responseMatches,
      coupons,
    });
  });
  return router;
}
