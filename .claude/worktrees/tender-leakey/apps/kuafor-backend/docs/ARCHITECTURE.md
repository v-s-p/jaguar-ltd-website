# Kuaför App — Architecture

## Konsept
WhatsApp üzerinden kuaför randevu sistemi. Müşteri mesaj yazar, bot konuşmayla randevu alır.

## Flow
```
Müşteri WhatsApp'ta "randevu" yazar
        ↓
Twilio → webhook → kuafor-backend
        ↓
Bot: Hizmet seç → Tarih → Saat → Onayla
        ↓
Supabase'e kaydet → Kuaför bildirim alır
```

## Phase 1 — Twilio Sandbox (Şu an)
- Twilio WhatsApp Sandbox (ücretsiz, test)
- Müşteri `join <sandbox-code>` yazar
- In-memory session state
- Hizmet menüsü + tarih/saat flow
- Supabase kaydı YOK (sadece console.log)

**Sandbox bağlantısı:**
1. twilio.com/console → Messaging → Try it out → WhatsApp
2. QR kodu veya "join XXX-XXX" kodu müşteriye gönder
3. ngrok ile localhost:4001 → public URL
4. Twilio webhook URL: `https://xxxx.ngrok.io/v1/webhook/whatsapp`

## Phase 2 — Production
- Twilio WhatsApp Business API (veya 360dialog/WATI)
- Supabase `bookings` tablosu
- Kuaför dashboard (web admin panel)
- Müşteri geçmişi + hatırlatma mesajları

## Tech Stack
| Layer | Tech |
|---|---|
| Backend | Express + TypeScript |
| Messaging | Twilio WhatsApp |
| Database | Supabase (PostgreSQL) |
| Deploy | Render (aynı repo) |
| Mobile/Web | Sonraki phase |

## Supabase Schema (Phase 2)
```sql
create table bookings (
  id uuid primary key default gen_random_uuid(),
  customer_phone text not null,
  customer_name text not null,
  service text not null,
  booking_date text not null,
  booking_time text not null,
  status text not null default 'pending',
  created_at timestamptz not null default now()
);
```

## Endpoints
| Method | Path | Açıklama |
|---|---|---|
| POST | /v1/webhook/whatsapp | Twilio'dan gelen mesajlar |
| GET | /v1/bookings | Randevu listesi (admin) |
| GET | /health | Servis durumu |

## Hizmet Menüsü (Değiştirilebilir)
1. Saç Kesimi
2. Sakal Tıraşı
3. Saç + Sakal
4. Boya
