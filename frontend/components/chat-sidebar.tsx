'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Plus, MessageSquare, Settings, Sparkles, User, Search, Code, FileText, Trash2 } from 'lucide-react';
import { tengenAPI } from '@/lib/api';

interface ChatSession {
  id: string;
  title: string;
  lastMessage: string;
  timestamp: Date;
}

interface ChatSidebarProps {
  onNewChat?: () => void;
  onSelectChat?: (chatId: string) => void;
  onQuickAction?: (action: string) => void;
}

export function ChatSidebar({ onNewChat, onSelectChat, onQuickAction }: ChatSidebarProps) {
  const [chatSessions, setChatSessions] = useState<ChatSession[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    checkConnection();
    loadChatHistory();
    
    // Listen for chat history updates
    const handleHistoryUpdate = () => {
      loadChatHistory();
    };
    
    window.addEventListener('chatHistoryUpdated', handleHistoryUpdate);
    
    return () => {
      window.removeEventListener('chatHistoryUpdated', handleHistoryUpdate);
    };
  }, []);

  const checkConnection = async () => {
    try {
      await tengenAPI.healthCheck();
      setIsConnected(true);
    } catch (error) {
      setIsConnected(false);
    }
  };

  const loadChatHistory = () => {
    const saved = localStorage.getItem('tengen-chat-history');
    if (saved) {
      const parsed = JSON.parse(saved);
      setChatSessions(parsed.map((session: any) => ({
        ...session,
        timestamp: new Date(session.timestamp)
      })));
    }
  };

  const handleNewChat = () => {
    onNewChat?.();
  };

  const handleQuickAction = (action: string, prompt: string) => {
    onQuickAction?.(prompt);
  };

  const handleSelectChat = (chatId: string) => {
    onSelectChat?.(chatId);
  };

  const clearAllChats = () => {
    if (confirm('Are you sure you want to clear all chat history?')) {
      localStorage.removeItem('tengen-chat-history');
      setChatSessions([]);
    }
  };

  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 60) return `${minutes}m`;
    if (hours < 24) return `${hours}h`;
    return `${days}d`;
  };

  return (
    <div className="w-80 bg-black border-r border-gray-800 flex flex-col h-screen">
      {/* Header */}
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-lime-400 to-green-500 flex items-center justify-center">
            <Sparkles className="h-4 w-4 text-black" />
          </div>
          <div>
            <h2 className="text-white font-medium">Tengen.ai 👋</h2>
            <p className="text-gray-400 text-sm">
              {isConnected ? 'Ready to explore!' : 'Connecting...'}
            </p>
          </div>
        </div>
        
        <Button 
          onClick={handleNewChat}
          className="w-full bg-gradient-to-r from-lime-400 to-green-500 hover:from-lime-300 hover:to-green-400 text-black font-medium rounded-2xl h-12"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Chat
        </Button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        {chatSessions.length === 0 ? (
          <div className="text-center py-8">
            <div className="w-12 h-12 bg-gray-800 rounded-xl flex items-center justify-center mx-auto mb-3">
              <MessageSquare className="h-6 w-6 text-gray-400" />
            </div>
            <p className="text-gray-400 text-sm">No chat history yet</p>
            <p className="text-gray-500 text-xs mt-1">Start a conversation to see your chats here</p>
          </div>
        ) : (
          <>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-gray-300 text-sm font-medium">History</h3>
              <button 
                onClick={clearAllChats}
                className="text-red-400 text-sm hover:text-red-300 transition-colors flex items-center gap-1"
              >
                <Trash2 className="h-3 w-3" />
                Clear
              </button>
            </div>
            
            <div className="space-y-3">
              {chatSessions.map((session) => (
                <button
                  key={session.id}
                  onClick={() => handleSelectChat(session.id)}
                  className="w-full text-left p-4 rounded-2xl bg-gray-900 border border-gray-800 hover:bg-gray-800 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-400 to-purple-500 rounded-xl flex items-center justify-center flex-shrink-0">
                      <MessageSquare className="h-4 w-4 text-white" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-white text-sm font-medium truncate mb-1">
                        {session.title}
                      </div>
                      <div className="text-gray-400 text-xs truncate">
                        {session.lastMessage}
                      </div>
                    </div>
                    <div className="text-gray-500 text-xs">
                      {formatTime(session.timestamp)}
                    </div>
                  </div>
                </button>
              ))}
            </div>
          </>
        )}
      </div>

      {/* Footer */}
      <div className="p-6 border-t border-gray-800">
        <div className="flex items-center gap-3 p-4 rounded-2xl bg-gray-900 border border-gray-800">
          <div className="w-10 h-10 bg-gradient-to-br from-gray-600 to-gray-700 rounded-xl flex items-center justify-center">
            <User className="h-5 w-5 text-white" />
          </div>
          <div className="flex-1">
            <p className="text-white text-sm font-medium">Guest User</p>
            <p className="text-gray-400 text-xs">
              {isConnected ? 'Connected' : 'Offline'}
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            className="text-gray-400 hover:text-white hover:bg-gray-800 rounded-xl"
            onClick={() => window.open('/docs', '_blank')}
          >
            <Settings className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </div>
  );
}