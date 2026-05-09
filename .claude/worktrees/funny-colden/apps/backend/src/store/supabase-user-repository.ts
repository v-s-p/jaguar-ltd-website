import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import type { Plan, UserRecord, UserRepository } from "./types";

type ProfileRow = {
  id: string;
  email: string;
  plan: Plan;
};

export class SupabaseUserRepository implements UserRepository {
  private readonly client: SupabaseClient;

  constructor(url: string, serviceRoleKey: string) {
    this.client = createClient(url, serviceRoleKey, {
      auth: { persistSession: false },
    });
  }

  async getUserById(userId: string): Promise<UserRecord | null> {
    const { data, error } = await this.client
      .from("profiles")
      .select("id,email,plan")
      .eq("id", userId)
      .maybeSingle<ProfileRow>();

    if (error) {
      throw new Error(`supabase_get_user_by_id_failed:${error.message}`);
    }
    if (!data) {
      return null;
    }
    return { id: data.id, email: data.email, plan: data.plan };
  }

  async getOrCreateByEmail(email: string, requestedPlan: Plan): Promise<UserRecord> {
    const { data: existing, error: readErr } = await this.client
      .from("profiles")
      .select("id,email,plan")
      .eq("email", email)
      .maybeSingle<ProfileRow>();

    if (readErr) {
      throw new Error(`supabase_get_user_by_email_failed:${readErr.message}`);
    }

    if (existing) {
      const nextPlan: Plan = existing.plan === "premium" && requestedPlan === "free"
        ? "premium"
        : requestedPlan;

      if (existing.plan !== nextPlan) {
        const { error: updateErr } = await this.client
          .from("profiles")
          .update({ plan: nextPlan })
          .eq("id", existing.id);
        if (updateErr) {
          throw new Error(`supabase_update_plan_failed:${updateErr.message}`);
        }
      }
      return {
        id: existing.id,
        email: existing.email,
        plan: nextPlan,
      };
    }

    const newUser: ProfileRow = {
      id: crypto.randomUUID(),
      email,
      plan: requestedPlan,
    };
    const { data: inserted, error: insertErr } = await this.client
      .from("profiles")
      .insert(newUser)
      .select("id,email,plan")
      .single<ProfileRow>();

    if (insertErr) {
      throw new Error(`supabase_insert_user_failed:${insertErr.message}`);
    }
    return {
      id: inserted.id,
      email: inserted.email,
      plan: inserted.plan,
    };
  }

  async setUserPlanByIdentifier(identifier: string, plan: Plan): Promise<UserRecord | null> {
    const isEmail = identifier.includes("@");
    const selector = isEmail ? { column: "email", value: identifier } : { column: "id", value: identifier };

    const { data: found, error: readErr } = await this.client
      .from("profiles")
      .select("id,email,plan")
      .eq(selector.column, selector.value)
      .maybeSingle<ProfileRow>();

    if (readErr) {
      throw new Error(`supabase_select_by_identifier_failed:${readErr.message}`);
    }

    if (!found) {
      if (!isEmail) {
        return null;
      }
      return this.getOrCreateByEmail(identifier, plan);
    }

    const { error: updateErr } = await this.client
      .from("profiles")
      .update({ plan })
      .eq("id", found.id);

    if (updateErr) {
      throw new Error(`supabase_set_plan_failed:${updateErr.message}`);
    }

    return {
      id: found.id,
      email: found.email,
      plan,
    };
  }
}
