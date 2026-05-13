"use client";

import React from 'react';
import { cn } from '@/lib/utils';
import { LayoutGrid, User } from 'lucide-react';

interface MessageProps {
  role: 'user' | 'assistant';
  content: string;
  citations?: string[];
}

export default function Message({ role, content, citations }: MessageProps) {
  const isUser = role === 'user';

  return (
    <div className={cn(
      "flex gap-4 w-full",
      isUser ? "flex-row-reverse" : "flex-row"
    )}>
      {/* Avatar */}
      <div className={cn(
        "w-8 h-8 rounded-lg flex items-center justify-center shrink-0 shadow-sm overflow-hidden",
        isUser ? "bg-groww-border text-groww-text" : "bg-groww-green"
      )}>
        {isUser ? <User size={16} /> : <img src="/logo.png" alt="AI" className="w-full h-full object-cover" />}
      </div>

      {/* Content */}
      <div className={cn(
        "max-w-[80%] space-y-3",
        isUser ? "text-right" : "text-left"
      )}>
        <div className={cn(
          "text-xs font-bold uppercase tracking-widest mb-1",
          isUser ? "text-groww-muted" : "text-groww-green"
        )}>
          {isUser ? "You" : "Groww AI"}
        </div>
        
        <div className={cn(
          "px-5 py-4 rounded-2xl text-sm leading-relaxed",
          isUser 
            ? "bg-groww-card text-groww-text rounded-tr-none border border-groww-border" 
            : "bg-groww-card text-groww-text rounded-tl-none border-l-4 border-l-groww-green border-y border-r border-groww-border shadow-md"
        )}>
          <div className="whitespace-pre-wrap">{content}</div>
          
          {!isUser && citations && citations.length > 0 && (
            <div className="mt-4 pt-4 border-t border-groww-border/50">
              <div className="text-[10px] font-bold text-groww-muted uppercase tracking-widest mb-2">Sources</div>
              <div className="flex flex-wrap gap-2">
                {citations.map((url, i) => {
                  const domain = new URL(url).hostname.replace('www.', '');
                  return (
                    <a 
                      key={i} 
                      href={url} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-[10px] bg-groww-black/50 hover:bg-groww-green/10 hover:text-groww-green px-2 py-1 rounded border border-groww-border transition-colors truncate max-w-[200px]"
                    >
                      {domain}
                    </a>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
