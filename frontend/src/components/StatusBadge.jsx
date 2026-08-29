import React from 'react';
import { getDiagnosisStatusStyle } from '../utils/formatters';
import { CheckCircle2, AlertTriangle, XCircle, Clock } from 'lucide-react';

export function StatusBadge({ status, className = '' }) {
  const style = getDiagnosisStatusStyle(status);

  const getIcon = () => {
    switch (status) {
      case 'DIAGNOSIS_SUPPORTED':
        return <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />;
      case 'PARTIALLY_SUPPORTED':
        return <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />;
      case 'INSUFFICIENT_EVIDENCE':
        return <AlertTriangle className="w-3.5 h-3.5 text-yellow-400" />;
      case 'CONFLICTING_EVIDENCE':
        return <XCircle className="w-3.5 h-3.5 text-rose-400" />;
      default:
        return <Clock className="w-3.5 h-3.5 text-slate-400" />;
    }
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-mono font-medium border ${style.badge} ${className}`}
    >
      {getIcon()}
      <span>{style.label}</span>
    </span>
  );
}

export default StatusBadge;
