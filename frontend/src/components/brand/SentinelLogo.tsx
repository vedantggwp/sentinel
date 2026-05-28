"use client";

interface SentinelLogoProps {
  size?: "sm" | "md" | "lg";
  showWordmark?: boolean;
  className?: string;
}

const sizes = {
  sm: { icon: 20, text: "text-[13px]", gap: "gap-2" },
  md: { icon: 26, text: "text-[15px]", gap: "gap-2.5" },
  lg: { icon: 34, text: "text-lg", gap: "gap-3" },
};

/**
 * Gate mark: two pillars + scan line + verdict point.
 * Reads as "intercept layer" without a generic shield.
 */
export function SentinelLogo({
  size = "md",
  showWordmark = true,
  className = "",
}: SentinelLogoProps) {
  const s = sizes[size];

  return (
    <span
      className={`inline-flex items-center ${s.gap} ${className}`}
    >
      <svg
        width={s.icon}
        height={s.icon}
        viewBox="0 0 32 32"
        fill="none"
        aria-hidden
        className="shrink-0 text-[var(--foreground)]"
      >
        <rect
          x="3"
          y="3"
          width="26"
          height="26"
          rx="7"
          stroke="currentColor"
          strokeWidth="1"
          opacity="0.2"
        />
        <path
          d="M11 9v14M21 9v14"
          stroke="currentColor"
          strokeWidth="2.25"
          strokeLinecap="round"
        />
        <path
          d="M11 16h10"
          stroke="var(--highlight)"
          strokeWidth="1.5"
          strokeLinecap="round"
        />
        <circle cx="16" cy="16" r="2.25" fill="var(--highlight)" />
        <path
          d="M16 11.5v2M16 18.5v2"
          stroke="var(--highlight)"
          strokeWidth="1.25"
          strokeLinecap="round"
          opacity="0.85"
        />
      </svg>
      {showWordmark && (
        <span className={`${s.text} font-medium tracking-[-0.04em]`}>
          <span className="text-[var(--foreground)]">sent</span>
          <span className="text-[var(--highlight)]">inel</span>
        </span>
      )}
    </span>
  );
}
