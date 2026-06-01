import Link from "next/link";
import { SentinelLogo } from "@/components/brand/SentinelLogo";
import { Kbd } from "@/components/landing/Kbd";
import { LandingNav } from "@/components/landing/LandingNav";
import { ModelLogoCloud } from "@/components/landing/ModelLogoCloud";

const CHANGELOG = [
  { title: "Fixture claim check", when: "today" },
  { title: "Deterministic gate v2", when: "2d ago" },
  { title: "Optional trace export", when: "5d ago" },
  { title: "Thrad bid adapter", when: "1w ago" },
];

const TOC = [
  { id: "hero", label: "Overview" },
  { id: "pipeline", label: "Pipeline" },
  { id: "primitives", label: "Primitives" },
  { id: "demo", label: "Demo scenarios" },
  { id: "cta", label: "Get started" },
];

const INTEGRATIONS = ["Thrad", "Tavily roadmap", "Overmind optional", "FastAPI", "MCP"];

const PRIMITIVES = [
  { code: "CTX", title: "Context gate", desc: "Vulnerability signals before any ad is considered." },
  { code: "EVD", title: "Claim verify", desc: "Offline fixture-backed evidence today; live Tavily is on the public-v1 roadmap." },
  { code: "GTE", title: "Deterministic gate", desc: "LLMs score. Code decides. Always auditable." },
  { code: "LOG", title: "Audit trace", desc: "Every verdict is persisted locally; Overmind export is optional when configured." },
];

function TracePreviewCard() {
  return (
    <div className="mt-10 rounded-lg border border-[var(--border)] bg-[var(--surface)] p-4 font-mono text-[11px] shadow-xl">
      <p className="text-[var(--muted)]">
        <span className="text-[var(--foreground)]">trace_a8f2c91b</span>
        <span className="text-[var(--muted-2)]"> · </span>
        sentinel.evaluate
        <span className="text-[var(--muted-2)]"> · </span>
        <span className="text-[var(--accent)]">1.24s</span>
      </p>
      <div className="mt-3 flex gap-2">
        <span className="rounded border border-[var(--approve)]/30 bg-[var(--approve)]/10 px-2 py-0.5 text-[10px] text-[var(--approve)]">
          accept
        </span>
        <span className="rounded border border-[var(--border)] px-2 py-0.5 text-[10px] text-[var(--muted-2)]">
          review
        </span>
        <span className="rounded border border-[var(--border)] px-2 py-0.5 text-[10px] text-[var(--muted-2)]">
          decline
        </span>
      </div>
      <ul className="mt-4 space-y-1.5 border-l border-[var(--border)] pl-3 text-[10px]">
        <li className="flex justify-between text-[var(--muted)]">
          <span>sentinel.context_gate</span>
          <span>18ms</span>
        </li>
        <li className="flex justify-between text-[var(--muted)]">
          <span>claim.verify.offline</span>
          <span className="text-[var(--highlight)]">890ms</span>
        </li>
        <li className="flex justify-between text-[var(--approve)]">
          <span>sentinel.deterministic_gate</span>
          <span>12ms ✓</span>
        </li>
      </ul>
    </div>
  );
}

