"use client";

import { shortTraceId, spanOperation } from "@/lib/trace-utils";
import type { EvaluationResult, TraceStep, Verdict } from "@/lib/types";

interface VerdictStripProps {
  traceId: string;
  steps: TraceStep[];
  result: EvaluationResult | null;
  isRunning: boolean;
  latencyMs?: number;
}

function VerdictPill({
  label,
  active,
  variant,
}: {
  label: string;
  active: boolean;
  variant: "approve" | "review" | "block";
}) {
  const colors = {
    approve: "text-[var(--approve)] border-[var(--approve)]/40 bg-[var(--approve)]/10",
    review: "text-[var(--review)] border-[var(--review)]/40 bg-[var(--review)]/10",
    block: "text-[var(--block)] border-[var(--block)]/40 bg-[var(--block)]/10",
  };
  const inactive = "text-[var(--muted-2)] border-[var(--border)] bg-transparent";

  return (
    <span
      className={`rounded-full border px-2.5 py-0.5 font-mono text-[10px] font-medium uppercase tracking-wide ${
        active ? colors[variant] : inactive
      }`}
    >
      {label}
    </span>
  );
}

function activeVerdict(
  result: EvaluationResult | null,
  isRunning: boolean,
): Verdict | "REVIEW" | null {
  if (isRunning) return "REVIEW";
  if (!result) return null;
  if (result.verdict === "ESCALATE") return "REVIEW";
  return result.verdict;
}

export function VerdictStrip({
  traceId,
  steps,
  result,
  isRunning,
  latencyMs,
}: VerdictStripProps) {
  const v = activeVerdict(result, isRunning);
  const lastStep = steps.filter((s) => s.status === "running").pop();
  const op = lastStep
    ? spanOperation(lastStep.id)
    : result
      ? "sentinel.evaluate"
      : "—";

  const ms =
    latencyMs ?? result?.latencyMs ?? (isRunning ? "…" : "—");

  return (
    <div className="border-b border-[var(--border)] bg-[var(--bg)] px-4 py-3">
      <p className="font-mono text-[11px] text-[var(--muted)]">
        <span className="text-[var(--foreground)]">
          trace_{shortTraceId(traceId)}
        </span>
        <span className="text-[var(--muted-2)]"> · </span>
        <span>{op}</span>
        <span className="text-[var(--muted-2)]"> · </span>
        <span className="text-[var(--highlight)]">{ms}ms</span>
      </p>

      <div className="mt-3 flex flex-wrap items-center gap-2">
        <VerdictPill
          label="Accept"
          active={v === "APPROVE"}
          variant="approve"
        />
        <VerdictPill
          label="Review"
          active={v === "REVIEW" || v === "ESCALATE"}
          variant="review"
        />
        <VerdictPill label="Decline" active={v === "BLOCK"} variant="block" />
      </div>

      {result?.receipt.headline && !isRunning && (
        <p className="mt-2 text-sm text-[var(--muted)]">
          {result.receipt.headline}
        </p>
      )}
      {isRunning && (
        <p className="mt-2 text-sm text-[var(--review)]">
          Pipeline running — candidate ad held at gateway
        </p>
      )}
    </div>
  );
}
