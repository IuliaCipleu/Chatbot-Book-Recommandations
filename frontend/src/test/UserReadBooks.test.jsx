// frontend/src/components/UserReadBooks.test.jsx
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import React from "react";
import { render, cleanup, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import UserReadBooks from "../components/UserReadBooks";

// Helper: route-aware fetch mock
function setFetchRoutes(handlers) {
  global.fetch = vi.fn(async (input, init) => {
    const url = typeof input === "string" ? input : input?.url ?? "";
    for (const h of handlers) {
      if (typeof h.match === "string" ? url.includes(h.match) : h.match.test(url)) {
        if (h.reject) return Promise.reject(h.reject);
        const payload = typeof h.body === "function" ? await h.body({ url, init }) : h.body;
        return Promise.resolve({
          ok: h.ok ?? true,
          status: h.status ?? 200,
          json: async () => payload ?? {},
        });
      }
    }
    // Default: harmless empty success to avoid "undefined.ok"
    return Promise.resolve({ ok: true, status: 200, json: async () => ({}) });
  });
}

beforeEach(() => {
  vi.resetAllMocks();
  window.localStorage.clear();
  window.localStorage.setItem("jwtToken", "fake-token");
});

afterEach(() => {
  cleanup();
  vi.resetAllMocks();
});

describe("UserReadBooks", () => {
  it("shows error if fetchBooks fails", async () => {
    setFetchRoutes([
      { match: "/user_read_books", reject: new Error("fail") }, // mount: read-books fails
      { match: "/search_titles", body: { titles: [], total: 0 } }, // still safe
    ]);

    const { container } = render(<UserReadBooks username="alice" />);
    const root = container.firstElementChild || container;
    const scoped = within(root);

    expect(await scoped.findByText("Failed to load read books.")).toBeTruthy();
  });

  it("shows success message when book is added", async () => {
    setFetchRoutes([
      // Mount
      { match: "/user_read_books", body: { books: [] } },
      { match: "/search_titles", body: { titles: [], total: 0 } },
      // Add POST
      { match: "/add_read_book", body: {}, ok: true, status: 200 },
      // After add the component may re-fetch one or both:
      { match: "/user_read_books", body: { books: [] } },
      { match: "/search_titles", body: { titles: [], total: 0 } },
    ]);

    const { container } = render(<UserReadBooks username="alice" />);
    const root = container.firstElementChild || container;
    const scoped = within(root);

    // Use the first form inputs (add form)
    const titleInput = scoped.getAllByPlaceholderText(/book title/i)[0];
    const ratingInput = scoped.getAllByPlaceholderText(/rating \(1-5\)/i)[0];

    await userEvent.clear(titleInput);
    await userEvent.type(titleInput, "Book B");
    await userEvent.clear(ratingInput);
    await userEvent.type(ratingInput, "4");

    await userEvent.click(scoped.getByRole("button", { name: /^add$/i }));

    // Component should show success after add
    expect(await scoped.findByText("Book added!")).toBeTruthy();
  });

  it("shows error if rating is invalid when adding from all books", async () => {
    setFetchRoutes([
      // Mount
      { match: "/user_read_books", body: { books: [] } },
      // Library search (empty or any)
      { match: "/search_titles", body: { titles: ["Book C"], total: 1 } },
    ]);

    const { container } = render(<UserReadBooks username="alice" />);
    const root = container.firstElementChild || container;
    const scoped = within(root);

    await userEvent.type(scoped.getByPlaceholderText(/search all books/i), "Book C");

    // Suggestion should appear
    expect(await scoped.findByText("Book C")).toBeTruthy();

    // Leave "all books" rating blank
    const ratingInputs = scoped.getAllByPlaceholderText(/rating \(1-5\)/i);
    await userEvent.clear(ratingInputs[ratingInputs.length - 1]);

    await userEvent.click(scoped.getByRole("button", { name: /mark as read/i }));

    expect(
      await scoped.findByText("Please enter a rating (1-5) before marking as read.")
    ).toBeTruthy();
  });


  it("shows 'No books found.' if no books in library", async () => {
    setFetchRoutes([
      { match: "/user_read_books", body: { books: [] } },
      { match: "/search_titles", body: { titles: [], total: 0 } },
    ]);

    const { container } = render(<UserReadBooks username="alice" />);
    const root = container.firstElementChild || container;
    const scoped = within(root);

    expect(await scoped.findByText("No books found.")).toBeTruthy();
  });

  it("shows 'No books added yet.' if user has no read books", async () => {
    setFetchRoutes([
      { match: "/user_read_books", body: { books: [] } },
      { match: "/search_titles", body: { titles: ["Book F"], total: 1 } },
    ]);

    const { container } = render(<UserReadBooks username="alice" />);
    const root = container.firstElementChild || container;
    const scoped = within(root);

    expect(await scoped.findByText("No books added yet.")).toBeTruthy();
  });
});
