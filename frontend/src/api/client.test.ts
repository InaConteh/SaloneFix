import { describe, it, expect, vi, beforeEach } from "vitest";
import {
  API_BASE_URL,
  API_ORIGIN,
  ApiError,
  mediaUrl,
  setAuthToken,
  getAuthToken,
  listReports,
  submitReport,
  login,
  getMe,
} from "./client";

const jsonResponse = (body: unknown, init: ResponseInit = {}) =>
  new Response(JSON.stringify(body), { status: 200, headers: { "Content-Type": "application/json" }, ...init });

describe("api client", () => {
  beforeEach(() => {
    setAuthToken(null);
  });

  it("derives the API origin from the base URL", () => {
    expect(API_BASE_URL.endsWith("/api/v1")).toBe(true);
    expect(API_ORIGIN).toBe(new URL(API_BASE_URL).origin);
  });

  it("turns relative signed media URLs into absolute ones", () => {
    const asset = { id: "a1", original_filename: "x.jpg", mime_type: "image/jpeg", file_size: 1, created_at: "", url: "/api/v1/media/a1?token=abc.def" };
    expect(mediaUrl(asset)).toBe(`${API_ORIGIN}/api/v1/media/a1?token=abc.def`);
    expect(mediaUrl({ ...asset, url: undefined })).toBeUndefined();
  });

  it("sends the bearer token and reads X-Total-Count for paginated lists", async () => {
    setAuthToken("tok-123");
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      jsonResponse([{ id: "r1" }, { id: "r2" }], { headers: { "Content-Type": "application/json", "X-Total-Count": "7" } })
    );

    const page = await listReports({ status: "VERIFIED", limit: 2, offset: 4 });

    expect(page.items).toHaveLength(2);
    expect(page.total).toBe(7);
    const [url, init] = fetchMock.mock.calls[0];
    expect(String(url)).toBe(`${API_BASE_URL}/reports?status=VERIFIED&limit=2&offset=4`);
    expect((init!.headers as Record<string, string>)["Authorization"]).toBe("Bearer tok-123");
  });

  it("attaches an Idempotency-Key to report submission", async () => {
    const fetchMock = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      jsonResponse({ id: "r1", tracking_reference: "SF-2026-000001", status: "SUBMITTED", next_step: "" })
    );
    await submitReport({ category_code: "ROAD_POTHOLE", description: "A large pothole on the main road." }, "fixed-key");
    const init = fetchMock.mock.calls[0][1]!;
    expect((init.headers as Record<string, string>)["Idempotency-Key"]).toBe("fixed-key");
    expect((init.headers as Record<string, string>)["Content-Type"]).toBe("application/json");
  });

  it("throws a typed ApiError carrying the stable error code", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      jsonResponse(
        { error_code: "RATE_LIMITED", message: "Slow down", details: { retry_after_seconds: 60 }, request_id: "req-1" },
        { status: 429 }
      )
    );
    await expect(getMe()).rejects.toMatchObject({
      name: "ApiError",
      status: 429,
      errorCode: "RATE_LIMITED",
      message: "Slow down",
      requestId: "req-1",
    } satisfies Partial<ApiError>);
  });

  it("stores the token after a successful login", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      jsonResponse({ access_token: "jwt-abc", user: { id: "u1", role: "CITIZEN", name_or_alias: "Fatu", contact: "c@x.sl", created_at: "" } })
    );
    const res = await login("c@x.sl", "secret123");
    expect(res.user.role).toBe("CITIZEN");
    expect(getAuthToken()).toBe("jwt-abc");
    expect(localStorage.getItem("salonefix_token")).toBe("jwt-abc");
  });
});
