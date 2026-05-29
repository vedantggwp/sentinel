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

interface UseSentinelDemoOptions {
  initialScenarioId?: string;
  capture?: boolean;
}

function adStateForVerdict(verdict: EvaluationResult["verdict"]): AdSlotState {
  if (verdict === "APPROVE") return "approved";
  return "blocked";
}

export function useSentinelDemo({
  initialScenarioId,
  capture = false,
}: UseSentinelDemoOptions = {}) {
  const initialId = getInitialScenarioId(initialScenarioId);
  const initialScenario = getScenario(initialId) ?? DEMO_SCENARIOS[0];
  const [scenarioId, setScenarioId] = useState(initialId);
  const [adState, setAdState] = useState<AdSlotState>(() =>
    capture ? adStateForVerdict(initialScenario.evaluation.verdict) : "idle",
  );
  const [steps, setSteps] = useState<TraceStep[]>(() =>
    capture ? initialScenario.evaluation.steps : [],
  );
  const [result, setResult] = useState<EvaluationResult | null>(() =>
    capture ? initialScenario.evaluation : null,
  );
  const [isRunning, setIsRunning] = useState(false);
  const [apiMode, setApiMode] = useState<ApiMode>("offline");
  const [apiHint, setApiHint] = useState<string | null>(null);
  const [mismatch, setMismatch] = useState<string | null>(null);

  const scenario: DemoScenario =
    getScenario(scenarioId) ?? DEMO_SCENARIOS[0];

  const refreshApiStatus = useCallback(async () => {
    if (capture) return false;
    const ok = await checkHealth();
    setApiMode(ok ? "live" : "offline");
    setApiHint(
      ok
        ? null
        : "Backend offline — using demo fixtures. Start: uvicorn sentinel.main:app --port 8000",
    );
    return ok;
  }, [capture]);

  useEffect(() => {
    if (capture) return;
    const id = window.setTimeout(() => {
      void refreshApiStatus();
    }, 0);
    return () => window.clearTimeout(id);
  }, [capture, refreshApiStatus]);

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
    const live = await checkHealth();
    setApiMode(live ? "live" : "offline");

    try {
      if (live) {
        setApiHint(null);
        const payload = scenarioToAnalyzePayload(scenario);
        const data = await analyzeAd(payload);
        const evaluation = mapAnalyzeToEvaluation(
          data,
          scenario.candidateAd,
          Math.round(performance.now() - started),
        );
        await runDemoPipeline(evaluation, setSteps);
        setResult(evaluation);

        if (
          !verdictMatchesExpected(
            evaluation.verdict,
            scenario.expectedVerdict,
          )
        ) {
          setMismatch(
            `Expected ${scenario.expectedVerdict}, API returned ${evaluation.verdict} (rule: ${evaluation.ruleFired})`,
          );
        }
        setAdState(adStateForVerdict(evaluation.verdict));
      } else {
        setApiHint(
          "Backend offline — demo fixtures. Start API then click reconnect.",
        );
        const evaluation = await runDemoPipeline(
          scenario.evaluation,
          setSteps,
        );
        setResult(evaluation);
        setAdState(adStateForVerdict(evaluation.verdict));
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "API request failed";
      setApiHint(`API error — fell back to demo fixtures. (${message})`);
      setApiMode("offline");
      const evaluation = await runDemoPipeline(
        scenario.evaluation,
        setSteps,
      );
      setResult(evaluation);
      setAdState(adStateForVerdict(evaluation.verdict));
    } finally {
      setIsRunning(false);
    }
  }, [isRunning, scenario]);

  useEffect(() => {
    if (capture) return;
    const id = window.setTimeout(() => {
      void runEvaluation();
    }, 0);
    return () => window.clearTimeout(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps -- re-run pipeline per scenario
  }, [scenarioId, capture]);

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
    apiHint,
    mismatch,
    refreshApiStatus,
  };
}

function getInitialScenarioId(explicitId?: string) {
  if (explicitId) return getScenario(explicitId)?.id ?? DEMO_SCENARIOS[0].id;
  if (typeof window === "undefined") return DEMO_SCENARIOS[0].id;
  const requested = new URLSearchParams(window.location.search).get("scenario");
  return getScenario(requested ?? "")?.id ?? DEMO_SCENARIOS[0].id;
}
