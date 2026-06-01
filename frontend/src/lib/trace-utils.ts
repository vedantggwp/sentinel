import type { TraceStep, TraceStepId } from "@/lib/types";

/** Mock span durations for Langfuse-style timing bars (ms). */
export const STEP_DURATIONS: Record<TraceStepId, number> = {
  context: 18,
  thrad: 42,
  vulnerability: 120,
  policy: 280,
  factcheck: 890,
  decision: 12,
  overmind: 8,
};

export function shortTraceId(fullId: string): string {
  const parts = fullId.split("_");
  return parts[parts.length - 1]?.slice(0, 8) ?? fullId.slice(0, 8);
}

export function spanOperation(id: TraceStepId): string {
  const ops: Record<TraceStepId, string> = {
    context: "sentinel.context_gate",
    thrad: "thrad.bid_request",
    vulnerability: "sentinel.vulnerability_check",
    policy: "sentinel.policy_eval",
    factcheck: "claim.verify.live_or_fixture",
    decision: "sentinel.deterministic_gate",
    overmind: "sentinel.trace_persist",
  };
  return ops[id];
}

export function totalDuration(steps: TraceStep[]): number {
  return steps.reduce(
    (sum, s) => sum + (STEP_DURATIONS[s.id] ?? 0),
    0,
  );
}
