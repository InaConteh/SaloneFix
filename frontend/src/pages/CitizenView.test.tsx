/**
 * CitizenView is the screen actual citizens use, and the only place in the app
 * where location precision is decided. These tests concentrate on the rules that
 * carry consequences: what coordinates leave the device, what happens when the
 * citizen refuses location access, and whether a rejected photo can silently
 * swallow an otherwise successful report.
 */
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { CitizenView } from "./CitizenView";
import * as client from "../api/client";
import type { ReportStatus, ServiceCategory } from "../types";

const categories: ServiceCategory[] = [
  {
    id: "c1",
    code: "ROAD_POTHOLE",
    name: "Roads & Potholes",
    description: "Damaged asphalt and road surface hazards.",
    requires_resolution_evidence: true,
    is_active: true,
  },
  {
    id: "c2",
    code: "DRAINAGE_FLOODING",
    name: "Drainage & Flooding",
    description: "Blocked drains and standing water.",
    requires_resolution_evidence: true,
    is_active: true,
  },
];

const submitted = {
  id: "r1",
  tracking_reference: "SF-2026-000001",
  status: "SUBMITTED" as ReportStatus,
  next_step: "A moderator will review your report.",
};

const DESCRIPTION = "Deep pothole across the whole lane outside the school gate.";

/** Replace navigator.geolocation with a stub that resolves or fails on demand. */
function mockGeolocation(behaviour: {
  coords?: { latitude: number; longitude: number; accuracy: number };
  errorCode?: number;
}) {
  const getCurrentPosition = vi.fn(
    (onSuccess: PositionCallback, onError?: PositionErrorCallback) => {
      if (behaviour.coords) {
        onSuccess({ coords: behaviour.coords } as GeolocationPosition);
      } else {
        onError?.({
          code: behaviour.errorCode ?? 1,
          PERMISSION_DENIED: 1,
          POSITION_UNAVAILABLE: 2,
          TIMEOUT: 3,
          message: "denied",
        } as GeolocationPositionError);
      }
    },
  );
  Object.defineProperty(navigator, "geolocation", {
    value: { getCurrentPosition },
    configurable: true,
  });
  return getCurrentPosition;
}

async function fillDescription(user: ReturnType<typeof userEvent.setup>) {
  await user.type(screen.getByLabelText(/description of problem/i), DESCRIPTION);
}

beforeEach(() => {
  vi.spyOn(client, "getCategories").mockResolvedValue(categories);
  vi.spyOn(client, "listReports").mockResolvedValue({ items: [], total: 0 });
});

afterEach(() => {
  Reflect.deleteProperty(navigator, "geolocation");
});

