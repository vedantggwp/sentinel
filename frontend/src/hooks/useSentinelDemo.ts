"use client";

import { useCallback, useState } from "react";
import { DEMO_SCENARIOS, getScenario } from "@/data/scenarios";
import { mergeEvaluationSteps, runDemoPipeline } from "@/lib/demo-engine";
import type {
  AdSlotState,
  DemoScenario,
  EvaluationResult,
  TraceStep,
} from "@/lib/types";

export function useSentinelDemo() {
  const [scenarioId, setScenarioId] = useState(DEMO_SCENARIOS[0].id);
  const [adState, setAdState] = useState<AdSlotState>("idle");
  const [steps, setSteps] = useState<TraceStep[]>([]);
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  const scenario: DemoScenario =
    getScenario(scenarioId) ?? DEMO_SCENARIOS[0];

  const selectScenario = useCallback((id: string) => {
    setScenarioId(id);
    setAdState("idle");
    setSteps([]);
    setResult(null);
    setIsRunning(false);
  }, []);

  const reset = useCallback(() => {
    selectScenario(scenarioId);
  }, [scenarioId, selectScenario]);

  const runEvaluation = useCallback(async () => {
    if (isRunning) return;
    setIsRunning(true);
    setAdState("evaluating");
    setResult(null);
    setSteps([]);

    try {
      const evaluation = await runDemoPipeline(
        scenario.evaluation,
        setSteps,
      );
      setResult(evaluation);
      setSteps(mergeEvaluationSteps(evaluation.steps, evaluation));
      setAdState(
        evaluation.verdict === "APPROVE" ? "approved" : "blocked",
      );
    } finally {
      setIsRunning(false);
    }
  }, [isRunning, scenario.evaluation]);

  return {
    scenarios: DEMO_SCENARIOS,
    scenario,
    scenarioId,
    selectScenario,
    adState,
    steps,
    result,
    isRunning,
    runEvaluation,
    reset,
  };
}
