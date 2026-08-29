import React from 'react';
import { Inbox, FolderSearch, RefreshCw } from 'lucide-react';

export function EmptyState({
  title = 'No Data Found',
  description = 'There are no records matching your current filter criteria.',
  icon: Icon = FolderSearch,
  actionLabel,
  onAction,
  className = '',
}) {
  return (
    <div
      className={`flex flex-col items-center justify-center p-12 text-center bg-navy-900/50 rounded-xl border border-slate-800/80 ${className}`}
    >
      <div className="p-4 rounded-2xl bg-navy-800/80 border border-slate-700/60 text-slate-400 mb-4 shadow-inner">
        <Icon className="w-8 h-8 text-cyan-400/80" />
      </div>
      <h3 className="text-base font-semibold text-slate-200 font-sans">
        {title}
      </h3>
      <p className="mt-1.5 text-xs text-slate-400 max-w-sm">
        {description}
      </p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="mt-5 inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-navy-800 hover:bg-navy-700 text-cyan-300 border border-cyan-500/30 text-xs font-semibold shadow-sm transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          {actionLabel}
        </button>
      )}
    </div>
  );
}

export default EmptyState;
