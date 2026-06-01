"use client";

import { useState } from "react";
import { STEP_DURATIONS, spanOperation, totalDuration } from "@/lib/trace-utils";
import type { TraceStep, TraceStepId } from "@/lib/types";

interface TraceSpanTreeProps {
  steps: TraceStep[];
  selectedId: TraceStepId | null;
  onSelect: (id: TraceStepId) => void;
}

const SPAN_ICONS: Record<TraceStepId, string> = {
  context: "◇",
  thrad: "↗",
  vulnerability: "⚠",
  policy: "⊞",
  factcheck: "⌕",
  decision: "◈",
  overmind: "◎",
};

function TimingBar({ ms, maxMs }: { ms: number; maxMs: number }) {
  const pct = Math.min(100, (ms / maxMs) * 100);
  return (
    <div className="flex w-16 items-center gap-1.5">
      <div className="h-1 flex-1 overflow-hidden rounded-full bg-[var(--border)]">
        <div
          className="h-full rounded-full bg-[var(--highlight)]/60"
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-9 text-right font-mono text-[10px] tabular-nums text-[var(--muted-2)]">
        {ms}ms
      </span>
    </div>
  );
}

export function TraceSpanTree({
  steps,
  selectedId,
  onSelect,
}: TraceSpanTreeProps) {
  const [expanded, setExpanded] = useState(true);
  const maxMs = Math.max(...Object.values(STEP_DURATIONS), 1);
  const rootMs = steps.length ? totalDuration(steps) : 0;

  if (steps.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <p className="font-mono text-xs text-[var(--muted-2)]">
          No observations yet
        </p>
        <p className="mt-2 max-w-xs text-sm text-[var(--muted)]">
          Run evaluation to persist a hierarchical local audit trace
        </p>
      </div>
    );
  }

  const rootStatus = steps.some((s) => s.status === "running")
    ? "running"
    : steps.every((s) => s.status === "done")
      ? "done"
      : "pending";

  return (
    <div className="font-mono text-xs">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left hover:bg-[var(--surface-2)]"
      >
        <span className="w-3 text-[var(--muted-2)]">{expanded ? "▼" : "▶"}</span>
        <span className="text-[var(--highlight)]">⬡</span>
        <span className="flex-1 font-medium text-[var(--foreground)]">
          sentinel.evaluate
        </span>
        <TimingBar ms={rootMs || 1} maxMs={maxMs} />
        {rootStatus === "running" && (
          <span className="text-[10px] text-[var(--review)]">running</span>
        )}
      </button>

      {expanded && (
        <ul className="ml-4 border-l border-[var(--border-subtle)] pl-2">
          {steps.map((step) => {
            const ms = STEP_DURATIONS[step.id];
            const selected = selectedId === step.id;
            const op = spanOperation(step.id);

            return (
              <li key={step.id}>
                <button
                  type="button"
                  onClick={() => onSelect(step.id)}
                  className={`flex w-full items-start gap-2 rounded-md px-2 py-1.5 text-left transition ${
                    selected
                      ? "bg-[var(--accent-dim)] ring-1 ring-[var(--accent)]/30"
                      : "hover:bg-[var(--surface-2)]"
                  }`}
                >
                  <span className="mt-0.5 w-3 shrink-0 text-[var(--muted-2)]">
                    {SPAN_ICONS[step.id]}
                  </span>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span
                        className={`truncate ${
                          step.status === "pending"
                            ? "text-[var(--muted-2)]"
                            : "text-[var(--foreground)]"
                        }`}
                      >
                        {op}
                      </span>
                      {step.status === "running" && (
                        <span className="shrink-0 text-[10px] text-[var(--review)]">
                          ●
                        </span>
                      )}
                      {step.status === "done" && (
                        <span className="shrink-0 text-[10px] text-[var(--approve)]">
                          ✓
                        </span>
                      )}
                    </div>
                    {step.detail && step.status !== "pending" && (
                      <p className="mt-0.5 line-clamp-2 text-[10px] leading-snug text-[var(--muted)]">
                        {step.detail}
                      </p>
                    )}
                  </div>
                  <TimingBar ms={ms} maxMs={maxMs} />
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
