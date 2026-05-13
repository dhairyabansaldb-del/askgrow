"use client";

import React from 'react';
import { Plus, MessageSquare, Settings, User, LayoutGrid } from 'lucide-react';
import { cn } from '@/lib/utils';

interface SidebarProps {
  history: any[];
  currentChatId: string | null;
  onNewChat: () => void;
  onSelectChat: (id: string) => void;
}

export default function Sidebar({ history, currentChatId, onNewChat, onSelectChat }: SidebarProps) {
  return (
    <aside className="w-64 h-screen bg-groww-card border-r border-groww-border flex flex-col">
      {/* Sidebar Header */}
      <div className="p-4">
        <div className="flex items-center gap-2 mb-6 px-2">
          <div className="w-8 h-8 rounded-lg overflow-hidden flex items-center justify-center">
            <img src="/logo.png" alt="Groww Logo" className="w-full h-full object-cover" />
          </div>
          <span className="font-semibold text-lg">Groww AI</span>
        </div>
        
        <button 
          onClick={onNewChat}
          className="w-full py-3 px-4 bg-groww-green hover:bg-opacity-90 transition-all text-groww-black font-semibold rounded-full flex items-center justify-center gap-2 mb-4"
        >
          <Plus size={20} />
          New Chat
        </button>
      </div>

      {/* Chat History */}
      <div className="flex-1 overflow-y-auto px-3 space-y-1">
        <div className="text-xs font-semibold text-groww-muted px-3 py-2 uppercase tracking-wider">
          Recent Chats
        </div>
        {history.length === 0 ? (
          <div className="text-sm text-groww-muted px-3 py-4 italic">
            No history yet
          </div>
        ) : (
          history.map((chat) => (
            <button
              key={chat.id}
              onClick={() => onSelectChat(chat.id)}
              className={cn(
                "w-full text-left px-3 py-3 rounded-xl flex items-center gap-3 transition-colors group",
                currentChatId === chat.id 
                  ? "bg-groww-border text-groww-green" 
                  : "hover:bg-groww-border/50 text-groww-muted hover:text-groww-text"
              )}
            >
              <MessageSquare size={18} className={currentChatId === chat.id ? "text-groww-green" : "text-groww-muted group-hover:text-groww-text"} />
              <span className="truncate text-sm font-medium">{chat.title}</span>
            </button>
          ))
        )}
      </div>

      {/* Sidebar Footer */}
      <div className="p-4 border-t border-groww-border space-y-1">
        <button className="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-groww-border/50 text-groww-muted hover:text-groww-text transition-colors">
          <Settings size={20} />
          <span className="text-sm font-medium">Settings</span>
        </button>
        <button className="w-full flex items-center gap-3 px-3 py-3 rounded-xl hover:bg-groww-border/50 text-groww-muted hover:text-groww-text transition-colors">
          <div className="w-6 h-6 bg-groww-border rounded-full flex items-center justify-center">
            <User size={14} />
          </div>
          <span className="text-sm font-medium">My Account</span>
        </button>
      </div>
    </aside>
  );
}
