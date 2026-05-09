import * as SecureStore from "expo-secure-store";
import { createClient } from "@supabase/supabase-js";
import { useEffect, useMemo, useRef, useState } from "react";
import Purchases, { type CustomerInfo } from "react-native-purchases";
import { ActivityIndicator, Linking, Platform, SafeAreaView, ScrollView, StyleSheet, Text, TextInput, TouchableOpacity, View } from "react-native";

declare const process: {
  env?: Record<string, string | undefined>;
};

type Plan = "free" | "premium";
type MatchItem = {
  id: number;
  home: string;
  away: string;
  prediction: string;
  xgHome: number;
  xgAway: number;
};
type Prediction = {
  id: number;
  bulletin_id: string;
  match_id: number;
  match_name: string;
  prediction: string;
  analysis_text: string;
  status: string;
};

type RecoveryTokens = {
  accessToken: string;
  refreshToken: string;
  type: string;
};

const TOKEN_KEY = "s8_access_token";
const apiFromEnv = process?.env?.EXPO_PUBLIC_API_BASE_URL;
const API_BASE_URL = String(apiFromEnv ?? "https://s8-professor-app.onrender.com").replace(/\/+$/, "");
const SUPABASE_URL = String(process?.env?.EXPO_PUBLIC_SUPABASE_URL ?? "");
const SUPABASE_PUBLISHABLE_KEY = String(process?.env?.EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY ?? "");
const REVENUECAT_IOS_API_KEY = String(process?.env?.EXPO_PUBLIC_REVENUECAT_API_KEY_IOS ?? "");
const REVENUECAT_ANDROID_API_KEY = String(process?.env?.EXPO_PUBLIC_REVENUECAT_API_KEY_ANDROID ?? "");
const REVENUECAT_ENTITLEMENT_ID = String(process?.env?.EXPO_PUBLIC_REVENUECAT_ENTITLEMENT_ID ?? "premium");
const PASSWORD_RESET_REDIRECT = String(
  process?.env?.EXPO_PUBLIC_PASSWORD_RESET_REDIRECT_URL ?? "s8professor://reset-password"
);
const IOS_SUBSCRIPTION_MANAGE_URL = "https://apps.apple.com/account/subscriptions";
const ANDROID_SUBSCRIPTION_MANAGE_URL = "https://play.google.com/store/account/subscriptions";
const DEFAULT_SUBSCRIPTION_INFO_URL = "https://s8-professor-app.onrender.com/health";
const PREMIUM_INFO_MESSAGE = "Premium satin alma ve restore RevenueCat ile calisir (dev/prod build gerekli).";
const supabase = SUPABASE_URL && SUPABASE_PUBLISHABLE_KEY
  ? createClient(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY, { auth: { persistSession: true } })
  : null;
const SAMPLE_MATCHES = [
  { home: "Galatasaray", away: "Fenerbahce" },
  { home: "Besiktas", away: "Trabzonspor" },
  { home: "Basaksehir", away: "Kasimpasa" },
  { home: "Antalyaspor", away: "Konyaspor" },
  { home: "Samsunspor", away: "Rizespor" },
];