describe("CitizenView report submission", () => {
  it("offers the seeded categories once they load", async () => {
    render(<CitizenView />);
    expect(await screen.findByRole("button", { name: /roads & potholes/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /drainage & flooding/i })).toBeInTheDocument();
  });

  it("marks the chosen category as pressed so it is not conveyed by colour alone", async () => {
    render(<CitizenView />);
    const user = userEvent.setup();

    const drainage = await screen.findByRole("button", { name: /drainage & flooding/i });
    await user.click(drainage);

    expect(drainage).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: /roads & potholes/i })).toHaveAttribute("aria-pressed", "false");
  });

  it("sends EXACT precision when the device fix is accurate to 100m or better", async () => {
    mockGeolocation({ coords: { latitude: 8.4851, longitude: -13.2285, accuracy: 40 } });
    const submitSpy = vi.spyOn(client, "submitReport").mockResolvedValue(submitted);
    render(<CitizenView />);
    const user = userEvent.setup();

    await screen.findByRole("button", { name: /roads & potholes/i });
    await fillDescription(user);
    await user.click(screen.getByRole("button", { name: /capture location/i }));
    await user.click(screen.getByRole("button", { name: /submit incident report/i }));

    await waitFor(() => expect(submitSpy).toHaveBeenCalled());
    expect(submitSpy.mock.calls[0][0]).toMatchObject({
      category_code: "ROAD_POTHOLE",
      latitude: 8.4851,
      longitude: -13.2285,
      location_precision: "EXACT",
    });
  });

  it("downgrades to APPROXIMATE precision when the fix is worse than 100m", async () => {
    mockGeolocation({ coords: { latitude: 8.4851, longitude: -13.2285, accuracy: 350 } });
    const submitSpy = vi.spyOn(client, "submitReport").mockResolvedValue(submitted);
    render(<CitizenView />);
    const user = userEvent.setup();

    await screen.findByRole("button", { name: /roads & potholes/i });
    await fillDescription(user);
    await user.click(screen.getByRole("button", { name: /capture location/i }));
    await user.click(screen.getByRole("button", { name: /submit incident report/i }));

    await waitFor(() => expect(submitSpy).toHaveBeenCalled());
    expect(submitSpy.mock.calls[0][0].location_precision).toBe("APPROXIMATE");
  });

  it("falls back to a landmark and sends no coordinates when location is refused", async () => {
    mockGeolocation({ errorCode: 1 });
    const submitSpy = vi.spyOn(client, "submitReport").mockResolvedValue(submitted);
    render(<CitizenView />);
    const user = userEvent.setup();

    await screen.findByRole("button", { name: /roads & potholes/i });
    await fillDescription(user);
    await user.click(screen.getByRole("button", { name: /capture location/i }));

    // The refusal is explained rather than leaving the citizen stuck.
    expect(await screen.findByLabelText(/landmark description/i)).toBeInTheDocument();

    await user.type(screen.getByLabelText(/landmark description/i), "Near St. John Roundabout by the market stalls");
    await user.click(screen.getByRole("button", { name: /submit incident report/i }));

    await waitFor(() => expect(submitSpy).toHaveBeenCalled());
    const payload = submitSpy.mock.calls[0][0];
    expect(payload.location_precision).toBe("USER_ENTERED");
    expect(payload.latitude).toBeUndefined();
    expect(payload.longitude).toBeUndefined();
    expect(payload.description).toContain("St. John Roundabout");
  });

  it("refuses to submit in GPS mode before a fix has been captured", async () => {
    mockGeolocation({ coords: { latitude: 8.4, longitude: -13.2, accuracy: 10 } });
    const submitSpy = vi.spyOn(client, "submitReport").mockResolvedValue(submitted);
    render(<CitizenView />);
    const user = userEvent.setup();

    await screen.findByRole("button", { name: /roads & potholes/i });
    await fillDescription(user);
    await user.click(screen.getByRole("button", { name: /submit incident report/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/capture your location first/i);
    expect(submitSpy).not.toHaveBeenCalled();
  });

  it("refuses a landmark too vague to locate the problem", async () => {
    mockGeolocation({ errorCode: 1 });
    const submitSpy = vi.spyOn(client, "submitReport").mockResolvedValue(submitted);
    render(<CitizenView />);
    const user = userEvent.setup();

    await screen.findByRole("button", { name: /roads & potholes/i });
    await fillDescription(user);
    await user.click(screen.getByRole("button", { name: /capture location/i }));
    await user.type(await screen.findByLabelText(/landmark description/i), "here");
    await user.click(screen.getByRole("button", { name: /submit incident report/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(/describe where the problem is/i);
    expect(submitSpy).not.toHaveBeenCalled();
  });

  it("shows the tracking reference after a successful submission", async () => {
    mockGeolocation({ coords: { latitude: 8.4851, longitude: -13.2285, accuracy: 20 } });
    vi.spyOn(client, "submitReport").mockResolvedValue(submitted);
    render(<CitizenView />);
    const user = userEvent.setup();

    await screen.findByRole("button", { name: /roads & potholes/i });
    await fillDescription(user);
    await user.click(screen.getByRole("button", { name: /capture location/i }));
    await user.click(screen.getByRole("button", { name: /submit incident report/i }));

    expect(await screen.findByText("SF-2026-000001")).toBeInTheDocument();
    expect(screen.getByText(/report submitted successfully/i)).toBeInTheDocument();
  });

  it("tells the citizen the photo failed without losing the saved report", async () => {
    mockGeolocation({ coords: { latitude: 8.4851, longitude: -13.2285, accuracy: 20 } });
    vi.spyOn(client, "submitReport").mockResolvedValue(submitted);
    vi.spyOn(client, "uploadReportMedia").mockRejectedValue(
      new client.ApiError(422, { error_code: "MEDIA_INVALID", message: "File is not a valid image." }),
    );
    render(<CitizenView />);
    const user = userEvent.setup();

    await screen.findByRole("button", { name: /roads & potholes/i });
    await fillDescription(user);
    await user.click(screen.getByRole("button", { name: /capture location/i }));

    const file = new File(["not-an-image"], "broken.jpg", { type: "image/jpeg" });
    await user.upload(screen.getByLabelText(/attach photo evidence/i), file);
    await user.click(screen.getByRole("button", { name: /submit incident report/i }));

    // Both facts have to reach the citizen: the report is safe, the photo is not.
    expect(await screen.findByRole("alert")).toHaveTextContent(/report saved, but the photo was rejected/i);
    expect(await screen.findByText("SF-2026-000001")).toBeInTheDocument();
  });

  it("surfaces a rejected submission as an actionable message", async () => {
    mockGeolocation({ coords: { latitude: 8.4851, longitude: -13.2285, accuracy: 20 } });
    const submitSpy = vi.spyOn(client, "submitReport").mockRejectedValue(
      new client.ApiError(429, { error_code: "RATE_LIMITED", message: "Too many reports. Try again in a minute." }),
    );
    render(<CitizenView />);
    const user = userEvent.setup();

    await screen.findByRole("button", { name: /roads & potholes/i });
    await fillDescription(user);
    await user.click(screen.getByRole("button", { name: /capture location/i }));
    await user.click(screen.getByRole("button", { name: /submit incident report/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent("Too many reports. Try again in a minute.");
    expect(submitSpy).toHaveBeenCalled();
    expect(screen.queryByText("SF-2026-000001")).not.toBeInTheDocument();
  });

  it("explains itself when the categories cannot be loaded", async () => {
    vi.spyOn(client, "getCategories").mockRejectedValue(
      new client.ApiError(503, { error_code: "DEPENDENCY_UNAVAILABLE", message: "Service list is unavailable." }),
    );
    render(<CitizenView />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Service list is unavailable.");
  });
});
