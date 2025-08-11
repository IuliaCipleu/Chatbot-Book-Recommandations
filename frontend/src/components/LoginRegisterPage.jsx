import React from "react";
export default function LoginRegisterPage({ onLogin }) {
  // Simple login/register form placeholder
  return (
    <div className="login-page">
      <h2>Login or Register</h2>
      {/* Add login/register form here */}
      <form onSubmit={e => { e.preventDefault(); onLogin(); }}>
        <input type="text" placeholder="Username or Email" required />
        <input type="password" placeholder="Password" required />
        <button type="submit">Login</button>
      </form>
      <p>Don't have an account? <button>Register</button></p>
    </div>
  );
}
