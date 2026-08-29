export function formatDate(dateString) {
  if (!dateString) return 'N/A';
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      hour12: false,
    }).format(date);
  } catch {
    return dateString;
  }
}

export function formatConfidence(confidence) {
  if (confidence === undefined || confidence === null) return '0%';
  const num = typeof confidence === 'number' ? confidence : parseFloat(confidence);
  if (isNaN(num)) return '0%';
  // If it's a decimal (e.g. 0.85) convert to percentage
  const percentage = num <= 1 ? Math.round(num * 100) : Math.round(num);
  return `${percentage}%`;
}

export function getConfidenceLevel(confidence) {
  const num = typeof confidence === 'number' ? confidence : parseFloat(confidence);
  const percentage = num <= 1 ? Math.round(num * 100) : Math.round(num);
  if (percentage >= 80) return { label: 'High Confidence', color: 'text-emerald-400', bar: 'bg-emerald-500' };
  if (percentage >= 50) return { label: 'Moderate Confidence', color: 'text-amber-400', bar: 'bg-amber-500' };
  return { label: 'Low Confidence — Additional Evidence Recommended', color: 'text-rose-400', bar: 'bg-rose-500' };
}

export function getSeverityStyle(severity) {
  const sev = String(severity || '').toUpperCase();
  switch (sev) {
    case 'CRITICAL':
      return {
        badge: 'bg-rose-950/80 text-rose-300 border-rose-700/60 shadow-sm shadow-rose-950',
        dot: 'bg-rose-400',
        border: 'border-rose-800/60',
        text: 'text-rose-400',
      };
    case 'HIGH':
      return {
        badge: 'bg-orange-950/80 text-orange-300 border-orange-700/60 shadow-sm shadow-orange-950',
        dot: 'bg-orange-400',
        border: 'border-orange-800/60',
        text: 'text-orange-400',
      };
    case 'MEDIUM':
      return {
        badge: 'bg-amber-950/80 text-amber-300 border-amber-700/60 shadow-sm shadow-amber-950',
        dot: 'bg-amber-400',
        border: 'border-amber-800/60',
        text: 'text-amber-400',
      };
    case 'LOW':
    default:
      return {
        badge: 'bg-sky-950/80 text-sky-300 border-sky-700/60 shadow-sm shadow-sky-950',
        dot: 'bg-sky-400',
        border: 'border-sky-800/60',
        text: 'text-sky-400',
      };
  }
}

export function getDiagnosisStatusStyle(status) {
  const st = String(status || '').toUpperCase();
  switch (st) {
    case 'DIAGNOSIS_SUPPORTED':
      return {
        label: 'Supported by Evidence',
        badge: 'bg-emerald-950/70 text-emerald-300 border-emerald-700/50',
        iconColor: 'text-emerald-400',
      };
    case 'PARTIALLY_SUPPORTED':
      return {
        label: 'Partially Supported',
        badge: 'bg-amber-950/70 text-amber-300 border-amber-700/50',
        iconColor: 'text-amber-400',
      };
    case 'INSUFFICIENT_EVIDENCE':
      return {
        label: 'Insufficient Evidence',
        badge: 'bg-yellow-950/70 text-yellow-300 border-yellow-700/50',
        iconColor: 'text-yellow-400',
      };
    case 'CONFLICTING_EVIDENCE':
      return {
        label: 'Conflicting Evidence',
        badge: 'bg-rose-950/70 text-rose-300 border-rose-700/50',
        iconColor: 'text-rose-400',
      };
    default:
      return {
        label: status || 'Pending',
        badge: 'bg-slate-800 text-slate-300 border-slate-700',
        iconColor: 'text-slate-400',
      };
  }
}
