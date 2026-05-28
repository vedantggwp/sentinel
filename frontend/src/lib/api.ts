import type { Verdict } from "@/lib/types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export type ApiEnvelope<T> = {
  success: boolean;
  data: T | null;
  error: string | null;
};

export type AnalyzeRequest = {
  ad_id: string;
  conversation: string;
  ad_creative: string;
  advertiser?: string | null;
  landing_url?: string | null;
};

export type ApiClaim = {
  text: string;
  type: string;
  verified: boolean | null;
  actual_value?: string | null;
  source_url?: string | null;
};

export type ApiPipelineResult = {
  ad_id: string;
  verdict: Verdict;
  scores: Record<string, number>;
  claims: ApiClaim[];
  reason: string;
  rule_fired: string;
  vulnerability_flags: string[];
};

export type ApiAttestation = {
  ad_id: string;
  ad_hash: string;
  verdict: Verdict;
  issued_at: string;
  signature: string;
  public_key: string;
};

export type ApiTrace = {
  trace_id: string;
  issued_at?: string;
  verdict?: string;
  rule_fired?: string;
  reason?: string;
};

export type AnalyzeResponse = {
  result: ApiPipelineResult;
  attestation: ApiAttestation;
  trace: ApiTrace;
};

export type ScenarioRow = {
  id: string;
  conversation: string;
  ad_creative: string;
  advertiser?: string;
  expected: Verdict;
  reason?: string;
};

export function getApiBase(): string {
  return API_BASE;
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`, { cache: "no-store" });
    const body = (await res.json()) as ApiEnvelope<{ status: string }>;
    return res.ok && body.success === true;
  } catch {
    return false;
  }
}

export async function fetchScenarios(): Promise<ScenarioRow[]> {
  const res = await fetch(`${API_BASE}/v1/scenarios`, { cache: "no-store" });
  const body = (await res.json()) as ApiEnvelope<{ scenarios: ScenarioRow[] }>;
  if (!res.ok || !body.success || !body.data) {
    throw new Error(body.error ?? `scenarios failed (${res.status})`);
  }
  return body.data.scenarios;
}

export async function analyzeAd(
  payload: AnalyzeRequest,
): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_BASE}/v1/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const body = (await res.json()) as ApiEnvelope<AnalyzeResponse>;
  if (!res.ok || !body.success || !body.data) {
    throw new Error(body.error ?? `analyze failed (${res.status})`);
  }
  return body.data;
}
