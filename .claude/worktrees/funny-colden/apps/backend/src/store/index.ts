import { MemoryUserRepository } from "./memory-user-repository";
import { SupabaseUserRepository } from "./supabase-user-repository";
import type { UserRepository } from "./types";

export function createUserRepository(): UserRepository {
  const provider = (process.env.USER_REPOSITORY_PROVIDER ?? "memory").toLowerCase();
  if (provider === "supabase") {
    const url = process.env.SUPABASE_URL;
    const serviceRole = process.env.SUPABASE_SERVICE_ROLE_KEY;
    if (!url || !serviceRole) {
      throw new Error("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required for supabase provider");
    }
    return new SupabaseUserRepository(url, serviceRole);
  }
  return new MemoryUserRepository();
}
