import Link from "next/link";
import { SentinelLogo } from "@/components/brand/SentinelLogo";
import { Kbd } from "@/components/landing/Kbd";

export function LandingNav() {
  return (
    <>
      <div className="border-b border-[var(--border)] bg-[var(--surface)] px-4 py-1.5 text-center font-mono text-[10px] text-[var(--muted)]">
        <span className="text-[var(--highlight)]">Cursor × Thrad</span>
        <span className="mx-2 text-[var(--border)]">|</span>
        Agentic commerce safety layer
        <span className="mx-2 text-[var(--border)]">|</span>
        <Link href="/demo" className="text-[var(--foreground)] hover:underline">
          Live demo
        </Link>
      </div>

      <header className="sticky top-0 z-50 border-b border-[var(--border)] bg-[var(--bg)]/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-[1400px] items-center justify-between gap-4 px-4 py-3 lg:px-6">
          <Link href="/">
            <SentinelLogo size="md" />
          </Link>

          <nav className="hidden items-center gap-6 text-sm text-[var(--muted)] md:flex">
            <a href="#pipeline" className="hover:text-[var(--foreground)]">
              Product
            </a>
            <a href="#primitives" className="hover:text-[var(--foreground)]">
              Primitives
            </a>
            <a href="#demo" className="hover:text-[var(--foreground)]">
              Demo
            </a>
            <span className="text-[var(--border)]">|</span>
            <span className="font-mono text-[11px]">Docs</span>
            <span className="font-mono text-[11px]">Changelog</span>
          </nav>

          <div className="flex items-center gap-2">
            <Link
              href="/demo"
              className="hidden rounded-md border border-[var(--border)] px-3 py-1.5 text-sm text-[var(--foreground)] sm:inline-flex sm:items-center hover:bg-[var(--surface-2)]"
            >
              Trace console
              <Kbd>L</Kbd>
            </Link>
            <Link
              href="/demo"
              className="inline-flex items-center rounded-md bg-[var(--foreground)] px-3 py-1.5 text-sm font-medium text-[var(--bg)] hover:opacity-90"
            >
              Launch demo
              <Kbd>D</Kbd>
            </Link>
          </div>
        </div>
      </header>
    </>
  );
}
