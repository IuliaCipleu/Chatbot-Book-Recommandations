import React, { useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LoginRegisterPage from "./components/LoginRegisterPage";
import ChatPage from "./components/ChatPage";
import UserProfilePage from "./components/UserProfilePage";

export default function AppRouter() {
  const [loggedIn, setLoggedIn] = useState(false);
  // You can replace this with real auth logic
  return (
    <Router>
      <Routes>
        <Route path="/" element={loggedIn ? <Navigate to="/chat" /> : <LoginRegisterPage onLogin={() => setLoggedIn(true)} />} />
        <Route path="/chat" element={loggedIn ? <ChatPage /> : <Navigate to="/" />} />
        <Route path="/profile" element={loggedIn ? <UserProfilePage /> : <Navigate to="/" />} />
      </Routes>
    </Router>
  );
}
