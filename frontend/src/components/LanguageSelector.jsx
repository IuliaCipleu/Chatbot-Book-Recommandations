import React from "react";
import { FaFlagUsa } from "react-icons/fa";

export default function LanguageSelector({ language, setLanguage }) {
  return (
    <div style={{ position: "absolute", top: 16, right: 16, display: "flex", gap: 8 }}>
      <button
        onClick={() => setLanguage("english")}
        style={{
          background: language === "english" ? "#e0e0e0" : "white",
          border: "1px solid #ccc",
          borderRadius: 4,
          padding: 8,
          cursor: "pointer"
        }}
        title="English"
      >
        <span style={{ fontSize: 24 }}>🇺🇸</span>
      </button>
      <button
        onClick={() => setLanguage("romanian")}
        style={{
          background: language === "romanian" ? "#e0e0e0" : "white",
          border: "1px solid #ccc",
          borderRadius: 4,
          padding: 8,
          cursor: "pointer"
        }}
        title="Romanian"
      >
        <span style={{ fontSize: 24 }}>🇷🇴</span>
      </button>
    </div>
  );
}