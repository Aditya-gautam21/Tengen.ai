'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Send, Bot, User, Loader2, Sparkles, Copy, RotateCcw, ThumbsUp, ThumbsDown, Upload, Download, Square } from 'lucide-react';
import { tengenAPI } from '@/lib/api';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  type?: 'text' | 'code' | 'research';
}

interface ChatInterfaceProps {
  chatId?: string | null;
  onChatCreated?: (chatId: string, title: string) => void;
}

export function ChatInterface({ chatId, onChatCreated }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [abortController, setAbortController] = useState<AbortController | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    checkConnection();
    
    const handleQuickAction = (event: CustomEvent) => {
      const { prompt } = event.detail;
      setInput(prompt);
      setTimeout(() => handleSend(prompt), 100);
    };

    window.addEventListener('quickAction', handleQuickAction as EventListener);
    
    return () => {
      window.removeEventListener('quickAction', handleQuickAction as EventListener);
    };
  }, []);

  useEffect(() => {
    if (chatId) {
      loadChatHistory(chatId);
    }
  }, [chatId]);

  const loadChatHistory = (chatId: string) => {
    const chatHistory = JSON.parse(localStorage.getItem('tengen-chat-history') || '[]');
    const chat = chatHistory.find((c: any) => c.id === chatId);
    if (chat && chat.messages) {
      setMessages(chat.messages.map((msg: any) => ({
        ...msg,
        timestamp: new Date(msg.timestamp)
      })));
      setCurrentChatId(chatId);
    }
  };

  const checkConnection = async () => {
    try {
      const health = await tengenAPI.healthCheck();
      setConnectionStatus('connected');
    } catch (error) {
      setConnectionStatus('disconnected');
    }
  };

  const stopGeneration = () => {
    if (abortController) {
      abortController.abort();
      setAbortController(null);
      setIsLoading(false);
    }
  };

  const handleSend = async (customPrompt?: string) => {
    const prompt = customPrompt || input;
    if (!prompt.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: prompt,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    const controller = new AbortController();
    setAbortController(controller);

    try {
      let messageType: 'text' | 'code' | 'research' = 'text';
      if (prompt.toLowerCase().includes('code') || prompt.toLowerCase().includes('function') || prompt.toLowerCase().includes('debug')) {
        messageType = 'code';
      } else if (prompt.toLowerCase().includes('research') || prompt.toLowerCase().includes('explain') || prompt.toLowerCase().includes('what is')) {
        messageType = 'research';
      }

      let stream: ReadableStream<Uint8Array> | null = null;

      if (messageType === 'code') {
        stream = await tengenAPI.codeAssist([{ role: 'user', content: prompt }]);
      } else {
        stream = await tengenAPI.chat([{ role: 'user', content: prompt }]);
      }

      if (stream) {
        const reader = stream.getReader();
        const decoder = new TextDecoder();
        let assistantContent = '';

        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: '',
          timestamp: new Date(),
          type: messageType,
        };

        setMessages(prev => [...prev, assistantMessage]);

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            assistantContent += chunk;

            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id 
                ? { ...msg, content: assistantContent }
                : msg
            ));
          }
        } catch (error: any) {
          if (error.name === 'AbortError') {
            assistantContent += '\n\n[Generation stopped by user]';
            setMessages(prev => prev.map(msg => 
              msg.id === assistantMessage.id 
                ? { ...msg, content: assistantContent }
                : msg
            ));
          }
        }

        // Save to chat history only after first exchange
        if (!currentChatId) {
          const newChatId = Date.now().toString();
          setCurrentChatId(newChatId);
          saveChatToHistory(newChatId, userMessage, { ...assistantMessage, content: assistantContent });
          onChatCreated?.(newChatId, userMessage.content.slice(0, 50));
        } else {
          updateChatHistory(currentChatId, userMessage, { ...assistantMessage, content: assistantContent });
        }
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please check if the backend is running on http://localhost:8000`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      setConnectionStatus('disconnected');
    } finally {
      setIsLoading(false);
      setAbortController(null);
    }
  };

  const saveChatToHistory = (chatId: string, userMsg: Message, assistantMsg: Message) => {
    const chatHistory = JSON.parse(localStorage.getItem('tengen-chat-history') || '[]');
    const newSession = {
      id: chatId,
      title: userMsg.content.slice(0, 50) + (userMsg.content.length > 50 ? '...' : ''),
      lastMessage: assistantMsg.content.slice(0, 100) + (assistantMsg.content.length > 100 ? '...' : ''),
      timestamp: new Date().toISOString(),
      messages: [userMsg, assistantMsg]
    };
    
    chatHistory.unshift(newSession);
    if (chatHistory.length > 50) chatHistory.pop();
    
    localStorage.setItem('tengen-chat-history', JSON.stringify(chatHistory));
    
    window.dispatchEvent(new CustomEvent('chatHistoryUpdated'));
  };

  const updateChatHistory = (chatId: string, userMsg: Message, assistantMsg: Message) => {
    const chatHistory = JSON.parse(localStorage.getItem('tengen-chat-history') || '[]');
    const chatIndex = chatHistory.findIndex((chat: any) => chat.id === chatId);
    
    if (chatIndex !== -1) {
      chatHistory[chatIndex].messages.push(userMsg, assistantMsg);
      chatHistory[chatIndex].lastMessage = assistantMsg.content.slice(0, 100) + (assistantMsg.content.length > 100 ? '...' : '');
      localStorage.setItem('tengen-chat-history', JSON.stringify(chatHistory));
      window.dispatchEvent(new CustomEvent('chatHistoryUpdated'));
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const regenerateResponse = (messageId: string) => {
    const messageIndex = messages.findIndex(m => m.id === messageId);
    if (messageIndex > 0) {
      const userMessage = messages[messageIndex - 1];
      if (userMessage.role === 'user') {
        setMessages(prev => prev.filter(m => m.id !== messageId));
        setTimeout(() => handleSend(userMessage.content), 100);
      }
    }
  };

  const clearChat = () => {
    if (confirm('Are you sure you want to clear this chat?')) {
      setMessages([]);
      setCurrentChatId(null);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setIsLoading(true);
      const result = await tengenAPI.uploadFile(file);
      
      const uploadMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `File "${file.name}" uploaded successfully! ${result.message || 'You can now ask questions about this document.'}`,
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, uploadMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: `Failed to upload file: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const exportChat = () => {
    const chatData = {
      timestamp: new Date().toISOString(),
      messages: messages
    };
    
    const blob = new Blob([JSON.stringify(chatData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tengen-chat-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="flex flex-col h-screen bg-black text-white">


      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-lime-400 to-green-500 flex items-center justify-center mx-auto mb-4">
                <Sparkles className="h-8 w-8 text-black" />
              </div>
              <h2 className="text-xl font-medium text-white mb-2">How may I help you today?</h2>
              <p className="text-gray-400 mb-4">Ask me anything and I'll research it for you!</p>
              {connectionStatus === 'disconnected' && (
                <div className="bg-red-900/20 border border-red-800 rounded-lg p-3 max-w-md mx-auto">
                  <p className="text-red-400 text-sm">
                    ⚠️ Backend not connected. Please ensure the backend server is running on http://localhost:8000
                  </p>
                  <Button
                    onClick={checkConnection}
                    variant="outline"
                    size="sm"
                    className="mt-2 text-red-400 border-red-800 hover:bg-red-900/30"
                  >
                    Retry Connection
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-4 ${
              message.role === 'user' ? 'justify-end' : 'justify-start'
            }`}
          >
            {message.role === 'assistant' && (
              <div className="flex-shrink-0 mt-1">
                <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-lime-400 to-green-500 flex items-center justify-center">
                  <Bot className="h-4 w-4 text-black" />
                </div>
              </div>
            )}
            
            <div className="flex flex-col max-w-[75%]">
              <div
                className={`rounded-3xl px-6 py-4 ${
                  message.role === 'user'
                    ? 'bg-gradient-to-br from-lime-400 to-green-500 text-black font-medium'
                    : `bg-gray-900 border border-gray-800 text-white ${
                        message.type === 'code' ? 'font-mono text-sm' : ''
                      }`
                }`}
              >
                <div className="whitespace-pre-wrap leading-relaxed">{message.content}</div>
              </div>
              
              {message.role === 'assistant' && (
                <div className="flex gap-2 mt-2 ml-2">
                  <Button
                    onClick={() => copyToClipboard(message.content)}
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0 text-gray-400 hover:text-white"
                    title="Copy message"
                  >
                    <Copy className="h-3 w-3" />
                  </Button>
                  <Button
                    onClick={() => regenerateResponse(message.id)}
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0 text-gray-400 hover:text-white"
                    title="Regenerate response"
                    disabled={isLoading}
                  >
                    <RotateCcw className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0 text-gray-400 hover:text-green-400"
                    title="Good response"
                  >
                    <ThumbsUp className="h-3 w-3" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-8 w-8 p-0 text-gray-400 hover:text-red-400"
                    title="Bad response"
                  >
                    <ThumbsDown className="h-3 w-3" />
                  </Button>
                </div>
              )}
            </div>

            {message.role === 'user' && (
              <div className="flex-shrink-0 mt-1">
                <div className="w-8 h-8 rounded-xl bg-gray-800 border border-gray-700 flex items-center justify-center">
                  <User className="h-4 w-4 text-white" />
                </div>
              </div>
            )}
          </div>
        ))}
        
        {isLoading && (
          <div className="flex gap-4 justify-start">
            <div className="flex-shrink-0 mt-1">
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-lime-400 to-green-500 flex items-center justify-center">
                <Bot className="h-4 w-4 text-black" />
              </div>
            </div>
            <div className="bg-gray-900 border border-gray-800 rounded-3xl px-6 py-4">
              <div className="flex items-center gap-3 text-gray-300">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-lime-400 rounded-full animate-bounce" />
                  <div className="w-2 h-2 bg-lime-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-lime-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
                <span className="text-sm">Thinking...</span>
                <Button
                  onClick={stopGeneration}
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 text-red-400 hover:text-red-300 ml-2"
                  title="Stop generation"
                >
                  <Square className="h-3 w-3" />
                </Button>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-6 border-t border-gray-800">
        <div className="flex gap-3 items-end">
          <div className="flex-1">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask me anything..."
              className="w-full bg-gray-900 border-gray-800 rounded-2xl px-6 py-4 text-white placeholder-gray-400 focus:border-lime-400 focus:ring-lime-400"
              disabled={isLoading}
            />
          </div>
          <Button
            onClick={() => handleSend()}
            disabled={!input.trim() || isLoading}
            className="w-12 h-12 rounded-2xl bg-gradient-to-br from-lime-400 to-green-500 hover:from-lime-300 hover:to-green-400 text-black"
          >
            {isLoading ? (
              <Loader2 className="h-5 w-5 animate-spin" />
            ) : (
              <Sparkles className="h-5 w-5" />
            )}
          </Button>
        </div>
      </div>
    </div>
  );
}