"use client";

import React, { useState } from 'react';
import { SendHorizonal } from 'lucide-react';
import { cn } from '@/lib/utils';

interface InputAreaProps {
  onSendMessage: (text: string) => void;
  disabled: boolean;
}

export default function InputArea({ onSendMessage, disabled }: InputAreaProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <form 
      onSubmit={handleSubmit}
      className="relative flex items-center"
    >
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={disabled}
        placeholder="Ask a question about GROW Mutual Funds..."
        className="w-full bg-groww-card border border-groww-border focus:border-groww-green outline-none text-groww-text px-6 py-5 rounded-2xl shadow-xl transition-all pr-16 disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className={cn(
          "absolute right-3 p-3 rounded-xl transition-all",
          input.trim() && !disabled 
            ? "bg-groww-green text-groww-black shadow-lg scale-100 hover:scale-105" 
            : "bg-groww-border text-groww-muted scale-95 opacity-50 cursor-not-allowed"
        )}
      >
        <SendHorizonal size={24} />
      </button>
    </form>
  );
}
