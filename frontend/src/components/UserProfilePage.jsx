import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import UserReadBooks from "./UserReadBooks";
import "../App.css";

export default function UserProfilePage() {
  const [user, setUser] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [form, setForm] = useState({ username: '', email: '', language: '', profile: '', voice_enabled: false });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const navigate = useNavigate();

  // Load user info from localStorage or backend
  useEffect(() => {
    // Try to get user from localStorage (set on login)
    const stored = localStorage.getItem('user');
    if (stored) {
      const u = JSON.parse(stored);
      setUser(u);
      setForm({
        username: u.username,
        email: u.email,
        language: u.language,
        profile: u.profile,
        voice_enabled: u.voice_enabled
      });
    }
    // Optionally, fetch from backend for fresh data
  }, []);

  const handleEdit = () => setEditMode(true);
  const handleCancel = () => { setEditMode(false); setError(null); setSuccess(null); };

  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleUpdate = async e => {
    e.preventDefault();
    setError(null); setSuccess(null);
    try {
      const token = localStorage.getItem("jwtToken");
      const res = await fetch("http://localhost:8000/update_user", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(form),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Update failed");
      setSuccess("Profile updated!");
      setEditMode(false);
      setUser(form);
      localStorage.setItem('user', JSON.stringify(form));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Are you sure you want to delete your profile? This cannot be undone.")) return;
    setError(null); setSuccess(null);
    try {
      const token = localStorage.getItem("jwtToken");
      const res = await fetch("http://localhost:8000/delete_user", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ username: user.username }),
      });
      if (!res.ok) throw new Error((await res.json()).detail || "Delete failed");
      localStorage.removeItem('user');
      setSuccess("Profile deleted. Redirecting...");
      setTimeout(() => { navigate('/'); }, 1200);
    } catch (err) {
      setError(err.message);
    }
  };

  if (!user) return (
    <div className="page-container">
      <div className="card profile-card">
        <h2>User Profile</h2>
        <p>Loading...</p>
        <div style={{ marginTop: 32 }}>
          <UserReadBooks username={user?.username} />
        </div>
      </div>
    </div>
  );

  return (
    <div className="page-container">
      <div className="card profile-card">
        <h2 style={{ textAlign: 'center', marginBottom: 18 }}>User Profile</h2>
        {error && <div className="error-message" style={{ marginBottom: 10 }}>{error}</div>}
        {success && <div className="success-message" style={{ marginBottom: 10 }}>{success}</div>}
        {!editMode ? (
          <>
            <div className="profile-info">
              <div><b>Username:</b> {user.username}</div>
              <div><b>Email:</b> {user.email}</div>
              <div><b>Language:</b> {user.language}</div>
              <div><b>Category:</b> {user.profile}</div>
              <div><b>Voice Enabled:</b> {user.voice_enabled ? 'Yes' : 'No'}</div>
            </div>
            <div style={{ display: 'flex', gap: 12, marginTop: 18, justifyContent: 'center' }}>
              <button className="primary-btn" onClick={handleEdit}>Edit Profile</button>
              <button className="danger-btn" onClick={handleDelete}>Delete Profile</button>
            </div>
          </>
        ) : (
          <form onSubmit={handleUpdate} className="profile-form">
            <label>Username:
              <input name="username" value={form.username} onChange={handleChange} disabled />
            </label>
            <label>Email:
              <input name="email" value={form.email} onChange={handleChange} />
            </label>
            <label>Language:
              <select name="language" value={form.language} onChange={handleChange}>
                <option value="English">English</option>
                <option value="Romanian">Romanian</option>
              </select>
            </label>
            <label>Category:
              <select name="profile" value={form.profile} onChange={handleChange}>
                <option value="Child">Child</option>
                <option value="Teen">Teen</option>
                <option value="Adult">Adult</option>
                <option value="Technical">Technical</option>
              </select>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', gap: 8 }}>Voice Enabled:
              <input name="voice_enabled" type="checkbox" checked={form.voice_enabled} onChange={handleChange} style={{ width: 18, height: 18 }} />
            </label>
            <div style={{ display: 'flex', gap: 10, justifyContent: 'center', marginTop: 10 }}>
              <button className="primary-btn" type="submit">Save</button>
              <button className="secondary-btn" type="button" onClick={handleCancel}>Cancel</button>
            </div>
          </form>
        )}
      </div>
      <style>{`
        .page-container {
          min-height: 100vh;
          display: flex;
          align-items: center;
          justify-content: center;
          background: #e3e7f0;
        }
        .card.profile-card {
          background: #f5f7fb;
          border-radius: 14px;
          box-shadow: 0 2px 16px 0 #0001;
          padding: 36px 32px 28px 32px;
          min-width: 340px;
          max-width: 380px;
          margin: 32px auto;
          color: #000;
        }
        .profile-info > div {
          margin-bottom: 8px;
          font-size: 1.08em;
          color: #000;
        }
        .profile-form {
          display: flex;
          flex-direction: column;
          gap: 12px;
          color: #000;
        }
        .profile-form label {
          display: flex;
          flex-direction: column;
          font-weight: 500;
          color: #000;
        }
        .profile-form input, .profile-form select {
          margin-top: 4px;
          padding: 7px 10px;
          border-radius: 6px;
          border: 1px solid #bbb;
          font-size: 1em;
          background: #fff;
          color: #000;
        }
        h2 {
          color: #000;
        }
        .primary-btn {
          background: #1976d2;
          color: #fff;
          border: none;
          border-radius: 6px;
          padding: 8px 18px;
          font-size: 1em;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.18s;
        }
        .primary-btn:hover {
          background: #1256a3;
        }
        .secondary-btn {
          background: #e3e7f0;
          color: #333;
          border: none;
          border-radius: 6px;
          padding: 8px 18px;
          font-size: 1em;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.18s;
        }
        .secondary-btn:hover {
          background: #cfd8e3;
        }
        .danger-btn {
          background: #d32f2f;
          color: #fff;
          border: none;
          border-radius: 6px;
          padding: 8px 18px;
          font-size: 1em;
          font-weight: 500;
          cursor: pointer;
          transition: background 0.18s;
        }
        .danger-btn:hover {
          background: #a31515;
        }
        .error-message {
          background: #ffeaea;
          color: #b71c1c;
          border-radius: 6px;
          padding: 8px 12px;
          font-size: 1em;
        }
        .success-message {
          background: #e8f5e9;
          color: #2e7d32;
          border-radius: 6px;
          padding: 8px 12px;
          font-size: 1em;
        }
      `}</style>
    </div>
  );
}
