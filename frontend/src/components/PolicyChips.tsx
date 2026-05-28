interface PolicyChipsProps {
  rules: { id: string; label: string }[];
}

export function PolicyChips({ rules }: PolicyChipsProps) {
  if (rules.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-1">
      {rules.map((rule) => (
        <span
          key={rule.id}
          className="rounded border border-[var(--border)] bg-[var(--bg)] px-2 py-0.5 font-mono text-[10px] text-[var(--muted)]"
          title={rule.id}
        >
          {rule.label}
        </span>
      ))}
    </div>
  );
}
