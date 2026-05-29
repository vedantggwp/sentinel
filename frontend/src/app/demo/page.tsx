import { SentinelDashboard } from "@/components/SentinelDashboard";

interface DemoPageProps {
  searchParams: Promise<{
    scenario?: string;
    capture?: string;
  }>;
}

export default async function DemoPage({ searchParams }: DemoPageProps) {
  const params = await searchParams;
  return (
    <main className="h-full">
      <SentinelDashboard
        initialScenarioId={params.scenario}
        capture={params.capture === "1"}
      />
    </main>
  );
}
