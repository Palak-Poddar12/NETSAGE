import React, { useState } from 'react';
import {
  BrainCircuit,
  Layers,
  HelpCircle,
  AlertTriangle,
  Flame,
  CheckCircle2,
  Wrench,
  Activity,
  Copy,
  Check,
  AlertOctagon,
  Sparkles,
  ShieldCheck,
  Terminal,
  RotateCcw,
} from 'lucide-react';
import { formatConfidence, getConfidenceLevel } from '../utils/formatters';
import { useToast } from './Toast';

export function DiagnosisCard({
  diagnosis,
  status = 'DIAGNOSIS_SUPPORTED',
  className = '',
}) {
  const { addToast } = useToast();
  const [copiedFix, setCopiedFix] = useState(false);
  const [copiedVerify, setCopiedVerify] = useState(false);

  if (!diagnosis) return null;

  const {
    root_cause,
    category,
    osi_layer,
    confidence = 0.85,
    evidence_correlation,
    alternative_causes = [],
    missing_evidence,
    next_diagnostic_command,
    proposed_fix,
    verification_command,
  } = diagnosis;

  const numConfidence =
    typeof confidence === 'number'
      ? confidence <= 1
        ? Math.round(confidence * 100)
        : Math.round(confidence)
      : parseFloat(confidence) || 0;

  const confLevel = getConfidenceLevel(numConfidence);

  const handleCopyFix = () => {
    if (!proposed_fix) return;
    navigator.clipboard.writeText(proposed_fix);
    setCopiedFix(true);
    addToast('Cisco IOS proposed fix copied to clipboard.', 'success');
    setTimeout(() => setCopiedFix(false), 2000);
  };

  const handleCopyVerify = () => {
    if (!verification_command) return;
    navigator.clipboard.writeText(verification_command);
    setCopiedVerify(true);
    addToast('Cisco verification command copied.', 'info');
    setTimeout(() => setCopiedVerify(false), 2000);
  };

  return (
    <div
      className={`bg-cisco-navy rounded-2xl border border-cisco-border overflow-hidden shadow-cisco-card space-y-6 p-6 ${className}`}
    >
      {/* Prominent Conflict / Insufficient Evidence Banners */}
      {status === 'CONFLICTING_EVIDENCE' && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-600/70 flex items-start gap-3.5 text-rose-200">
          <AlertOctagon className="w-5 h-5 text-rose-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-bold text-rose-300 font-mono tracking-wide">
              EVIDENCE CONFLICT DETECTED
            </h4>
            <p className="text-xs text-rose-200/90 mt-1 leading-relaxed font-sans">
              AI hypothesis contradicts deterministic Cisco rule checks. Do not push changes to production without mandatory human review.
            </p>
          </div>
        </div>
      )}

      {status === 'INSUFFICIENT_EVIDENCE' && (
        <div className="p-4 rounded-xl bg-amber-950/60 border border-amber-600/70 flex items-start gap-3.5 text-amber-200">
          <AlertTriangle className="w-5 h-5 text-amber-400 flex-shrink-0 mt-0.5" />
          <div>
            <h4 className="text-sm font-bold text-amber-300 font-mono tracking-wide">
              INSUFFICIENT TELEMETRY EVIDENCE
            </h4>
            <p className="text-xs text-amber-200/90 mt-1 leading-relaxed font-sans">
              Additional Cisco IOS show commands are required before a definitive root cause can be confirmed.
            </p>
          </div>
        </div>
      )}

      {/* Header: AI Badge + Confidence Meter */}
      <div className="flex items-start justify-between flex-wrap gap-4 pb-5 border-b border-cisco-border">
        <div className="space-y-1.5">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-cisco-sky/15 text-cisco-sky border border-cisco-sky/30">
              <BrainCircuit className="w-4 h-4" />
            </div>
            <span className="text-xs font-mono font-bold tracking-wider text-cisco-sky uppercase">
              Cisco TAC AI Diagnosis (Advisory)
            </span>
          </div>
          <div className="flex items-center gap-2 text-xs text-slate-400 font-mono">
            <span className="font-semibold text-slate-200">{category || 'General'}</span>
            <span>•</span>
            <span className="text-cisco-sky font-bold">{osi_layer || 'Layer 3'}</span>
          </div>
        </div>

        {/* Cisco Confidence Gauge Box */}
        <div className="w-full sm:w-64 bg-cisco-dark p-3.5 rounded-xl border border-cisco-border">
          <div className="flex items-center justify-between text-xs mb-1.5 font-mono">
            <span className="text-slate-400">Diagnosis Confidence</span>
            <span className={`font-bold ${confLevel.color}`}>
              {numConfidence}%
            </span>
          </div>
          <div className="w-full bg-cisco-surface rounded-full h-2 overflow-hidden border border-cisco-border">
            <div
              className={`h-full transition-all duration-700 rounded-full ${confLevel.bar}`}
              style={{ width: `${numConfidence}%` }}
            />
          </div>
          <div className="mt-1.5 text-[10px] text-right text-slate-400 font-mono">
            {confLevel.label}
          </div>
        </div>
      </div>

      {/* Root Cause Section */}
      <div className="space-y-2">
        <h4 className="text-xs font-bold uppercase tracking-wider text-cisco-sky font-mono">
          Identified Root Cause
        </h4>
        <div className="p-4 rounded-xl bg-cisco-dark border border-cisco-border text-sm font-medium text-slate-100 leading-relaxed font-sans shadow-inner">
          {root_cause}
        </div>
      </div>

      {/* Evidence Correlation */}
      {evidence_correlation && (
        <div className="space-y-2">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
            Cisco Show Command Correlation
          </h4>
          <p className="text-xs text-slate-300 bg-cisco-dark/70 p-4 rounded-xl border border-cisco-border leading-relaxed font-sans">
            {evidence_correlation}
          </p>
        </div>
      )}

      {/* Grid: Alternative Hypotheses & Missing Evidence */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Alternative Causes */}
        <div className="bg-cisco-dark p-4 rounded-xl border border-cisco-border space-y-2">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-300 font-mono">
            <HelpCircle className="w-3.5 h-3.5 text-amber-400" />
            <span>Alternative Hypotheses</span>
          </div>
          {alternative_causes && alternative_causes.length > 0 ? (
            <ul className="space-y-1.5 text-xs text-slate-400 list-disc list-inside font-sans">
              {alternative_causes.map((alt, idx) => (
                <li key={idx} className="leading-relaxed">
                  {alt}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-xs text-slate-400 italic">None identified.</p>
          )}
        </div>

        {/* Missing Evidence */}
        <div className="bg-cisco-dark p-4 rounded-xl border border-cisco-border space-y-2">
          <div className="flex items-center gap-1.5 text-xs font-bold text-slate-300 font-mono">
            <Activity className="w-3.5 h-3.5 text-cisco-sky" />
            <span>Recommended Telemetry</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed font-sans">
            {missing_evidence || 'Sufficient evidence captured in initial Cisco buffer.'}
          </p>
        </div>
      </div>

      {/* Next Diagnostic Command */}
      {next_diagnostic_command && (
        <div className="space-y-2">
          <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
            Next Diagnostic Commands (Read-Only)
          </h4>
          <pre className="cisco-terminal text-xs bg-cisco-dark border-cisco-border">
            {next_diagnostic_command}
          </pre>
        </div>
      )}

      {/* Proposed Fix (Configuration Advice) */}
      {proposed_fix && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Wrench className="w-4 h-4 text-emerald-400" />
              <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-400 font-mono">
                Proposed Cisco IOS Remediation (Requires Review)
              </h4>
            </div>
            <button
              onClick={handleCopyFix}
              className="inline-flex items-center gap-1 text-xs text-emerald-400 hover:text-emerald-300 font-mono font-bold transition-colors"
            >
              {copiedFix ? (
                <>
                  <Check className="w-3.5 h-3.5" />
                  <span>Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy Fix</span>
                </>
              )}
            </button>
          </div>
          <pre className="cisco-terminal border-emerald-900/60 text-emerald-300 text-xs bg-cisco-dark">
            {proposed_fix}
          </pre>
        </div>
      )}

      {/* Verification Command */}
      {verification_command && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-cisco-sky" />
              <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 font-mono">
                Post-Remediation Verification Commands
              </h4>
            </div>
            <button
              onClick={handleCopyVerify}
              className="inline-flex items-center gap-1 text-xs text-cisco-sky hover:text-cyan-300 font-mono font-bold transition-colors"
            >
              {copiedVerify ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy Syntax</span>
                </>
              )}
            </button>
          </div>
          <pre className="cisco-terminal text-xs bg-cisco-dark border-cisco-border">
            {verification_command}
          </pre>
        </div>
      )}
    </div>
  );
}

export default DiagnosisCard;
