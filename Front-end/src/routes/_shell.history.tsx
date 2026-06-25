import { createFileRoute } from "@tanstack/react-router";
import { EmptyState, Button } from "@/components/agentforge/primitives";

export const Route = createFileRoute("/_shell/history")({
  head: () => ({
    meta: [{ title: "History — AgentForge" }],
  }),
  component: HistoryPage,
});

function HistoryPage() {
  return (
    <div className="p-8 max-w-[1400px] mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">History</h1>
        <p className="mt-1 text-sm text-muted-foreground">All past agent runs and conversations</p>
      </div>
      <div className="mt-8 rounded-xl border border-border bg-surface">
        <EmptyState
          icon="📜"
          title="Your activity will appear here"
          description="Once your agents start running, you'll see every conversation and task in one timeline."
          action={<Button>Build your first agent</Button>}
        />
      </div>
    </div>
  );
}
