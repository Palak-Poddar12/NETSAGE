import React from 'react';
import { getSeverityStyle } from '../utils/formatters';

export function SeverityBadge({ severity, className = '' }) {
  const style = getSeverityStyle(severity);
  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold tracking-wide border ${style.badge} ${className}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${style.dot}`} />
      {String(severity || 'LOW').toUpperCase()}
    </span>
  );
}

export default SeverityBadge;
