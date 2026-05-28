"use client";

import { useCallback, useEffect, useState } from "react";
import { DEMO_SCENARIOS, getScenario } from "@/data/scenarios";
import { analyzeAd, checkHealth } from "@/lib/api";
import { runDemoPipeline } from "@/lib/demo-engine";
import {
  mapAnalyzeToEvaluation,
  scenarioToAnalyzePayload,
  verdictMatchesExpected,
} from "@/lib/map-analyze";
import type {
  AdSlotState,
  DemoScenario,
  EvaluationResult,
  TraceStep,
} from "@/lib/types";

export type ApiMode = "live" | "offline";

export function useSentinelDemo() {
  const [scenarioId, setScenarioId] = useState(DEMO_SCENARIOS[0].id);
  const [adState, setAdState] = useState<AdSlotState>("idle");
  const [steps, setSteps] = useState<TraceStep[]>([]);
  const [result, setResult] = useState<EvaluationResult | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [apiMode, setApiMode] = useState<ApiMode>("offline");
  const [mismatch, setMismatch] = useState<string | null>(null);

  const scenario: DemoScenario =
    getScenario(scenarioId) ?? DEMO_SCENARIOS[0];

  useEffect(() => {
    checkHealth().then((ok) => setApiMode(ok ? "live" : "offline"));
  }, []);

  const selectScenario = useCallback((id: string) => {
    setScenarioId(id);
    setAdState("idle");
    setSteps([]);
    setResult(null);
    setMismatch(null);
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
    setMismatch(null);

    const started = performance.now();

    try {
      if (apiMode === "live") {
        const payload = scenarioToAnalyzePayload(scenario);
        const [data] = await Promise.all([
          analyzeAd(payload),
          runDemoPipeline(scenario.evaluation, setSteps),
        ]);
        const evaluation = mapAnalyzeToEvaluation(
          data,
          scenario.candidateAd,
          Math.round(performance.now() - started),
        );
        setResult(evaluation);
        setSteps(evaluation.steps);

        if (!verdictMatchesExpected(evaluation.verdict, scenario.expectedVerdict)) {
          setMismatch(
            `Expected ${scenario.expectedVerdict}, API returned ${evaluation.verdict} (rule: ${evaluation.ruleFired})`,
          );
        }

        setAdState(
          evaluation.verdict === "APPROVE"
            ? "approved"
            : "blocked",
        );
      } else {
        const evaluation = await runDemoPipeline(
          scenario.evaluation,
          setSteps,
        );
        setResult(evaluation);
        setAdState(
          evaluation.verdict === "APPROVE" ? "approved" : "blocked",
        );
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "API request failed";
      setMismatch(message);
      setApiMode("offline");
      const evaluation = await runDemoPipeline(
        scenario.evaluation,
        setSteps,
      );
      setResult(evaluation);
      setAdState(
        evaluation.verdict === "APPROVE" ? "approved" : "blocked",
      );
    } finally {
      setIsRunning(false);
    }
  }, [apiMode, isRunning, scenario]);

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
    apiMode,
    mismatch,
  };
}
