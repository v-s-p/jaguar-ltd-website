import "dotenv/config";
import cors from "cors";
import express from "express";
import helmet from "helmet";
import { buildRoutes } from "./routes";
import { createUserRepository } from "./store";

const app = express();
const port = Number(process.env.PORT ?? 4000);
const userRepository = createUserRepository();
const userRepositoryProvider = (process.env.USER_REPOSITORY_PROVIDER ?? "memory").toLowerCase();
const allowedOrigins = (process.env.ALLOWED_ORIGINS ?? "")
  .split(",")
  .map((value) => value.trim())
  .filter(Boolean);

app.use(helmet());
app.use(
  cors({
    origin: (origin, callback) => {
      if (!origin || allowedOrigins.length === 0 || allowedOrigins.includes(origin)) {
        callback(null, true);
        return;
      }
      callback(new Error("cors_origin_not_allowed"));
    },
  })
);
app.use(express.json({ limit: "1mb" }));

app.get("/health", (_req, res) => {
  res.json({ ok: true, service: "s8-backend", repository: userRepositoryProvider });
});

app.use("/v1", buildRoutes(userRepository));
app.use((err: Error, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  console.error("unhandled_request_error", err.message);
  res.status(500).json({ error: "internal_server_error" });
});

app.listen(port, () => {
  console.log(`s8 backend listening on :${port} using ${userRepositoryProvider} repository`);
});
