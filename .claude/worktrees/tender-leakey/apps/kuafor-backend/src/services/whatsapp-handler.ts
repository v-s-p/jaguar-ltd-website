import twilio from "twilio";
import { createClient } from "@supabase/supabase-js";

const { MessagingResponse } = twilio.twiml;

const supabase = process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_ROLE_KEY
  ? createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_ROLE_KEY)
  : null;

// ─── Salon Config (from .env) ──────────────────────────────────────────────
const SALON_NAME = process.env.SALON_NAME ?? "Kuaför Salonu";
const SALON_ADDRESS = process.env.SALON_ADDRESS ?? "Adres belirtilmemiş";
const OPEN_HOUR = parseInt(process.env.OPEN_HOUR ?? "10");
const CLOSE_HOUR = parseInt(process.env.CLOSE_HOUR ?? "22");

const SERVICES: string[] = process.env.SERVICES
  ? process.env.SERVICES.split(",").map((s) => s.trim())
  : ["Saç Kesimi", "Fön", "Boya", "Manikür"];

const STYLISTS: string[] = process.env.STYLISTS
  ? process.env.STYLISTS.split(",").map((s) => s.trim())
  : ["Usta 1", "Usta 2"];

// ─── Types ─────────────────────────────────────────────────────────────────
type IncomingMessage = {
  from: string;
  body: string;
  profileName: string;
};

type BookingStep =
  | "idle"
  | "awaiting_service"
  | "awaiting_stylist"
  | "awaiting_date"
  | "awaiting_time"
  | "confirming";

type BookingSession = {
  step: BookingStep;
  name: string;
  service?: string;
  stylist?: string;
  date?: string;
  time?: string;
};

// ─── Session Store (in-memory, Phase 1) ───────────────────────────────────
const sessions = new Map<string, BookingSession>();

function getOrCreateSession(from: string, name: string): BookingSession {
  if (!sessions.has(from)) {
    sessions.set(from, { step: "idle", name });
  }
  return sessions.get(from)!;
}

// ─── Helpers ───────────────────────────────────────────────────────────────
function buildMenu(items: string[]): string {
  return items.map((item, i) => `${i + 1}. ${item}`).join("\n");
}

function parseTimeInput(input: string): number | null {
  const match = input.match(/^(\d{1,2})[:.]?(\d{0,2})$/);
  if (!match) return null;
  const hour = parseInt(match[1]);
  const min = parseInt(match[2] || "0");
  if (hour < 0 || hour > 23 || min < 0 || min > 59) return null;
  return hour * 60 + min;
}

function isWithinWorkingHours(input: string): boolean {
  const totalMin = parseTimeInput(input);
  if (totalMin === null) return false;
  const openMin = OPEN_HOUR * 60;
  const closeMin = CLOSE_HOUR * 60;
  return totalMin >= openMin && totalMin < closeMin;
}

function formatTime(input: string): string {
  const match = input.match(/^(\d{1,2})[:.]?(\d{0,2})$/);
  if (!match) return input;
  const h = match[1].padStart(2, "0");
  const m = (match[2] || "0").padStart(2, "0");
  return `${h}:${m}`;
}

function selectFromList(msg: string, list: string[]): string | null {
  const num = parseInt(msg);
  if (!isNaN(num) && num >= 1 && num <= list.length) {
    return list[num - 1];
  }
  return list.find((item) => item.toLowerCase().includes(msg.toLowerCase())) ?? null;
}

const RESET_KEYWORDS = ["iptal", "baştan", "cancel", "reset", "menu", "başla"];
const START_KEYWORDS = ["randevu", "merhaba", "selam", "hello", "hi", "1"];
const INFO_KEYWORDS = ["adres", "nerede", "konum", "saat", "kaçta", "açık", "çalışma"];

