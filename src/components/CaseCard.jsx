import React from 'react';
import { Link } from 'react-router-dom';
import { SeverityBadge } from './SeverityBadge';
import { formatDate } from '../utils/formatters';
import { ArrowRight, Layers, Tag, Clock } from 'lucide-react';

export function CaseCard({ caseItem }) {
  const diagnosisId = caseItem.diagnosis_id || `DIAG-${caseItem.case_id}`;

  return (
    <div className="bg-white dark:bg-[#0d1524] rounded-2xl border border-slate-200 dark:border-slate-800 p-5 hover:border-sky-400 transition-all duration-200 flex flex-col justify-between shadow-card hover:shadow-card-hover group">
      <div>
        {/* Header: Case ID + Severity */}
        <div className="flex items-center justify-between gap-2 mb-3">
          <span className="font-mono text-xs font-bold text-sky-700 dark:text-sky-300 px-2.5 py-1 rounded-full bg-sky-50 dark:bg-sky-950/80 border border-sky-200 dark:border-sky-800/60">
            {caseItem.case_id}
          </span>
          <SeverityBadge severity={caseItem.severity} />
        </div>

        {/* Symptom */}
        <h4 className="text-sm font-bold text-slate-900 dark:text-white group-hover:text-sky-600 dark:group-hover:text-sky-400 transition-colors line-clamp-2">
          {caseItem.symptom}
        </h4>

        {/* Metadata Chips */}
        <div className="mt-4 space-y-2 text-xs text-slate-500 dark:text-slate-400">
          <div className="flex items-center gap-2">
            <Tag className="w-3.5 h-3.5" />
            <span className="text-slate-700 dark:text-slate-300 font-medium">{caseItem.category}</span>
          </div>

          <div className="flex items-center gap-2">
            <Layers className="w-3.5 h-3.5" />
            <span>{caseItem.osi_layer || 'Layer 3 (Network)'}</span>
          </div>

          <div className="flex items-center gap-2 text-[11px]">
            <Clock className="w-3.5 h-3.5" />
            <span>{formatDate(caseItem.created_at)}</span>
          </div>
        </div>
      </div>

      {/* Footer / Actions */}
      <div className="mt-5 pt-3 border-t border-slate-100 dark:border-slate-800/80 flex items-center justify-between">
        <span
          className={`text-[11px] font-mono px-2.5 py-0.5 rounded-full border ${
            caseItem.status === 'REVIEWED'
              ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800/40'
              : 'bg-amber-50 text-amber-700 dark:bg-amber-950/60 dark:text-amber-300 border-amber-200 dark:border-amber-800/40'
          }`}
        >
          {caseItem.status || 'PENDING'}
        </span>

        <Link
          to={`/diagnosis/${diagnosisId}`}
          className="inline-flex items-center gap-1 text-xs font-bold text-sky-600 dark:text-sky-400 hover:text-sky-500 transition-colors"
        >
          <span>Diagnose</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}

export default CaseCard;
