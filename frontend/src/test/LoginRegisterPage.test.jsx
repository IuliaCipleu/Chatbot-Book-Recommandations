import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { render, fireEvent, waitFor } from "@testing-library/react";
import LoginRegisterPage from "../components/LoginRegisterPage";

// filepath: frontend/src/components/LoginRegisterPage.test.jsx

// Helper to mock localStorage
function mockLocalStorage() {
  let store = {};
  return {
    getItem: vi.fn((key) => store[key] || null),
    setItem: vi.fn((key, value) => { store[key] = value.toString(); }),
    removeItem: vi.fn((key) => { delete store[key]; }),
    clear: vi.fn(() => { store = {}; }),
  };
}

describe("LoginRegisterPage", () => {
  let originalLocalStorage;
  beforeEach(() => {
    // Mock localStorage
    originalLocalStorage = global.localStorage;
    global.localStorage = mockLocalStorage();
  });

  afterEach(() => {
    global.localStorage = originalLocalStorage;
  });

  it("renders login form and calls onLogin on successful login", async () => {
    const onLogin = vi.fn();
    const onShowRegister = vi.fn();

    // Mock fetch to simulate successful login
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        user: { username: "alice", language: "english" },
        access_token: "fake-jwt-token"
      })
    });

    const { getByLabelText, getByRole } = render(
      <LoginRegisterPage onLogin={onLogin} onShowRegister={onShowRegister} />
    );

    fireEvent.change(getByLabelText(/Username or Email/i), { target: { value: "alice" } });
    fireEvent.change(getByLabelText(/Password/i), { target: { value: "Password123!" } });
    fireEvent.click(getByRole("button", { name: /Login/i }));

    await waitFor(() => {
      expect(onLogin).toHaveBeenCalled();
      expect(global.localStorage.setItem).toHaveBeenCalledWith(
        "user",
        JSON.stringify({ username: "alice", language: "english" })
      );
      expect(global.localStorage.setItem).toHaveBeenCalledWith(
        "jwtToken",
        "fake-jwt-token"
      );
    });
  });
});