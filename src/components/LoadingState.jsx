import React from 'react';
import { Loader2, Activity, Cpu, Server } from 'lucide-react';

export function LoadingState({
  message = 'Loading diagnostic data...',
  type = 'skeleton', // 'skeleton' | 'spinner' | 'diagnosis'
  rows = 4,
  className = '',
}) {
  if (type === 'diagnosis') {
    return (
      <div
        className={`flex flex-col items-center justify-center p-12 bg-navy-900/60 rounded-xl border border-slate-800/80 text-center ${className}`}
      >
        <div className="relative mb-5">
          <div className="w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center animate-pulse">
            <Cpu className="w-8 h-8 text-cyan-400" />
          </div>
          <span className="absolute -top-1 -right-1 flex h-3 w-3">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-3 w-3 bg-cyan-500"></span>
          </span>
        </div>
        <h4 className="text-sm font-semibold text-slate-200 font-sans tracking-wide">
          {message}
        </h4>
        <p className="mt-1 text-xs text-slate-400 font-mono">
          Correlating Cisco show outputs with deterministic rule engine...
        </p>
      </div>
    );
  }

  if (type === 'spinner') {
    return (
      <div
        className={`flex flex-col items-center justify-center p-8 space-y-3 ${className}`}
      >
        <Loader2 className="w-7 h-7 text-cyan-400 animate-spin" />
        <span className="text-xs text-slate-400 font-mono tracking-wide">
          {message}
        </span>
      </div>
    );
  }

  // Skeleton Table/Card Loader
  return (
    <div className={`space-y-4 animate-pulse ${className}`}>
      <div className="h-8 bg-navy-800/80 rounded-lg w-1/3 border border-slate-800/50" />
      <div className="space-y-3">
        {Array.from({ length: rows }).map((_, idx) => (
          <div
            key={idx}
            className="h-16 bg-navy-900/70 rounded-xl border border-slate-800/60 flex items-center px-4 gap-4"
          >
            <div className="w-10 h-10 rounded-lg bg-navy-800/80" />
            <div className="flex-1 space-y-2">
              <div className="h-3 bg-navy-800/80 rounded w-1/4" />
              <div className="h-2.5 bg-navy-800/50 rounded w-3/4" />
            </div>
            <div className="w-20 h-6 bg-navy-800/80 rounded-full" />
          </div>
        ))}
      </div>
    </div>
  );
}

export default LoadingState;
