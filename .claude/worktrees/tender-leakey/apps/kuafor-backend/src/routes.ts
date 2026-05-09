import { Router, type Request, type Response } from "express";
import twilio from "twilio";
import { handleIncomingMessage } from "./services/whatsapp-handler";

export const router = Router();

// ─── Twilio WhatsApp Webhook ───────────────────────────────────────────────
// Twilio sends POST to this endpoint when user messages the WhatsApp number.
router.post(
  "/webhook/whatsapp",
  async (req: Request, res: Response) => {
    // Optional: validate Twilio signature in production
    const validateWebhook = process.env.TWILIO_WEBHOOK_VALIDATE === "true";
    if (validateWebhook) {
      const authToken = process.env.TWILIO_AUTH_TOKEN ?? "";
      const signature = req.headers["x-twilio-signature"] as string;
      const url = `${req.protocol}://${req.get("host")}${req.originalUrl}`;
      const isValid = twilio.validateRequest(authToken, signature, url, req.body as Record<string, string>);
      if (!isValid) {
        res.status(403).send("Forbidden");
        return;
      }
    }

    const from: string = req.body.From ?? "";
    const body: string = req.body.Body ?? "";
    const profileName: string = req.body.ProfileName ?? "Müşteri";

    console.log(`[WhatsApp] ${profileName} (${from}): ${body}`);

    const twiml = await handleIncomingMessage({ from, body, profileName });

    res.type("text/xml").send(twiml);
  }
);

// ─── Admin: List bookings ──────────────────────────────────────────────────
router.get("/bookings", async (_req: Request, res: Response) => {
  // TODO: fetch from Supabase
  res.json({ bookings: [], message: "Supabase integration coming soon" });
});
