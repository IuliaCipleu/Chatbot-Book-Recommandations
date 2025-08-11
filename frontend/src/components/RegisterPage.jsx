import React from "react";
import { FaUserPlus } from "react-icons/fa";

export default function RegisterPage({ onRegister, onBack }) {
  return (
    <div className="login-page">
      <h2><span className="login-icon"><FaUserPlus /></span> Create Account</h2>
      <form onSubmit={e => { e.preventDefault(); onRegister && onRegister(); }}>
        <input type="text" placeholder="Username" required />
        <input type="email" placeholder="Email" required />
        <input type="password" placeholder="Password" required />
        <input type="password" placeholder="Confirm Password" required />
        <button type="submit">Register</button>
      </form>
      <p>Already have an account? <button onClick={onBack}>Back to Login</button></p>
    </div>
  );
}
