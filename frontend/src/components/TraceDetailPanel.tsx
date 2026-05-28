"use client";

import { useState } from "react";
import { ReceiptPanel } from "@/components/ReceiptPanel";
import { TraceSpanTree } from "@/components/TraceSpanTree";
import { VerdictStrip } from "@/components/VerdictStrip";
import type { EvaluationResult, TraceStep, TraceStepId } from "@/lib/types";

interface TraceDetailPanelProps {
  traceId: string;
  steps: TraceStep[];
  result: EvaluationResult | null;
  isRunning: boolean;
  apiMode?: "live" | "offline";
  apiHint?: string | null;
  mismatch?: string | null;
  onRun: () => void;
  onReset: () => void;
  onReconnect?: () => void;
}

export function TraceDetailPanel({
  traceId,
  steps,
  result,
  isRunning,
  apiMode = "offline",
  apiHint,
  mismatch,
  onRun,
  onReset,
  onReconnect,
}: TraceDetailPanelProps) {
  const [selectedStepId, setSelectedStepId] = useState<TraceStepId | null>(
    null,
  );

  const selectedStep = steps.find((s) => s.id === selectedStepId);

  return (
    <section className="flex min-h-0 min-w-0 flex-1 flex-col bg-[var(--bg)]">
      <header className="flex shrink-0 items-center justify-between gap-3 border-b border-[var(--border)] px-4 py-2">
        <nav className="flex min-w-0 flex-wrap items-center gap-1.5 font-mono text-[11px] text-[var(--muted)]">
          <span className="text-[var(--muted-2)]">Sentinel</span>
          <span>/</span>
          <span className="text-[var(--foreground)]">Traces</span>
          <span>/</span>
          <span className="truncate text-[var(--accent)]">
            {traceId.replace("ovm_demo_", "").slice(0, 12)}
          </span>
          <span
            className={`rounded px-1.5 py-0.5 text-[10px] ${
              apiMode === "live"
                ? "bg-[var(--approve)]/15 text-[var(--approve)]"
                : "bg-[var(--review)]/15 text-[var(--review)]"
            }`}
          >
            {apiMode === "live" ? "api" : "offline"}
          </span>
        </nav>
        <div className="flex shrink-0 gap-2">
          {apiMode === "offline" && onReconnect && (
            <button
              type="button"
              onClick={onReconnect}
              disabled={isRunning}
              className="rounded-md border border-[var(--border)] px-2.5 py-1 font-mono text-[10px] text-[var(--muted)] hover:text-[var(--foreground)] disabled:opacity-40"
            >
              reconnect
            </button>
          )}
          <button
            type="button"
            onClick={onReset}
            disabled={isRunning}
            className="rounded-md border border-[var(--border)] px-2.5 py-1 font-mono text-[10px] text-[var(--muted)] hover:text-[var(--foreground)] disabled:opacity-40"
          >
            reset
          </button>
          <button
            type="button"
            onClick={onRun}
            disabled={isRunning}
            className="rounded-md bg-[var(--highlight)] px-3 py-1 font-mono text-[10px] font-medium text-[var(--bg)] hover:brightness-110 disabled:opacity-50"
          >
            {isRunning ? "running…" : "run trace"}
          </button>
        </div>
      </header>

      {apiHint && !mismatch && (
        <div className="border-b border-[var(--review)]/30 bg-[var(--review)]/10 px-4 py-2 font-mono text-[10px] text-[var(--review)]">
          {apiHint}
        </div>
      )}

      {mismatch && (
        <div className="border-b border-[var(--block)]/40 bg-[var(--block)]/10 px-4 py-2 font-mono text-[10px] text-[var(--block)]">
          {mismatch}
        </div>
      )}

      <VerdictStrip
        traceId={traceId}
        steps={steps}
        result={result}
        isRunning={isRunning}
      />

      <div className="flex min-h-0 flex-1 overflow-hidden">
        <div className="flex min-w-0 flex-1 flex-col border-r border-[var(--border)]">
          <div className="border-b border-[var(--border)] px-4 py-2">
            <p className="text-[10px] font-medium uppercase tracking-widest text-[var(--muted-2)]">
              Observations
            </p>
          </div>
          <div className="flex-1 overflow-y-auto p-3">
            <TraceSpanTree
              steps={steps}
              selectedId={selectedStepId}
              onSelect={setSelectedStepId}
            />
          </div>

          {selectedStep && selectedStep.detail && (
            <div className="shrink-0 border-t border-[var(--border)] bg-[var(--surface)] p-3">
              <p className="font-mono text-[10px] text-[var(--muted-2)]">
                span output
              </p>
              <pre className="mt-1 overflow-x-auto rounded-md bg-[var(--bg)] p-2 font-mono text-[10px] leading-relaxed text-[var(--muted)]">
                {selectedStep.detail}
              </pre>
            </div>
          )}
        </div>

        <div className="w-[min(100%,380px)] shrink-0 overflow-y-auto bg-[var(--surface)] p-4">
          <p className="mb-3 font-mono text-[10px] uppercase tracking-widest text-[var(--muted-2)]">
            / VRF Verification
          </p>
          {result ? (
            <ReceiptPanel result={result} />
          ) : (
            <div className="rounded-lg border border-dashed border-[var(--border)] p-6 text-center">
              <p className="font-mono text-[11px] text-[var(--muted-2)]">
                awaiting verdict
              </p>
              <p className="mt-2 text-xs text-[var(--muted)]">
                Signed attestation renders after deterministic gate
              </p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
