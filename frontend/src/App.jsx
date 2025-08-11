import React, { useState } from "react";
import { FaMicrophone, FaVolumeUp } from "react-icons/fa";
import "./App.css";
import LanguageSelector from "./components/LanguageSelector";


function App() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [language, setLanguage] = useState("english");
  const [listening, setListening] = useState(false);

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
      <LanguageSelector language={language} setLanguage={setLanguage} />
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
            justifyContent: 'center',
            boxShadow: listening ? '0 0 0 4px #ff000055, 0 0 8px 4px #ff000099' : undefined,
            animation: listening ? 'pulse 1s infinite' : undefined
          }}
          title={listening ? (language === "romanian" ? "Ascultă..." : "Listening...") : "Speak"}
          onClick={handleMic}
        >
          <FaMicrophone size={20} color={listening ? "#e53935" : "#888"} />
        </button>
        {/* Add keyframes for pulse animation */}
        <style>{`
          @keyframes pulse {
            0% { box-shadow: 0 0 0 4px #ff000055, 0 0 8px 4px #ff000099; }
            50% { box-shadow: 0 0 0 8px #ff000022, 0 0 16px 8px #ff000044; }
            100% { box-shadow: 0 0 0 4px #ff000055, 0 0 8px 4px #ff000099; }
          }
        `}</style>
      </div>
    </div>
  );
}

export default App;
