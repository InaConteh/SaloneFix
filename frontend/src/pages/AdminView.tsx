import React, { useState, useEffect, useCallback } from "react";
import { Settings2, UserPlus, Building2, Users, ShieldCheck, FolderKanban, Inbox } from "lucide-react";
import type { Institution, User, UserRole } from "../types";
import {
  adminListUsers,
  adminCreateStaffUser,
  adminUpdateUser,
  adminCreateInstitution,
  adminUpdateInstitution,
  getInstitutions,
  ApiError,
} from "../api/client";
import { ModeratorView } from "./ModeratorView";

interface Props {
  currentUser: User;
}

type Tab = "users" | "institutions" | "moderation";

const STAFF_ROLES: UserRole[] = ["MODERATOR", "OFFICER", "AUDITOR", "ADMIN"];

const describeError = (err: unknown, fallback: string) =>
  err instanceof ApiError ? err.message : err instanceof Error ? err.message : fallback;

export const AdminView: React.FC<Props> = ({ currentUser }) => {
  const [tab, setTab] = useState<Tab>("users");
  const [users, setUsers] = useState<User[]>([]);
  const [usersTotal, setUsersTotal] = useState(0);
  const [institutions, setInstitutions] = useState<Institution[]>([]);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  // New staff form
  const [newName, setNewName] = useState("");
  const [newContact, setNewContact] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState<UserRole>("MODERATOR");
  const [newInstitution, setNewInstitution] = useState("");

  // New institution form
  const [instName, setInstName] = useState("");
  const [instArea, setInstArea] = useState("Freetown");
  const [instContact, setInstContact] = useState("");
  const [instDescription, setInstDescription] = useState("");

  const load = useCallback(async () => {
    try {
      const [u, insts] = await Promise.all([adminListUsers({ limit: 100 }), getInstitutions()]);
      setUsers(u.items);
      setUsersTotal(u.total);
      setInstitutions(insts);
      setNewInstitution((cur) => cur || insts[0]?.id || "");
      setError(null);
    } catch (err) {
      setError(describeError(err, "Could not load administration data."));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const flash = (msg: string) => {
    setMessage(msg);
    setTimeout(() => setMessage(null), 4000);
  };

  const run = async (label: string, fn: () => Promise<unknown>) => {
    setBusy(true);
    setError(null);
    try {
      await fn();
      flash(label);
      await load();
    } catch (err) {
      setError(describeError(err, `${label} failed.`));
    } finally {
      setBusy(false);
    }
  };

  const handleCreateStaff = (e: React.FormEvent) => {
    e.preventDefault();
    void run("Staff account created.", async () => {
      await adminCreateStaffUser({
        name_or_alias: newName.trim(),
        contact: newContact.trim(),
        password: newPassword,
        role: newRole,
        institution_id: newRole === "OFFICER" ? newInstitution : null,
      });
      setNewName(""); setNewContact(""); setNewPassword("");
    });
  };

  const handleToggleActive = (user: User) => {
    const activating = user.is_active === false;
    const reason = window.prompt(`Reason for ${activating ? "reactivating" : "deactivating"} ${user.name_or_alias}? (recorded in the audit trail)`);
    if (!reason || reason.trim().length < 3) return;
    void run(activating ? "Account reactivated." : "Account deactivated.", () =>
      adminUpdateUser(user.id, { is_active: activating, reason: reason.trim() }));
  };

  const handleCreateInstitution = (e: React.FormEvent) => {
    e.preventDefault();
    void run("Institution registered.", async () => {
      await adminCreateInstitution({
        name: instName.trim(),
        service_area: instArea.trim(),
        contact_channel: instContact.trim() || undefined,
        description: instDescription.trim() || undefined,
      });
      setInstName(""); setInstContact(""); setInstDescription("");
    });
  };

  const tabButton = (value: Tab, label: string, Icon: React.ComponentType<{ size?: number; "aria-hidden"?: boolean | "true" }>) => (
    <button type="button" role="tab" aria-selected={tab === value}
            className={`btn-sm ${tab === value ? "btn-primary" : "btn-secondary"}`}
            onClick={() => setTab(value)} style={{ display: "flex", alignItems: "center", gap: 6 }}>
      <Icon size={14} aria-hidden="true" /> {label}
    </button>
  );

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Settings2 size={22} color="var(--color-primary)" aria-hidden="true" />
            <h2 style={{ fontSize: "1.4rem", fontWeight: 700 }}>System Administration</h2>
          </div>
          <p style={{ fontSize: "0.85rem", color: "var(--color-text-muted)", marginTop: 2 }}>
            Staff provisioning and responding institutions. Every change is written to the audit trail with your reason.
          </p>
        </div>
        <div role="tablist" aria-label="Administration" style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {tabButton("users", `Staff & users (${usersTotal})`, Users)}
          {tabButton("institutions", `Institutions (${institutions.length})`, Building2)}
          {tabButton("moderation", "Moderation workspace", FolderKanban)}
        </div>
      </div>

      {message && (
        <div role="status" style={{ backgroundColor: "var(--color-success-bg)", color: "var(--color-success)", padding: "10px 16px", borderRadius: "var(--radius-md)", fontWeight: 600, display: "flex", gap: 8, alignItems: "center" }}>
          <ShieldCheck size={16} aria-hidden="true" /> {message}
        </div>
      )}
      {error && (
        <div role="alert" style={{ backgroundColor: "var(--color-danger-bg)", color: "var(--color-danger)", padding: "10px 16px", borderRadius: "var(--radius-md)", fontWeight: 600, display: "flex", justifyContent: "space-between", gap: 8 }}>
          <span>{error}</span>
          <button type="button" className="btn-sm btn-secondary" onClick={() => setError(null)}>Dismiss</button>
        </div>
      )}

      {tab === "moderation" && <ModeratorView />}

      {tab === "users" && (
        <div style={{ display: "grid", gridTemplateColumns: "minmax(280px, 1fr) 2fr", gap: 20 }}>
          <form className="card" onSubmit={handleCreateStaff} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 700, display: "flex", alignItems: "center", gap: 6 }}>
              <UserPlus size={16} aria-hidden="true" /> Provision staff account
            </h3>
            <p style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>
              Citizens self-register. Moderators, officers, auditors and administrators can only be created here.
            </p>
            <div>
              <label className="input-label" htmlFor="staff-name">Name</label>
              <input id="staff-name" className="input-field" required minLength={2} value={newName} onChange={(e) => setNewName(e.target.value)} />
            </div>
            <div>
              <label className="input-label" htmlFor="staff-contact">Email / phone</label>
              <input id="staff-contact" className="input-field" required value={newContact} onChange={(e) => setNewContact(e.target.value)} autoComplete="off" />
            </div>
            <div>
              <label className="input-label" htmlFor="staff-password">Temporary password</label>
              <input id="staff-password" className="input-field" type="password" required minLength={8} value={newPassword} onChange={(e) => setNewPassword(e.target.value)} autoComplete="new-password" />
            </div>
            <div>
              <label className="input-label" htmlFor="staff-role">Role</label>
              <select id="staff-role" className="input-field" value={newRole} onChange={(e) => setNewRole(e.target.value as UserRole)}>
                {STAFF_ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>
            {newRole === "OFFICER" && (
              <div>
                <label className="input-label" htmlFor="staff-inst">Institution</label>
                <select id="staff-inst" className="input-field" value={newInstitution} onChange={(e) => setNewInstitution(e.target.value)} required>
                  {institutions.map((i) => <option key={i.id} value={i.id}>{i.name}</option>)}
                </select>
              </div>
            )}
            <button type="submit" className="btn-primary" disabled={busy}>{busy ? "Saving…" : "Create account"}</button>
          </form>

          <div className="card" style={{ padding: 0, overflow: "hidden" }}>
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
                <thead>
                  <tr style={{ backgroundColor: "var(--color-surface)", borderBottom: "1px solid var(--color-border)", textAlign: "left" }}>
                    <th scope="col" style={{ padding: "10px 14px", color: "var(--color-text-muted)" }}>NAME</th>
                    <th scope="col" style={{ padding: "10px 14px", color: "var(--color-text-muted)" }}>CONTACT</th>
                    <th scope="col" style={{ padding: "10px 14px", color: "var(--color-text-muted)" }}>ROLE</th>
                    <th scope="col" style={{ padding: "10px 14px", color: "var(--color-text-muted)" }}>INSTITUTION</th>
                    <th scope="col" style={{ padding: "10px 14px", color: "var(--color-text-muted)" }}>STATUS</th>
                    <th scope="col" style={{ padding: "10px 14px", color: "var(--color-text-muted)" }}></th>
                  </tr>
                </thead>
                <tbody>
                  {users.length === 0 && (
                    <tr><td colSpan={6} style={{ padding: 24, textAlign: "center", color: "var(--color-text-muted)" }}>{loading ? "Loading…" : "No users."}</td></tr>
                  )}
                  {users.map((u, i) => (
                    <tr key={u.id} style={{ borderBottom: "1px solid var(--color-border)", backgroundColor: i % 2 ? "var(--color-surface)" : "#fff" }}>
                      <td style={{ padding: "10px 14px", fontWeight: 600 }}>{u.name_or_alias}{u.id === currentUser.id && <span style={{ fontSize: "0.7rem", color: "var(--color-text-muted)" }}> (you)</span>}</td>
                      <td style={{ padding: "10px 14px" }}>{u.contact}</td>
                      <td style={{ padding: "10px 14px" }}><span className="badge" style={{ backgroundColor: "var(--color-primary-light)", color: "var(--color-primary)" }}>{u.role}</span></td>
                      <td style={{ padding: "10px 14px", color: "var(--color-text-muted)" }}>{u.institution_name ?? "—"}</td>
                      <td style={{ padding: "10px 14px" }}>
                        <span style={{ fontWeight: 700, color: u.is_active === false ? "var(--color-danger)" : "var(--color-success)" }}>
                          {u.is_active === false ? "INACTIVE" : "ACTIVE"}
                        </span>
                      </td>
                      <td style={{ padding: "10px 14px", textAlign: "right" }}>
                        {u.id !== currentUser.id && (
                          <button type="button" className={`btn-sm ${u.is_active === false ? "btn-secondary" : "btn-danger"}`} disabled={busy} onClick={() => handleToggleActive(u)}>
                            {u.is_active === false ? "Reactivate" : "Deactivate"}
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {tab === "institutions" && (
        <div style={{ display: "grid", gridTemplateColumns: "minmax(280px, 1fr) 2fr", gap: 20 }}>
          <form className="card" onSubmit={handleCreateInstitution} style={{ display: "flex", flexDirection: "column", gap: 12 }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 700, display: "flex", alignItems: "center", gap: 6 }}>
              <Building2 size={16} aria-hidden="true" /> Register institution
            </h3>
            <div>
              <label className="input-label" htmlFor="inst-name">Name</label>
              <input id="inst-name" className="input-field" required minLength={2} value={instName} onChange={(e) => setInstName(e.target.value)} />
            </div>
            <div>
              <label className="input-label" htmlFor="inst-area">Service area</label>
              <input id="inst-area" className="input-field" required minLength={2} value={instArea} onChange={(e) => setInstArea(e.target.value)} />
            </div>
            <div>
              <label className="input-label" htmlFor="inst-contact">Contact channel</label>
              <input id="inst-contact" className="input-field" value={instContact} onChange={(e) => setInstContact(e.target.value)} placeholder="ops@example.gov.sl" />
            </div>
            <div>
              <label className="input-label" htmlFor="inst-desc">Description</label>
              <textarea id="inst-desc" className="input-field" rows={3} value={instDescription} onChange={(e) => setInstDescription(e.target.value)} />
            </div>
            <button type="submit" className="btn-primary" disabled={busy}>{busy ? "Saving…" : "Register"}</button>
          </form>

          <div className="card" style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 700, display: "flex", alignItems: "center", gap: 6 }}>
              <Inbox size={16} aria-hidden="true" /> Active institutions
            </h3>
            {institutions.map((inst) => (
              <div key={inst.id} style={{ border: "1px solid var(--color-border)", borderRadius: "var(--radius-md)", padding: 12, display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
                <div>
                  <div style={{ fontWeight: 700 }}>{inst.name}</div>
                  <div style={{ fontSize: "0.8rem", color: "var(--color-text-muted)" }}>{inst.service_area}{inst.contact_channel ? ` · ${inst.contact_channel}` : ""}</div>
                  {inst.description && <div style={{ fontSize: "0.85rem", marginTop: 4 }}>{inst.description}</div>}
                </div>
                <button type="button" className="btn-sm btn-danger" disabled={busy}
                        onClick={() => {
                          if (window.confirm(`Deactivate ${inst.name}? Existing assignments are kept; it will no longer be offered for new assignments.`)) {
                            void run("Institution deactivated.", () => adminUpdateInstitution(inst.id, { is_active: false }));
                          }
                        }}>
                  Deactivate
                </button>
              </div>
            ))}
            {institutions.length === 0 && <p style={{ color: "var(--color-text-muted)", fontSize: "0.9rem" }}>No active institutions.</p>}
          </div>
        </div>
      )}
    </div>
  );
};
