import "dotenv/config";
import express from "express";
import helmet from "helmet";
import cors from "cors";
import { router } from "./routes";

const app = express();
const PORT = process.env.PORT ?? 4001;

app.use(helmet());
app.use(cors());

// Twilio webhook sends application/x-www-form-urlencoded
app.use(express.urlencoded({ extended: false }));
app.use(express.json());

app.get("/health", (_req, res) => {
  res.json({ ok: true, service: "kuafor-backend" });
});

app.use("/v1", router);

app.listen(PORT, () => {
  console.log(`kuafor-backend listening on :${PORT}`);
});
