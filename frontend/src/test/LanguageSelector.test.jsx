import { describe, it, expect, vi } from "vitest";
import React from "react";
import { render, fireEvent } from "@testing-library/react";
import LanguageSelector from "../components/LanguageSelector";

describe("LanguageSelector", () => {
  it("renders both language buttons", () => {
    const { getByTitle } = render(
      <LanguageSelector language="english" setLanguage={() => { }} />
    );
    expect(getByTitle("English")).toBeTruthy();
    expect(getByTitle("Romanian")).toBeTruthy();
  });

  it("shows 🇺🇸 and 🇷🇴 icons", () => {
    const { getAllByText } = render(
      <LanguageSelector language="english" setLanguage={() => { }} />
    );
    expect(getAllByText("🇺🇸").length).toBeGreaterThan(0);
    expect(getAllByText("🇷🇴").length).toBeGreaterThan(0);
  });
});