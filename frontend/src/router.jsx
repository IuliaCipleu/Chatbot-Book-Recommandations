import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LoginRegisterPage from "./components/LoginRegisterPage";
import RegisterPage from "./components/RegisterPage";
import ChatPage from "./components/ChatPage";
import UserProfilePage from "./components/UserProfilePage";
import UserReadBooks from "./components/UserReadBooks";

export default function AppRouter() {
  const [loggedIn, setLoggedIn] = useState(false);
  const [showRegister, setShowRegister] = useState(false);
  // You can replace this with real auth logic
  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={
            loggedIn ? (
              <Navigate to="/chat" />
            ) : showRegister ? (
              <RegisterPage onRegister={() => setShowRegister(false)} onBack={() => setShowRegister(false)} />
            ) : (
              <LoginRegisterPage onLogin={() => setLoggedIn(true)} onShowRegister={() => setShowRegister(true)} />
            )
          }
        />
        <Route path="/register" element={<RegisterPage onRegister={() => setShowRegister(false)} onBack={() => setShowRegister(false)} />} />
        <Route path="/chat" element={loggedIn ? <ChatPage onLogout={() => setLoggedIn(false)} /> : <Navigate to="/" />} />
  <Route path="/profile" element={loggedIn ? <UserProfilePage /> : <Navigate to="/" />} />
  <Route path="/read-books" element={loggedIn ? <UserReadBooks username={JSON.parse(localStorage.getItem('user')||'{}').username} /> : <Navigate to="/" />} />
      </Routes>
    </Router>
  );
}
