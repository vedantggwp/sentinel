import { PolicyChips } from "@/components/PolicyChips";
import type { EvaluationResult } from "@/lib/types";

interface ReceiptPanelProps {
  result: EvaluationResult;
}

export function ReceiptPanel({ result }: ReceiptPanelProps) {
  const { receipt } = result;

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2">
        <span className="font-mono text-[10px] text-[var(--muted-2)]">/ LOG</span>
        <h3 className="text-sm font-medium">Audit trail</h3>
      </div>

      <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-4">
        <p className="font-mono text-[10px] text-[var(--muted-2)]">
          Signed evidence per trace
        </p>
        <p className="mt-2 text-sm leading-relaxed text-[var(--foreground)]">
          {receipt.headline}
        </p>

        {result.ruleFired && (
          <div className="mt-3 rounded-md bg-[var(--bg)] px-3 py-2 font-mono text-[11px] text-[var(--muted)]">
            <span className="text-[var(--muted-2)]">rule_fired </span>
            {result.ruleFired}
          </div>
        )}

        {receipt.policySummary && (
          <p className="mt-3 text-xs leading-relaxed text-[var(--muted)]">
            {receipt.policySummary}
          </p>
        )}
      </div>

      {receipt.conversationExcerpt && (
        <div>
          <span className="font-mono text-[10px] text-[var(--muted-2)]">
            / CTX
          </span>
          <blockquote className="mt-1 rounded-lg border-l-2 border-[var(--review)] bg-[var(--surface)] py-2 pl-3 text-xs italic text-[var(--muted)]">
            {receipt.conversationExcerpt}
          </blockquote>
        </div>
      )}

      {receipt.vulnerability && receipt.vulnerability.signals.length > 0 && (
        <div>
          <span className="font-mono text-[10px] text-[var(--muted-2)]">
            / VUL
          </span>
          <p className="mt-1 text-[10px] text-[var(--muted)]">
            severity · {receipt.vulnerability.severity}
          </p>
          <ul className="mt-2 flex flex-wrap gap-1">
            {receipt.vulnerability.signals.map((s) => (
              <li
                key={s}
                className="rounded border border-[var(--review)]/30 bg-[var(--review)]/5 px-2 py-0.5 font-mono text-[10px] text-[var(--review)]"
              >
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {receipt.claims && receipt.claims.length > 0 && (
        <div>
          <span className="font-mono text-[10px] text-[var(--muted-2)]">
            / TAV
          </span>
          <p className="mt-0.5 text-[10px] text-[var(--muted)]">
            Tavily fact-check
          </p>
          <div className="mt-2 space-y-2">
            {receipt.claims.map((claim) => (
              <div
                key={claim.text}
                className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3"
              >
                <div className="flex justify-between gap-2">
                  <p className="text-xs font-medium">{claim.text}</p>
                  <span
                    className={`shrink-0 font-mono text-[10px] font-bold ${
                      claim.verified
                        ? "text-[var(--approve)]"
                        : "text-[var(--block)]"
                    }`}
                  >
                    {claim.verified ? "verified" : "failed"}
                  </span>
                </div>
                {claim.actualValue && (
                  <p className="mt-1 text-xs text-[var(--block)]">
                    {claim.actualValue}
                  </p>
                )}
                {claim.snippet && (
                  <p className="mt-2 text-[11px] text-[var(--muted)]">
                    {claim.snippet}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div>
        <span className="font-mono text-[10px] text-[var(--muted-2)]">/ POL</span>
        <div className="mt-2">
          <PolicyChips rules={receipt.rulesTriggered} />
        </div>
      </div>

      <footer className="rounded-lg border border-dashed border-[var(--border)] bg-[var(--bg)] px-3 py-2 font-mono text-[10px] text-[var(--muted-2)]">
        <div className="flex flex-wrap gap-x-4 gap-y-1">
          <span>trace_id={result.traceId}</span>
          <span>latency={result.latencyMs}ms</span>
          <span>sig=ed25519</span>
          <span className="text-[var(--highlight)]">overmind.synced</span>
        </div>
      </footer>
    </div>
  );
}
