import React from 'react';
import { Link } from 'react-router-dom';
import {
  Activity,
  CheckCircle2,
  Edit3,
  XCircle,
  Percent,
  AlertTriangle,
  Layers,
  ArrowUpRight,
  ShieldAlert,
  Server,
  Zap,
  FolderGit2,
  Plus,
  Radio,
  BarChart3,
  Search,
  Brain,
  UserCheck,
  Target,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { StatCard } from '../components/StatCard';
import { FindingCard } from '../components/FindingCard';
import { SeverityBadge } from '../components/SeverityBadge';
import { SafeDisclaimer } from '../components/SafeDisclaimer';
import { useCaseContext } from '../context/CaseContext';
import { useTheme } from '../context/ThemeContext';

export function Dashboard() {
  const { metrics, cases } = useCaseContext();
  const { isDark } = useTheme();

  const {
    total_cases = cases.length || 30,
    accepted = 21,
    edited = 6,
    rejected = 3,
    agreement_rate = 82.5,
    target_kpi = 80.0,
    issue_distribution = [],
    severity_distribution = [],
    common_rule_findings = [],
    conflicting_cases = [],
  } = metrics || {};

  const SEVERITY_COLORS = {
    LOW: '#0284c7',
    MEDIUM: '#f59e0b',
    HIGH: '#f97316',
    CRITICAL: '#ef4444',
  };

  const isKpiMet = agreement_rate >= target_kpi;

  return (
    <div className="space-y-6 pb-12">
      {/* Top Advisory Banner */}
      <SafeDisclaimer />

      {/* Cisco NOC Command Header */}
      <div className="bg-white dark:bg-[#0d1524] rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-card flex flex-col md:flex-row md:items-center justify-between gap-4 transition-colors">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Radio className="w-4 h-4 text-sky-600 dark:text-sky-400 animate-pulse" />
            <span className="text-xs font-mono font-bold tracking-wider text-sky-600 dark:text-sky-400 uppercase">
              Cisco Catalyst NOC Telemetry
            </span>
          </div>
          <h2 className="text-xl sm:text-2xl font-bold text-slate-900 dark:text-white tracking-tight">
            Network Operations & Diagnosis Center
          </h2>
          <p className="text-xs text-slate-500 dark:text-slate-300 mt-1 max-w-xl font-sans">
            NetSage AI combines deterministic Cisco rule checks with context-aware AI root-cause analysis and structured human verification.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Target KPI Indicator */}
          <div className="px-4 py-2.5 rounded-xl bg-slate-50 dark:bg-slate-800/80 border border-slate-200 dark:border-slate-700 text-center">
            <div className="flex items-center justify-center gap-1 text-[10px] font-mono text-slate-500 dark:text-slate-400 uppercase">
              <Target className="w-3 h-3 text-sky-600 dark:text-sky-400" />
              <span>Target KPI: &gt;80%</span>
            </div>
            <div className="flex items-center justify-center gap-1.5 mt-0.5">
              <span className={`text-base font-mono font-extrabold ${isKpiMet ? 'text-emerald-600 dark:text-emerald-400' : 'text-amber-600 dark:text-amber-400'}`}>
                {Math.round(agreement_rate)}%
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.2 rounded-full bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-700 font-bold">
                {isKpiMet ? 'KPI MET' : 'CALIBRATING'}
              </span>
            </div>
          </div>

          <Link
            to="/new-case"
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-sky-600 hover:bg-sky-500 text-white text-xs font-bold font-mono shadow-sm hover:shadow transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Ingest Incident</span>
          </Link>
        </div>
      </div>

      {/* The 4 Architectural Pillars */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
        <div className="bg-white dark:bg-[#0d1524] rounded-xl border border-slate-200 dark:border-slate-800 p-4 flex items-center gap-3.5 shadow-subtle hover:shadow-card transition-all">
          <div className="p-2.5 rounded-xl bg-sky-50 dark:bg-sky-950/60 text-sky-600 dark:text-sky-400 border border-sky-200 dark:border-sky-800/60 flex-shrink-0">
            <Search className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-slate-900 dark:text-white font-mono">1. Evidence Analysis</div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">Cisco IOS telemetry & topology</div>
          </div>
        </div>

        <div className="bg-white dark:bg-[#0d1524] rounded-xl border border-slate-200 dark:border-slate-800 p-4 flex items-center gap-3.5 shadow-subtle hover:shadow-card transition-all">
          <div className="p-2.5 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 text-emerald-600 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800/60 flex-shrink-0">
            <Zap className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-slate-900 dark:text-white font-mono">2. Rule Engine Checks</div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">Deterministic violation matrix</div>
          </div>
        </div>

        <div className="bg-white dark:bg-[#0d1524] rounded-xl border border-slate-200 dark:border-slate-800 p-4 flex items-center gap-3.5 shadow-subtle hover:shadow-card transition-all">
          <div className="p-2.5 rounded-xl bg-indigo-50 dark:bg-indigo-950/60 text-indigo-600 dark:text-indigo-400 border border-indigo-200 dark:border-indigo-800/60 flex-shrink-0">
            <Brain className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-slate-900 dark:text-white font-mono">3. AI Diagnosis</div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">Confidence-backed fixes</div>
          </div>
        </div>

        <div className="bg-white dark:bg-[#0d1524] rounded-xl border border-slate-200 dark:border-slate-800 p-4 flex items-center gap-3.5 shadow-subtle hover:shadow-card transition-all">
          <div className="p-2.5 rounded-xl bg-amber-50 dark:bg-amber-950/60 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-800/60 flex-shrink-0">
            <UserCheck className="w-4 h-4" />
          </div>
          <div>
            <div className="text-xs font-bold text-slate-900 dark:text-white font-mono">4. Human Review</div>
            <div className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5">Accept, Edit, or Reject audit</div>
          </div>
        </div>
      </div>

      {/* Top Statistics 5-Card Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <StatCard
          title="Total Ingested"
          value={total_cases}
          icon={FolderGit2}
          color="blue"
          subtitle="All active Cisco cases"
        />
        <StatCard
          title="TAC Accepted"
          value={accepted}
          icon={CheckCircle2}
          color="emerald"
          subtitle="Verified by NetOps team"
        />
        <StatCard
          title="Human Edited"
          value={edited}
          icon={Edit3}
          color="amber"
          subtitle="Adjusted during review"
        />
        <StatCard
          title="Rejected"
          value={rejected}
          icon={XCircle}
          color="rose"
          subtitle="Declined hypotheses"
        />
        <StatCard
          title="Agreement Rate"
          value={`${Math.round(agreement_rate)}%`}
          icon={Percent}
          color="cyan"
          subtitle="Target: >80% Alignment"
        />
      </div>

      {/* Main Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Issue Distribution Chart */}
        <div className="lg:col-span-2 bg-white dark:bg-[#0d1524] rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-card">
          <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
            <div className="flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-sky-600 dark:text-sky-400" />
              <h3 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight font-mono">
                Cisco Incident Category Telemetry
              </h3>
            </div>
            <span className="text-xs font-mono text-sky-600 dark:text-sky-400 px-2.5 py-0.5 rounded-full bg-sky-50 dark:bg-sky-950/80 border border-sky-200 dark:border-sky-800/60 font-semibold">
              Live Feed
            </span>
          </div>

          <div className="h-72 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={issue_distribution}
                margin={{ top: 10, right: 10, left: -20, bottom: 25 }}
              >
                <XAxis
                  dataKey="category"
                  stroke={isDark ? '#64748b' : '#94a3b8'}
                  fontSize={11}
                  tickLine={false}
                  angle={-25}
                  textAnchor="end"
                  interval={0}
                />
                <YAxis stroke={isDark ? '#64748b' : '#94a3b8'} fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: isDark ? '#0f172a' : '#ffffff',
                    borderColor: isDark ? '#1e293b' : '#e2e8f0',
                    borderRadius: '0.75rem',
                    fontSize: '12px',
                    color: isDark ? '#f8fafc' : '#0f172a',
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.08)',
                  }}
                  cursor={{ fill: isDark ? 'rgba(2, 132, 199, 0.08)' : 'rgba(2, 132, 199, 0.05)' }}
                />
                <Bar
                  dataKey="count"
                  fill="#0284c7"
                  radius={[6, 6, 0, 0]}
                  name="Cases"
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Severity Distribution Donut Chart */}
        <div className="bg-white dark:bg-[#0d1524] rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-card flex flex-col justify-between">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-amber-500" />
              <h3 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight font-mono">
                Risk Posture
              </h3>
            </div>
            <span className="text-xs font-mono text-slate-500 dark:text-slate-400">
              Severity
            </span>
          </div>

          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severity_distribution}
                  dataKey="count"
                  nameKey="severity"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={5}
                >
                  {severity_distribution.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={SEVERITY_COLORS[entry.severity] || '#64748b'}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: isDark ? '#0f172a' : '#ffffff',
                    borderColor: isDark ? '#1e293b' : '#e2e8f0',
                    borderRadius: '0.75rem',
                    fontSize: '12px',
                    color: isDark ? '#f8fafc' : '#0f172a',
                  }}
                />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  formatter={(val) => (
                    <span className="text-xs text-slate-600 dark:text-slate-300 font-semibold font-mono">
                      {val}
                    </span>
                  )}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="grid grid-cols-2 gap-2 pt-3 border-t border-slate-100 dark:border-slate-800 text-xs">
            {severity_distribution.map((item) => (
              <div key={item.severity} className="flex items-center justify-between px-3 py-1.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200/60 dark:border-slate-700/60">
                <span className="text-slate-500 dark:text-slate-400 font-mono text-[11px]">{item.severity}:</span>
                <span className="font-mono font-bold text-slate-900 dark:text-slate-100">{item.count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Section: Rule Engine Findings & Conflicting Cases */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Most Common Rule Engine Findings */}
        <div className="bg-white dark:bg-[#0d1524] rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Zap className="w-4 h-4 text-sky-600 dark:text-sky-400" />
              <h3 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight font-mono">
                Deterministic Cisco Rule Hits
              </h3>
            </div>
            <span className="text-xs font-mono text-sky-600 dark:text-sky-400 font-bold">
              Automated Checks
            </span>
          </div>

          <div className="space-y-3">
            {common_rule_findings.map((rule) => (
              <div
                key={rule.rule_id}
                className="p-3.5 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200/80 dark:border-slate-700 flex items-center justify-between gap-3 hover:border-sky-400 transition-colors"
              >
                <div className="flex items-center gap-3">
                  <span className="font-mono text-xs font-bold text-sky-600 dark:text-sky-400 px-2 py-0.5 rounded bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700">
                    {rule.rule_id}
                  </span>
                  <div>
                    <h5 className="text-xs font-semibold text-slate-800 dark:text-slate-200 font-sans">
                      {rule.name}
                    </h5>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400 font-mono">
                      Category: {rule.category}
                    </span>
                  </div>
                </div>

                <div className="flex items-center gap-2.5">
                  <span className="text-xs font-mono px-2.5 py-0.5 rounded-full bg-white dark:bg-slate-900 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 font-medium">
                    {rule.occurrences} hits
                  </span>
                  <SeverityBadge severity={rule.severity} />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Conflicting Cases */}
        <div className="bg-white dark:bg-[#0d1524] rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-card">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-500" />
              <h3 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight font-mono">
                Evidence Conflicts (AI vs Cisco Rules)
              </h3>
            </div>
            <span className="text-xs font-mono text-rose-600 dark:text-rose-400 px-2.5 py-0.5 rounded-full bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-900 font-bold">
              {conflicting_cases.length} Conflicts
            </span>
          </div>

          {conflicting_cases.length === 0 ? (
            <div className="p-8 text-center bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-800">
              <CheckCircle2 className="w-8 h-8 text-emerald-500 mx-auto mb-2" />
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Zero active conflicts detected between AI hypotheses and deterministic Cisco rule checks.
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {conflicting_cases.map((c) => (
                <div
                  key={c.case_id}
                  className="p-4 bg-slate-50 dark:bg-slate-800/50 rounded-xl border border-rose-200 dark:border-rose-900/50 space-y-2 hover:border-rose-400 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs font-bold text-rose-700 dark:text-rose-300 px-2.5 py-0.5 rounded-full bg-rose-100 dark:bg-rose-950/80 border border-rose-300 dark:border-rose-800">
                      {c.case_id}
                    </span>
                    <Link
                      to={`/diagnosis/DIAG-${c.case_id}`}
                      className="inline-flex items-center gap-1 text-xs font-bold text-sky-600 dark:text-sky-400 hover:underline font-mono"
                    >
                      <span>Investigate</span>
                      <ArrowUpRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>

                  <p className="text-xs font-medium text-slate-800 dark:text-slate-200">
                    {c.symptom}
                  </p>

                  <div className="p-3 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 text-[11px] space-y-1.5 font-mono">
                    <div className="text-sky-600 dark:text-sky-300">
                      <span className="text-slate-400">AI Hypothesis:</span> {c.ai_diagnosis}
                    </div>
                    <div className="text-rose-600 dark:text-rose-300">
                      <span className="text-slate-400">Rule Finding:</span> {c.rule_finding}
                    </div>
                    <div className="text-amber-600 dark:text-amber-300 pt-1 border-t border-slate-100 dark:border-slate-800">
                      <span className="text-slate-400">Conflict Reason:</span> {c.conflict_reason}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
