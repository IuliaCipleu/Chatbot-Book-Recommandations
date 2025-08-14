import React from "react";
import { render, fireEvent, waitFor, within, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import RegisterPage from "../components/RegisterPage";
import { vi, describe, it, expect } from "vitest";

describe("RegisterPage", () => {
    it("renders registration form", () => {
        const { getAllByLabelText, getByLabelText, getAllByRole } = render(
            <RegisterPage onRegister={vi.fn()} onBack={vi.fn()} />
        );
        expect(getByLabelText(/Username/i)).toBeTruthy();
        expect(getByLabelText(/Email/i)).toBeTruthy();
        // Use getAllByLabelText for ambiguous 'Password' label
        expect(getAllByLabelText(/Password/i)[0]).toBeTruthy(); // Password
        expect(getAllByLabelText(/Password/i)[1]).toBeTruthy(); // Confirm Password
        expect(getAllByRole("button", { name: /Register/i })[0]).toBeTruthy();
    });

    it("shows error if passwords do not match", async () => {
        const { getByLabelText, getAllByRole, findByText } = render(
            <RegisterPage onRegister={vi.fn()} onBack={vi.fn()} />
        );
        fireEvent.change(getByLabelText(/Username/i), { target: { value: "alice" } });
        fireEvent.change(getByLabelText(/Email/i), { target: { value: "alice@example.com" } });
        fireEvent.change(getByLabelText(/^Password$/i), { target: { value: "Password123!" } });
        fireEvent.change(getByLabelText(/Confirm Password/i), { target: { value: "Password456!" } });
        // Use getAllByRole for ambiguous Register button
        fireEvent.click(getAllByRole("button", { name: /Register/i })[0]);
        expect(await findByText("Passwords do not match")).toBeTruthy();
    });

    it("calls onBack when Back to Login is clicked", async () => {
        const onBack = vi.fn();
        const { container } = render(<RegisterPage onRegister={vi.fn()} onBack={onBack} />);

        const page = container.querySelector(".login-page");
        if (!page) throw new Error("'.login-page' not found");

        const backBtn = within(page).getByRole("button", { name: /back to login/i });
        await userEvent.click(backBtn);

        expect(onBack).toHaveBeenCalledTimes(1);
    });
    // You can add more tests for successful registration and error handling with mock fetch
});
