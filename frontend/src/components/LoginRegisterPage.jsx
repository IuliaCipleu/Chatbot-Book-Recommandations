import React, { useState } from "react";
import { FaBookOpen } from "react-icons/fa";

export default function LoginRegisterPage({ onLogin, onShowRegister }) {
  const [error, setError] = useState(null);

  async function handleLogin(e) {
    e.preventDefault();
    const username = e.target[0].value;
    const password = e.target[1].value;
    setError(null);
    try {
      const res = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Login failed");
      onLogin();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="login-page">
      <h2><span className="login-icon"><FaBookOpen /></span> Smart Librarian Login</h2>
      <form onSubmit={handleLogin}>
        <input type="text" placeholder="Username or Email" required />
        <input type="password" placeholder="Password" required />
        <button type="submit">Login</button>
      </form>
      {error && <div className="error">{error}</div>}
      <p>Don't have an account? <button onClick={onShowRegister}>Register</button></p>
    </div>
  );
}
