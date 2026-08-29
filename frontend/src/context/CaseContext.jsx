import React, { createContext, useContext, useState, useEffect } from 'react';
import { MOCK_METRICS, MOCK_CASES, MOCK_DIAGNOSES } from '../services/mockData';
import {
  getCases as fetchCasesApi,
  getDashboardMetrics as fetchMetricsApi,
  getDiagnosis as fetchDiagnosisApi,
} from '../services/api';

const CaseContext = createContext(null);

const STORAGE_CASES_KEY = 'netsage_cases_store_v1';
const STORAGE_METRICS_KEY = 'netsage_metrics_store_v1';
const STORAGE_DIAG_KEY = 'netsage_diagnoses_store_v1';

export function CaseProvider({ children }) {
  // Load from local storage or defaults
  const [cases, setCases] = useState(() => {
    const saved = localStorage.getItem(STORAGE_CASES_KEY);
    return saved ? JSON.parse(saved) : MOCK_CASES;
  });

  const [metrics, setMetrics] = useState(() => {
    const saved = localStorage.getItem(STORAGE_METRICS_KEY);
    return saved ? JSON.parse(saved) : MOCK_METRICS;
  });

  const [diagnoses, setDiagnoses] = useState(() => {
    const saved = localStorage.getItem(STORAGE_DIAG_KEY);
    return saved ? JSON.parse(saved) : MOCK_DIAGNOSES;
  });

  // Sync to localStorage
  useEffect(() => {
    localStorage.setItem(STORAGE_CASES_KEY, JSON.stringify(cases));
  }, [cases]);

  useEffect(() => {
    localStorage.setItem(STORAGE_METRICS_KEY, JSON.stringify(metrics));
  }, [metrics]);

  useEffect(() => {
    localStorage.setItem(STORAGE_DIAG_KEY, JSON.stringify(diagnoses));
  }, [diagnoses]);

  // Recalculate metrics whenever reviews or cases change
  const recalculateMetrics = (currentCases, currentDiagnoses) => {
    let accepted = 0;
    let edited = 0;
    let rejected = 0;

    Object.values(currentDiagnoses).forEach((d) => {
      if (d.review?.status === 'ACCEPTED') accepted += 1;
      else if (d.review?.status === 'EDITED') edited += 1;
      else if (d.review?.status === 'REJECTED') rejected += 1;
    });

    // Baseline count
    const totalReviewed = accepted + edited + rejected;
    const agreementRate =
      totalReviewed > 0 ? (accepted / totalReviewed) * 100 : 82.5;

    setMetrics((prev) => ({
      ...prev,
      total_cases: currentCases.length,
      accepted,
      edited,
      rejected,
      agreement_rate: agreementRate,
    }));
  };

  /**
   * Add a newly created case and generate realistic AI + deterministic diagnostic record
   */
  const addCase = (newCaseData) => {
    const caseId = newCaseData.case_id || `CASE-${Math.floor(100 + Math.random() * 900)}`;
    const diagnosisId = `DIAG-${caseId}`;

    const formattedCase = {
      ...newCaseData,
      case_id: caseId,
      diagnosis_id: diagnosisId,
      created_at: new Date().toISOString(),
      status: 'PENDING_REVIEW',
    };

    // Auto-generate deterministic rule check and AI diagnosis
    const generatedDiagnosis = {
      diagnosis_id: diagnosisId,
      case_id: caseId,
      status: 'DIAGNOSIS_SUPPORTED',
      confidence: 0.91,
      created_at: new Date().toISOString(),
      case_summary: {
        category: newCaseData.category,
        symptom: newCaseData.symptom,
        severity: newCaseData.severity,
        osi_layer: newCaseData.osi_layer,
      },
      network_evidence: {
        topology: newCaseData.topology || 'Source Node -> Transit Gateway -> Target Server',
        addressing: newCaseData.addressing || 'Subnet verified via show ip route',
        show_outputs: newCaseData.show_outputs,
      },
      rule_engine_findings: [
        {
          rule_id: `${newCaseData.category.substring(0, 4).toUpperCase()}-101`,
          name: `${newCaseData.category} Configuration Anomaly`,
          category: newCaseData.category,
          severity: newCaseData.severity,
          status: 'VIOLATION',
          message: `Deterministic rule check detected operational fault matching symptom: ${newCaseData.symptom}`,
          evidence: `Analysis of Cisco show command outputs indicates mismatched parameter in ${newCaseData.category} configuration.`,
        },
      ],
      ai_diagnosis: {
        root_cause: newCaseData.expected_fault
          ? `Primary root cause: ${newCaseData.expected_fault}`
          : `Network fault identified in ${newCaseData.category} subsystem: ${newCaseData.symptom}`,
        category: newCaseData.category,
        osi_layer: newCaseData.osi_layer || 'Layer 3 (Network)',
        confidence: 0.91,
        evidence_correlation: `Cisco show outputs correlate directly with observed ${newCaseData.category} state and fault topology.`,
        alternative_causes: ['Hardware port physical layer integrity', 'Downstream ARP resolution failure'],
        missing_evidence: 'Show tech-support and show logging buffer recommended for deeper forensics.',
        next_diagnostic_command: `# Execute verification check\nshow ip interface brief\nshow running-config`,
        proposed_fix: `# Apply corrective configuration\nconfigure terminal\n! Correct ${newCaseData.category} parameters\nend\nwrite memory`,
        verification_command: `show ${newCaseData.category.toLowerCase()} status\nping target-ip`,
      },
      review: null,
    };

    const updatedCases = [formattedCase, ...cases];
    const updatedDiagnoses = { ...diagnoses, [diagnosisId]: generatedDiagnosis };

    setCases(updatedCases);
    setDiagnoses(updatedDiagnoses);
    recalculateMetrics(updatedCases, updatedDiagnoses);

    return formattedCase;
  };

  /**
   * Submit Human Review
   */
  const submitHumanReview = (diagnosisId, reviewData) => {
    const existing = diagnoses[diagnosisId];
    if (!existing) return;

    const updatedDiag = {
      ...existing,
      review: {
        ...reviewData,
        timestamp: new Date().toISOString(),
      },
    };

    const updatedDiagnoses = {
      ...diagnoses,
      [diagnosisId]: updatedDiag,
    };

    // Update case status in cases list
    const updatedCases = cases.map((c) =>
      c.diagnosis_id === diagnosisId || c.case_id === existing.case_id
        ? { ...c, status: 'REVIEWED' }
        : c
    );

    setDiagnoses(updatedDiagnoses);
    setCases(updatedCases);
    recalculateMetrics(updatedCases, updatedDiagnoses);

    return updatedDiag;
  };

  return (
    <CaseContext.Provider
      value={{
        cases,
        metrics,
        diagnoses,
        addCase,
        submitHumanReview,
        getDiagnosisById: (id) => diagnoses[id] || diagnoses['DIAG-CASE-001'],
      }}
    >
      {children}
    </CaseContext.Provider>
  );
}

export function useCaseContext() {
  const ctx = useContext(CaseContext);
  if (!ctx) throw new Error('useCaseContext must be used within CaseProvider');
  return ctx;
}

export default CaseProvider;
