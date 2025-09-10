import React, { useState } from "react";
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
} from "@mui/material";
import SendIcon from "@mui/icons-material/Send";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const ChatWidget: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessage: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, newMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:8000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      const data = await res.json();

      let reply = "";
      if (data.response) {
        reply += data.response;
      }
      if (data.data) {
        // If scraping returns structured data
        reply += "\n\n" + JSON.stringify(data.data, null, 2);
      }

      const assistantMessage: Message = { role: "assistant", content: reply };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        role: "assistant",
        content: "⚠️ Error fetching response from server.",
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        position: "fixed",
        bottom: 20,
        right: 20,
        width: 350,
        height: 500,
        display: "flex",
        flexDirection: "column",
        borderRadius: 2,
        overflow: "hidden",
      }}
    >
      <Box sx={{ p: 2, bgcolor: "primary.main", color: "white" }}>
        <Typography variant="h6">💬 Tengen.ai Chatbot</Typography>
      </Box>

      <Box sx={{ flex: 1, overflowY: "auto", p: 2 }}>
        <List>
          {messages.map((msg, idx) => (
            <ListItem
              key={idx}
              sx={{
                display: "flex",
                justifyContent:
                  msg.role === "user" ? "flex-end" : "flex-start",
              }}
            >
              <ListItemText
                primary={msg.content}
                sx={{
                  bgcolor: msg.role === "user" ? "primary.light" : "grey.200",
                  color: msg.role === "user" ? "white" : "black",
                  px: 2,
                  py: 1,
                  borderRadius: 2,
                  maxWidth: "80%",
                  whiteSpace: "pre-wrap",
                }}
              />
            </ListItem>
          ))}
          {loading && (
            <ListItem>
              <CircularProgress size={20} />
            </ListItem>
          )}
        </List>
      </Box>

      <Box
        sx={{
          p: 1,
          display: "flex",
          borderTop: "1px solid #ccc",
          bgcolor: "background.paper",
        }}
      >
        <TextField
          fullWidth
          placeholder="Type your message..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyPress}
          size="small"
        />
        <IconButton color="primary" onClick={sendMessage}>
          <SendIcon />
        </IconButton>
      </Box>
    </Paper>
  );
};

export default ChatWidget;