export default function App() {
  const [plan, setPlan] = useState<Plan | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [email, setEmail] = useState("free@s8.local");
  const [password, setPassword] = useState("ChangeMe123!");
  const [newPassword, setNewPassword] = useState("");
  const [newPasswordConfirm, setNewPasswordConfirm] = useState("");
  const [isRecoveryMode, setIsRecoveryMode] = useState(false);
  const [matches, setMatches] = useState<MatchItem[]>([]);
  const [coupons, setCoupons] = useState<string[]>([]);
  const [weeklyPredictions, setWeeklyPredictions] = useState<Prediction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [info, setInfo] = useState<string | null>(null);
  const purchasesConfigured = useRef(false);
  const purchasesUserId = useRef<string | null>(null);

  const description = useMemo(() => {
    if (!plan) {
      return "Supabase ile giris yap, sonra backend tokeni al ve analiz calistir.";
    }
    if (plan === "premium") {
      return "Tum maclar + genisletilmis istatistikler + 4 kupon onerisi aktif.";
    }
    return "Freemium mod: ilk 3 mac ve temel tahminler gosterilir.";
  }, [plan]);

  useEffect(() => {
    void bootstrapFromStorage();
  }, []);

  useEffect(() => {
    if (!supabase) {
      return;
    }

    const parseRecoveryTokens = (url: string): RecoveryTokens | null => {
      const [rawPath, rawFragment] = url.split("#");
      const queryString = rawPath.includes("?") ? rawPath.split("?")[1] : "";
      const fragmentString = rawFragment ?? "";
      const merged = new URLSearchParams([queryString, fragmentString].filter(Boolean).join("&"));
      const accessToken = merged.get("access_token");
      const refreshToken = merged.get("refresh_token");
      const type = merged.get("type");
      if (!accessToken || !refreshToken || !type) {
        return null;
      }
      return { accessToken, refreshToken, type };
    };

    const handleIncomingUrl = async (url: string) => {
      const parsed = parseRecoveryTokens(url);
      if (!parsed || parsed.type !== "recovery") {
        return;
      }
      const { error: sessionErr } = await supabase.auth.setSession({
        access_token: parsed.accessToken,
        refresh_token: parsed.refreshToken,
      });
      if (sessionErr) {
        setError(sessionErr.message);
        return;
      }
      setIsRecoveryMode(true);
      setInfo("password_recovery_ready_set_new_password");
      setError(null);
    };

    const subscription = Linking.addEventListener("url", ({ url }) => {
      void handleIncomingUrl(url);
    });

    void (async () => {
      const initialUrl = await Linking.getInitialURL();
      if (initialUrl) {
        await handleIncomingUrl(initialUrl);
      }
    })();

    const { data: authListener } = supabase.auth.onAuthStateChange((event) => {
      if (event === "PASSWORD_RECOVERY") {
        setIsRecoveryMode(true);
        setInfo("password_recovery_ready_set_new_password");
      }
    });

    return () => {
      subscription.remove();
      authListener.subscription.unsubscribe();
    };
  }, []);

  async function bootstrapFromStorage() {
    const stored = await SecureStore.getItemAsync(TOKEN_KEY);
    if (!stored) {
      return;
    }
    setToken(stored);
    const payload = await loadPlan(stored);
    if (payload?.email) {
      try {
        await ensureRevenueCatConfigured(String(payload.email));
      } catch {
        setInfo("revenuecat_not_ready_in_this_build");
      }
    }
  }

  function getRevenueCatApiKey(): string {
    if (Platform.OS === "ios") {
      return REVENUECAT_IOS_API_KEY;
    }
    if (Platform.OS === "android") {
      return REVENUECAT_ANDROID_API_KEY;
    }
    return "";
  }

  function hasPremiumEntitlement(customerInfo: CustomerInfo): boolean {
    return Boolean(customerInfo.entitlements.active[REVENUECAT_ENTITLEMENT_ID]);
  }

  async function ensureRevenueCatConfigured(appUserId: string) {
    const apiKey = getRevenueCatApiKey();
    if (!apiKey) {
      throw new Error("revenuecat_api_key_missing");
    }

    if (!purchasesConfigured.current) {
      Purchases.configure({ apiKey, appUserID: appUserId });
      purchasesConfigured.current = true;
      purchasesUserId.current = appUserId;
      return;
    }

    if (purchasesUserId.current !== appUserId) {
      await Purchases.logIn(appUserId);
      purchasesUserId.current = appUserId;
    }
  }

  async function exchangeSupabaseToken(providerAccessToken: string) {
    const response = await fetch(`${API_BASE_URL}/v1/auth/exchange`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ provider: "supabase", accessToken: providerAccessToken }),
    });
    if (!response.ok) {
      throw new Error(`exchange_failed_${response.status}`);
    }
    const payload = await response.json();
    const nextToken = String(payload.accessToken);
    const nextEmail = String(payload.user?.email ?? email);
    setToken(nextToken);
    setEmail(nextEmail);
    await SecureStore.setItemAsync(TOKEN_KEY, nextToken);
    try {
      await ensureRevenueCatConfigured(nextEmail);
    } catch {
      setInfo("revenuecat_not_ready_in_this_build");
    }
    await loadPlan(nextToken);
  }

  async function login() {
    setLoading(true);
    setError(null);
    setInfo(null);
    try {
      if (!supabase) {
        throw new Error("supabase_config_missing");
      }
      const { data, error: signInError } = await supabase.auth.signInWithPassword({ email, password });
      if (signInError || !data.session?.access_token) {
        throw new Error(signInError?.message ?? "supabase_login_failed");
      }
      await exchangeSupabaseToken(data.session.access_token);
    } catch (e) {
      setError(e instanceof Error ? e.message : "login_failed");
    } finally {
      setLoading(false);
    }
  }

  async function signUp() {
    setLoading(true);
    setError(null);
    setInfo(null);
    try {
      if (!supabase) {
        throw new Error("supabase_config_missing");
      }
      const { data, error: signUpError } = await supabase.auth.signUp({ email, password });
      if (signUpError) {
        throw new Error(signUpError.message);
      }
      if (data.session?.access_token) {
        await exchangeSupabaseToken(data.session.access_token);
      } else {
        setInfo("signup_ok_check_email_verification");
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "signup_failed");
    } finally {
      setLoading(false);
    }
  }

  async function logout() {
    setToken(null);
    setPlan(null);
    setMatches([]);
    setCoupons([]);
    setError(null);
    setInfo(null);
    await SecureStore.deleteItemAsync(TOKEN_KEY);
    if (supabase) {
      await supabase.auth.signOut();
    }
    if (purchasesConfigured.current) {
      try {
        await Purchases.logOut();
      } catch {
        // Ignore native purchase logout errors during local/dev fallback.
      }
      purchasesUserId.current = null;
    }
  }

  async function sendPasswordReset() {
    setLoading(true);
    setError(null);
    setInfo(null);
    try {
      if (!supabase) {
        throw new Error("supabase_config_missing");
      }
      const { error: resetErr } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: PASSWORD_RESET_REDIRECT,
      });
      if (resetErr) {
        throw new Error(resetErr.message);
      }
      setInfo("password_reset_email_sent");
    } catch (e) {
      setError(e instanceof Error ? e.message : "password_reset_failed");
    } finally {
      setLoading(false);
    }
  }

  async function submitNewPassword() {
    setLoading(true);
    setError(null);
    setInfo(null);
    try {
      if (!supabase) {
        throw new Error("supabase_config_missing");
      }
      if (newPassword.length < 8) {
        throw new Error("password_min_8_chars");
      }
      if (newPassword !== newPasswordConfirm) {
        throw new Error("password_confirmation_mismatch");
      }
      const { error: updateErr } = await supabase.auth.updateUser({ password: newPassword });
      if (updateErr) {
        throw new Error(updateErr.message);
      }
      setIsRecoveryMode(false);
      setNewPassword("");
      setNewPasswordConfirm("");
      setInfo("password_updated_login_with_new_password");
    } catch (e) {
      setError(e instanceof Error ? e.message : "password_update_failed");
    } finally {
      setLoading(false);
    }
  }

  async function loadPlan(usedToken: string) {
    const response = await fetch(`${API_BASE_URL}/v1/me/plan`, {
      headers: { Authorization: `Bearer ${usedToken}` },
    });
    if (!response.ok) {
      throw new Error(`plan_fetch_failed_${response.status}`);
    }
    const payload = await response.json();
    setPlan(payload.plan as Plan);
    if (payload.email) {
      setEmail(String(payload.email));
    }
    return payload;
  }

  async function restoreAccess() {
    setLoading(true);
    setError(null);
    setInfo(null);
    try {
      if (token && email) {
        await ensureRevenueCatConfigured(email);
        const customerInfo = await Purchases.restorePurchases();
        const hasPremium = hasPremiumEntitlement(customerInfo);
        await loadPlan(token);
        setInfo(hasPremium ? "restore_purchase_ok_plan_refresh_requested" : "restore_done_no_active_premium");
        return;
      }

      if (token) {
        await loadPlan(token);
        setInfo("plan_refreshed_from_backend");
        return;
      }
      if (!supabase) {
        throw new Error("supabase_config_missing");
      }
      const { data, error: sessionErr } = await supabase.auth.getSession();
      if (sessionErr || !data.session?.access_token) {
        throw new Error(sessionErr?.message ?? "no_active_supabase_session");
      }
      await exchangeSupabaseToken(data.session.access_token);
      setInfo("session_restored_and_plan_refreshed");
    } catch (e) {
      setError(e instanceof Error ? e.message : "restore_failed");
    } finally {
      setLoading(false);
    }
  }

  async function openManageSubscription() {
    const url = Platform.OS === "ios"
      ? IOS_SUBSCRIPTION_MANAGE_URL
      : Platform.OS === "android"
        ? ANDROID_SUBSCRIPTION_MANAGE_URL
        : DEFAULT_SUBSCRIPTION_INFO_URL;

    const canOpen = await Linking.canOpenURL(url);
    if (!canOpen) {
      setError("manage_subscription_url_unavailable");
      return;
    }
    await Linking.openURL(url);
  }

  async function purchasePremium() {
    setLoading(true);
    setError(null);
    setInfo(null);
    try {
      if (!token) {
        throw new Error("not_authenticated");
      }
      if (!email) {
        throw new Error("missing_user_email");
      }

      await ensureRevenueCatConfigured(email);
      const offerings = await Purchases.getOfferings();
      const selectedPackage = offerings.current?.availablePackages[0];
      if (!selectedPackage) {
        throw new Error("no_available_package");
      }

      const { customerInfo } = await Purchases.purchasePackage(selectedPackage);
      const hasPremium = hasPremiumEntitlement(customerInfo);
      await loadPlan(token);
      setInfo(hasPremium ? "purchase_ok_plan_refresh_requested" : "purchase_ok_entitlement_missing");
    } catch (e) {
      setError(e instanceof Error ? e.message : "purchase_failed");
    } finally {
      setLoading(false);
    }
  }

  async function runAnalyze() {
    if (!token) {
      setError("not_authenticated");
      return;
    }
    setLoading(true);
    setError(null);
    setInfo(null);
    try {
      const response = await fetch(`${API_BASE_URL}/v1/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ matches: SAMPLE_MATCHES }),
      });
      if (!response.ok) {
        throw new Error(`analyze_failed_${response.status}`);
      }
      const payload = await response.json();
      setPlan(payload.plan as Plan);
      setMatches(payload.matches as MatchItem[]);
      setCoupons(payload.coupons as string[]);
    } catch (e) {
      setError(e instanceof Error ? e.message : "analyze_failed");
    } finally {
      setLoading(false);
    }
  }

  async function fetchWeeklyPredictions() {
    if (loading) return;
    setLoading(true);
    setError(null);
    setInfo(null);
    try {
      const response = await fetch(`${API_BASE_URL}/v1/predictions/latest`);
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail ?? `fetch_failed_${response.status}`);
      }
      const payload = await response.json();
      setWeeklyPredictions(payload.predictions as Prediction[]);
      setInfo(`Bulletin ${payload.bulletinId} loaded.`);
    } catch (e) {
      setError(e instanceof Error ? e.message : "fetch_weekly_failed");
      setWeeklyPredictions([]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scroll}>
        <Text style={styles.title}>S8 Professor</Text>
        <Text style={styles.subtitle}>Auth + Plan Flow</Text>

        {isRecoveryMode ? (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Set New Password</Text>
            <Text style={styles.label}>New Password</Text>
            <TextInput
              value={newPassword}
              onChangeText={setNewPassword}
              style={styles.input}
              autoCapitalize="none"
              secureTextEntry
            />
            <Text style={styles.label}>Confirm New Password</Text>
            <TextInput
              value={newPasswordConfirm}
              onChangeText={setNewPasswordConfirm}
              style={styles.input}
              autoCapitalize="none"
              secureTextEntry
            />
            <TouchableOpacity style={styles.primaryButton} onPress={submitNewPassword} disabled={loading}>
              <Text style={styles.buttonText}>Update Password</Text>
            </TouchableOpacity>
          </View>
        ) : null}

        <View style={styles.card}>
          <Text style={styles.label}>Email</Text>
          <TextInput value={email} onChangeText={setEmail} style={styles.input} autoCapitalize="none" />
          <Text style={styles.label}>Password</Text>
          <TextInput
            value={password}
            onChangeText={setPassword}
            style={styles.input}
            autoCapitalize="none"
            secureTextEntry
          />
          <View style={styles.row}>
            <TouchableOpacity style={styles.button} onPress={login} disabled={loading}>
              <Text style={styles.buttonText}>Login</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.button} onPress={signUp} disabled={loading}>
              <Text style={styles.buttonText}>Sign Up</Text>
            </TouchableOpacity>
          </View>
          <TouchableOpacity style={styles.secondaryButton} onPress={sendPasswordReset} disabled={loading}>
            <Text style={styles.buttonText}>Forgot Password</Text>
          </TouchableOpacity>
          {token ? (
            <TouchableOpacity style={styles.secondaryButton} onPress={logout} disabled={loading}>
              <Text style={styles.buttonText}>Logout</Text>
            </TouchableOpacity>
          ) : null}
        </View>

        <View style={styles.card}>
          <Text style={styles.badge}>{plan ? plan.toUpperCase() : "NOT AUTHENTICATED"}</Text>
          <Text style={styles.description}>{description}</Text>
          <Text style={styles.note}>{PREMIUM_INFO_MESSAGE}</Text>
          <TouchableOpacity style={styles.primaryButton} onPress={purchasePremium} disabled={loading || !token}>
            <Text style={styles.buttonText}>Upgrade to Premium</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.primaryButton} onPress={runAnalyze} disabled={loading || !token}>
            <Text style={styles.buttonText}>Run Analyze</Text>
          </TouchableOpacity>
          <View style={styles.row}>
            <TouchableOpacity style={styles.button} onPress={restoreAccess} disabled={loading}>
              <Text style={styles.buttonText}>Restore Access</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.button} onPress={openManageSubscription} disabled={loading}>
              <Text style={styles.buttonText}>Manage Subscription</Text>
            </TouchableOpacity>
          </View>
          {loading ? <ActivityIndicator color="#8de7bf" style={styles.loader} /> : null}
          {error ? <Text style={styles.error}>{error}</Text> : null}
          {info ? <Text style={styles.info}>{info}</Text> : null}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Matches ({matches.length})</Text>
          {matches.map((m) => (
            <Text key={m.id} style={styles.listItem}>
              {m.home} - {m.away} | {m.prediction} | xG {m.xgHome.toFixed(2)}-{m.xgAway.toFixed(2)}
            </Text>
          ))}
          <Text style={styles.sectionTitle}>Coupons ({coupons.length})</Text>
          {coupons.map((c) => (
            <Text key={c} style={styles.listItem}>
              {c}
            </Text>
          ))}
        </View>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Haftalık Bülten</Text>
          <TouchableOpacity style={styles.primaryButton} onPress={fetchWeeklyPredictions} disabled={loading}>
            <Text style={styles.buttonText}>Haftanın Tahminlerini Getir</Text>
          </TouchableOpacity>
          {weeklyPredictions.map((p) => (
            <Text key={p.id} style={styles.listItem}>
              {p.match_id}. {p.match_name}: {p.prediction}
            </Text>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#09121f",
  },
  scroll: {
    padding: 24,
  },
  title: {
    color: "#d9fce9",
    fontSize: 30,
    fontWeight: "700",
    marginBottom: 12,
  },
  subtitle: {
    color: "#a7f3d0",
    marginBottom: 14,
  },
  note: {
    color: "#a7f3d0",
    marginBottom: 14,
  },
  card: {
    backgroundColor: "#0f1c2b",
    borderWidth: 1,
    borderColor: "#1d3348",
    borderRadius: 12,
    padding: 14,
    marginBottom: 14,
  },
  label: {
    color: "#cce5ff",
    marginBottom: 8,
  },
  input: {
    backgroundColor: "#14263a",
    color: "#e7eef9",
    borderWidth: 1,
    borderColor: "#254562",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    marginBottom: 12,
  },
  badge: {
    color: "#8de7bf",
    borderWidth: 1,
    borderColor: "#2b8c62",
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    marginBottom: 16,
  },
  description: {
    color: "#e7eef9",
    fontSize: 16,
    textAlign: "center",
    marginBottom: 24,
  },
  row: {
    flexDirection: "row",
    gap: 10,
    marginBottom: 10,
  },
  button: {
    backgroundColor: "#13422f",
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  primaryButton: {
    backgroundColor: "#14532d",
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 10,
    marginBottom: 8,
  },
  secondaryButton: {
    backgroundColor: "#374151",
    borderRadius: 10,
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  buttonText: {
    color: "#dcfce7",
    fontWeight: "600",
    textAlign: "center",
  },
  sectionTitle: {
    color: "#a7f3d0",
    marginBottom: 8,
    fontWeight: "700",
  },
  listItem: {
    color: "#e7eef9",
    marginBottom: 6,
  },
  loader: {
    marginTop: 8,
  },
  error: {
    color: "#fca5a5",
    marginTop: 8,
  },
  info: {
    color: "#93c5fd",
    marginTop: 8,
  },
});