export function LandingPage() {
  return (
    <div className="min-h-screen bg-grid">
      <LandingNav />

      <div className="mx-auto max-w-[1400px] px-4 lg:px-6">
        <div className="grid gap-8 lg:grid-cols-[200px_minmax(0,1fr)_180px] lg:gap-10 xl:grid-cols-[220px_minmax(0,1fr)_200px]">
          {/* Left rail — Langfuse changelog / stats */}
          <aside className="hidden pt-10 lg:block">
            <div className="sticky top-24 space-y-8 text-sm">
              <div>
                <p className="font-mono text-[10px] uppercase tracking-wider text-[var(--muted-2)]">
                  Open source
                </p>
                <p className="mt-2 text-2xl font-semibold tabular-nums">95</p>
                <p className="mt-1 text-xs text-[var(--muted)]">
                  pytest cases · MIT
                </p>
              </div>

              <div>
                <p className="mb-3 font-mono text-[10px] uppercase tracking-wider text-[var(--muted-2)]">
                  Changelog
                </p>
                <ul className="space-y-2">
                  {CHANGELOG.map((item) => (
                    <li key={item.title}>
                      <p className="text-xs leading-snug text-[var(--foreground)]">
                        {item.title}
                      </p>
                      <p className="font-mono text-[10px] text-[var(--muted-2)]">
                        {item.when}
                      </p>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <p className="mb-3 font-mono text-[10px] uppercase tracking-wider text-[var(--muted-2)]">
                  Integrations
                </p>
                <ul className="space-y-1.5 text-xs text-[var(--muted)]">
                  {INTEGRATIONS.map((name) => (
                    <li key={name}>{name}</li>
                  ))}
                </ul>
              </div>
            </div>
          </aside>

          {/* Center — Hero */}
          <main className="min-w-0 border-x border-[var(--border)] px-0 py-10 sm:px-8 lg:py-14">
            <section id="hero">
              <p className="text-center text-xs text-[var(--muted)] sm:text-sm">
                Built for conversational ad safety ·{" "}
                <span className="text-[var(--foreground)]">
                  Thrad bid-request → Sentinel → user
                </span>
              </p>

              <h1 className="mx-auto mt-8 max-w-3xl text-center text-4xl font-semibold leading-[1.08] tracking-[-0.03em] sm:text-5xl lg:text-[3.5rem]">
                Open source{" "}
                <span className="text-highlight-marker">commerce safety</span>{" "}
                for{" "}
                <span className="text-highlight-marker">AI conversations</span>
              </h1>

              <p className="mx-auto mt-6 max-w-xl text-center text-base leading-relaxed text-[var(--muted)]">
                Debug unsafe ads in minutes. Evaluate Thrad-style candidates,
                check claims against fixture-backed evidence, and ship a signed
                receipt before anything reaches the user. Any model,
                deterministic gate.
              </p>

              <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
                <Link
                  href="/demo"
                  className="inline-flex items-center rounded-md bg-[var(--foreground)] px-5 py-2.5 text-sm font-medium text-[var(--bg)] hover:opacity-90"
                >
                  Start demo
                  <Kbd>S</Kbd>
                </Link>
                <a
                  href="#pipeline"
                  className="inline-flex items-center rounded-md border border-[var(--border)] bg-[var(--surface)] px-5 py-2.5 text-sm text-[var(--foreground)] hover:bg-[var(--surface-2)]"
                >
                  Documentation
                  <Kbd>O</Kbd>
                </a>
              </div>

              <TracePreviewCard />

              <ModelLogoCloud />
            </section>

            <section id="pipeline" className="mt-24 scroll-mt-24">
              <p className="font-mono text-[10px] uppercase tracking-wider text-[var(--muted-2)]">
                / Pipeline
              </p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight">
                One connected workflow
              </h2>
              <p className="mt-3 max-w-lg text-sm leading-relaxed text-[var(--muted)]">
                Context gate, claim extraction, fixture-backed verification,
                safety judge, deterministic gate, signed attestation, local
                audit trace with optional Overmind export.
              </p>
              <ol className="mt-8 space-y-4">
                {[
                  "User converses in AI chat",
                  "Thrad returns candidate ad",
                  "Sentinel evaluates and traces",
                  "Verdict + receipt before render",
                ].map((step, i) => (
                  <li
                    key={step}
                    className="flex gap-4 border-b border-[var(--border-subtle)] pb-4 last:border-0"
                  >
                    <span className="font-mono text-xs text-[var(--accent)]">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <span className="text-sm">{step}</span>
                  </li>
                ))}
              </ol>
            </section>

            <section id="primitives" className="mt-24 scroll-mt-24">
              <p className="font-mono text-[10px] uppercase tracking-wider text-[var(--muted-2)]">
                / Primitives
              </p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight">
                Verification stack
              </h2>
              <div className="mt-8 divide-y divide-[var(--border)] border-y border-[var(--border)]">
                {PRIMITIVES.map((p) => (
                  <div
                    key={p.code}
                    className="grid gap-2 py-5 sm:grid-cols-[4rem_1fr]"
                  >
                    <span className="font-mono text-xs text-[var(--highlight)]">
                      /{p.code}
                    </span>
                    <div>
                      <p className="text-sm font-medium">{p.title}</p>
                      <p className="mt-1 text-sm text-[var(--muted)]">
                        {p.desc}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </section>

            <section id="demo" className="mt-24 scroll-mt-24">
              <p className="font-mono text-[10px] uppercase tracking-wider text-[var(--muted-2)]">
                / Demo
              </p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight">
                Four judge scenarios
              </h2>
              <ul className="mt-6 space-y-2">
                {[
                  ["Approved laptop", "accept"],
                  ["Mental health block", "decline"],
                  ["False 4.9★ rating", "decline"],
                  ["Manufactured urgency", "decline"],
                ].map(([label, v]) => (
                  <li
                    key={label}
                    className="flex justify-between border-b border-[var(--border-subtle)] py-3 text-sm"
                  >
                    <span>{label}</span>
                    <span
                      className={`font-mono text-[10px] uppercase ${
                        v === "accept"
                          ? "text-[var(--approve)]"
                          : "text-[var(--block)]"
                      }`}
                    >
                      {v}
                    </span>
                  </li>
                ))}
              </ul>
            </section>

            <section id="cta" className="mt-24 scroll-mt-24 pb-24">
              <div className="rounded-lg border border-[var(--border)] bg-[var(--surface)] p-8 text-center">
                <SentinelLogo size="lg" className="justify-center" />
                <p className="mx-auto mt-4 max-w-md text-sm text-[var(--muted)]">
                  Enter the trace console: local pipeline, accept / review /
                  decline, signed audit trail.
                </p>
                <Link
                  href="/demo"
                  className="mt-6 inline-flex items-center rounded-md bg-[var(--accent)] px-6 py-2.5 text-sm font-medium text-[var(--bg)] hover:brightness-110"
                >
                  Launch trace console
                  <Kbd>L</Kbd>
                </Link>
              </div>
            </section>
          </main>

          {/* Right rail — On this page */}
          <aside className="hidden pt-10 lg:block">
            <div className="sticky top-24">
              <p className="font-mono text-[10px] uppercase tracking-wider text-[var(--muted-2)]">
                On this page
              </p>
              <ul className="mt-4 space-y-2 text-sm text-[var(--muted)]">
                {TOC.map((item) => (
                  <li key={item.id}>
                    <a
                      href={`#${item.id}`}
                      className="hover:text-[var(--foreground)]"
                    >
                      {item.label}
                    </a>
                  </li>
                ))}
              </ul>

              <div className="mt-10 rounded-lg border border-[var(--border)] bg-[var(--surface)] p-3">
                <p className="text-xs font-medium">Hackathon build</p>
                <p className="mt-1 text-[11px] leading-relaxed text-[var(--muted)]">
                  DoubleVerify for conversational AI. Questions? Open the
                  demo and run a trace.
                </p>
              </div>
            </div>
          </aside>
        </div>
      </div>

      {/* Floating prompt bar — Langfuse-style */}
      <div className="pointer-events-none fixed inset-x-0 bottom-6 flex justify-center px-4">
        <div className="pointer-events-auto flex w-full max-w-md items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface)]/95 px-4 py-2.5 shadow-2xl backdrop-blur-md">
          <span className="text-sm text-[var(--muted)]">
            Run a safety evaluation
          </span>
          <span className="flex-1" />
          <Link
            href="/demo"
            className="flex h-8 w-8 items-center justify-center rounded-full bg-[var(--foreground)] text-[var(--bg)]"
            aria-label="Open demo"
          >
            →
          </Link>
          <Kbd>A</Kbd>
        </div>
      </div>
    </div>
  );
}
