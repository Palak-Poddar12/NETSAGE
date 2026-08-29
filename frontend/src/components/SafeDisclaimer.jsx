import React from 'react';
import { ShieldCheck } from 'lucide-react';

export function SafeDisclaimer({ className = '' }) {
  return (
    <div
      className={`flex items-center gap-3 px-4 py-2.5 rounded-xl bg-sky-50 dark:bg-[#0d1524] border border-sky-200 dark:border-slate-800 text-xs text-slate-600 dark:text-slate-400 shadow-subtle ${className}`}
    >
      <ShieldCheck className="w-4 h-4 text-sky-600 dark:text-sky-400 flex-shrink-0" />
      <p className="leading-snug">
        <strong className="text-slate-900 dark:text-slate-200 font-semibold">NetSage AI Advisory:</strong> NetSage AI provides evidence-based troubleshooting recommendations.
        <span className="text-slate-900 dark:text-slate-200 font-semibold ml-1">No network configuration changes are executed automatically.</span>
      </p>
    </div>
  );
}

export default SafeDisclaimer;
