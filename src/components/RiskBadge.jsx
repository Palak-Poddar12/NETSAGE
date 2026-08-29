import React from 'react';
import { formatConfidence, getConfidenceLevel } from '../utils/formatters';
import { ShieldCheck, ShieldAlert, Shield } from 'lucide-react';

export function RiskBadge({ confidence, showBar = false, className = '' }) {
  const confLevel = getConfidenceLevel(confidence);
  const formatted = formatConfidence(confidence);
  const num = typeof confidence === 'number' ? (confidence <= 1 ? confidence * 100 : confidence) : parseFloat(confidence);

  return (
    <div className={`inline-flex flex-col gap-1.5 ${className}`}>
      <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-navy-900 border border-slate-700/60 shadow-inner">
        {num >= 80 ? (
          <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
        ) : num >= 50 ? (
          <Shield className="w-3.5 h-3.5 text-amber-400" />
        ) : (
          <ShieldAlert className="w-3.5 h-3.5 text-rose-400" />
        )}
        <span className="text-slate-400 font-mono">Confidence:</span>
        <span className={`font-mono font-bold ${confLevel.color}`}>{formatted}</span>
      </div>

      {showBar && (
        <div className="w-full bg-navy-950 rounded-full h-1.5 border border-slate-800 overflow-hidden">
          <div
            className={`h-full transition-all duration-500 rounded-full ${confLevel.bar}`}
            style={{ width: `${Math.min(100, Math.max(0, num))}%` }}
          />
        </div>
      )}
    </div>
  );
}

export default RiskBadge;
