import type { Verdict } from "@/lib/types";

/** Browser uses Next proxy; avoids CORS. Server-side uses env URL. */
export function getApiBase(): string {
  if (typeof window !== "undefined") {
    return "/api/backend";
  }
  return (
    process.env.SENTINEL_API_URL?.replace(/\/$/, "") ??
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
    "http://127.0.0.1:8000"
  );
}

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

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${getApiBase()}/health`, {
      cache: "no-store",
    });
    const body = (await res.json()) as ApiEnvelope<{ status: string }>;
    return res.ok && body.success === true;
  } catch {
    return false;
  }
}

export async function fetchScenarios(): Promise<ScenarioRow[]> {
  const res = await fetch(`${getApiBase()}/v1/scenarios`, {
    cache: "no-store",
  });
  const body = (await res.json()) as ApiEnvelope<{ scenarios: ScenarioRow[] }>;
  if (!res.ok || !body.success || !body.data) {
    throw new Error(body.error ?? `scenarios failed (${res.status})`);
  }
  return body.data.scenarios;
}

export async function analyzeAd(
  payload: AnalyzeRequest,
): Promise<AnalyzeResponse> {
  const res = await fetch(`${getApiBase()}/v1/analyze`, {
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
