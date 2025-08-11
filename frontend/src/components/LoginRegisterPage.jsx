import React from "react";
import { FaBookOpen } from "react-icons/fa";

export default function LoginRegisterPage({ onLogin }) {
  return (
    <div className="login-page">
      <h2><span className="login-icon"><FaBookOpen /></span> Smart Librarian Login</h2>
      <form onSubmit={e => { e.preventDefault(); onLogin(); }}>
        <input type="text" placeholder="Username or Email" required />
        <input type="password" placeholder="Password" required />
        <button type="submit">Login</button>
      </form>
      <p>Don't have an account? <button>Register</button></p>
    </div>
  );
}
