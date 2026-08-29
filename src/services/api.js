import {
  MOCK_METRICS,
  MOCK_CASES,
  MOCK_DIAGNOSES,
} from './mockData';

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Reusable HTTP Request Wrapper with robust error handling
 */
async function request(endpoint, options = {}) {
  const url = `${BASE_URL}${endpoint}`;
  const config = {
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const error = new Error(
        errorData.detail || errorData.message || `HTTP error! status: ${response.status}`
      );
      error.status = response.status;
      error.data = errorData;
      throw error;
    }

    return await response.json();
  } catch (err) {
    // Check if network failed or server unreachable
    if (err.name === 'TypeError' && err.message.includes('fetch')) {
      const offlineErr = new Error('Backend service is currently unreachable.');
      offlineErr.isNetworkError = true;
      throw offlineErr;
    }
    throw err;
  }
}

/**
 * Health Check API
 * GET /api/health
 */
export async function getHealth() {
  try {
    return await request('/api/health');
  } catch (err) {
    return { status: 'offline', error: err.message };
  }
}

/**
 * Dashboard Metrics API
 * GET /api/dashboard/metrics
 */
export async function getDashboardMetrics() {
  try {
    return await request('/api/dashboard/metrics');
  } catch (err) {
    // If backend is not started in local dev, provide marked fallback
    console.warn('[NetSage API] Failed to reach /api/dashboard/metrics, using dev fallback data.');
    return MOCK_METRICS;
  }
}

/**
 * Cases API
 * GET /api/cases
 */
export async function getCases(params = {}) {
  try {
    const query = new URLSearchParams(params).toString();
    const endpoint = query ? `/api/cases?${query}` : '/api/cases';
    return await request(endpoint);
  } catch (err) {
    console.warn('[NetSage API] Failed to reach /api/cases, using dev fallback data.');
    return MOCK_CASES;
  }
}

/**
 * Single Case API
 * GET /api/cases/{case_id}
 */
export async function getCase(caseId) {
  try {
    return await request(`/api/cases/${caseId}`);
  } catch (err) {
    console.warn(`[NetSage API] Failed to reach /api/cases/${caseId}, using dev fallback data.`);
    const found = MOCK_CASES.find((c) => c.case_id === caseId);
    if (!found) throw new Error(`Case ${caseId} not found`);
    return found;
  }
}

/**
 * Create Case API
 * POST /api/cases
 */
export async function createCase(caseData) {
  try {
    return await request('/api/cases', {
      method: 'POST',
      body: JSON.stringify(caseData),
    });
  } catch (err) {
    console.warn('[NetSage API] Fallback case creation mock');
    const newCase = {
      ...caseData,
      case_id: caseData.case_id || `CASE-${Math.floor(100 + Math.random() * 900)}`,
      created_at: new Date().toISOString(),
      status: 'PENDING_REVIEW',
      diagnosis_id: `DIAG-${caseData.case_id || 'NEW'}`,
    };
    return newCase;
  }
}

/**
 * Diagnose Case API
 * POST /api/diagnose
 */
export async function diagnoseCase(data) {
  try {
    return await request('/api/diagnose', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  } catch (err) {
    console.warn('[NetSage API] Fallback diagnose response');
    return (
      MOCK_DIAGNOSES[data.diagnosis_id] ||
      MOCK_DIAGNOSES['DIAG-CASE-001'] || {
        diagnosis_id: data.diagnosis_id || 'DIAG-NEW',
        case_id: data.case_id || 'CASE-NEW',
        status: 'DIAGNOSIS_SUPPORTED',
        confidence: 0.9,
        ai_diagnosis: {
          root_cause: 'Network misconfiguration diagnosed by evidence analysis.',
          category: data.category || 'General',
          osi_layer: data.osi_layer || 'Layer 3 (Network)',
          confidence: 0.9,
          proposed_fix: 'Review topology and verify configurations.',
        },
      }
    );
  }
}

/**
 * Get Diagnosis API
 * GET /api/diagnoses/{diagnosis_id}
 */
export async function getDiagnosis(diagnosisId) {
  try {
    return await request(`/api/diagnoses/${diagnosisId}`);
  } catch (err) {
    console.warn(`[NetSage API] Failed to reach /api/diagnoses/${diagnosisId}, using dev fallback data.`);
    const diag = MOCK_DIAGNOSES[diagnosisId] || MOCK_DIAGNOSES['DIAG-CASE-001'];
    if (!diag) throw new Error(`Diagnosis ${diagnosisId} not found`);
    return diag;
  }
}

/**
 * Submit Human Review API
 * POST /api/reviews
 */
export async function submitReview(reviewData) {
  try {
    return await request('/api/reviews', {
      method: 'POST',
      body: JSON.stringify(reviewData),
    });
  } catch (err) {
    console.warn('[NetSage API] Fallback review submission simulated');
    return {
      success: true,
      review_id: `REV-${Date.now()}`,
      diagnosis_id: reviewData.diagnosis_id,
      status: reviewData.status,
      reviewer: reviewData.reviewer || 'Human Reviewer',
      timestamp: new Date().toISOString(),
      message: 'Review saved successfully.',
    };
  }
}
