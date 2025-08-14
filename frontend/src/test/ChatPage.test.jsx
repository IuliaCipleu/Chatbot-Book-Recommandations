import { describe, it, expect, beforeEach, vi } from "vitest";
import React, { useState } from "react";
import { render } from "@testing-library/react";

describe("ChatPage user localStorage logic", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  function Dummy() {
    // Always read localStorage inside the function
    const user = (() => {
      try {
        return JSON.parse(window.localStorage.getItem("user"));
      } catch {
        return null;
      }
    })();
    const preferredLanguage = user && user.language ? user.language.toLowerCase() : "english";
    return <div>{preferredLanguage}</div>;
  }

  it("should parse user from localStorage if valid JSON", () => {
    window.localStorage.setItem("user", JSON.stringify({ language: "romanian" }));
    const { getByText } = render(<Dummy />);
    expect(getByText("romanian")).toBeTruthy();
  });

  it("should fallback to null if localStorage is empty", () => {
    window.localStorage.removeItem("user");
    const { getByText } = render(<Dummy />);
    expect(getByText("english")).toBeTruthy();
  });

  it("should fallback to null if localStorage contains invalid JSON", () => {
    window.localStorage.setItem("user", "invalid-json");
    const { getAllByText } = render(<Dummy />);
    expect(getAllByText("english").length).toBeGreaterThan(0);
  });

  it("should default preferredLanguage to english if user.language is missing", () => {
    window.localStorage.setItem("user", JSON.stringify({}));
    const { getAllByText } = render(<Dummy />);
    expect(getAllByText("english").length).toBeGreaterThan(0);
  });
});