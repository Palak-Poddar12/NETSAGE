import React from 'react';

export function CiscoBridgeIcon({ className = 'w-6 h-6' }) {
  return (
    <svg
      viewBox="0 0 48 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <rect x="2" y="16" width="3.2" height="14" rx="1.6" fill="currentColor" />
      <rect x="7" y="11" width="3.2" height="19" rx="1.6" fill="currentColor" />
      <rect x="12" y="6" width="3.2" height="24" rx="1.6" fill="currentColor" />
      <rect x="17" y="11" width="3.2" height="19" rx="1.6" fill="currentColor" />
      <rect x="22.4" y="1" width="3.2" height="29" rx="1.6" fill="currentColor" />
      <rect x="27.8" y="11" width="3.2" height="19" rx="1.6" fill="currentColor" />
      <rect x="32.8" y="6" width="3.2" height="24" rx="1.6" fill="currentColor" />
      <rect x="37.8" y="11" width="3.2" height="19" rx="1.6" fill="currentColor" />
      <rect x="42.8" y="16" width="3.2" height="14" rx="1.6" fill="currentColor" />
    </svg>
  );
}

export function CiscoLogo({ className = '' }) {
  return (
    <div className={`flex items-center gap-3 select-none ${className}`}>
      <div className="w-10 h-10 rounded-xl bg-sky-500/10 dark:bg-sky-500/20 border border-sky-500/30 flex items-center justify-center text-sky-600 dark:text-sky-400 shadow-sm flex-shrink-0">
        <CiscoBridgeIcon className="w-6 h-5" />
      </div>
      <div>
        <div className="flex items-center gap-1.5 leading-none">
          <span className="font-bold tracking-wider text-base text-slate-900 dark:text-white font-mono">
            NETSAGE
          </span>
          <span className="text-[10px] px-2 py-0.5 rounded-full font-mono font-bold bg-sky-500/10 text-sky-600 dark:bg-sky-500/20 dark:text-sky-400 border border-sky-500/20">
            NetAcad
          </span>
        </div>
        <p className="text-[10px] text-slate-500 dark:text-slate-400 font-mono tracking-tight mt-1 flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
          <span>CISCO NETWORKING ACADEMY</span>
        </p>
      </div>
    </div>
  );
}

export default CiscoLogo;
