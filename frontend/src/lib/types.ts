/** Mirrors sentinel/contracts.py — keep in sync with backend teammate. */

export type Verdict = "APPROVE" | "BLOCK" | "ESCALATE";

export type TraceStepId =
  | "context"
  | "thrad"
  | "vulnerability"
  | "policy"
  | "factcheck"
  | "decision"
  | "overmind";

export type StepStatus = "pending" | "running" | "done";

export interface TraceStep {
  id: TraceStepId;
  label: string;
  status: StepStatus;
  detail?: string;
}

export interface ClaimEvidence {
  text: string;
  verified: boolean;
  actualValue?: string;
  sourceTitle?: string;
  sourceUrl?: string;
  snippet?: string;
}

export interface EvaluationReceipt {
  headline: string;
  rulesTriggered: { id: string; label: string }[];
  vulnerability?: {
    signals: string[];
    severity: "low" | "medium" | "high";
  };
  policySummary?: string;
  claims?: ClaimEvidence[];
  conversationExcerpt?: string;
}

export interface CandidateAd {
  headline: string;
  body: string;
  cta?: string;
  advertiser?: string;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export interface EvaluationResult {
  traceId: string;
  verdict: Verdict;
  receipt: EvaluationReceipt;
  candidateAd: CandidateAd;
  steps: TraceStep[];
  latencyMs: number;
  ruleFired?: string;
}

export interface DemoScenario {
  id: string;
  title: string;
  description: string;
  messages: ChatMessage[];
  candidateAd: CandidateAd;
  expectedVerdict: Verdict;
  evaluation: EvaluationResult;
}

export type AdSlotState =
  | "idle"
  | "evaluating"
  | "approved"
  | "blocked";
