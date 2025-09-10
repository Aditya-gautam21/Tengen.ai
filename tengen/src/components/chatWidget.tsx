import React, { useEffect, useState, useRef } from "react";
import {
  Paper,
  List,
  ListItem,
  ListItemText,
  TextField,
  IconButton,
  Avatar,
  Typography,
  Divider,
} from "@material-ui/core";
import SendIcon from "@material-ui/icons/Send";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export default function ChatWidget() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: "Hi! How can I help you today?" },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);

  // auto scroll
  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = { role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage.content }),
      });

      if (!res.ok) {
        throw new Error("Failed to fetch response");
      }

      const data = await res.json();
      const botMessage: ChatMessage = {
        role: "assistant",
        content: data.reply || "⚠️ No reply from server",
      };
      setMessages((prev) => [...prev, botMessage]);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "❌ Error reaching backend." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper
      style={{
        width: "100%",
        maxWidth: 600,
        height: "80vh",
        margin: "auto",
        display: "flex",
        flexDirection: "column",
      }}
      elevation={3}
    >
      {/* Header */}
      <Typography variant="h6" style={{ padding: 12, textAlign: "center" }}>
        Tengen.ai Chat
      </Typography>
      <Divider />

      {/* Messages */}
      <div
        ref={listRef}
        style={{ flex: 1, overflowY: "auto", padding: "8px 12px" }}
      >
        <List>
          {messages.map((m, i) => (
            <ListItem
              key={i}
              style={{
                justifyContent:
                  m.role === "user" ? "flex-end" : "flex-start",
              }}
            >
              {m.role === "assistant" && (
                <Avatar style={{ marginRight: 8 }}>AI</Avatar>
              )}
              <Paper
                style={{
                  padding: "8px 12px",
                  maxWidth: "70%",
                  backgroundColor:
                    m.role === "user" ? "#1976d2" : "#f5f5f5",
                  color: m.role === "user" ? "#fff" : "#000",
                }}
              >
                <ListItemText primary={m.content} />
              </Paper>
              {m.role === "user" && (
                <Avatar style={{ marginLeft: 8, background: "#1976d2" }}>
                  U
                </Avatar>
              )}
            </ListItem>
          ))}
        </List>
      </div>

      {/* Input */}
      <Divider />
      <div style={{ padding: 8, display: "flex" }}>
        <TextField
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message..."
          fullWidth
          disabled={loading}
          onKeyDown={(e) => {
            if (e.key === "Enter") sendMessage();
          }}
        />
        <IconButton onClick={sendMessage} disabled={loading}>
          <SendIcon />
        </IconButton>
      </div>
    </Paper>
  );
}
