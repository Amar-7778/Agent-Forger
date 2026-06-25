import { Outlet, createFileRoute } from "@tanstack/react-router";
import { Shell } from "@/components/agentforge/Shell";

export const Route = createFileRoute("/_shell")({
  component: () => (
    <Shell>
      <Outlet />
    </Shell>
  ),
});
