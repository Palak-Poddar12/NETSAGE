import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  CheckSquare,
  Activity,
  Layers,
  ArrowLeft,
  ShieldCheck,
  Zap,
  CheckCircle2,
  FileCode,
  Clock,
} from 'lucide-react';
import { ReviewPanel } from '../components/ReviewPanel';
import { FindingCard } from '../components/FindingCard';
import { SeverityBadge } from '../components/SeverityBadge';
import { SafeDisclaimer } from '../components/SafeDisclaimer';
import { LoadingState } from '../components/LoadingState';
import { ErrorState } from '../components/ErrorState';
import { formatDate } from '../utils/formatters';
import { useCaseContext } from '../context/CaseContext';

export function HumanReview() {
  const { diagnosisId = 'DIAG-CASE-001' } = useParams();
  const { getDiagnosisById } = useCaseContext();

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const timer = setTimeout(() => {
      const result = getDiagnosisById(diagnosisId);
      setData(result);
      setLoading(false);
    }, 200);
    return () => clearTimeout(timer);
  }, [diagnosisId, getDiagnosisById]);

  if (loading) {
    return (
      <div className="space-y-6">
        <LoadingState message={`Preparing review audit session for ${diagnosisId}...`} />
      </div>
    );
  }

  if (!data) {
    return (
      <ErrorState
        title="Audit Record Unavailable"
        message={`Unable to find session to review for ${diagnosisId}.`}
      />
    );
  }

  const {
    case_id,
    case_summary = {},
    rule_engine_findings = [],
    ai_diagnosis = {},
    status = 'DIAGNOSIS_SUPPORTED',
    review,
  } = data;

  return (
    <div className="space-y-6 pb-16">
      {/* Advisory Banner */}
      <SafeDisclaimer />

      {/* Navigation Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <Link
            to={`/diagnosis/${diagnosisId}`}
            className="p-2.5 rounded-xl bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:text-slate-900 dark:hover:text-white shadow-sm transition-colors"
            title="Back to Diagnosis"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-slate-900 dark:text-white tracking-tight">
                Human Validation & Review
              </h2>
              <span className="font-mono text-xs px-2.5 py-0.5 rounded-full bg-sky-50 dark:bg-sky-950 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-800 font-bold">
                {case_id}
              </span>
            </div>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Review AI diagnostic hypotheses against deterministic network evidence.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 text-xs font-mono">
          <span className="text-slate-500 dark:text-slate-400">Diagnosis Session:</span>
          <span className="text-sky-600 dark:text-sky-400 font-bold">{diagnosisId}</span>
        </div>
      </div>

      {/* Main Review Form & Dual View */}
      <ReviewPanel
        diagnosisId={diagnosisId}
        originalDiagnosis={ai_diagnosis}
        existingReview={review}
        onReviewSubmitted={(res) => {
          setData((prev) => ({
            ...prev,
            review: res,
          }));
        }}
      />

      {/* Supporting Rule Findings Correlation Grid */}
      <div className="bg-white dark:bg-[#0d1524] rounded-2xl border border-slate-200 dark:border-slate-800 p-6 space-y-4 shadow-card">
        <div className="flex items-center justify-between pb-3 border-b border-slate-100 dark:border-slate-800">
          <div className="flex items-center gap-2">
            <Zap className="w-4 h-4 text-sky-600 dark:text-sky-400" />
            <h3 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight">
              Rule Engine Corroboration
            </h3>
          </div>
          <span className="text-xs font-mono text-slate-500 dark:text-slate-400">
            Deterministic Evidence
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {rule_engine_findings.map((finding) => (
            <FindingCard key={finding.rule_id} finding={finding} />
          ))}
        </div>
      </div>

      {/* Existing Review Audit Record if already submitted */}
      {review && (
        <div className="p-5 bg-emerald-50 dark:bg-emerald-950/40 rounded-2xl border border-emerald-200 dark:border-emerald-800 space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-bold text-emerald-800 dark:text-emerald-300">
              <CheckCircle2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              <span>Prior Human Decision on Record</span>
            </div>
            <span className="text-xs font-mono px-2.5 py-0.5 rounded-full bg-emerald-100 dark:bg-emerald-900 text-emerald-800 dark:text-emerald-300 border border-emerald-300 dark:border-emerald-700 font-bold">
              {review.status}
            </span>
          </div>
          <p className="text-xs text-slate-700 dark:text-slate-300 font-sans">
            <strong>Reviewer:</strong> {review.reviewer} • <strong>Timestamp:</strong> {formatDate(review.timestamp)}
          </p>
          {review.comment && (
            <p className="text-xs text-slate-600 dark:text-slate-400 bg-white dark:bg-slate-900 p-3 rounded-xl border border-emerald-200 dark:border-emerald-900/60 font-sans">
              "{review.comment}"
            </p>
          )}
        </div>
      )}
    </div>
  );
}

export default HumanReview;
