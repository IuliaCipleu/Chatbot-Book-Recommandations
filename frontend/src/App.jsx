import React, { useState } from "react";
import { FaMicrophone } from "react-icons/fa";
import "./App.css";
import LanguageSelector from "./components/LanguageSelector";

function App() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [language, setLanguage] = useState("english");

  // Handle microphone button click
  const handleMic = async () => {
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

  return (
    <div className="app">
      <LanguageSelector language={language} setLanguage={setLanguage} />
      <h1>📚 Smart Librarian Chatbot</h1>
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat-message ${msg.role === "user" ? "user" : "bot"}`}
          >
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
          placeholder="Type your question here..."
          style={{ flex: 1 }}
        />
        <button onClick={handleSend}>Send</button>
        <button
          style={{
            background: '#fff',
            border: '1px solid #ccc',
            borderRadius: 4,
            padding: 8,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}
          title="Speak"
          onClick={handleMic}
        >
          <FaMicrophone size={20} color="#888" />
        </button>
      </div>
    </div>
  );
}

export default App;
