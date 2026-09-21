import React, { useEffect, useState } from "react";
import type { User } from "./types";
import { getAuthToken, getMe, logout } from "./api/client";
import { Header } from "./components/Header";
import { LoginView } from "./pages/LoginView";
import { CitizenView } from "./pages/CitizenView";
import { ModeratorView } from "./pages/ModeratorView";
import { OfficerView } from "./pages/OfficerView";
import { AuditorView } from "./pages/AuditorView";
import { AdminView } from "./pages/AdminView";

type AuthState = { status: "checking" } | { status: "anonymous" } | { status: "authenticated"; user: User };

export const App: React.FC = () => {
  // Restore the session from a stored token once on load; a stale/expired
  // token simply drops the user back to the login screen.
  const [auth, setAuth] = useState<AuthState>(() => (getAuthToken() ? { status: "checking" } : { status: "anonymous" }));

  useEffect(() => {
    if (auth.status !== "checking") return;
    let cancelled = false;
    getMe()
      .then((user) => { if (!cancelled) setAuth({ status: "authenticated", user }); })
      .catch(() => { if (!cancelled) { logout(); setAuth({ status: "anonymous" }); } });
    return () => { cancelled = true; };
  }, [auth.status]);

  const handleSignOut = () => {
    logout();
    setAuth({ status: "anonymous" });
  };

  if (auth.status === "checking") {
    return (
      <div role="status" aria-live="polite" style={{ minHeight: "100vh", display: "grid", placeItems: "center", color: "var(--color-text-muted)" }}>
        Restoring your session…
      </div>
    );
  }

  if (auth.status === "anonymous") {
    return <LoginView onAuthenticated={(user) => setAuth({ status: "authenticated", user })} />;
  }

  const { user } = auth;

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <a href="#main-content" className="skip-link">Skip to main content</a>
      <Header currentUser={user} onSignOut={handleSignOut} />

      <main id="main-content" style={{ flex: 1, padding: "24px 16px" }} tabIndex={-1}>
        <div className="container">
          {user.role === "CITIZEN" && <CitizenView />}
          {user.role === "MODERATOR" && <ModeratorView />}
          {user.role === "OFFICER" && <OfficerView currentUser={user} />}
          {user.role === "AUDITOR" && <AuditorView />}
          {user.role === "ADMIN" && <AdminView currentUser={user} />}
        </div>
      </main>

      <footer style={{
        borderTop: "1px solid var(--color-border)",
        backgroundColor: "#ffffff",
        padding: "16px 24px",
        marginTop: "auto",
        fontSize: "0.8rem",
        color: "var(--color-text-muted)",
        textAlign: "center",
      }}>
        <div className="container">
          SaloneFix Freetown Prototype • Phase 1: Human-First Foundation Launch (AI &amp; WhatsApp Disabled) • WCAG 2.2 AA target
        </div>
      </footer>
    </div>
  );
};

export default App;
