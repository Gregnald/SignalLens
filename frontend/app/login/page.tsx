"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { api, ApiError } from "@/lib/api";
import { Button } from "@/components/ui/button";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("demo@signallens.app");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.login(email, password);
      window.localStorage.setItem("signallens.token", res.access_token);
      router.push("/dashboard");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm rounded-lg border border-border bg-card p-8 shadow-sm"
      >
        <h1 className="text-xl font-semibold">SignalLens</h1>
        <p className="mb-6 text-sm text-muted-foreground">
          Sign in as the Flipkart enterprise admin to analyze your product catalog.
        </p>

        <label className="mb-1 block text-xs font-medium text-muted-foreground">Email</label>
        <input
          className="mb-4 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <label className="mb-1 block text-xs font-medium text-muted-foreground">Password</label>
        <input
          type="password"
          className="mb-4 w-full rounded-lg border border-border bg-background px-3 py-2 text-sm"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="See .env.example / README for the demo password"
        />

        {error && <p className="mb-4 text-xs text-critical">{error}</p>}

        <Button type="submit" className="w-full" disabled={loading}>
          {loading ? "Signing in…" : "Sign in"}
        </Button>

        <p className="mt-4 text-center text-xs text-muted-foreground">
          Demo-only account — see README for credentials.
        </p>
      </form>
    </div>
  );
}
