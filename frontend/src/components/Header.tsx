import React from "react";
import { Shield, CheckCircle2, LogOut, UserCircle2 } from "lucide-react";
import type { User } from "../types";

interface Props {
  currentUser: User | null;
  onSignOut: () => void;
}

const ROLE_LABELS: Record<string, string> = {
  CITIZEN: "Citizen",
  MODERATOR: "Civic Moderator",
  OFFICER: "Institutional Officer",
  AUDITOR: "Independent Auditor",
  ADMIN: "System Administrator",
};

export const Header: React.FC<Props> = ({ currentUser, onSignOut }) => {
  return (
    <header style={{
      backgroundColor: "#ffffff",
      borderBottom: "1px solid var(--color-border)",
      padding: "12px 24px",
      boxShadow: "var(--shadow-sm)",
      position: "sticky",
      top: 0,
      zIndex: 100,
    }}>
      <div style={{
        maxWidth: "1200px",
        margin: "0 auto",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        flexWrap: "wrap",
        gap: "16px",
      }}>
        {/* Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div style={{
            width: "40px",
            height: "40px",
            borderRadius: "8px",
            backgroundColor: "var(--color-primary)",
            color: "#ffffff",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontWeight: 700,
          }} aria-hidden="true">
            <Shield size={22} />
          </div>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <span style={{ fontSize: "1.25rem", fontWeight: 700, color: "var(--color-text)", letterSpacing: "-0.02em" }}>
                SaloneFix
              </span>
              <span style={{
                fontSize: "0.7rem",
                backgroundColor: "#F2F4F7",
                color: "#344054",
                padding: "2px 6px",
                borderRadius: "4px",
                fontWeight: 600,
              }}>
                FREETOWN
              </span>
            </div>
            <p style={{ fontSize: "0.75rem", color: "var(--color-text-muted)" }}>
              Public-Service Incident Management Platform
            </p>
          </div>
        </div>

        {/* Phase indicator & signed-in identity */}
        <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
          <div style={{
            display: "flex",
            alignItems: "center",
            gap: "6px",
            fontSize: "0.75rem",
            backgroundColor: "var(--color-success-bg)",
            color: "var(--color-success)",
            padding: "4px 10px",
            borderRadius: "9999px",
            fontWeight: 600,
            border: "1px solid rgba(24, 121, 78, 0.2)",
          }}>
            <CheckCircle2 size={13} aria-hidden="true" />
            <span>Human-First Foundation (AI &amp; WhatsApp Disabled)</span>
          </div>

          {currentUser && (
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              backgroundColor: "var(--color-surface)",
              padding: "4px 8px 4px 10px",
              borderRadius: "var(--radius-md)",
              border: "1px solid var(--color-border)",
            }}>
              <UserCircle2 size={18} color="var(--color-primary)" aria-hidden="true" />
              <div style={{ lineHeight: 1.2 }}>
                <div style={{ fontSize: "0.85rem", fontWeight: 700, color: "var(--color-text)" }}>
                  {currentUser.name_or_alias}
                </div>
                <div style={{ fontSize: "0.7rem", color: "var(--color-text-muted)" }}>
                  {ROLE_LABELS[currentUser.role] ?? currentUser.role}
                  {currentUser.institution_name ? ` · ${currentUser.institution_name}` : ""}
                </div>
              </div>
              <button
                type="button"
                className="btn-sm btn-secondary"
                onClick={onSignOut}
                aria-label="Sign out"
                style={{ display: "flex", alignItems: "center", gap: "4px" }}
              >
                <LogOut size={14} aria-hidden="true" /> Sign out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};
