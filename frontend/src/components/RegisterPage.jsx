import React, { useState } from "react";
import { FaBookOpen } from "react-icons/fa";

export default function RegisterPage({ onRegister, onBack }) {
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  async function handleRegister(e) {
    e.preventDefault();
    const username = e.target[0].value;
    const email = e.target[1].value;
    const password = e.target[2].value;
    const confirm = e.target[3].value;
    setError(null);
    setSuccess(false);
    if (password !== confirm) {
      setError("Passwords do not match");
      return;
    }
    try {
      const res = await fetch("http://localhost:8000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Registration failed");
      setSuccess(true);
      setTimeout(() => {
        setSuccess(false);
        onRegister && onRegister();
      }, 1200);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="login-page">
      <h2><span className="login-icon"><FaBookOpen /></span> Register for Smart Librarian</h2>
      <form onSubmit={handleRegister}>
        <label htmlFor="register-username" style={{alignSelf: 'flex-start', marginBottom: 2, fontWeight: 500, color: '#222'}}>Username</label>
        <input id="register-username" type="text" autoComplete="username" required style={{background: '#fff', color: '#222', border: '1.5px solid #bdbdbd'}} />
        <label htmlFor="register-email" style={{alignSelf: 'flex-start', marginBottom: 2, fontWeight: 500, color: '#222'}}>Email</label>
        <input id="register-email" type="email" autoComplete="email" required style={{background: '#fff', color: '#222', border: '1.5px solid #bdbdbd'}} />
        <label htmlFor="register-password" style={{alignSelf: 'flex-start', marginBottom: 2, fontWeight: 500, color: '#222'}}>Password</label>
        <input id="register-password" type="password" autoComplete="new-password" required style={{background: '#fff', color: '#222', border: '1.5px solid #bdbdbd'}} />
        <label htmlFor="register-confirm" style={{alignSelf: 'flex-start', marginBottom: 2, fontWeight: 500, color: '#222'}}>Confirm Password</label>
        <input id="register-confirm" type="password" autoComplete="new-password" required style={{background: '#fff', color: '#222', border: '1.5px solid #bdbdbd'}} />
        <button type="submit" style={{
          height: '20px',
          padding: '0 16px',
          fontSize: '1rem',
          borderRadius: 8,
          marginTop: 6,
          minWidth: 0,
          background: '#1976d2',
          color: '#fff',
          border: 'none',
          fontWeight: 600,
          boxShadow: '0 1px 4px #1976d222',
          cursor: 'pointer',
          transition: 'background 0.2s'
        }}>Register</button>
      </form>
      {error && <div className="error">{error}</div>}
      {success && <div className="success">Registration successful!</div>}
      <p>Already have an account? <button onClick={onBack}>Back to Login</button></p>
    </div>
  );
}
