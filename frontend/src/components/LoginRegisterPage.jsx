import React, { useState } from "react";
import { FaBookOpen } from "react-icons/fa";
import { FaGoogle, FaFacebookF, FaUser } from "react-icons/fa";

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
      const data = await res.json();
      if (data.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
        // After successful login:
        localStorage.setItem("jwtToken", data.access_token);
      }
      onLogin();
    } catch (err) {
      setError(err.message);
    }
  }

  // Handler for Google login
  function handleGoogleLogin() {
    window.location.href = "http://localhost:8000/auth/google/login";
  }

  // Handler for Facebook login
  function handleFacebookLogin() {
    window.location.href = "http://localhost:8000/auth/facebook/login";
  }

  const buttonStyle = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    width: '100%',
    minWidth: '220px',
    maxWidth: '320px',
    height: '40px',
    fontSize: '1rem',
    borderRadius: 8,
    fontWeight: 600,
    margin: '0 auto',
    boxShadow: '0 1px 4px #1976d222',
    cursor: 'pointer',
    transition: 'background 0.2s',
    gap: '10px',
    marginBottom: '8px',
  };

  return (
    <div className="login-page">
      <h2><span className="login-icon"><FaBookOpen /></span> Smart Librarian Login</h2>
      <form onSubmit={handleLogin} style={{width: '100%', maxWidth: '320px', margin: '0 auto'}}>
        <label htmlFor="login-username" style={{alignSelf: 'flex-start', marginBottom: 2, fontWeight: 500, color: '#222'}}>Username or Email</label>
        <input id="login-username" type="text" autoComplete="username" required style={{background: '#fff', color: '#222', border: '1.5px solid #bdbdbd'}} />
        <label htmlFor="login-password" style={{alignSelf: 'flex-start', marginBottom: 2, fontWeight: 500, color: '#222'}}>Password</label>
        <input id="login-password" type="password" autoComplete="current-password" required style={{background: '#fff', color: '#222', border: '1.5px solid #bdbdbd'}} />
        <button type="submit" style={{
          ...buttonStyle,
          background: '#1976d2',
          color: '#fff',
          border: 'none',
        }}><FaUser style={{fontSize: '1.2em'}} />Login</button>
      </form>
      <div style={{margin: '16px 0', display: 'flex', flexDirection: 'column', gap: '8px', width: '100%', maxWidth: '320px', marginLeft: 'auto', marginRight: 'auto'}}>
        <button type="button" onClick={handleGoogleLogin} style={{
          ...buttonStyle,
          background: '#fff',
          color: '#222',
          border: '1.5px solid #4285F4',
          boxShadow: '0 1px 4px #4285F422',
        }}><FaGoogle style={{color: '#4285F4', fontSize: '1.2em'}} />Login with Google</button>
        <button type="button" onClick={handleFacebookLogin} style={{
          ...buttonStyle,
          background: '#fff',
          color: '#222',
          border: '1.5px solid #4267B2',
          boxShadow: '0 1px 4px #4267B222',
        }}><FaFacebookF style={{color: '#4267B2', fontSize: '1.2em'}} />Login with Facebook</button>
      </div>
      {error && <div className="error">{error}</div>}
      <p>Don't have an account? <button onClick={onShowRegister}>Register</button></p>
    </div>
  );
}
