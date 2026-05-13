"use client";

import { useState, useEffect } from 'react';
import Sidebar from '@/components/Sidebar';
import ChatPanel from '@/components/ChatPanel';
import { v4 as uuidv4 } from 'uuid';

// Use environment variable for production, fallback to local for dev
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function Home() {
  const [history, setHistory] = useState<any[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const [messages, setMessages] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Load history from localStorage on mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('groww_chat_history');
    if (savedHistory) {
      const parsed = JSON.parse(savedHistory);
      setHistory(parsed);
      if (parsed.length > 0) {
        // Load the most recent chat
        setCurrentChatId(parsed[0].id);
        setMessages(parsed[0].messages);
      }
    }
  }, []);

  // Save history to localStorage whenever it changes
  useEffect(() => {
    if (history.length > 0) {
      localStorage.setItem('groww_chat_history', JSON.stringify(history));
    }
  }, [history]);

  const handleNewChat = () => {
    setCurrentChatId(null);
    setMessages([]);
  };

  const handleSelectChat = (id: string) => {
    const chat = history.find(c => c.id === id);
    if (chat) {
      setCurrentChatId(id);
      setMessages(chat.messages);
    }
  };

  const handleSendMessage = async (text: string) => {
    // 1. Add user message locally
    const userMsg = { role: 'user', content: text };
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setIsLoading(true);

    // 2. Prepare API call
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text }),
      });

      if (!response.ok) throw new Error('API request failed');

      const data = await response.json();

      // 3. Add assistant message
      const assistantMsg = { 
        role: 'assistant', 
        content: data.response,
        citations: data.citations
      };
      
      const finalMessages = [...updatedMessages, assistantMsg];
      setMessages(finalMessages);

      // 4. Update or Create history item
      if (!currentChatId) {
        const newId = uuidv4();
        const newChat = {
          id: newId,
          title: text.substring(0, 30) + (text.length > 30 ? '...' : ''),
          messages: finalMessages,
          timestamp: Date.now()
        };
        setHistory([newChat, ...history]);
        setCurrentChatId(newId);
      } else {
        setHistory(prev => prev.map(chat => 
          chat.id === currentChatId 
            ? { ...chat, messages: finalMessages, timestamp: Date.now() } 
            : chat
        ).sort((a, b) => b.timestamp - a.timestamp));
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages([...updatedMessages, { 
        role: 'assistant', 
        content: "I'm sorry, I encountered an error connecting to the backend server. Please make sure the API is running." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-groww-black text-groww-text">
      <Sidebar 
        history={history} 
        currentChatId={currentChatId}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
      />
      <ChatPanel 
        messages={messages}
        isLoading={isLoading}
        onSendMessage={handleSendMessage}
      />
    </div>
  );
}
