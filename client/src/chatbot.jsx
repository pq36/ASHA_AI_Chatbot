import React, { useEffect, useState } from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import { useNavigate } from "react-router-dom";

const Chatbot = () => {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi! How can I help you today?" },
  ]);
  const [input, setInput] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const cookies = document.cookie;
    const userIdCookie = cookies
      .split("; ")
      .find((row) => row.startsWith("user_email="));

    setIsLoggedIn(!!userIdCookie);

    if (!userIdCookie) {
      alert("Please log in to access the chatbot.");
      navigate("/login");
    }
  }, [navigate]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { sender: "user", text: input }];
    setMessages(newMessages);
    setInput("");

    try {
      const response = await fetch("http://localhost:5000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
        credentials: "include",
      });

      const data = await response.json();
      setMessages((prev) => [...prev, { sender: "bot", text: data.response }]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "❌ Error connecting to the server." },
      ]);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") sendMessage();
  };

  const handleLogout = async () => {
    await fetch("http://localhost:5000/logout", { credentials: "include" });
    document.cookie = "user_id=; Max-Age=0; path=/;"; // Remove cookie manually
    setIsLoggedIn(false);
    navigate("/login");
  };

  return (
    <div>
      {/* 🔷 Navbar */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-primary px-3">
        <a className="navbar-brand" href="/">Asha AI</a>
        <div className="ms-auto d-flex gap-2">
          {isLoggedIn ? (
            <button className="btn btn-light btn-sm" onClick={handleLogout}>Logout</button>
          ) : (
            <>
              <button className="btn btn-light btn-sm" onClick={() => navigate("/login")}>Login</button>
              <button className="btn btn-light btn-sm" onClick={() => navigate("/login")}>Register</button>
            </>
          )}
        </div>
      </nav>

      {/* 🧠 Chat UI */}
      <div className="container mt-4">
        <div className="card h-100" style={{ height: "80vh" }}>
          <div className="card-header bg-primary text-white">
            Chatbot
          </div>

          <div className="card-body overflow-auto" style={{ height: "calc(80vh - 140px)" }}>
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`d-flex mb-2 ${
                  msg.sender === "user" ? "justify-content-end" : "justify-content-start"
                }`}
              >
                <div
                  className={`p-2 rounded shadow-sm ${
                    msg.sender === "user" ? "bg-primary text-white" : "bg-light text-dark"
                  }`}
                  style={{ maxWidth: "75%" }}
                >
                  {msg.text}
                </div>
              </div>
            ))}
          </div>

          <div className="card-footer d-flex gap-2">
            <input
              type="text"
              className="form-control"
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button className="btn btn-primary" onClick={sendMessage}>
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;
