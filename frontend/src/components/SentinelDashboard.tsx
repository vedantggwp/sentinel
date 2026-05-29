"use client";

import { ConversationPanel } from "@/components/ConversationPanel";
import { TraceDetailPanel } from "@/components/TraceDetailPanel";
import { TraceSidebar } from "@/components/TraceSidebar";
import { useSentinelDemo } from "@/hooks/useSentinelDemo";

interface SentinelDashboardProps {
  initialScenarioId?: string;
  capture?: boolean;
}

export function SentinelDashboard({
  initialScenarioId,
  capture = false,
}: SentinelDashboardProps) {
  const {
    scenarios,
    scenario,
    scenarioId,
    selectScenario,
    adState,
    steps,
    result,
    isRunning,
    runEvaluation,
    reset,
    apiMode,
    apiHint,
    mismatch,
    refreshApiStatus,
  } = useSentinelDemo({ initialScenarioId, capture });

  return (
    <div className="flex h-full min-h-0 bg-[var(--bg)]">
      <TraceSidebar
        scenarios={scenarios}
        scenarioId={scenarioId}
        onSelect={selectScenario}
        adState={adState}
        isRunning={isRunning}
      />

      <div className="flex min-h-0 min-w-0 flex-1">
        <div className="flex w-[min(100%,340px)] shrink-0 flex-col border-r border-[var(--border)]">
          <ConversationPanel
            scenario={scenario}
            adState={adState}
          />
        </div>

        <TraceDetailPanel
          traceId={scenario.evaluation.traceId}
          steps={steps}
          result={result}
          isRunning={isRunning}
          apiMode={apiMode}
          apiHint={apiHint}
          mismatch={mismatch}
          onRun={runEvaluation}
          onReset={reset}
          onReconnect={refreshApiStatus}
        />
      </div>
    </div>
  );
}
