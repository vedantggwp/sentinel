import type { DemoScenario } from "@/lib/types";

function steps(
  overrides: Partial<
    Record<
      import("@/lib/types").TraceStepId,
      { status?: import("@/lib/types").StepStatus; detail?: string }
    >
  >,
): import("@/lib/types").TraceStep[] {
  const base: import("@/lib/types").TraceStep[] = [
    { id: "context", label: "Context ingested", status: "done" },
    { id: "thrad", label: "Thrad bid received", status: "done" },
    {
      id: "vulnerability",
      label: "Vulnerability signal check",
      status: "done",
    },
    { id: "policy", label: "Safety policy evaluation", status: "done" },
    { id: "factcheck", label: "Fact-check (Tavily)", status: "done" },
    { id: "decision", label: "Deterministic gate", status: "done" },
    { id: "overmind", label: "Overmind trace logged", status: "done" },
  ];
  return base.map((s) => ({
    ...s,
    ...overrides[s.id],
  }));
}

export const DEMO_SCENARIOS: DemoScenario[] = [
  {
    id: "laptop_clean",
    title: "Approved — laptop",
    description: "Neutral shopping intent; clean trace.",
    messages: [
      {
        id: "1",
        role: "user",
        content: "What laptop should I buy for coding under £1000?",
      },
      {
        id: "2",
        role: "assistant",
        content:
          "For coding, prioritize 16GB RAM, a solid keyboard, and battery life. The Acme Pro 14 is a strong value pick in that range.",
      },
    ],
    candidateAd: {
      headline: "Acme Pro 14",
      body: "Starting at $999. Free next-day delivery.",
      cta: "Shop now",
      advertiser: "Acme",
    },
    expectedVerdict: "APPROVE",
    evaluation: {
      traceId: "ovm_demo_laptop_8f2a",
      verdict: "APPROVE",
      ruleFired: "passed",
      latencyMs: 1240,
      candidateAd: {
        headline: "Acme Pro 14",
        body: "Starting at $999. Free next-day delivery.",
        cta: "Shop now",
        advertiser: "Acme",
      },
      receipt: {
        headline: "Clean trace — all checks passed",
        rulesTriggered: [
          { id: "contextual_sensitivity", label: "Contextual sensitivity" },
          { id: "truthfulness", label: "Truthfulness" },
          { id: "transparency", label: "Transparency (Sponsored label)" },
        ],
        vulnerability: { signals: [], severity: "low" },
        policySummary:
          "No vulnerability signals. Claims are generic pricing copy with no disputed facts. Urgency and tone-mimicry scores within policy.",
        claims: [
          {
            text: "Starting at $999",
            verified: true,
            snippet: "No conflicting public pricing found for Acme Pro 14.",
          },
        ],
      },
      steps: steps({
        vulnerability: {
          detail: "No mental health, financial distress, or bereavement signals.",
        },
        factcheck: { detail: "No verifiable false claims detected." },
        decision: { detail: "APPROVE — deterministic gate passed." },
      }),
    },
  },
  {
    id: "anxiety_block",
    title: "Blocked — mental health",
    description: "Vulnerable context blocks predatory lending ad.",
    messages: [
      {
        id: "1",
        role: "user",
        content:
          "I've been really anxious about money lately and can't sleep.",
      },
      {
        id: "2",
        role: "assistant",
        content:
          "That sounds really hard. If you're in crisis, consider speaking with a trusted person or a professional support line.",
      },
    ],
    candidateAd: {
      headline: "QuickCash payday loans",
      body: "Get $500 now — no credit check!",
      cta: "Apply instantly",
      advertiser: "QuickCash",
    },
    expectedVerdict: "BLOCK",
    evaluation: {
      traceId: "ovm_demo_anxiety_c41b",
      verdict: "BLOCK",
      ruleFired: "vulnerability_auto_block",
      latencyMs: 890,
      candidateAd: {
        headline: "QuickCash payday loans",
        body: "Get $500 now — no credit check!",
        cta: "Apply instantly",
        advertiser: "QuickCash",
      },
      receipt: {
        headline: "Mental health & financial distress context detected",
        rulesTriggered: [
          {
            id: "contextual_sensitivity",
            label: "Contextual sensitivity",
          },
          { id: "emotional_integrity", label: "Emotional integrity" },
        ],
        vulnerability: {
          signals: [
            "financial_anxiety",
            "sleep_disturbance",
            "mental_health_context",
          ],
          severity: "high",
        },
        policySummary:
          "Hard rule: vulnerability gate auto-blocks all ads when financial distress or mental-health context is detected. Predatory lending creative would exploit vulnerable state.",
        conversationExcerpt:
          "…really anxious about money lately and can't sleep…",
      },
      steps: steps({
        vulnerability: {
          detail:
            "HIGH — financial_anxiety, mental_health_context (auto-block).",
        },
        factcheck: { detail: "Skipped — context gate already failed." },
        decision: {
          detail: "BLOCK — vulnerability_auto_block (deterministic).",
        },
      }),
    },
  },
  {
    id: "false_rating",
    title: "Blocked — false claim",
    description: "Tavily finds rating mismatch; truthfulness rule fires.",
    messages: [
      {
        id: "1",
        role: "user",
        content: "Recommend good noise-cancelling headphones.",
      },
      {
        id: "2",
        role: "assistant",
        content:
          "Look for ANC quality, comfort, and codec support. Popular options include Sony WH-1000XM5 and Bose QC Ultra.",
      },
    ],
    candidateAd: {
      headline: "SonicMax ANC Pro",
      body: "#1 rated — 4.9 stars on Amazon!",
      cta: "Buy SonicMax",
      advertiser: "SonicMax",
    },
    expectedVerdict: "BLOCK",
    evaluation: {
      traceId: "ovm_demo_rating_7d19",
      verdict: "BLOCK",
      ruleFired: "false_claim",
      latencyMs: 2100,
      candidateAd: {
        headline: "SonicMax ANC Pro",
        body: "#1 rated — 4.9 stars on Amazon!",
        cta: "Buy SonicMax",
        advertiser: "SonicMax",
      },
      receipt: {
        headline: "False product claim — rating does not verify",
        rulesTriggered: [
          { id: "truthfulness", label: "Truthfulness" },
          { id: "authenticity", label: "Authenticity" },
        ],
        vulnerability: { signals: [], severity: "low" },
        policySummary:
          "Claim truthfulness score below threshold. Advertised 4.9★ conflicts with live marketplace data.",
        claims: [
          {
            text: "4.9 stars on Amazon",
            verified: false,
            actualValue: "~3.2 stars (Amazon listing aggregate)",
            sourceTitle: "Amazon — SonicMax ANC Pro",
            sourceUrl: "https://amazon.example/sonicmax",
            snippet:
              "Current aggregate rating 3.2/5 from 1,847 reviews (fetched via Tavily).",
          },
        ],
      },
      steps: steps({
        factcheck: {
          detail: "FAILED — advertised 4.9★ vs ~3.2★ on Amazon (Tavily).",
        },
        decision: {
          detail: "BLOCK — false_claim.",
        },
      }),
    },
  },
  {
    id: "urgency",
    title: "Blocked — manufactured urgency",
    description: "High-pressure CTA violates emotional integrity policy.",
    messages: [
      {
        id: "1",
        role: "user",
        content: "I'm comparing travel insurance options for a trip to Japan.",
      },
      {
        id: "2",
        role: "assistant",
        content:
          "Compare medical limits, cancellation cover, and gadget protection. Annual multi-trip policies can be cheaper if you travel often.",
      },
    ],
    candidateAd: {
      headline: "TripSure Insurance",
      body: "LAST CHANCE — only 2 policies left at this price!!!",
      cta: "Lock in now",
      advertiser: "TripSure",
    },
    expectedVerdict: "BLOCK",
    evaluation: {
      traceId: "ovm_demo_urgency_3e88",
      verdict: "BLOCK",
      ruleFired: "urgency_manipulation",
      latencyMs: 1050,
      candidateAd: {
        headline: "TripSure Insurance",
        body: "LAST CHANCE — only 2 policies left at this price!!!",
        cta: "Lock in now",
        advertiser: "TripSure",
      },
      receipt: {
        headline: "Manufactured urgency detected",
        rulesTriggered: [
          { id: "emotional_integrity", label: "Emotional integrity" },
          { id: "authenticity", label: "Authenticity" },
        ],
        vulnerability: { signals: [], severity: "low" },
        policySummary:
          "Scarcity language ('LAST CHANCE', 'only 2 left') scores above urgency threshold without inventory evidence. Blocked per Thrad emotional-integrity standard.",
      },
      steps: steps({
        policy: {
          detail:
            "Urgency score 0.94 — manufactured scarcity patterns matched.",
        },
        factcheck: { detail: "No factual claims to verify." },
        decision: { detail: "BLOCK — urgency_manipulation." },
      }),
    },
  },
];

export function getScenario(id: string): DemoScenario | undefined {
  return DEMO_SCENARIOS.find((s) => s.id === id);
}
