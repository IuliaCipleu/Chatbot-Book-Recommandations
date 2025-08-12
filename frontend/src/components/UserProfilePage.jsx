import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

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
      const res = await fetch("http://localhost:8000/update_user", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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
      const res = await fetch("http://localhost:8000/delete_user", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
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

  if (!user) return <div className="profile-page"><h2>User Profile</h2><p>Loading...</p></div>;

  return (
    <div className="profile-page">
      <h2>User Profile</h2>
      {error && <div className="error">{error}</div>}
      {success && <div className="success">{success}</div>}
      {!editMode ? (
        <>
          <p><b>Username:</b> {user.username}</p>
          <p><b>Email:</b> {user.email}</p>
          <p><b>Language:</b> {user.language}</p>
          <p><b>Profile:</b> {user.profile}</p>
          <p><b>Voice Enabled:</b> {user.voice_enabled ? 'Yes' : 'No'}</p>
          <button onClick={handleEdit} style={{marginRight: 12}}>Edit Profile</button>
          <button onClick={handleDelete} style={{color: '#d32f2f'}}>Delete Profile</button>
        </>
      ) : (
        <form onSubmit={handleUpdate} style={{display: 'flex', flexDirection: 'column', gap: 10, maxWidth: 340}}>
          <label>Username: <input name="username" value={form.username} onChange={handleChange} disabled /></label>
          <label>Email: <input name="email" value={form.email} onChange={handleChange} /></label>
          <label>Language: <input name="language" value={form.language} onChange={handleChange} /></label>
          <label>Profile: <input name="profile" value={form.profile} onChange={handleChange} /></label>
          <label>Voice Enabled: <input name="voice_enabled" type="checkbox" checked={form.voice_enabled} onChange={handleChange} /></label>
          <div style={{display: 'flex', gap: 10}}>
            <button type="submit">Save</button>
            <button type="button" onClick={handleCancel}>Cancel</button>
          </div>
        </form>
      )}
    </div>
  );
}
