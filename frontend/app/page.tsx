'use client';

import { useState, useCallback } from 'react';
import { ChatSidebar } from '@/components/chat-sidebar';
import { ChatInterface } from '@/components/chat-interface';

export default function Page() {
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleNewChat = useCallback(() => {
    setCurrentChatId(null);
    setRefreshKey(prev => prev + 1);
  }, []);

  const handleSelectChat = useCallback((chatId: string) => {
    setCurrentChatId(chatId);
  }, []);

  const handleChatCreated = useCallback((chatId: string, title: string) => {
    setCurrentChatId(chatId);
  }, []);

  return (
    <div className="flex h-screen bg-black">
      <ChatSidebar 
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
      />
      <div className="flex-1">
        <ChatInterface 
          key={refreshKey}
          chatId={currentChatId}
          onChatCreated={handleChatCreated}
        />
      </div>
    </div>
  );
}