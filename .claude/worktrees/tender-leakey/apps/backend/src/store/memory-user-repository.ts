import type { Plan, UserRecord, UserRepository } from "./types";

const seededUsers = new Map<string, UserRecord>([
  [
    "u_free_demo",
    {
      id: "u_free_demo",
      email: "free@s8.local",
      plan: "free",
    },
  ],
  [
    "u_premium_demo",
    {
      id: "u_premium_demo",
      email: "premium@s8.local",
      plan: "premium",
    },
  ],
]);

export class MemoryUserRepository implements UserRepository {
  private readonly users = seededUsers;

  async getUserById(userId: string): Promise<UserRecord | null> {
    return this.users.get(userId) ?? null;
  }

  async getOrCreateByEmail(email: string, requestedPlan: Plan): Promise<UserRecord> {
    const existing = Array.from(this.users.values()).find((user) => user.email.toLowerCase() === email.toLowerCase());
    if (existing) {
      const nextPlan: Plan = existing.plan === "premium" && requestedPlan === "free"
        ? "premium"
        : requestedPlan;
      existing.plan = nextPlan;
      this.users.set(existing.id, existing);
      return existing;
    }

    const id = `u_${email.toLowerCase().replace(/[^a-z0-9]/g, "_")}`;
    const next: UserRecord = {
      id,
      email,
      plan: requestedPlan,
    };
    this.users.set(id, next);
    return next;
  }

  async setUserPlanByIdentifier(identifier: string, plan: Plan): Promise<UserRecord | null> {
    const byId = this.users.get(identifier);
    if (byId) {
      byId.plan = plan;
      this.users.set(byId.id, byId);
      return byId;
    }

    const byEmail = Array.from(this.users.values()).find((user) => user.email.toLowerCase() === identifier.toLowerCase());
    if (byEmail) {
      byEmail.plan = plan;
      this.users.set(byEmail.id, byEmail);
      return byEmail;
    }

    if (identifier.includes("@")) {
      return this.getOrCreateByEmail(identifier, plan);
    }
    return null;
  }
}
