import React from 'react';

export function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  color = 'cyan',
  className = '',
}) {
  const colorMap = {
    cyan: {
      border: 'border-slate-200 dark:border-slate-800 hover:border-sky-400',
      iconBg: 'bg-sky-50 dark:bg-sky-950/60 text-sky-600 dark:text-sky-400 border border-sky-200 dark:border-sky-800/60',
      accent: 'text-sky-600 dark:text-sky-400',
    },
    emerald: {
      border: 'border-slate-200 dark:border-slate-800 hover:border-emerald-400',
      iconBg: 'bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60',
      accent: 'text-emerald-600 dark:text-emerald-400',
    },
    amber: {
      border: 'border-slate-200 dark:border-slate-800 hover:border-amber-400',
      iconBg: 'bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-800/60',
      accent: 'text-amber-600 dark:text-amber-400',
    },
    rose: {
      border: 'border-slate-200 dark:border-slate-800 hover:border-rose-400',
      iconBg: 'bg-rose-50 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 border border-rose-200 dark:border-rose-800/60',
      accent: 'text-rose-600 dark:text-rose-400',
    },
    blue: {
      border: 'border-slate-200 dark:border-slate-800 hover:border-blue-400',
      iconBg: 'bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-800/60',
      accent: 'text-blue-600 dark:text-blue-400',
    },
  };

  const scheme = colorMap[color] || colorMap.cyan;

  return (
    <div
      className={`bg-white dark:bg-[#0d1524] rounded-2xl p-5 border ${scheme.border} transition-all duration-200 shadow-card hover:shadow-card-hover ${className}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 font-mono">
            {title}
          </p>
          <div className="mt-2.5 flex items-baseline gap-2">
            <span className="text-3xl font-extrabold font-mono tracking-tight text-slate-900 dark:text-white">
              {value ?? '—'}
            </span>
            {trend && (
              <span className="text-xs font-mono font-bold text-emerald-600 dark:text-emerald-400">
                {trend}
              </span>
            )}
          </div>
        </div>
        {Icon && (
          <div className={`p-3 rounded-xl ${scheme.iconBg}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>
      {subtitle && (
        <p className="mt-3.5 text-xs text-slate-500 dark:text-slate-400 border-t border-slate-100 dark:border-slate-800/80 pt-2.5 font-sans">
          {subtitle}
        </p>
      )}
    </div>
  );
}

export default StatCard;
