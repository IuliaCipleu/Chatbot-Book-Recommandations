import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { FaMicrophone, FaVolumeUp, FaUserCircle } from "react-icons/fa";
import "../App.css";
import LanguageSelector from "./LanguageSelector";

function ChatPage({ onLogout }) {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [language, setLanguage] = useState("english");
  const [listening, setListening] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  // Handle microphone button click
  const handleMic = async () => {
    setListening(true);
    try {
      // Call backend endpoint for voice input
      const res = await fetch("http://localhost:8000/voice", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ language }),
      });
      const data = await res.json();
      if (data.text) {
        setUserInput(data.text);
      } else {
        setMessages((prev) => [...prev, { role: "bot", text: "No speech detected." }]);
      }
    } catch (err) {
      setMessages((prev) => [...prev, { role: "bot", text: "Voice input error." }]);
    } finally {
      setListening(false);
    }
  };

  const handleSend = async () => {
    if (!userInput.trim()) return;
    const newMessages = [...messages, { role: "user", text: userInput }];
    setMessages(newMessages);
    setUserInput("");
    try {
      const res = await fetch("http://localhost:8000/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: userInput,
          role: "adult",
          language,
        }),
      });
      const data = await res.json();
      let botResponse;
      if (data.error) {
        botResponse = { text: data.error };
      } else {
        let text = `Recommended Book: ${data.title}\n\nSummary: ${data.summary}`;
        if (language === "romanian") {
          text = await translateText(text, "romanian");
        }
        botResponse = {
          text,
          image_url: data.image_url
        };
      }
      setMessages((prev) => [...prev, { role: "bot", ...botResponse }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "bot", text: "Server error." }]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

  async function translateText(text, targetLang) {
    if (targetLang === "english") return text;
    // Call your backend translation endpoint or a public API
    const res = await fetch("http://localhost:8000/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, target_lang: targetLang }),
    });
    const data = await res.json();
    return data.translated || text;
  }

  // Text-to-speech function with toggle (stop if already speaking) and best voice selection
  function speak(text, lang = "en-US") {
    if ('speechSynthesis' in window) {
      const synth = window.speechSynthesis;
      if (synth.speaking) {
        synth.cancel();
        return;
      }
      const utterance = new window.SpeechSynthesisUtterance(text);
      utterance.lang = lang;
      // Try to select a matching voice for the language
      const voices = synth.getVoices();
      let selectedVoice = null;
      if (lang === "ro-RO") {
        selectedVoice = voices.find(v => v.lang === "ro-RO");
      } else {
        selectedVoice = voices.find(v => v.lang === "en-US") || voices.find(v => v.lang && v.lang.startsWith("en"));
      }
      if (selectedVoice) {
        utterance.voice = selectedVoice;
      }
      synth.speak(utterance);
    }
  }

  return (
    <div className="app">
      {/* Profile icon button top-left */}
      <button
        onClick={() => setMenuOpen(v => !v)}
        style={{
          position: 'fixed',
          top: 18,
          left: 18,
          zIndex: 1200,
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: 0,
        }}
        title="Profile menu"
      >
        <FaUserCircle size={34} color="#1976d2" />
      </button>

      {/* Side menu */}
      {menuOpen && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          width: 220,
          height: '100vh',
          background: 'rgba(255,255,255,0.98)',
          boxShadow: '2px 0 16px #0002',
          zIndex: 1300,
          display: 'flex',
          flexDirection: 'column',
          padding: '32px 18px 18px 18px',
          gap: 18,
        }}>
          <div style={{fontWeight: 700, fontSize: 18, marginBottom: 18, color: '#1976d2'}}>👤 Profile</div>
          <button style={{
            background: 'none',
            border: 'none',
            color: '#1976d2',
            fontSize: 16,
            textAlign: 'left',
            marginBottom: 12,
            cursor: 'pointer',
            padding: 0,
          }} onClick={() => {
            setMenuOpen(false);
            navigate('/profile');
          }}>See Profile</button>
          <button style={{
            background: 'none',
            border: 'none',
            color: '#d32f2f',
            fontSize: 16,
            textAlign: 'left',
            cursor: 'pointer',
            padding: 0,
          }} onClick={() => {
            if (onLogout) onLogout();
          }}>Logout</button>
        </div>
      )}

      <div style={{ position: 'fixed', top: 16, right: 16, zIndex: 1000 }}>
        <LanguageSelector language={language} setLanguage={setLanguage} />
      </div>
      <h1>📚 Smart Librarian Chatbot</h1>
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat-message ${msg.role === "user" ? "user" : "bot"}`}
            style={{ position: 'relative' }}
          >
            {msg.role === "bot" && (
              <div style={{ width: '100%', display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  onClick={() => speak(msg.text, language === "romanian" ? "ro-RO" : "en-US")}
                  style={{
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    padding: 4,
                    color: '#565656ff',
                  }}
                  title={language === "romanian" ? "Citește cu voce" : "Read aloud"}
                >
                  <FaVolumeUp size={18} />
                </button>
              </div>
            )}
            {msg.role === "bot" && <div style={{ height: 12 }} />}
            <strong>{msg.role === "user" ? "🤓 You" : "🤖 Bot"}:</strong>{" "}
            {msg.text}
            {msg.image_url && (
              <div style={{ marginTop: 12 }}>
                <img src={msg.image_url} alt="Book cover" style={{ maxWidth: 320, borderRadius: 8, boxShadow: '0 2px 8px #0002' }} />
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="input-area" style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={language === "romanian" ? "Scrie întrebarea ta aici..." : "Type your question here..."}
          style={{ flex: 1 }}
        />
        <button onClick={handleSend}>{language === "romanian" ? "Trimite" : "Send"}</button>
        <button
          style={{
            background: '#fff',
            border: '1px solid #ccc',
            borderRadius: 4,
            padding: 8,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: listening ? '0 0 0 4px #4fc3f755, 0 0 8px 4px #1976d299' : undefined,
            animation: listening ? 'pulse-blue 1s infinite' : undefined
          }}
          title={listening ? (language === "romanian" ? "Ascultă..." : "Listening...") : "Speak"}
          onClick={handleMic}
        >
          <FaMicrophone size={20} color={listening ? "#1976d2" : "#888"} />
        </button>
        {/* Add keyframes for blue pulse animation */}
        <style>{`
          @keyframes pulse-blue {
            0% { box-shadow: 0 0 0 4px #4fc3f755, 0 0 8px 4px #1976d299; }
            50% { box-shadow: 0 0 0 8px #4fc3f722, 0 0 16px 8px #1976d244; }
            100% { box-shadow: 0 0 0 4px #4fc3f755, 0 0 8px 4px #1976d299; }
          }
        `}</style>
      </div>
    </div>
  );
}

export default ChatPage;
