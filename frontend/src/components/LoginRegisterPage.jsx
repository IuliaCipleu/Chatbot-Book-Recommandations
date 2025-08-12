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
    <label htmlFor="login-username" style={{alignSelf: 'flex-start', marginBottom: 2, fontWeight: 500, color: '#222'}}>Username or Email</label>
    <input id="login-username" type="text" autoComplete="username" required style={{background: '#fff', color: '#222', border: '1.5px solid #bdbdbd'}} />
    <label htmlFor="login-password" style={{alignSelf: 'flex-start', marginBottom: 2, fontWeight: 500, color: '#222'}}>Password</label>
    <input id="login-password" type="password" autoComplete="current-password" required style={{background: '#fff', color: '#222', border: '1.5px solid #bdbdbd'}} />
  <button type="submit" style={{padding: '8px 0', fontSize: '0.98rem', borderRadius: 8, marginTop: 6, minWidth: 90}}>Login</button>
      </form>
      {error && <div className="error">{error}</div>}
      <p>Don't have an account? <button onClick={onShowRegister}>Register</button></p>
    </div>
  );
}
