import type { ReactElement, SVGProps } from "react";

export type ModelLogoEntry = {
  id: string;
  name: string;
  Logo: (props: SVGProps<SVGSVGElement>) => ReactElement;
};

function LogoShell({
  children,
  viewBox = "0 0 24 24",
  ...props
}: SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox={viewBox}
      fill="currentColor"
      aria-hidden
      {...props}
    >
      {children}
    </svg>
  );
}

/** Simplified marks for demo — monochrome, currentColor */
function OpenAILogo(props: SVGProps<SVGSVGElement>) {
  return (
    <LogoShell {...props}>
      <path d="M22.282 9.821a5.985 5.985 0 0 0-.516-4.91 6.046 6.046 0 0 0-6.51-2.9A6.065 6.065 0 0 0 4.98 4.18a5.985 5.985 0 0 0-3.998 2.9 6.046 6.046 0 0 0 .742 7.097 5.98 5.98 0 0 0 .51 4.911 6.051 6.051 0 0 0 6.515 2.9A5.985 5.985 0 0 0 13.463 24a6.055 6.055 0 0 0 5.804-4.972 5.98 5.98 0 0 0 3.997-2.9 6.055 6.055 0 0 0-.982-7.307zm-11.79-2.86a4.78 4.78 0 0 1 2.66-1.29 4.78 4.78 0 0 1 3.1.45 4.77 4.77 0 0 1 2.29 2.29 4.78 4.78 0 0 1 .45 3.1 4.78 4.78 0 0 1-1.29 2.66 4.77 4.77 0 0 1-4.52 1.74 4.78 4.78 0 0 1-2.66-1.29 4.77 4.77 0 0 1-1.74-4.52 4.78 4.78 0 0 1 1.29-2.66 4.77 4.77 0 0 1 4.52-1.74z" />
    </LogoShell>
  );
}

function AnthropicLogo(props: SVGProps<SVGSVGElement>) {
  return (
    <LogoShell viewBox="0 0 24 24" {...props}>
      <path d="M13.827 3.52h3.603L24 20.48h-3.603l-2.05-5.09h-5.09l-2.05 5.09H7.57L13.827 3.52zm.45 11.88 1.7-4.35-1.7-4.35-1.7 4.35 1.7 4.35zM0 3.52h3.77l7.26 16.96H7.26L6.18 17.1H2.82L1.74 20.48H0V3.52z" />
    </LogoShell>
  );
}

function GeminiLogo(props: SVGProps<SVGSVGElement>) {
  return (
    <LogoShell viewBox="0 0 24 24" {...props}>
      <path d="M12 2L14.09 8.26L20 6l-1.74 5.91L24 12l-5.74 1.09L20 19l-5.91-2.26L12 22l-2.09-5.26L4 19l1.74-5.91L0 12l5.74-1.09L4 5l5.91 2.26L12 2z" />
    </LogoShell>
  );
}

function MetaLogo(props: SVGProps<SVGSVGElement>) {
  return (
    <LogoShell viewBox="0 0 24 24" {...props}>
      <path d="M6.915 4.03c-1.968 0-3.683 1.28-4.871 3.113C.704 9.208 0 11.883 0 14.449c0 .706.07 1.369.21 1.972a6.222 6.222 0 0 0 .782 1.628 3.64 3.64 0 0 0 1.21 1.088c.45.26.96.39 1.478.39.68 0 1.315-.247 1.87-.704a5.54 5.54 0 0 0 1.028-1.238c.466.616 1 1.165 1.59 1.628.7.56 1.55.86 2.437.86.887 0 1.737-.3 2.437-.86a9.34 9.34 0 0 0 1.59-1.628 5.54 5.54 0 0 0 1.028 1.238c.555.457 1.19.704 1.87.704.519 0 1.028-.13 1.479-.39a3.64 3.64 0 0 0 1.21-1.088 6.222 6.222 0 0 0 .782-1.628c.14-.603.21-1.266.21-1.972 0-2.566-.704-5.24-2.044-7.306C20.768 5.31 19.053 4.03 17.085 4.03c-1.123 0-2.143.4-2.985 1.053a7.339 7.339 0 0 0-2.1 2.815 7.339 7.339 0 0 0-2.1-2.815C9.058 4.43 8.038 4.03 6.915 4.03zm10.17 2.81c1.328 0 2.49.86 3.128 2.14.638 1.28.956 2.99.956 4.47 0 .45-.04.87-.12 1.24a4.55 4.55 0 0 1-.5 1.01 2.38 2.38 0 0 1-.78.67c-.28.16-.6.24-.93.24-.42 0-.82-.15-1.17-.43a4.1 4.1 0 0 1-.65-.58 11.77 11.77 0 0 1-1.4-1.72 11.77 11.77 0 0 1-1.4 1.72 4.1 4.1 0 0 1-.65.58c-.35.28-.75.43-1.17.43-.33 0-.65-.08-.93-.24a2.38 2.38 0 0 1-.78-.67 4.55 4.55 0 0 1-.5-1.01 5.1 5.1 0 0 1-.12-1.24c0-1.48.318-3.19.956-4.47.638-1.28 1.8-2.14 3.128-2.14zM6.915 6.74c.78 0 1.48.28 2.05.78.57.5 1.02 1.2 1.32 2.02-.3.82-.75 1.52-1.32 2.02-.57.5-1.27.78-2.05.78-.78 0-1.48-.28-2.05-.78-.57-.5-1.02-1.2-1.32-2.02.3-.82.75-1.52 1.32-2.02.57-.5 1.27-.78 2.05-.78z" />
    </LogoShell>
  );
}

