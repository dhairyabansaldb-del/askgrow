"use client";

import React, { useRef, useEffect } from 'react';
import { BarChart3, ShieldCheck, AlertCircle } from 'lucide-react';
import Message from './Message';
import ComplianceBanner from './ComplianceBanner';
import InputArea from './InputArea';

interface ChatPanelProps {
  messages: any[];
  isLoading: boolean;
  onSendMessage: (text: string) => void;
}

export default function ChatPanel({ messages, isLoading, onSendMessage }: ChatPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);

  return (
    <main className="flex-1 flex flex-col h-screen bg-groww-black overflow-hidden relative">
      {/* Persistent Header */}
      <header className="h-16 border-b border-groww-border flex items-center justify-between px-6 bg-groww-black/80 backdrop-blur-md z-10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded overflow-hidden">
            <img src="/logo.png" alt="Logo" className="w-full h-full object-cover" />
          </div>
          <div>
            <h1 className="font-semibold text-groww-text">Groww AI Companion</h1>
            <div className="flex items-center gap-1.5">
              <div className="w-2 h-2 bg-groww-green rounded-full shadow-[0_0_8px_rgba(0,208,156,0.5)]"></div>
              <span className="text-[10px] text-groww-muted font-medium uppercase tracking-tighter">Online & Factual</span>
            </div>
          </div>
        </div>
      </header>

      {/* Compliance Banner & Messages */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-6 py-4 space-y-6 scroll-smooth"
      >
        <ComplianceBanner />

        {messages.length === 0 && !isLoading && (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto space-y-4 pt-20">
            <div className="w-20 h-20 bg-groww-card rounded-2xl flex items-center justify-center overflow-hidden mb-2">
              <img src="/logo.png" alt="Groww Logo" className="w-full h-full object-cover scale-110" />
            </div>
            <h2 className="text-2xl font-bold text-groww-text">How can I help you today?</h2>
            <p className="text-groww-muted">
              I can provide factual information about HDFC Mutual Fund schemes, exit loads, expense ratios, and fund management.
            </p>
          </div>
        )}

        <div className="space-y-8 max-w-4xl mx-auto w-full pb-32">
          {messages.map((msg, idx) => (
            <Message key={idx} {...msg} />
          ))}
          {isLoading && (
            <div className="flex gap-4 animate-pulse">
              <div className="w-8 h-8 rounded-lg bg-groww-card shrink-0" />
              <div className="space-y-2 flex-1">
                <div className="h-4 bg-groww-card rounded w-1/4" />
                <div className="h-4 bg-groww-card rounded w-3/4" />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Input Section */}
      <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-groww-black via-groww-black to-transparent">
        <div className="max-w-4xl mx-auto w-full">
          <InputArea onSendMessage={onSendMessage} disabled={isLoading} />
          <div className="flex items-center justify-center gap-2 mt-3 text-groww-muted text-[10px] font-medium uppercase tracking-wider">
            <ShieldCheck size={12} />
            Secured with local PII Filtering (PAN/Aadhaar detection active)
          </div>
        </div>
      </div>
    </main>
  );
}
