"use client";

import Link from "next/link";
import { SentinelLogo } from "@/components/brand/SentinelLogo";
import { shortTraceId } from "@/lib/trace-utils";
import type { AdSlotState, DemoScenario } from "@/lib/types";

interface TraceSidebarProps {
  scenarios: DemoScenario[];
  scenarioId: string;
  onSelect: (id: string) => void;
  adState: AdSlotState;
  isRunning: boolean;
}

function verdictDot(expected: string, adState: AdSlotState) {
  if (adState === "evaluating") {
    return "bg-[var(--review)] animate-pulse";
  }
  if (adState === "approved") return "bg-[var(--approve)]";
  if (adState === "blocked") return "bg-[var(--block)]";
  if (expected === "APPROVE") return "bg-[var(--muted-2)]";
  return "bg-[var(--muted-2)]";
}

export function TraceSidebar({
  scenarios,
  scenarioId,
  onSelect,
  adState,
  isRunning,
}: TraceSidebarProps) {
  return (
    <aside className="flex w-[220px] shrink-0 flex-col border-r border-[var(--border)] bg-[var(--surface)]">
      <div className="border-b border-[var(--border)] px-3 py-3">
        <div className="flex items-center justify-between gap-2">
          <Link href="/">
            <SentinelLogo size="sm" />
          </Link>
          <Link
            href="/"
            className="font-mono text-[10px] text-[var(--muted-2)] hover:text-[var(--foreground)]"
            title="Back to landing"
          >
            ← home
          </Link>
        </div>
        <p className="mt-2 font-mono text-[10px] text-[var(--muted-2)]">
          Overmind traces
        </p>
      </div>

      <div className="px-3 py-2">
        <p className="text-[10px] font-medium uppercase tracking-widest text-[var(--muted-2)]">
          Traces
        </p>
      </div>

      <nav className="flex-1 overflow-y-auto px-2 pb-2">
        <ul className="space-y-0.5">
          {scenarios.map((s) => {
            const active = s.id === scenarioId;
            const traceShort = shortTraceId(s.evaluation.traceId);
            return (
              <li key={s.id}>
                <button
                  type="button"
                  onClick={() => onSelect(s.id)}
                  disabled={isRunning}
                  className={`group w-full rounded-md px-2 py-2 text-left transition ${
                    active
                      ? "bg-[var(--surface-3)] ring-1 ring-[var(--border)]"
                      : "hover:bg-[var(--surface-2)]"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    <span
                      className={`h-1.5 w-1.5 shrink-0 rounded-full ${verdictDot(s.expectedVerdict, active ? adState : "idle")}`}
                    />
                    <span className="truncate font-mono text-[11px] text-[var(--muted)]">
                      {traceShort}
                    </span>
                  </div>
                  <p
                    className={`mt-0.5 truncate pl-3.5 text-xs ${
                      active ? "text-[var(--foreground)]" : "text-[var(--muted)]"
                    }`}
                  >
                    {s.title}
                  </p>
                  <p className="pl-3.5 font-mono text-[10px] text-[var(--muted-2)]">
                    {s.evaluation.latencyMs}ms · demo
                  </p>
                </button>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="border-t border-[var(--border)] p-3">
        <p className="font-mono text-[10px] leading-relaxed text-[var(--muted-2)]">
          / VRF Verification
          <br />
          / LOG Audit trail
        </p>
      </div>
    </aside>
  );
}