function MistralLogo(props: SVGProps<SVGSVGElement>) {
  return (
    <LogoShell viewBox="0 0 24 24" {...props}>
      <path d="M3.428 3.784v4.8h2.304v8.608h2.304V8.584h2.304V3.784H3.428zm8.416 0v4.8h2.304v8.608h2.304V8.584h2.304V3.784h-6.912zm8.416 0v4.8h2.304v8.608h2.304V8.584h2.304V3.784h-6.912z" />
    </LogoShell>
  );
}

function CohereLogo(props: SVGProps<SVGSVGElement>) {
  return (
    <LogoShell viewBox="0 0 24 24" {...props}>
      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 15v-4H7l5-9v4h4l-5 9z" />
    </LogoShell>
  );
}

function PerplexityLogo(props: SVGProps<SVGSVGElement>) {
  return (
    <LogoShell viewBox="0 0 24 24" {...props}>
      <path d="M12 2l1.5 5.5L19 9l-5.5 1.5L12 16l-1.5-5.5L5 9l5.5-1.5L12 2zM4 14l2 2-2 2 2 2-2 2 2-2 2 2 2-2-2-2 2-2-2-2 2-2-2 2zm16 0l-2 2 2 2-2 2 2-2 2 2 2-2-2-2 2-2-2-2 2-2 2 2z" />
    </LogoShell>
  );
}

function XaiLogo(props: SVGProps<SVGSVGElement>) {
  return (
    <LogoShell viewBox="0 0 24 24" {...props}>
      <path d="M4 4h6.5l3.5 6 3.5-6H24l-7 12 7 8h-6.5l-3.5-6-3.5 6H0l7-12-7-8z" />
    </LogoShell>
  );
}

function DeepSeekLogo(props: SVGProps<SVGSVGElement>) {
  return (
    <LogoShell viewBox="0 0 24 24" {...props}>
      <path d="M12 2C6.48 2 2 6.48 2 12c0 1.85.5 3.58 1.37 5.07L2 22l4.93-1.37A9.96 9.96 0 0 0 12 22c5.52 0 10-4.48 10-10S17.52 2 12 2zm0 18c-1.55 0-3-.45-4.22-1.23l-.3-.18-2.88.8.8-2.88-.18-.3A7.96 7.96 0 0 1 4 12c0-4.41 3.59-8 8-8s8 3.59 8 8-3.59 8-8 8z" />
      <circle cx="9" cy="12" r="1.25" />
      <circle cx="15" cy="12" r="1.25" />
    </LogoShell>
  );
}

/** LLM surfaces where conversational ads appear */
export const LLM_MODELS: ModelLogoEntry[] = [
  { id: "openai", name: "OpenAI", Logo: OpenAILogo },
  { id: "anthropic", name: "Anthropic", Logo: AnthropicLogo },
  { id: "gemini", name: "Google Gemini", Logo: GeminiLogo },
  { id: "meta", name: "Meta AI", Logo: MetaLogo },
  { id: "mistral", name: "Mistral", Logo: MistralLogo },
  { id: "cohere", name: "Cohere", Logo: CohereLogo },
  { id: "perplexity", name: "Perplexity", Logo: PerplexityLogo },
  { id: "xai", name: "xAI", Logo: XaiLogo },
  { id: "deepseek", name: "DeepSeek", Logo: DeepSeekLogo },
];

/** Stack partners (text fallback where no SVG) */
export const STACK_PARTNERS = [
  { id: "thrad", name: "Thrad" },
  { id: "tavily", name: "Tavily" },
  { id: "overmind", name: "Overmind" },
];
