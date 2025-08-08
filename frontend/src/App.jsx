import React, { useState } from "react";
import "./App.css";
import LanguageSelector from "./components/LanguageSelector";

function App() {
  const [messages, setMessages] = useState([]);
  const [userInput, setUserInput] = useState("");
  const [language, setLanguage] = useState("english");

  const handleSend = async () => {
    if (!userInput.trim()) return;

    // Add user message to chat
    const newMessages = [...messages, { role: "user", text: userInput }];
    setMessages(newMessages);
    setUserInput("");

    // Simulate bot reply (replace this with actual backend call)
    const botResponse = `This is a placeholder reply to: "${userInput}"`;
    setTimeout(() => {
      setMessages((prev) => [...prev, { role: "bot", text: botResponse }]);
    }, 500);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleSend();
    }
  };

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
          </div>
        ))}
      </div>

      <div className="input-area">
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your question here..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default App;
