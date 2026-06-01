import type { AnalyzeResponse } from "@/lib/api";
import type {
  CandidateAd,
  DemoScenario,
  EvaluationResult,
  TraceStep,
  Verdict,
} from "@/lib/types";

export function scenarioToAnalyzePayload(scenario: DemoScenario) {
  const conversation = scenario.messages
    .map((m) => `${m.role === "user" ? "User" : "Assistant"}: ${m.content}`)
    .join("\n");
  const ad_creative = `${scenario.candidateAd.headline} — ${scenario.candidateAd.body}`;

  return {
    ad_id: scenario.id,
    conversation,
    ad_creative,
    advertiser: scenario.candidateAd.advertiser ?? null,
  };
}

function severityFromFlags(flags: string[]): "low" | "medium" | "high" {
  if (flags.length === 0) return "low";
  if (flags.length >= 2) return "high";
  return "medium";
}

function headlineFor(verdict: Verdict, reason: string, rule: string): string {
  if (reason) return reason;
  if (verdict === "APPROVE") return "Clean trace — all checks passed";
  if (verdict === "ESCALATE") return "Grey zone — human review required";
  return `Blocked — ${rule.replaceAll("_", " ")}`;
}

function rulesFromResult(ruleFired: string, flags: string[]) {
  const rules: { id: string; label: string }[] = [];
  if (flags.length) {
    rules.push({ id: "contextual_sensitivity", label: "Contextual sensitivity" });
  }
  if (ruleFired === "false_claim") {
    rules.push({ id: "truthfulness", label: "Truthfulness" });
  }
  if (ruleFired === "urgency_manipulation") {
    rules.push({ id: "emotional_integrity", label: "Emotional integrity" });
  }
  if (ruleFired === "passed") {
    rules.push({ id: "truthfulness", label: "Truthfulness" });
    rules.push({ id: "transparency", label: "Transparency" });
  }
  if (rules.length === 0 && ruleFired) {
    rules.push({ id: ruleFired, label: ruleFired.replaceAll("_", " ") });
  }
  return rules;
}

function buildSteps(data: AnalyzeResponse): TraceStep[] {
  const { result } = data;
  const vulnDetail =
    result.vulnerability_flags.length > 0
      ? `HIGH — ${result.vulnerability_flags.join(", ")} (auto-block).`
      : "No vulnerability signals.";

  const failedClaim = result.claims.find((c) => c.verified === false);
  const factDetail = failedClaim
    ? `FAILED — ${failedClaim.text} (actual: ${failedClaim.actual_value ?? "unknown"})`
    : result.claims.length
      ? "Claims verified or non-falsifiable."
      : "No verifiable claims to check.";

  return [
    { id: "context", label: "Context ingested", status: "done" },
    { id: "thrad", label: "Thrad bid received", status: "done" },
    {
      id: "vulnerability",
      label: "Vulnerability signal check",
      status: "done",
      detail: vulnDetail,
    },
    {
      id: "policy",
      label: "Safety policy evaluation",
      status: "done",
      detail: Object.keys(result.scores).length
        ? `Scores: ${Object.entries(result.scores)
            .map(([k, v]) => `${k}=${v.toFixed(1)}`)
            .join(", ")}`
        : undefined,
    },
    {
      id: "factcheck",
      label: "Fact-check (Tavily)",
      status: "done",
      detail: factDetail,
    },
    {
      id: "decision",
      label: "Deterministic gate",
      status: "done",
      detail: `${result.verdict} — ${result.rule_fired}`,
    },
    {
      id: "overmind",
      label: "Overmind trace logged",
      status: "done",
      detail: data.attestation.signature ? "signed attestation" : "unsigned",
    },
  ];
}

export function mapAnalyzeToEvaluation(
  data: AnalyzeResponse,
  candidateAd: CandidateAd,
  latencyMs: number,
): EvaluationResult {
  const { result, trace } = data;
  const excerpt =
    result.vulnerability_flags.length > 0
      ? result.reason.slice(0, 120)
      : undefined;

  return {
    traceId: trace.trace_id,
    verdict: result.verdict,
    ruleFired: result.rule_fired,
    latencyMs,
    candidateAd,
    receipt: {
      headline: headlineFor(result.verdict, result.reason, result.rule_fired),
      rulesTriggered: rulesFromResult(
        result.rule_fired,
        result.vulnerability_flags,
      ),
      vulnerability:
        result.vulnerability_flags.length > 0
          ? {
              signals: result.vulnerability_flags,
              severity: severityFromFlags(result.vulnerability_flags),
            }
          : { signals: [], severity: "low" },
      policySummary: result.reason,
      conversationExcerpt: excerpt,
      claims: result.claims.map((c) => ({
        text: c.text,
        verified: c.verified === true,
        actualValue: c.actual_value ?? undefined,
        sourceUrl: c.source_url ?? undefined,
        snippet: c.actual_value ? `Source: ${c.source_url ?? "offline fixture"}` : undefined,
      })),
    },
    steps: buildSteps(data),
  };
}

/** Compare live API verdict to scenario fixture expectation (hackathon checklist). */
export function verdictMatchesExpected(
  actual: Verdict,
  expected: Verdict,
): boolean {
  return actual === expected;
}
