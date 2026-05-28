import type {
  EvaluationResult,
  TraceStep,
  TraceStepId,
} from "@/lib/types";

const STEP_ORDER: TraceStepId[] = [
  "context",
  "thrad",
  "vulnerability",
  "policy",
  "factcheck",
  "decision",
  "overmind",
];

const STEP_DELAY_MS = 320;

export function initialSteps(): TraceStep[] {
  return STEP_ORDER.map((id) => ({
    id,
    label: stepLabel(id),
    status: "pending",
  }));
}

function stepLabel(id: TraceStepId): string {
  const labels: Record<TraceStepId, string> = {
    context: "Context ingested",
    thrad: "Thrad bid received",
    vulnerability: "Vulnerability signal check",
    policy: "Safety policy evaluation",
    factcheck: "Fact-check (Tavily)",
    decision: "Deterministic gate",
    overmind: "Overmind trace logged",
  };
  return labels[id];
}

export function mergeEvaluationSteps(
  partial: TraceStep[],
  final: EvaluationResult,
): TraceStep[] {
  const byId = new Map(final.steps.map((s) => [s.id, s]));
  return partial.map((p) => {
    const fin = byId.get(p.id);
    return {
      ...p,
      label: fin?.label ?? p.label,
      detail: fin?.detail,
      status: "done" as const,
    };
  });
}

export async function runDemoPipeline(
  final: EvaluationResult,
  onStep: (steps: TraceStep[]) => void,
): Promise<EvaluationResult> {
  let current = initialSteps();
  onStep(current);

  for (let i = 0; i < STEP_ORDER.length; i++) {
    const id = STEP_ORDER[i];
    current = current.map((s) =>
      s.id === id ? { ...s, status: "running" } : s,
    );
    onStep(current);
    await sleep(STEP_DELAY_MS);

    const finalStep = final.steps.find((s) => s.id === id);
    current = current.map((s) =>
      s.id === id
        ? {
            ...s,
            status: "done",
            label: finalStep?.label ?? s.label,
            detail: finalStep?.detail,
          }
        : s,
    );
    onStep(current);
  }

  return final;
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
