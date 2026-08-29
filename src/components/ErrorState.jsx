import React from 'react';
import { AlertTriangle, RefreshCw, ServerCrash, ShieldAlert } from 'lucide-react';

export function ErrorState({
  title = 'Service Error',
  message = 'Failed to load diagnostic information. Please ensure the backend service is reachable.',
  onRetry,
  className = '',
}) {
  return (
    <div
      className={`p-6 bg-rose-950/20 rounded-xl border border-rose-800/40 text-slate-200 ${className}`}
    >
      <div className="flex items-start gap-4">
        <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 flex-shrink-0">
          <AlertTriangle className="w-6 h-6" />
        </div>
        <div className="flex-1">
          <h4 className="text-sm font-semibold text-rose-300 font-sans tracking-wide">
            {title}
          </h4>
          <p className="mt-1 text-xs text-rose-200/70 leading-relaxed font-sans">
            {message}
          </p>

          {onRetry && (
            <div className="mt-4">
              <button
                onClick={onRetry}
                className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-lg bg-rose-900/40 hover:bg-rose-900/60 text-rose-200 border border-rose-700/50 text-xs font-semibold shadow-sm transition-all"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Retry Request
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ErrorState;
