import React from "react";
import { render, fireEvent, waitFor } from "@testing-library/react";
import RegisterPage from "../components/RegisterPage";
import { vi } from "vitest";

describe("RegisterPage", () => {
  it("renders registration form", () => {
    const { getByLabelText, getByRole } = render(
      <RegisterPage onRegister={vi.fn()} onBack={vi.fn()} />
    );
    expect(getByLabelText(/Username/i)).toBeTruthy();
    expect(getByLabelText(/Email/i)).toBeTruthy();
    expect(getByLabelText(/Password/i)).toBeTruthy();
    expect(getByLabelText(/Confirm Password/i)).toBeTruthy();
    expect(getByRole("button", { name: /Register/i })).toBeTruthy();
  });

  it("shows error if passwords do not match", async () => {
    const { getByLabelText, getByRole, findByText } = render(
      <RegisterPage onRegister={vi.fn()} onBack={vi.fn()} />
    );
    fireEvent.change(getByLabelText(/Username/i), { target: { value: "alice" } });
    fireEvent.change(getByLabelText(/Email/i), { target: { value: "alice@example.com" } });
    fireEvent.change(getByLabelText(/^Password$/i), { target: { value: "Password123!" } });
    fireEvent.change(getByLabelText(/Confirm Password/i), { target: { value: "Password456!" } });
    fireEvent.click(getByRole("button", { name: /Register/i }));
    expect(await findByText("Passwords do not match")).toBeTruthy();
  });

  it("calls onBack when Back to Login is clicked", () => {
    const onBack = vi.fn();
    const { getByText } = render(
      <RegisterPage onRegister={vi.fn()} onBack={onBack} />
    );
    fireEvent.click(getByText(/Back to Login/i));
    expect(onBack).toHaveBeenCalled();
  });

  // You can add more tests for successful registration and error handling with mock fetch
});
