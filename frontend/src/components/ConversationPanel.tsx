"use client";

import { AdSlot } from "@/components/AdSlot";
import { MessageList } from "@/components/MessageList";
import type { AdSlotState, DemoScenario } from "@/lib/types";

interface ConversationPanelProps {
  scenario: DemoScenario;
  adState: AdSlotState;
}

export function ConversationPanel({
  scenario,
  adState,
}: ConversationPanelProps) {
  return (
    <section className="flex h-full min-h-0 flex-col bg-[var(--surface)]">
      <div className="border-b border-[var(--border)] px-3 py-2.5">
        <p className="font-mono text-[10px] uppercase tracking-widest text-[var(--muted-2)]">
          / CTX Conversation
        </p>
        <p className="mt-0.5 text-xs text-[var(--muted)]">
          {scenario.description}
        </p>
      </div>

      <div className="flex-1 overflow-y-auto px-3 py-4">
        <MessageList messages={scenario.messages} />
      </div>

      <div className="shrink-0 border-t border-[var(--border)] p-3">
        <p className="mb-2 font-mono text-[10px] text-[var(--muted-2)]">
          / AD Thrad candidate
        </p>
        <AdSlot state={adState} ad={scenario.candidateAd} />
      </div>
    </section>
  );
}
