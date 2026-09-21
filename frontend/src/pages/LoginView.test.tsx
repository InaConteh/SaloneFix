import { describe, it, expect, vi } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { LoginView } from "./LoginView";
import * as client from "../api/client";

const citizen = { id: "u1", role: "CITIZEN" as const, name_or_alias: "Fatu", contact: "citizen@freetown.sl", created_at: "" };

describe("LoginView", () => {
  it("signs in with typed credentials and reports the user", async () => {
    const loginSpy = vi.spyOn(client, "login").mockResolvedValue({ access_token: "t", user: citizen });
    const onAuthenticated = vi.fn();
    render(<LoginView onAuthenticated={onAuthenticated} />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/email or phone/i), "citizen@freetown.sl");
    await user.type(screen.getByLabelText(/^password$/i), "CitizenPass123!");
    await user.click(screen.getByRole("button", { name: /^sign in$/i }));

    await waitFor(() => expect(onAuthenticated).toHaveBeenCalledWith(citizen));
    expect(loginSpy).toHaveBeenCalledWith("citizen@freetown.sl", "CitizenPass123!");
  });

  it("shows an actionable error when the API rejects the login", async () => {
    vi.spyOn(client, "login").mockRejectedValue(new client.ApiError(401, { error_code: "UNAUTHORIZED", message: "Invalid contact or password." }));
    render(<LoginView onAuthenticated={vi.fn()} />);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/email or phone/i), "nobody@x.sl");
    await user.type(screen.getByLabelText(/^password$/i), "wrongpass1");
    await user.click(screen.getByRole("button", { name: /^sign in$/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Invalid contact or password.");
  });

  it("registers a citizen account without exposing a role selector", async () => {
    const registerSpy = vi.spyOn(client, "register").mockResolvedValue({ access_token: "t", user: citizen });
    render(<LoginView onAuthenticated={vi.fn()} />);

    const user = userEvent.setup();
    await user.click(screen.getByRole("tab", { name: /create citizen account/i }));
    expect(screen.queryByLabelText(/role/i)).not.toBeInTheDocument();

    await user.type(screen.getByLabelText(/name or alias/i), "Fatu");
    await user.type(screen.getByLabelText(/email or phone/i), "fatu@x.sl");
    await user.type(screen.getByLabelText(/^password$/i), "LongEnough1!");
    await user.click(screen.getByRole("button", { name: /create account/i }));

    await waitFor(() => expect(registerSpy).toHaveBeenCalled());
    expect(registerSpy.mock.calls[0][0]).toMatchObject({ name_or_alias: "Fatu", contact: "fatu@x.sl", consent_status: true });
  });
});
