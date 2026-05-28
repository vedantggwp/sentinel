"use client";

import type { ReactElement, SVGProps } from "react";
import {
  LLM_MODELS,
  STACK_PARTNERS,
  type ModelLogoEntry,
} from "@/components/landing/model-logos";

function LogoItem({
  name,
  Logo,
}: {
  name: string;
  Logo?: (props: SVGProps<SVGSVGElement>) => ReactElement;
}) {
  return (
    <li
      className="flex shrink-0 items-center gap-2.5 text-[var(--muted)] transition hover:text-[var(--foreground)]"
      title={name}
    >
      {Logo ? (
        <Logo className="h-6 w-6 shrink-0 opacity-70" />
      ) : (
        <span className="flex h-6 w-6 items-center justify-center rounded border border-[var(--border)] font-mono text-[9px]">
          {name.slice(0, 2)}
        </span>
      )}
      <span className="hidden text-xs font-medium sm:inline">{name}</span>
    </li>
  );
}

/** Marquee row — duplicates list for seamless loop */
function MarqueeRow({
  items,
  reverse,
}: {
  items: ModelLogoEntry[];
  reverse?: boolean;
}) {
  const doubled = [...items, ...items];

  return (
    <div
      className={`flex overflow-hidden ${reverse ? "[--marquee-dir:-1]" : ""}`}
    >
      <ul
        className="animate-marquee flex shrink-0 items-center gap-12 pr-12"
        aria-hidden={false}
      >
        {doubled.map((model, i) => (
          <LogoItem
            key={`${model.id}-${i}`}
            name={model.name}
            Logo={model.Logo}
          />
        ))}
      </ul>
    </div>
  );
}

export function ModelLogoCloud() {
  return (
    <div className="mt-12 border-t border-[var(--border)] pt-10">
      <p className="text-center font-mono text-[10px] uppercase tracking-widest text-[var(--muted-2)]">
        Safety layer for ads inside any LLM surface
      </p>

      <div className="relative mt-8">
        <div
          className="pointer-events-none absolute inset-y-0 left-0 z-10 w-16 bg-gradient-to-r from-[var(--bg)] to-transparent"
          aria-hidden
        />
        <div
          className="pointer-events-none absolute inset-y-0 right-0 z-10 w-16 bg-gradient-to-r from-transparent to-[var(--bg)]"
          aria-hidden
        />
        <MarqueeRow items={LLM_MODELS} />
      </div>

      <ul className="mt-8 flex flex-wrap items-center justify-center gap-x-8 gap-y-3">
        {LLM_MODELS.map((model) => (
          <LogoItem
            key={model.id}
            name={model.name}
            Logo={model.Logo}
          />
        ))}
      </ul>

      <p className="mt-10 text-center font-mono text-[10px] uppercase tracking-widest text-[var(--muted-2)]">
        Powered by
      </p>
      <ul className="mt-4 flex flex-wrap items-center justify-center gap-6">
        {STACK_PARTNERS.map((p) => (
          <li
            key={p.id}
            className="font-mono text-xs text-[var(--muted)] transition hover:text-[var(--highlight)]"
          >
            {p.name}
          </li>
        ))}
      </ul>
    </div>
  );
}
