import React, { useState } from "react";
import { FaUserPlus } from "react-icons/fa";

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
      <h2><span className="login-icon"><FaUserPlus /></span> Create Account</h2>
      <form onSubmit={handleRegister}>
        <input type="text" placeholder="Username" required />
        <input type="email" placeholder="Email" required />
        <input type="password" placeholder="Password" required />
        <input type="password" placeholder="Confirm Password" required />
        <button type="submit">Register</button>
      </form>
      {error && <div className="error">{error}</div>}
      {success && <div className="success">Registration successful!</div>}
      <p>Already have an account? <button onClick={onBack}>Back to Login</button></p>
    </div>
  );
}
