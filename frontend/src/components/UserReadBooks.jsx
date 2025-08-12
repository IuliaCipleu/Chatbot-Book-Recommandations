import React, { useState, useEffect } from "react";

export default function UserReadBooks({ username }) {
  // All ChromaDB books
  const [allBooks, setAllBooks] = useState([]);
  const [searchAll, setSearchAll] = useState("");
  const [sortAllBy, setSortAllBy] = useState("title");
  const [sortAllDir, setSortAllDir] = useState("asc");
  const [addRating, setAddRating] = useState("");
  const [newBook, setNewBook] = useState("");
  const [rating, setRating] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [books, setBooks] = useState([]);
  const [sortBy, setSortBy] = useState("title");
  const [sortDir, setSortDir] = useState("asc");
  // Pagination for All Books
  const [allPage, setAllPage] = useState(1);
  const ALL_PER_PAGE = 15;

  // Pagination state for total
  const [allTotal, setAllTotal] = useState(0);

  // Fetch books for the current page and search
  useEffect(() => {
    async function fetchAllBooks() {
      try {
        const res = await fetch(`http://localhost:8000/search_titles?q=${encodeURIComponent(searchAll)}&limit=${ALL_PER_PAGE}&offset=${(allPage-1)*ALL_PER_PAGE}`);
        const data = await res.json();
        setAllBooks(data.titles || []);
        setAllTotal(data.total || 0);
      } catch {
        setAllBooks([]);
        setAllTotal(0);
      }
    }
    fetchAllBooks();
  }, [allPage, searchAll]);

  // No need to filter/sort here, backend does it
  function filteredAllBooks() {
    return allBooks;
  }

  // No need to slice, backend returns only the current page
  function pagedAllBooks() {
    return allBooks;
  }

  // We don't know total pages unless backend provides it, so just show arrows

  async function handleAddFromAll(title) {
    setError(null); setSuccess(null);
    try {
      const res = await fetch("http://localhost:8000/add_read_book", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, book_title: title, rating: addRating ? Number(addRating) : null })
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Failed to add book.");
      setSuccess("Book added!");
      setAddRating("");
      fetchBooks();
    } catch (e) {
      setError(e.message);
    }
  }

  async function fetchBooks() {
    setError(null);
    try {
      const res = await fetch(`http://localhost:8000/user_read_books?username=${encodeURIComponent(username)}`);
      const data = await res.json();
      setBooks(data.books || []);
    } catch (e) {
      setError("Failed to load read books.");
    }
  }

  async function handleAdd(e) {
    e.preventDefault();
    setError(null); setSuccess(null);
    if (!newBook) return setError("Enter a book title.");
    try {
      const res = await fetch("http://localhost:8000/add_read_book", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, book_title: newBook, rating: rating ? Number(rating) : null })
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Failed to add book.");
      setSuccess("Book added!");
      setNewBook("");
      setRating("");
      fetchBooks();
    } catch (e) {
      setError(e.message);
    }
  }

  // Auto-suggest for book titles from ChromaDB
  async function handleBookInput(e) {
    const value = e.target.value;
    setNewBook(value);
    if (value.length > 1) {
      try {
        const res = await fetch(`http://localhost:8000/search_titles?q=${encodeURIComponent(value)}`);
        const data = await res.json();
        setSuggestions(data.titles || []);
        setShowSuggestions(true);
      } catch {
        setSuggestions([]);
      }
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  }

  function handleSuggestionClick(title) {
    setNewBook(title);
    setSuggestions([]);
    setShowSuggestions(false);
  }

  // Sorting
  function sortBooks(list) {
    const sorted = [...list].sort((a, b) => {
      let v1 = a[sortBy] || "";
      let v2 = b[sortBy] || "";
      if (sortBy === "rating") {
        v1 = v1 || 0; v2 = v2 || 0;
      }
      if (v1 < v2) return sortDir === "asc" ? -1 : 1;
      if (v1 > v2) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
    return sorted;
  }

  return (
    <div className="read-books-card" style={{
      background: '#f5f7fb',
      borderRadius: 12,
      boxShadow: '0 2px 12px #0001',
      border: '1px solid #d0d7e2',
      padding: 24,
      margin: '0 auto',
      maxWidth: 1400,
      marginBottom: 24
    }}>
      <h3 style={{ marginTop: 0, marginBottom: 14, color: '#1976d2', textAlign: 'center' }}>Books You've Read</h3>
      <form onSubmit={handleAdd} style={{ display: 'flex', gap: 8, marginBottom: 12, justifyContent: 'center', position: 'relative' }} autoComplete="off">
        <div style={{ flex: 2, minWidth: 0, position: 'relative' }}>
          <input
            type="text"
            placeholder="Book title"
            value={newBook}
            onChange={handleBookInput}
            onFocus={() => setShowSuggestions(suggestions.length > 0)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 120)}
            style={{ width: '100%' }}
            autoComplete="off"
          />
          {showSuggestions && suggestions.length > 0 && (
            <ul style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              background: '#fff',
              border: '1px solid #bbb',
              borderRadius: 6,
              zIndex: 10,
              maxHeight: 180,
              overflowY: 'auto',
              margin: 0,
              padding: 0,
              listStyle: 'none',
              boxShadow: '0 2px 8px #0002'
            }}>
              {suggestions.map((s, i) => (
                <li key={i} style={{ padding: '7px 12px', cursor: 'pointer' }} onMouseDown={() => handleSuggestionClick(s)}>{s}</li>
              ))}
            </ul>
          )}
        </div>
        <input
          type="number"
          min="1"
          max="5"
          placeholder="Rating (1-5)"
          value={rating}
          onChange={e => setRating(e.target.value)}
          style={{ width: 90 }}
        />
        <button type="submit" style={{ background: '#1976d2', color: '#fff', border: 'none', borderRadius: 6, padding: '6px 14px', fontWeight: 500, cursor: 'pointer' }}>Add</button>
      </form>
      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}
      <div style={{ overflowX: 'auto', marginBottom: 32 }}>
        <h3 style={{ marginTop: 30, marginBottom: 10, color: '#1976d2', textAlign: 'center' }}>All Books in Library</h3>
        <div style={{ display: 'flex', gap: 10, marginBottom: 10, justifyContent: 'center' }}>
          <input
            type="text"
            placeholder="Search all books..."
            value={searchAll}
            onChange={e => { setSearchAll(e.target.value); setAllPage(1); }}
            style={{ padding: 7, borderRadius: 6, border: '1px solid #bbb', minWidth: 180 }}
          />
          <input
            type="number"
            min="1"
            max="5"
            placeholder="Rating (1-5)"
            value={addRating}
            onChange={e => setAddRating(e.target.value)}
            style={{ width: 90 }}
          />
        </div>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', background: '#fff', borderRadius: 8 }}>
            <thead>
              <tr>
                <th style={{ cursor: 'pointer', padding: 8, borderBottom: '1px solid #ccc', color: '#000' }} onClick={() => {
                  setSortAllBy('title'); setSortAllDir(sortAllBy === 'title' && sortAllDir === 'asc' ? 'desc' : 'asc');
                }}>Title {sortAllDir === 'asc' ? '▲' : '▼'}</th>
                <th style={{ padding: 8, borderBottom: '1px solid #ccc', color: '#000' }}>Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredAllBooks().length === 0 && (
                <tr><td colSpan={2} style={{ color: '#888', textAlign: 'center', padding: 12 }}>No books found.</td></tr>
              )}
              {pagedAllBooks().map((title, i) => (
                <tr key={i}>
                  <td style={{ padding: 8, borderBottom: '1px solid #eee', color: '#000' }}>{title}</td>
                  <td style={{ padding: 8, borderBottom: '1px solid #eee', textAlign: 'center' }}>
                    <button onClick={() => handleAddFromAll(title)} style={{ background: '#1976d2', color: '#fff', border: 'none', borderRadius: 6, padding: '4px 12px', fontWeight: 500, cursor: 'pointer' }}>Mark as Read</button>
                  </td>
                </tr>
              ))}
        {/* Pagination controls for All Books */}
        <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 12, margin: '12px 0' }}>
          <button
            onClick={() => setAllPage(p => Math.max(1, p - 1))}
            disabled={allPage === 1}
            style={{ padding: '4px 12px', borderRadius: 6, border: '1px solid #bbb', background: allPage === 1 ? '#eee' : '#fff', color: '#1976d2', cursor: allPage === 1 ? 'not-allowed' : 'pointer', fontSize: 18 }}
          >&lt;-</button>
          <span style={{ fontWeight: 600, color: '#1976d2', fontSize: 18 }}>
            Page {allPage} of {Math.max(1, Math.ceil(allTotal / ALL_PER_PAGE))}
          </span>
          <button
            onClick={() => setAllPage(p => p + 1)}
            disabled={allPage >= Math.ceil(allTotal / ALL_PER_PAGE)}
            style={{ padding: '4px 12px', borderRadius: 6, border: '1px solid #bbb', background: allPage >= Math.ceil(allTotal / ALL_PER_PAGE) ? '#eee' : '#fff', color: '#1976d2', cursor: allPage >= Math.ceil(allTotal / ALL_PER_PAGE) ? 'not-allowed' : 'pointer', fontSize: 18 }}
          >-&gt;</button>
        </div>
            </tbody>
          </table>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: 10, background: '#fff', borderRadius: 8 }}>
          <thead>
            <tr>
              <th style={{ cursor: 'pointer', padding: 8, borderBottom: '1px solid #ccc', color: '#000' }} onClick={() => {
                setSortBy('title'); setSortDir(sortBy === 'title' && sortDir === 'asc' ? 'desc' : 'asc');
              }}>Title {sortBy === 'title' ? (sortDir === 'asc' ? '▲' : '▼') : ''}</th>
              <th style={{ cursor: 'pointer', padding: 8, borderBottom: '1px solid #ccc', color: '#000' }} onClick={() => {
                setSortBy('rating'); setSortDir(sortBy === 'rating' && sortDir === 'asc' ? 'desc' : 'asc');
              }}>Rating {sortBy === 'rating' ? (sortDir === 'asc' ? '▲' : '▼') : ''}</th>
              <th style={{ cursor: 'pointer', padding: 8, borderBottom: '1px solid #ccc', color: '#000' }} onClick={() => {
                setSortBy('read_date'); setSortDir(sortBy === 'read_date' && sortDir === 'asc' ? 'desc' : 'asc');
              }}>Date {sortBy === 'read_date' ? (sortDir === 'asc' ? '▲' : '▼') : ''}</th>
            </tr>
          </thead>
          <tbody>
            {sortBooks(books).length === 0 && (
              <tr><td colSpan={3} style={{ color: '#888', textAlign: 'center', padding: 12 }}>No books added yet.</td></tr>
            )}
            {sortBooks(books).map((b, i) => (
              <tr key={i}>
                <td style={{ padding: 8, borderBottom: '1px solid #eee', color: '#000' }}>{b.title}</td>
                <td style={{ padding: 8, borderBottom: '1px solid #eee', textAlign: 'center' }}>{b.rating ? b.rating + '/5' : ''}</td>
                <td style={{ padding: 8, borderBottom: '1px solid #eee', textAlign: 'center' }}>{b.read_date}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
