export function Kbd({ children }: { children: string }) {
  return (
    <kbd className="ml-1.5 inline-flex min-w-[1.25rem] items-center justify-center rounded border border-[var(--border)] bg-[var(--surface-2)] px-1 py-0.5 font-mono text-[10px] font-medium text-[var(--muted)]">
      {children}
    </kbd>
  );
}