// ─── Main Handler ──────────────────────────────────────────────────────────
export async function handleIncomingMessage({
  from,
  body,
  profileName,
}: IncomingMessage): Promise<string> {
  const twiml = new MessagingResponse();
  const raw = body.trim();
  const msg = raw.toLowerCase();
  const session = getOrCreateSession(from, profileName);

  // ── RESET
  if (RESET_KEYWORDS.includes(msg)) {
    sessions.delete(from);
    twiml.message(`İşlem iptal edildi.\n\nYeniden başlamak için *randevu* yazın. 😊`);
    return twiml.toString();
  }

  // ── INFO (herhangi bir adımda çalışır)
  if (INFO_KEYWORDS.some((kw) => msg.includes(kw))) {
    twiml.message(
      `ℹ️ *${SALON_NAME}*\n\n` +
      `📍 ${SALON_ADDRESS}\n` +
      `🕐 Çalışma saatleri: ${OPEN_HOUR}:00 - ${CLOSE_HOUR}:00\n\n` +
      `Randevu almak için *randevu* yazın.`
    );
    return twiml.toString();
  }

  // ── STEP: idle
  if (session.step === "idle") {
    if (START_KEYWORDS.some((kw) => msg.includes(kw))) {
      session.step = "awaiting_service";
      twiml.message(
        `Merhaba ${profileName}! 💅 *${SALON_NAME}*'a hoş geldiniz!\n\n` +
        `Hangi hizmeti almak istersiniz?\n\n` +
        `${buildMenu(SERVICES)}\n\n` +
        `Numara veya hizmet adı yazın.\n` +
        `_(Adres/saat için "adres" yazın)_`
      );
    } else {
      twiml.message(
        `Merhaba! 👋 *${SALON_NAME}*\n\n` +
        `• Randevu → *randevu* yazın\n` +
        `• Adres & saat → *adres* yazın`
      );
    }
    return twiml.toString();
  }

  // ── STEP: awaiting_service
  if (session.step === "awaiting_service") {
    const selected = selectFromList(msg, SERVICES);
    if (!selected) {
      twiml.message(
        `Lütfen listeden bir numara seçin (1-${SERVICES.length}):\n\n${buildMenu(SERVICES)}`
      );
      return twiml.toString();
    }
    session.service = selected;
    session.step = "awaiting_stylist";
    twiml.message(
      `✅ *${selected}* seçildi!\n\n` +
      `Hangi ustamızla çalışmak istersiniz?\n\n` +
      `${buildMenu(STYLISTS)}\n\n` +
      `Numara seçin veya *fark etmez* yazın.`
    );
    return twiml.toString();
  }

  // ── STEP: awaiting_stylist
  if (session.step === "awaiting_stylist") {
    if (msg.includes("fark etmez") || msg.includes("farketmez") || msg === "0") {
      session.stylist = "Müsait usta";
    } else {
      const selected = selectFromList(msg, STYLISTS);
      if (!selected) {
        twiml.message(
          `Lütfen listeden seçin veya *fark etmez* yazın:\n\n${buildMenu(STYLISTS)}`
        );
        return twiml.toString();
      }
      session.stylist = selected;
    }
    session.step = "awaiting_date";
    twiml.message(
      `✅ *${session.stylist}* seçildi!\n\n` +
      `📅 Hangi gün randevu istersiniz?\n` +
      `Örnek: *Pazartesi*, *Yarın*, *04/04*`
    );
    return twiml.toString();
  }

  // ── STEP: awaiting_date
  if (session.step === "awaiting_date") {
    session.date = raw;
    session.step = "awaiting_time";
    twiml.message(
      `✅ *${raw}* tarihi alındı!\n\n` +
      `🕐 Saat tercihiniz? (${OPEN_HOUR}:00 - ${CLOSE_HOUR}:00)\n` +
      `Örnek: *10:30*, *14:00*, *18:30*`
    );
    return twiml.toString();
  }

  // ── STEP: awaiting_time
  if (session.step === "awaiting_time") {
    if (!isWithinWorkingHours(raw)) {
      twiml.message(
        `⚠️ Geçersiz saat. Lütfen çalışma saatleri içinde bir saat girin:\n` +
        `🕐 ${OPEN_HOUR}:00 - ${CLOSE_HOUR}:00\n\n` +
        `Örnek: *10:30*, *15:00*, *21:00*`
      );
      return twiml.toString();
    }
    session.time = formatTime(raw);
    session.step = "confirming";
    twiml.message(
      `📋 *Randevu Özeti*\n\n` +
      `👤 Ad: ${session.name}\n` +
      `✂️ Hizmet: ${session.service}\n` +
      `💇 Usta: ${session.stylist}\n` +
      `📅 Tarih: ${session.date}\n` +
      `🕐 Saat: ${session.time}\n\n` +
      `Onaylıyor musunuz?\n*Evet* ✅ / *Hayır* ❌`
    );
    return twiml.toString();
  }

  // ── STEP: confirming
  if (session.step === "confirming") {
    if (msg === "evet" || msg === "e" || msg === "yes") {
      // Save to Supabase
      if (supabase) {
        const { data, error } = await supabase.from("bookings").insert({
          customer_name: session.name,
          phone_number: from,
          service: session.service,
          stylist: session.stylist,
          booking_date: session.date,
          booking_time: session.time,
          status: "confirmed",
        }).select("id").single();

        if (error) {
          console.error("[BOOKING ERROR]", error.message);
        } else {
          console.log(`[BOOKING SAVED] ID: ${data.id} | ${session.name} | ${session.service} | ${session.date} ${session.time}`);
        }
      } else {
        console.log(`[BOOKING CONFIRMED - no DB] ${session.name} | ${session.service} | ${session.date} ${session.time}`);
      }

      sessions.delete(from);
      twiml.message(
        `✅ *Randevunuz onaylandı!*\n\n` +
        `✂️ ${session.service}\n` +
        `💇 ${session.stylist}\n` +
        `📅 ${session.date} - ${session.time}\n\n` +
        `📍 ${SALON_ADDRESS}\n\n` +
        `Görüşmek üzere! 💅 Değişiklik için *iptal* yazın.`
      );
    } else {
      sessions.delete(from);
      twiml.message(
        `❌ Randevu iptal edildi.\n\nYeniden başlamak için *randevu* yazın.`
      );
    }
    return twiml.toString();
  }

  twiml.message(`Anlamadım 😊\n\n• Randevu → *randevu* yazın\n• Adres → *adres* yazın\n• İptal → *iptal* yazın`);
  return twiml.toString();
}
