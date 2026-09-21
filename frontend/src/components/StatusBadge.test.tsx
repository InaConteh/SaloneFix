import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { StatusBadge } from "./StatusBadge";

describe("StatusBadge", () => {
  it.each([
    ["SUBMITTED", "Submitted"],
    ["RESOLUTION_UNDER_REVIEW", /review/i],
    ["RESOLVED", /resolved/i],
    ["DISPUTED", /disputed/i],
  ])("renders a text label for %s (status is never colour-only)", (status, label) => {
    render(<StatusBadge status={status} />);
    expect(screen.getByText(label)).toBeInTheDocument();
  });

  it("falls back gracefully for an unknown status", () => {
    render(<StatusBadge status="SOMETHING_NEW" />);
    expect(screen.getByText(/something_new/i)).toBeInTheDocument();
  });
});
