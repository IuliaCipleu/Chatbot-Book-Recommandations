import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import React from "react";
import { render, fireEvent, waitFor, within, cleanup } from "@testing-library/react";
// optional but nicer than fireEvent:
import userEvent from "@testing-library/user-event";
import UserProfilePage from "../components/UserProfilePage";

afterEach(() => {
  cleanup();
  vi.resetAllMocks();   // or vi.restoreAllMocks();
});

// Mock useNavigate from react-router-dom
vi.mock("react-router-dom", () => ({
  ...vi.importActual("react-router-dom"),
  useNavigate: () => vi.fn(),
}));

describe("UserProfilePage handleUpdate", () => {
  beforeEach(() => {
    window.localStorage.clear();
    window.localStorage.setItem(
      "user",
      JSON.stringify({
        username: "alice",
        email: "alice@endava.com",
        language: "English",
        profile: "Teen",
        voice_enabled: true,
      })
    );
    window.localStorage.setItem("jwtToken", "fake-token");
  });

  it("updates user profile successfully", async () => {
  global.fetch = vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) });

  const { container } = render(<UserProfilePage />);
  const page = container.querySelector(".page-container");
  if (!page) throw new Error("'.page-container' not found");

  const editBtn = within(page).getByRole("button", { name: /edit profile/i });
  await userEvent.click(editBtn);

  const emailInput = within(page).getByLabelText(/Email:/i);
  await userEvent.type(emailInput, "{Control>}a{/Control}alice2@endava.com");

  const saveBtn = within(page).getByRole("button", { name: /^save$/i });
  await userEvent.click(saveBtn);

  await waitFor(() => {
    expect(within(page).getByText("Profile updated!")).toBeTruthy();
    expect(window.localStorage.getItem("user")).toContain("alice2@endava.com");
  });
});

it("shows error message on failed update", async () => {
  global.fetch = vi.fn().mockResolvedValue({
    ok: false,
    json: async () => ({ detail: "Update failed" }),
  });

  const { container } = render(<UserProfilePage />);
  const page = container.querySelector(".page-container");
  if (!page) throw new Error("'.page-container' not found");

  const editBtn = within(page).getByRole("button", { name: /edit profile/i });
  await userEvent.click(editBtn);

  const emailInput = within(page).getByLabelText(/Email:/i);
  await userEvent.clear(emailInput);
  await userEvent.type(emailInput, "bad@email.com");

  const saveBtn = within(page).getByRole("button", { name: /^save$/i });
  await userEvent.click(saveBtn);

  // If your error is shown as plain text:
  expect(await within(page).findByText("Update failed")).toBeTruthy();
  // Even better if you add role="alert" to your error container:
  // expect(await within(page).findByRole('alert', { name: /update failed/i })).toBeTruthy();
});

it("does not update if fetch throws", async () => {
  global.fetch = vi.fn().mockRejectedValue(new Error("Network error"));

  const { container } = render(<UserProfilePage />);
  const page = container.querySelector(".page-container");
  if (!page) throw new Error("'.page-container' not found");

  const editBtn = within(page).getByRole("button", { name: /edit profile/i });
  await userEvent.click(editBtn);

  const emailInput = within(page).getByLabelText(/Email:/i);
  await userEvent.clear(emailInput);
  await userEvent.type(emailInput, "fail@email.com");

  const saveBtn = within(page).getByRole("button", { name: /^save$/i });
  await userEvent.click(saveBtn);

  expect(await within(page).findByText("Network error")).toBeTruthy();
});

});