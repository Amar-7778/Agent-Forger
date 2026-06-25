import { Link, useRouterState } from "@tanstack/react-router";
import {
  Bell,
  LayoutDashboard,
  Bot,
  Clock,
  History,
  Settings,
  HelpCircle,
  Plus,
  Database,
} from "lucide-react";
import { useState, useEffect, type ReactNode } from "react";
import { SectionLabel } from "./primitives";

const navItems = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, exact: true },
  { to: "/agents", label: "My Agents", icon: Bot },
  { to: "/schedules", label: "Scheduled Tasks", icon: Clock },
  { to: "/knowledge-base", label: "Knowledge Base", icon: Database },
  { to: "/history", label: "History", icon: History },
];

function NavBar() {
  return (
    <header className="fixed top-0 inset-x-0 z-30 h-[60px] bg-surface/80 backdrop-blur border-b border-border flex items-center justify-between px-6">
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-accent to-accent/70 flex items-center justify-center text-accent-foreground font-bold text-base shadow-sm">
          A
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[18px] font-bold tracking-tight text-foreground">AgentForge</span>
          <span className="rounded-full bg-accent-tint border border-accent/20 px-1.5 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-accent">
            Beta
          </span>
        </div>
      </div>
      <div className="flex items-center gap-3">
        <button
          className="relative h-9 w-9 rounded-lg flex items-center justify-center text-muted-foreground hover:bg-surface-muted hover:text-foreground transition-colors"
          aria-label="Notifications"
        >
          <Bell size={20} />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-accent" />
        </button>
      </div>
    </header>
  );
}

function NavItem({
  to,
  icon: Icon,
  label,
  exact,
}: {
  to: string;
  icon: typeof LayoutDashboard;
  label: string;
  exact?: boolean;
}) {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const active = exact ? pathname === to : pathname === to || pathname.startsWith(to + "/");
  return (
    <Link
      to={to}
      className={`relative flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
        active
          ? "bg-accent-tint text-accent"
          : "text-foreground/80 hover:bg-surface-muted hover:text-foreground"
      }`}
    >
      {active && (
        <span className="absolute left-0 top-1.5 bottom-1.5 w-[3px] rounded-r-full bg-accent" />
      )}
      <Icon size={16} className={active ? "text-accent" : ""} />
      <span>{label}</span>
    </Link>
  );
}

function Sidebar() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const [sidebarAgents, setSidebarAgents] = useState<any[]>([]);

  useEffect(() => {
    fetch("/api/agents")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setSidebarAgents(data);
        }
      })
      .catch((err) => console.error("Error fetching agents for sidebar", err));
  }, [pathname]);

  return (
    <aside className="fixed top-[60px] bottom-0 left-0 w-[240px] border-r border-border bg-sidebar flex flex-col py-6 px-3">
      <div className="flex-1 flex flex-col overflow-y-auto af-scroll -mx-3 px-3">
        <SectionLabel>Workspace</SectionLabel>
        <nav className="flex flex-col gap-0.5">
          {navItems.map((item) => (
            <NavItem key={item.to} {...item} />
          ))}
        </nav>

        <div className="my-4 border-t border-border" />

        <SectionLabel
          action={
            <Link
              to="/agents"
              className="text-[12px] font-semibold text-accent hover:underline"
            >
              New +
            </Link>
          }
        >
          My Agents
        </SectionLabel>
        <div className="flex flex-col gap-0.5">
          {sidebarAgents.map((agent) => {
            const isSelected = pathname === `/agents/${agent.id}`;
            return (
              <Link
                key={agent.id}
                to="/agents/$id"
                params={{ id: agent.id }}
                className={`relative rounded-lg px-3 py-2.5 transition-colors ${
                  isSelected
                    ? "bg-accent-tint"
                    : "hover:bg-surface-muted"
                }`}
              >
                {isSelected && (
                  <span className="absolute left-0 top-1.5 bottom-1.5 w-[3px] rounded-r-full bg-accent" />
                )}
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <span className="text-base shrink-0">{agent.icon}</span>
                    <span
                      className={`truncate text-[13px] font-semibold ${
                        isSelected ? "text-accent" : "text-foreground"
                      }`}
                    >
                      {agent.name}
                    </span>
                  </div>
                  <span
                    className={`shrink-0 h-2 w-2 rounded-full ${
                      agent.status === "active"
                        ? "bg-success af-pulse shadow-[0_0_6px_oklch(0.65_0.17_150)]"
                        : "bg-muted-foreground/40"
                    }`}
                  />
                </div>
                <p className="mt-0.5 truncate text-[12px] text-muted-foreground pl-6">
                  {agent.purpose}
                </p>
              </Link>
            );
          })}
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-border flex flex-col gap-0.5">
        <Link
          to="/settings"
          className="flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium text-foreground/80 hover:bg-surface-muted hover:text-foreground transition-colors"
        >
          <Settings size={16} /> Settings
        </Link>
        <Link
          to="/help"
          className="flex items-center gap-2.5 rounded-lg px-3 py-2.5 text-sm font-medium text-foreground/80 hover:bg-surface-muted hover:text-foreground transition-colors"
        >
          <HelpCircle size={16} /> Help
        </Link>
      </div>
    </aside>
  );
}

export function Shell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <NavBar />
      <Sidebar />
      <main className="ml-[240px] pt-[60px] min-h-screen">
        <div className="af-scroll">{children}</div>
      </main>
    </div>
  );
}

export { Plus };
