import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Activity,
  Layers,
  ArrowRight,
  Shield,
  Zap,
  Terminal,
  CheckSquare,
  AlertTriangle,
  RefreshCw,
  FolderGit2,
  FileCode,
} from 'lucide-react';
import { SeverityBadge } from '../components/SeverityBadge';
import { FindingCard } from '../components/FindingCard';
import { EvidencePanel } from '../components/EvidencePanel';
import { DiagnosisCard } from '../components/DiagnosisCard';
import { SafeDisclaimer } from '../components/SafeDisclaimer';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { formatDate } from '../utils/formatters';
import { useCaseContext } from '../context/CaseContext';
import { useToast } from '../components/Toast';

export function Diagnosis() {
  const { diagnosisId = 'DIAG-CASE-001' } = useParams();
  const { getDiagnosisById } = useCaseContext();
  const { addToast } = useToast();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const timer = setTimeout(() => {
      const result = getDiagnosisById(diagnosisId);
      setData(result);
      setLoading(false);
    }, 250);
    return () => clearTimeout(timer);
  }, [diagnosisId, getDiagnosisById]);

  if (loading) {
    return (
      <div className="space-y-6">
        <LoadingState
          type="diagnosis"
          message={`Synthesizing network telemetry for ${diagnosisId}...`}
        />
      </div>
    );
  }

  if (!data) {
    return (
      <ErrorState
        title="Diagnostic Record Unavailable"
        message={`Unable to locate diagnosis session for ${diagnosisId}.`}
      />
    );
  }

  const {
    case_id,
    status = 'DIAGNOSIS_SUPPORTED',
    confidence = 0.9,
    case_summary = {},
    network_evidence = {},
    rule_engine_findings = [],
    ai_diagnosis = {},
    review,
  } = data;

  return (
    <div className="space-y-6 pb-16">
      {/* Advisory Security Banner */}
      <SafeDisclaimer />

      {/* Case Header Card */}
      <div className="bg-white dark:bg-[#0d1524] rounded-2xl border border-slate-200 dark:border-slate-800 p-6 shadow-card transition-colors">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div className="space-y-1">
            <div className="flex items-center gap-2.5 flex-wrap">
              <span className="font-mono text-xs font-bold text-sky-700 dark:text-sky-300 px-2.5 py-1 rounded-full bg-sky-50 dark:bg-sky-950/80 border border-sky-200 dark:border-sky-800/60">
                {case_id || 'CASE-001'}
              </span>
              <span className="font-mono text-xs text-slate-500 dark:text-slate-400">
                Session: {diagnosisId}
              </span>
              <SeverityBadge severity={case_summary.severity || 'HIGH'} />
            </div>
            <h2 className="text-base sm:text-lg font-bold text-slate-900 dark:text-white tracking-tight mt-1">
              {case_summary.symptom || 'Network connectivity fault under analysis.'}
            </h2>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to={`/review/${diagnosisId}`}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold uppercase tracking-wider shadow-sm hover:shadow transition-all active:scale-95"
            >
              <CheckSquare className="w-4 h-4" />
              <span>Human Review</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>

        {/* Case Metadata Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-4 text-xs">
          <div>
            <span className="text-slate-500 dark:text-slate-400 font-medium block">Category:</span>
            <span className="text-slate-800 dark:text-slate-200 font-semibold mt-0.5 block">
              {case_summary.category || 'General'}
            </span>
          </div>

          <div>
            <span className="text-slate-500 dark:text-slate-400 font-medium block">OSI Layer:</span>
            <span className="text-sky-600 dark:text-sky-400 font-mono font-bold mt-0.5 block">
              {case_summary.osi_layer || 'Layer 3 (Network)'}
            </span>
          </div>

          <div>
            <span className="text-slate-500 dark:text-slate-400 font-medium block">Evaluation Status:</span>
            <span
              className={`font-mono text-[11px] font-bold mt-0.5 block ${
                status === 'DIAGNOSIS_SUPPORTED'
                  ? 'text-emerald-600 dark:text-emerald-400'
                  : status === 'CONFLICTING_EVIDENCE'
                  ? 'text-rose-600 dark:text-rose-400'
                  : 'text-amber-600 dark:text-amber-400'
              }`}
            >
              {status}
            </span>
          </div>

          <div>
            <span className="text-slate-500 dark:text-slate-400 font-medium block">Human Verdict:</span>
            <span className="text-slate-800 dark:text-slate-200 font-mono mt-0.5 block">
              {review?.status ? (
                <span className="text-emerald-600 dark:text-emerald-400 font-bold">{review.status}</span>
              ) : (
                <span className="text-amber-600 dark:text-amber-400">PENDING_REVIEW</span>
              )}
            </span>
          </div>
        </div>
      </div>

      {/* Main Diagnostic Workspace (2 Column Grid on lg) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Network Evidence & Deterministic Rules (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          <EvidencePanel evidence={network_evidence} />

          {/* Deterministic Rule Engine Findings */}
          <div className="bg-white dark:bg-[#0d1524] rounded-2xl border border-slate-200 dark:border-slate-800 p-5 shadow-card space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
              <div className="flex items-center gap-2">
                <Zap className="w-4 h-4 text-sky-600 dark:text-sky-400" />
                <h3 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight">
                  Deterministic Rule Findings
                </h3>
              </div>
              <span className="text-xs font-mono text-sky-600 dark:text-sky-400 px-2 py-0.5 rounded-full bg-sky-50 dark:bg-sky-950/80 border border-sky-200 dark:border-sky-800/40 font-bold">
                {rule_engine_findings.length} Evaluated
              </span>
            </div>

            {rule_engine_findings.length === 0 ? (
              <p className="text-xs text-slate-400 italic py-3 text-center">
                No deterministic rule violations detected.
              </p>
            ) : (
              <div className="space-y-3">
                {rule_engine_findings.map((finding) => (
                  <FindingCard key={finding.rule_id} finding={finding} />
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: AI Diagnosis, Confidence & Proposed Fixes (7 cols) */}
        <div className="lg:col-span-7">
          <DiagnosisCard diagnosis={ai_diagnosis} status={status} />
        </div>
      </div>
    </div>
  );
}

export default Diagnosis;
