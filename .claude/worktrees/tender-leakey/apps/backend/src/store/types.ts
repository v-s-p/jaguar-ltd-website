export type Plan = "free" | "premium";

export type UserRecord = {
  id: string;
  email: string;
  plan: Plan;
};

export interface UserRepository {
  getUserById(userId: string): Promise<UserRecord | null>;
  getOrCreateByEmail(email: string, requestedPlan: Plan): Promise<UserRecord>;
  setUserPlanByIdentifier(identifier: string, plan: Plan): Promise<UserRecord | null>;
}
