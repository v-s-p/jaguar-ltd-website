import { type NextFunction, type Request, type Response, Router } from "express";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { z } from "zod";
import { requireAuth, signAccessToken, type AuthenticatedRequest } from "./auth";
import { analyzeMatchesWithGem } from "./services/gemini-service";
import { scrapeWeeklyTotoBulletin } from "./services/toto-scraper";
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

function requireAdmin(req: Request, res: Response, next: NextFunction) {
  const adminSecret = process.env.ADMIN_SECRET;
  if (!adminSecret) {
    console.error("ADMIN_SECRET is not configured.");
    return res.status(500).json({ error: "server_misconfigured", detail: "admin_secret_missing" });
  }

  const providedSecret = req.header("X-Admin-Secret");
  if (providedSecret !== adminSecret) {
    return res.status(403).json({ error: "forbidden", detail: "invalid_admin_secret" });
  }
  next();
}

function asyncHandler(
  handler: (req: Request, res: Response, next: NextFunction) => Promise<void | Response>
) {
  return (req: Request, res: Response, next: NextFunction) => {
    Promise.resolve(handler(req, res, next)).catch(next);
  };
}

function getWeekNumber(d: Date): number {
  d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
  const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  const weekNo = Math.ceil(((d.getTime() - yearStart.getTime()) / 86400000 + 1) / 7);
  return weekNo;
}

// Renaming this for clarity, as it uses the service role key
function createSupabaseAdminClient(): SupabaseClient | null {
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
  const supabaseAdminClient = createSupabaseAdminClient();

  router.post("/auth/exchange", asyncHandler(async (req, res) => {
    const parsed = authExchangeBody.safeParse(req.body);
    if (!parsed.success) {
      return res.status(400).json({ error: "invalid_request", detail: parsed.error.flatten() });
    }
    if (parsed.data.provider !== "supabase") {
      return res.status(400).json({ error: "invalid_request", detail: "unsupported_provider" });
    }
    if (!supabaseAdminClient) {
      return res.status(500).json({ error: "server_misconfigured", detail: "supabase_env_missing" });
    }

    const { data, error } = await supabaseAdminClient.auth.getUser(parsed.data.accessToken);
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

  // New Admin endpoint for batch processing
  router.post(
    "/admin/process-weekly-toto",
    requireAdmin,
    asyncHandler(async (_req, res) => {
      if (!supabaseAdminClient) {
        return res.status(500).json({ error: "server_misconfigured", detail: "supabase_env_missing" });
      }

      // 1. Scrape matches
      const scrapedMatches = await scrapeWeeklyTotoBulletin();
      if (!scrapedMatches || scrapedMatches.length === 0) {
        return res.status(500).json({ error: "scraping_failed" });
      }

      // 2. Analyze with GEM
      const analysisResults = await analyzeMatchesWithGem(scrapedMatches);

      // 3. Save to Supabase
      const now = new Date();
      const bulletinId = `toto-${now.getFullYear()}-w${getWeekNumber(now)}`;

      const recordsToInsert = analysisResults.map((result, index) => ({
        bulletin_id: bulletinId,
        match_id: index + 1,
        match_name: result.matchName,
        prediction: result.prediction,
        analysis_text: result.analysisText,
        status: "completed",
      }));

      const { data, error } = await supabaseAdminClient
        .from("predictions")
        .upsert(recordsToInsert, { onConflict: "bulletin_id, match_id" })
        .select(); // Explicitly select the data to get it back

      if (error) {
        console.error("Supabase insert error:", error);
        return res.status(500).json({ error: "database_error", detail: error.message });
      }

      // Log for debugging in case data is null
      if (data === null) {
        console.warn("Supabase returned null data for upsert, this usually indicates a permissions issue or misconfigured RLS/service key.");
      }

      const processedCount = data?.length ?? 0;

      return res.json({ ok: true, message: `Successfully processed and saved ${processedCount} predictions for bulletin ${bulletinId}.`, processed: processedCount });
    })
  );

  router.get(
    "/predictions/latest",
    asyncHandler(async (_req, res) => {
      if (!supabaseAdminClient) {
        return res.status(500).json({ error: "server_misconfigured", detail: "supabase_env_missing" });
      }

      // Find the most recent bulletin_id
      const { data: latestBulletin, error: bulletinError } = await supabaseAdminClient
        .from("predictions")
        .select("bulletin_id")
        .order("created_at", { ascending: false })
        .limit(1)
        .single();

      if (bulletinError || !latestBulletin) {
        return res.status(404).json({ error: "not_found", detail: "No predictions found." });
      }

      const { bulletin_id } = latestBulletin;

      // Fetch all predictions for the latest bulletin
      const { data: predictions, error: predictionsError } = await supabaseAdminClient
        .from("predictions")
        .select("*")
        .eq("bulletin_id", bulletin_id)
        .order("match_id", { ascending: true });

      if (predictionsError) {
        return res.status(500).json({ error: "database_error", detail: predictionsError.message });
      }

      return res.json({ bulletinId: bulletin_id, predictions });
    })
  );

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
