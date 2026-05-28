import type { ChatMessage } from "@/lib/types";

interface MessageListProps {
  messages: ChatMessage[];
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <div className="flex flex-col gap-3">
      {messages.map((msg) => (
        <div
          key={msg.id}
          className={msg.role === "user" ? "text-right" : "text-left"}
        >
          <span className="font-mono text-[10px] text-[var(--muted-2)]">
            {msg.role === "user" ? "user" : "assistant"}
          </span>
          <div
            className={`mt-1 inline-block max-w-full rounded-lg px-3 py-2 text-left text-[13px] leading-relaxed ${
              msg.role === "user"
                ? "bg-[var(--surface-3)] text-[var(--foreground)]"
                : "border border-[var(--border)] bg-[var(--bg)] text-[var(--muted)]"
            }`}
          >
            {msg.content}
          </div>
        </div>
      ))}
    </div>
  );
}
