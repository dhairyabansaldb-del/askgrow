"use client";

import React from 'react';
import { AlertCircle } from 'lucide-react';

export default function ComplianceBanner() {
  return (
    <div className="max-w-4xl mx-auto w-full bg-[#3D1414] border-2 border-[#FF4D4D] rounded-2xl p-4 flex gap-4 shadow-lg">
      <div className="text-[#FF4D4D] shrink-0 pt-0.5">
        <AlertCircle size={24} />
      </div>
      <div>
        <h3 className="font-bold text-[#FF4D4D] text-sm uppercase tracking-wider mb-1">Not Financial Advice</h3>
        <p className="text-sm text-[#FFB3B3] leading-relaxed">
          This AI assistant provides factual information only. It cannot provide investment recommendations or financial advice. Please consult a SEBI-registered financial advisor before making any investment decisions.
        </p>
      </div>
    </div>
  );
}
