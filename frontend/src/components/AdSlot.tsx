import type { AdSlotState, CandidateAd } from "@/lib/types";

interface AdSlotProps {
  state: AdSlotState;
  ad: CandidateAd;
}

export function AdSlot({ state, ad }: AdSlotProps) {
  if (state === "idle") {
    return (
      <div className="rounded-lg border border-[var(--border)] bg-[var(--bg)] px-3 py-5">
        <p className="font-mono text-[10px] text-[var(--muted-2)]">
          pending · thrad.bid
        </p>
        <div className="mt-3 opacity-40">
          <p className="text-sm font-medium text-[var(--foreground)]">
            {ad.headline}
          </p>
          <p className="mt-0.5 text-xs text-[var(--muted)]">{ad.body}</p>
        </div>
        <p className="mt-3 text-[11px] text-[var(--muted-2)]">
          Run trace to intercept
        </p>
      </div>
    );
  }

  if (state === "evaluating") {
    return (
      <div className="rounded-lg border border-[var(--review)]/40 bg-[var(--review)]/5 px-3 py-4">
        <p className="flex items-center gap-2 font-mono text-[10px] text-[var(--review)]">
          <span className="inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-[var(--review)]" />
          held · sentinel.gateway
        </p>
        <div className="mt-3 rounded-md border border-[var(--border)] bg-[var(--bg)] p-3">
          <p className="text-sm font-medium">{ad.headline}</p>
          <p className="mt-0.5 text-xs text-[var(--muted)]">{ad.body}</p>
        </div>
      </div>
    );
  }

  if (state === "approved") {
    return (
      <div className="rounded-lg border border-[var(--approve)]/30 bg-[var(--approve)]/5 p-3">
        <div className="flex items-center justify-between">
          <span className="font-mono text-[10px] text-[var(--approve)]">
            sponsored · accept
          </span>
        </div>
        <p className="mt-2 text-sm font-medium">{ad.headline}</p>
        <p className="mt-0.5 text-xs text-[var(--muted)]">{ad.body}</p>
        {ad.cta && (
          <span className="mt-2 inline-block rounded bg-[var(--approve)] px-2 py-1 text-[10px] font-medium text-black">
            {ad.cta}
          </span>
        )}
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-[var(--block)]/30 bg-[var(--block)]/5 p-3">
      <p className="font-mono text-[10px] text-[var(--block)]">
        withheld · decline
      </p>
      <div className="mt-2 rounded-md border border-[var(--border)] bg-[var(--bg)] p-3 opacity-40 line-through">
        <p className="text-sm font-medium">{ad.headline}</p>
        <p className="mt-0.5 text-xs">{ad.body}</p>
      </div>
      <p className="mt-2 text-[11px] text-[var(--muted)]">
        See verification panel →
      </p>
    </div>
  );
}
