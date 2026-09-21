import React, { useState } from "react";
import { Shield, LogIn, UserPlus, Users } from "lucide-react";
import type { User, UserRole } from "../types";
import { login, register, ApiError } from "../api/client";

interface Props {
  onAuthenticated: (user: User) => void;
}

const DEMO_ENABLED = String(import.meta.env.VITE_DEMO_PERSONAS ?? "true") === "true";

// Development-only seeded accounts (see backend/app/db/init_db.py). Hidden when
// VITE_DEMO_PERSONAS=false so UAT runs against real credentials.
const DEMO_PERSONAS: { role: UserRole; label: string; contact: string; password: string }[] = [
  { role: "CITIZEN", label: "Citizen — Fatu Kamara", contact: "citizen@freetown.sl", password: "CitizenPass123!" },
  { role: "MODERATOR", label: "Civic Moderator", contact: "moderator@salonefix.gov.sl", password: "ModPass123!" },
  { role: "OFFICER", label: "FCC Works Officer", contact: "officer.fcc@salonefix.gov.sl", password: "OfficerPass123!" },
  { role: "OFFICER", label: "SLRA Roads Officer", contact: "officer.slra@salonefix.gov.sl", password: "OfficerPass123!" },
  { role: "AUDITOR", label: "Independent Auditor", contact: "auditor@salonefix.gov.sl", password: "AuditorPass123!" },
  { role: "ADMIN", label: "System Administrator", contact: "admin@salonefix.gov.sl", password: "AdminPass123!" },
];

export const LoginView: React.FC<Props> = ({ onAuthenticated }) => {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [contact, setContact] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [consent, setConsent] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const describeError = (err: unknown): string => {
    if (err instanceof ApiError) {
      if (err.errorCode === "RATE_LIMITED") return "Too many attempts. Please wait a minute and try again.";
      return err.message;
    }
    return "Could not reach the SaloneFix server. Check that the API is running.";
  };

  const signIn = async (c: string, p: string) => {
    setBusy(true);
    setError(null);
    try {
      const res = await login(c, p);
      onAuthenticated(res.user);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setBusy(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (mode === "login") {
      await signIn(contact.trim(), password);
      return;
    }
    if (!consent) {
      setError("You must consent to the privacy notice to create an account.");
      return;
    }
    setBusy(true);
    setError(null);
    try {
      const res = await register({ name_or_alias: name.trim(), contact: contact.trim(), password, consent_status: consent });
      onAuthenticated(res.user);
    } catch (err) {
      setError(describeError(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "grid", placeItems: "center", padding: "24px 16px", backgroundColor: "var(--color-surface)" }}>
      <div style={{ width: "100%", maxWidth: "440px" }}>
        <div style={{ textAlign: "center", marginBottom: "24px" }}>
          <div aria-hidden="true" style={{
            width: 56, height: 56, borderRadius: 12, margin: "0 auto 12px",
            backgroundColor: "var(--color-primary)", color: "#fff", display: "grid", placeItems: "center",
          }}>
            <Shield size={30} />
          </div>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 800, letterSpacing: "-0.02em" }}>SaloneFix</h1>
          <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>
            Freetown public-service incident reporting
          </p>
        </div>

        <div className="card" style={{ padding: "24px" }}>
          <div role="tablist" aria-label="Authentication mode" style={{ display: "flex", gap: 8, marginBottom: 20 }}>
            <button
              type="button" role="tab" aria-selected={mode === "login"}
              className={`btn-sm ${mode === "login" ? "btn-primary" : "btn-secondary"}`}
              onClick={() => { setMode("login"); setError(null); }}
              style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}
            >
              <LogIn size={14} aria-hidden="true" /> Sign in
            </button>
            <button
              type="button" role="tab" aria-selected={mode === "register"}
              className={`btn-sm ${mode === "register" ? "btn-primary" : "btn-secondary"}`}
              onClick={() => { setMode("register"); setError(null); }}
              style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 6 }}
            >
              <UserPlus size={14} aria-hidden="true" /> Create citizen account
            </button>
          </div>

          <form onSubmit={handleSubmit} noValidate>
            {mode === "register" && (
              <div style={{ marginBottom: 14 }}>
                <label className="input-label" htmlFor="login-name">Name or alias</label>
                <input
                  id="login-name" className="input-field" value={name} required minLength={2} maxLength={120}
                  onChange={(e) => setName(e.target.value)} autoComplete="nickname"
                  placeholder="You may use an alias to protect your identity"
                />
              </div>
            )}
            <div style={{ marginBottom: 14 }}>
              <label className="input-label" htmlFor="login-contact">Email or phone</label>
              <input
                id="login-contact" className="input-field" value={contact} required autoComplete="username"
                onChange={(e) => setContact(e.target.value)} placeholder="you@example.sl"
              />
            </div>
            <div style={{ marginBottom: 14 }}>
              <label className="input-label" htmlFor="login-password">Password</label>
              <input
                id="login-password" className="input-field" type="password" value={password} required minLength={8}
                autoComplete={mode === "login" ? "current-password" : "new-password"}
                onChange={(e) => setPassword(e.target.value)}
                aria-describedby={mode === "register" ? "password-hint" : undefined}
              />
              {mode === "register" && (
                <p id="password-hint" style={{ fontSize: "0.75rem", color: "var(--color-text-muted)", marginTop: 4 }}>
                  At least 8 characters.
                </p>
              )}
            </div>
            {mode === "register" && (
              <label style={{ display: "flex", gap: 8, alignItems: "flex-start", fontSize: "0.8rem", marginBottom: 14, cursor: "pointer" }}>
                <input type="checkbox" checked={consent} onChange={(e) => setConsent(e.target.checked)} style={{ marginTop: 3 }} />
                <span>
                  I understand that my reports are reviewed by human moderators, that exact locations and photos are
                  visible only to verified responders, and that I can use an alias.
                </span>
              </label>
            )}

            {error && (
              <div role="alert" style={{
                backgroundColor: "var(--color-danger-bg)", color: "var(--color-danger)",
                padding: "10px 12px", borderRadius: "var(--radius-md)", fontSize: "0.85rem", marginBottom: 14,
              }}>
                {error}
              </div>
            )}

            <button type="submit" className="btn-primary" disabled={busy} style={{ width: "100%" }}>
              {busy ? "Please wait…" : mode === "login" ? "Sign in" : "Create account"}
            </button>
          </form>
        </div>

        {DEMO_ENABLED && (
          <div className="card" style={{ padding: "16px 20px", marginTop: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
              <Users size={16} color="var(--color-text-muted)" aria-hidden="true" />
              <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "var(--color-text-muted)", textTransform: "uppercase", letterSpacing: "0.04em" }}>
                Demo personas (development only)
              </span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: 8 }}>
              {DEMO_PERSONAS.map((p) => (
                <button
                  key={p.contact} type="button" className="btn-sm btn-secondary" disabled={busy}
                  onClick={() => signIn(p.contact, p.password)}
                  style={{ textAlign: "left", justifyContent: "flex-start" }}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
