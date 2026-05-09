import type { NextFunction, Request, Response } from "express";
import jwt from "jsonwebtoken";
import type { UserRepository } from "./store/types";

type JwtClaims = {
  sub: string;
  email: string;
  iat: number;
  exp: number;
};

const JWT_EXPIRES_IN = "12h";

export function signAccessToken(userId: string, email: string): string {
  const secret = process.env.JWT_SECRET;
  if (!secret) {
    throw new Error("JWT_SECRET is not configured");
  }
  return jwt.sign({ email }, secret, {
    subject: userId,
    expiresIn: JWT_EXPIRES_IN,
  });
}

export type AuthContext = {
  userId: string;
  email: string;
  plan: "free" | "premium";
};

export type AuthenticatedRequest = Request & {
  auth?: AuthContext;
};

export function requireAuth(userRepository: UserRepository) {
  return async (req: AuthenticatedRequest, res: Response, next: NextFunction): Promise<Response | void> => {
    const header = req.header("authorization");
    if (!header || !header.startsWith("Bearer ")) {
      return res.status(401).json({ error: "unauthorized", detail: "missing_bearer_token" });
    }

    const token = header.slice("Bearer ".length).trim();
    const secret = process.env.JWT_SECRET;
    if (!secret) {
      return res.status(500).json({ error: "server_misconfigured", detail: "missing_jwt_secret" });
    }

    try {
      const decoded = jwt.verify(token, secret) as JwtClaims;
      if (!decoded.sub || !decoded.email) {
        return res.status(401).json({ error: "unauthorized", detail: "invalid_token_claims" });
      }

      const user = await userRepository.getUserById(decoded.sub);
      if (!user) {
        return res.status(401).json({ error: "unauthorized", detail: "unknown_user" });
      }

      req.auth = {
        userId: user.id,
        email: user.email,
        plan: user.plan,
      };
      return next();
    } catch {
      return res.status(401).json({ error: "unauthorized", detail: "invalid_or_expired_token" });
    }
  };
}
