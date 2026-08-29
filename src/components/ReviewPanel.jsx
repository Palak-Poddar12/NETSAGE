import React, { useState } from 'react';
import {
  CheckCircle,
  Edit3,
  XCircle,
  Send,
  UserCheck,
  ShieldCheck,
  AlertCircle,
  FileCheck,
} from 'lucide-react';
import { useCaseContext } from '../context/CaseContext';
import { useToast } from './Toast';

export function ReviewPanel({
  diagnosisId,
  originalDiagnosis,
  existingReview,
  onReviewSubmitted,
}) {
  const { submitHumanReview } = useCaseContext();
  const { addToast } = useToast();

  const [actionType, setActionType] = useState('ACCEPT'); // 'ACCEPT' | 'EDIT' | 'REJECT'
  const [correctedDiagnosis, setCorrectedDiagnosis] = useState('');
  const [reviewerComment, setReviewerComment] = useState('');
  const [reviewerName, setReviewerName] = useState('Senior NetOps Engineer');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccessMessage(null);

    // Validation
    if (actionType === 'EDIT') {
      if (!correctedDiagnosis.trim()) {
        setError('Corrected diagnosis is required when choosing Edit.');
        return;
      }
      if (!reviewerComment.trim()) {
        setError('Reviewer reason/comment is required when editing diagnosis.');
        return;
      }
    } else if (actionType === 'REJECT') {
      if (!reviewerComment.trim()) {
        setError('Rejection reason is required when choosing Reject.');
        return;
      }
    }

    setSubmitting(true);

    try {
      const payload = {
        diagnosis_id: diagnosisId,
        status: actionType === 'ACCEPT' ? 'ACCEPTED' : actionType === 'EDIT' ? 'EDITED' : 'REJECTED',
        reviewer: reviewerName,
        comment: reviewerComment,
        corrected_diagnosis: actionType === 'EDIT' ? correctedDiagnosis : null,
        timestamp: new Date().toISOString(),
      };

      const updated = submitHumanReview(diagnosisId, payload);
      const msg =
        actionType === 'ACCEPT'
          ? 'Diagnosis verified and marked ACCEPTED.'
          : actionType === 'EDIT'
          ? 'Diagnosis updated and marked EDITED.'
          : 'Diagnosis rejected and marked REJECTED.';

      setSuccessMessage(msg);
      addToast(msg, actionType === 'ACCEPT' ? 'success' : actionType === 'EDIT' ? 'warning' : 'error');

      if (onReviewSubmitted) {
        onReviewSubmitted(updated?.review || payload);
      }
    } catch (err) {
      setError(err.message || 'Failed to submit review. Please retry.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="bg-white dark:bg-[#0d1524] rounded-2xl border border-slate-200 dark:border-slate-800 overflow-hidden shadow-card transition-colors">
      {/* Header */}
      <div className="px-6 py-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50/80 dark:bg-slate-900/60 flex items-center justify-between flex-wrap gap-2">
        <div className="flex items-center gap-2.5">
          <UserCheck className="w-5 h-5 text-sky-600 dark:text-sky-400" />
          <h3 className="text-sm font-bold text-slate-900 dark:text-white tracking-tight">
            Human-in-the-Loop Review & Validation
          </h3>
        </div>
        <span className="text-xs font-mono px-2.5 py-1 rounded-full bg-slate-100 dark:bg-slate-800 text-sky-700 dark:text-sky-300 border border-slate-200 dark:border-slate-700 font-bold">
          ID: {diagnosisId}
        </span>
      </div>

      <div className="p-6 space-y-6">
        {/* Dual Pane / Original AI vs Human Decision Comparison */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left Column: ORIGINAL AI DIAGNOSIS (Immutable) */}
          <div className="bg-slate-50 dark:bg-slate-900/70 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 space-y-3">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400">
                ORIGINAL AI DIAGNOSIS
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400 font-bold">
                READ-ONLY
              </span>
            </div>

            <div className="space-y-3 text-xs">
              <div>
                <span className="text-slate-500 dark:text-slate-400 font-medium">Root Cause:</span>
                <p className="mt-1 text-slate-800 dark:text-slate-200 bg-white dark:bg-[#0a0f1a] p-3 rounded-xl border border-slate-200 dark:border-slate-800 leading-relaxed font-sans shadow-subtle">
                  {originalDiagnosis?.root_cause || 'No diagnosis generated.'}
                </p>
              </div>

              {originalDiagnosis?.proposed_fix && (
                <div>
                  <span className="text-slate-500 dark:text-slate-400 font-medium">Proposed Fix:</span>
                  <pre className="mt-1 cisco-terminal text-[11px] max-h-36 overflow-y-auto">
                    {originalDiagnosis.proposed_fix}
                  </pre>
                </div>
              )}
            </div>
          </div>

          {/* Right Column: HUMAN REVIEW ACTION */}
          <div className="bg-slate-50 dark:bg-slate-900/70 rounded-2xl border border-slate-200 dark:border-slate-800 p-5 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
              <span className="text-xs font-mono font-bold uppercase tracking-wider text-sky-600 dark:text-sky-400">
                HUMAN REVIEW
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-sky-100 dark:bg-sky-950 text-sky-700 dark:text-sky-300 border border-sky-200 dark:border-sky-800 font-bold">
                DECISION
              </span>
            </div>

            {/* Action Selector Tabs */}
            <div className="grid grid-cols-3 gap-2">
              <button
                type="button"
                onClick={() => setActionType('ACCEPT')}
                className={`py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                  actionType === 'ACCEPT'
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-slate-700'
                }`}
              >
                <CheckCircle className="w-3.5 h-3.5" />
                <span>Accept</span>
              </button>

              <button
                type="button"
                onClick={() => setActionType('EDIT')}
                className={`py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                  actionType === 'EDIT'
                    ? 'bg-amber-600 text-white shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-slate-700'
                }`}
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span>Edit</span>
              </button>

              <button
                type="button"
                onClick={() => setActionType('REJECT')}
                className={`py-2 px-3 rounded-xl text-xs font-bold flex items-center justify-center gap-1.5 transition-all ${
                  actionType === 'REJECT'
                    ? 'bg-rose-600 text-white shadow-sm'
                    : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white border border-slate-200 dark:border-slate-700'
                }`}
              >
                <XCircle className="w-3.5 h-3.5" />
                <span>Reject</span>
              </button>
            </div>

            {/* Dynamic Form based on actionType */}
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-600 dark:text-slate-400 mb-1">
                  Reviewer Signature
                </label>
                <input
                  type="text"
                  value={reviewerName}
                  onChange={(e) => setReviewerName(e.target.value)}
                  className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-sky-500 font-sans"
                  placeholder="e.g. Lead Network Engineer"
                />
              </div>

              {actionType === 'EDIT' && (
                <div className="space-y-1">
                  <label className="block text-xs font-bold text-amber-700 dark:text-amber-300">
                    Corrected Diagnosis <span className="text-rose-500">*</span>
                  </label>
                  <textarea
                    rows={3}
                    value={correctedDiagnosis}
                    onChange={(e) => setCorrectedDiagnosis(e.target.value)}
                    className="w-full bg-white dark:bg-slate-900 border border-amber-300 dark:border-amber-500/40 rounded-xl p-3 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-amber-500 font-sans"
                    placeholder="Enter human-verified corrected root cause & remediation..."
                    required
                  />
                </div>
              )}

              <div className="space-y-1">
                <label className="block text-xs font-medium text-slate-700 dark:text-slate-300">
                  {actionType === 'ACCEPT'
                    ? 'Reviewer Notes (Optional)'
                    : actionType === 'EDIT'
                    ? 'Reason for Edit / Commentary *'
                    : 'Rejection Reason *'}
                </label>
                <textarea
                  rows={actionType === 'ACCEPT' ? 2 : 3}
                  value={reviewerComment}
                  onChange={(e) => setReviewerComment(e.target.value)}
                  className="w-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl p-3 text-xs text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:border-sky-500 font-sans"
                  placeholder={
                    actionType === 'ACCEPT'
                      ? 'Add any operational observations...'
                      : actionType === 'EDIT'
                      ? 'Explain why the AI diagnosis required correction...'
                      : 'State why the diagnosis was rejected...'
                  }
                  required={actionType !== 'ACCEPT'}
                />
              </div>

              {error && (
                <div className="p-3 rounded-xl bg-rose-50 dark:bg-rose-950/60 border border-rose-200 dark:border-rose-800 text-rose-700 dark:text-rose-300 text-xs flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              {successMessage && (
                <div className="p-3 rounded-xl bg-emerald-50 dark:bg-emerald-950/60 border border-emerald-200 dark:border-emerald-800 text-emerald-700 dark:text-emerald-300 text-xs flex items-center gap-2">
                  <FileCheck className="w-4 h-4 flex-shrink-0" />
                  <span>{successMessage}</span>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={submitting}
                className={`w-full py-2.5 px-4 rounded-xl font-bold text-xs text-white shadow-sm hover:shadow transition-all flex items-center justify-center gap-2 ${
                  actionType === 'ACCEPT'
                    ? 'bg-emerald-600 hover:bg-emerald-500'
                    : actionType === 'EDIT'
                    ? 'bg-amber-600 hover:bg-amber-500'
                    : 'bg-rose-600 hover:bg-rose-500'
                } disabled:opacity-50`}
              >
                <Send className="w-3.5 h-3.5" />
                <span>
                  {submitting
                    ? 'Submitting Review...'
                    : actionType === 'ACCEPT'
                    ? '✓ Accept Diagnosis'
                    : actionType === 'EDIT'
                    ? 'Edit & Submit'
                    : 'Reject Diagnosis'}
                </span>
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReviewPanel;
