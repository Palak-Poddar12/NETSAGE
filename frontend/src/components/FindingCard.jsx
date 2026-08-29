import React from 'react';
import { SeverityBadge } from './SeverityBadge';
import { CheckCircle2, AlertTriangle, XCircle, FileCode } from 'lucide-react';

export function FindingCard({ finding }) {
  const getStatusIcon = () => {
    if (finding.status === 'PASSED') {
      return <CheckCircle2 className="w-5 h-5 text-emerald-500 flex-shrink-0" />;
    }
    if (finding.severity === 'CRITICAL' || finding.severity === 'HIGH') {
      return <XCircle className="w-5 h-5 text-rose-500 flex-shrink-0" />;
    }
    return <AlertTriangle className="w-5 h-5 text-amber-500 flex-shrink-0" />;
  };

  return (
    <div className="bg-slate-50 dark:bg-slate-900/60 rounded-2xl border border-slate-200 dark:border-slate-800 p-4 hover:border-sky-400 transition-colors shadow-subtle">
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-3">
          {getStatusIcon()}
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <span className="font-mono text-xs font-bold text-sky-700 dark:text-sky-400 px-2 py-0.5 rounded-full bg-sky-50 dark:bg-sky-950 border border-sky-200 dark:border-sky-800">
                {finding.rule_id}
              </span>
              <span className="text-xs font-semibold text-slate-900 dark:text-slate-200 font-sans">
                {finding.name || finding.category}
              </span>
            </div>
            <p className="mt-1.5 text-xs text-slate-600 dark:text-slate-300 leading-relaxed font-sans">
              {finding.message}
            </p>
          </div>
        </div>

        <SeverityBadge severity={finding.severity} />
      </div>

      {finding.evidence && (
        <div className="mt-3 pt-3 border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 rounded-xl p-3 shadow-inner">
          <div className="flex items-center gap-1.5 text-[11px] font-mono text-slate-500 dark:text-slate-400 mb-1">
            <FileCode className="w-3.5 h-3.5 text-sky-600 dark:text-sky-400" />
            <span>Deterministic Rule Evidence:</span>
          </div>
          <p className="text-xs font-mono text-slate-800 dark:text-sky-200 leading-relaxed">
            {finding.evidence}
          </p>
        </div>
      )}
    </div>
  );
}

export default FindingCard;
