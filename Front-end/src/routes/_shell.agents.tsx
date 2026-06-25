import { createFileRoute, Link } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { Search, MoreVertical } from "lucide-react";
import {
  Button,
  StatusBadge,
  ToolBadge,
  Modal,
} from "@/components/agentforge/primitives";

export interface Agent {
  id: string;
  name: string;
  icon: string;
  company: string;
  status: "active" | "inactive";
  purpose: string;
  tools: string[];
  lastUsed: string;
  quickActions: string[];
}

export const Route = createFileRoute("/_shell/agents")({
  head: () => ({
    meta: [
      { title: "My Agents — AgentForge" },
      { name: "description", content: "Manage your AI workforce." },
    ],
  }),
  component: AgentsPage,
});

type Filter = "All" | "Active" | "Inactive" | "Scheduled";
const filters: Filter[] = ["All", "Active", "Inactive", "Scheduled"];

function AgentsPage() {
  const [agentsList, setAgentsList] = useState<Agent[]>([]);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<Filter>("All");
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [confirmDelete, setConfirmDelete] = useState<Agent | null>(null);
  const [buildOpen, setBuildOpen] = useState(false);

  // Form states
  const [newAgentName, setNewAgentName] = useState("");
  const [newAgentDesc, setNewAgentDesc] = useState("");
  const [newAgentScope, setNewAgentScope] = useState("");
  const [newAgentRestr, setNewAgentRestr] = useState("");
  const [newAgentTheme, setNewAgentTheme] = useState("cyberpunk");
  const [newAgentIcon, setNewAgentIcon] = useState("🤖");
  const [selectedTools, setSelectedTools] = useState<string[]>([]);

  const fetchAgents = () => {
    fetch("/api/agents")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setAgentsList(data);
        }
      })
      .catch((err) => console.error("Error fetching agents", err));
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  const handleCreateAgent = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newAgentName.trim() || !newAgentDesc.trim()) return;

    fetch("/api/agents", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        name: newAgentName,
        description: newAgentDesc,
        scope: newAgentScope,
        restrictions: newAgentRestr,
        tools: selectedTools,
        theme: newAgentTheme,
        icon: newAgentIcon
      })
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to create agent");
        return res.json();
      })
      .then(() => {
        setNewAgentName("");
        setNewAgentDesc("");
        setNewAgentScope("");
        setNewAgentRestr("");
        setNewAgentTheme("cyberpunk");
        setNewAgentIcon("🤖");
        setSelectedTools([]);
        setBuildOpen(false);
        fetchAgents();
      })
      .catch((err) => console.error("Error creating agent:", err));
  };

  const handleDeleteAgent = () => {
    if (!confirmDelete) return;
    fetch(`/api/agents/${confirmDelete.name}`, {
      method: "DELETE"
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to delete agent");
        setConfirmDelete(null);
        fetchAgents();
      })
      .catch((err) => console.error("Error deleting agent:", err));
  };

  const toggleTool = (tool: string) => {
    setSelectedTools((prev) =>
      prev.includes(tool) ? prev.filter((t) => t !== tool) : [...prev, tool]
    );
  };

  const filtered = agentsList.filter((a) => {
    if (query && !a.name.toLowerCase().includes(query.toLowerCase())) return false;
    if (filter === "Active") return a.status === "active";
    if (filter === "Inactive") return a.status === "inactive";
    return true;
  });

  return (
    <div className="p-8 max-w-[1400px] mx-auto">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">My Agents</h1>
          <p className="mt-1 text-sm text-muted-foreground">Manage your AI workforce</p>
        </div>
        <Button onClick={() => setBuildOpen(true)}>Build New Agent</Button>
      </div>

      <div className="mt-6 mb-5 flex flex-wrap items-center justify-between gap-3">
        <div className="relative w-full sm:w-[280px]">
          <Search
            size={14}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search agents..."
            className="w-full rounded-lg border border-border bg-surface-muted py-2 pl-9 pr-3 text-sm placeholder:text-muted-foreground focus:outline-none focus:border-accent focus:ring-4 focus:ring-accent/15"
          />
        </div>
        <div className="flex gap-2 flex-wrap">
          {filters.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-full px-3.5 py-1.5 text-xs font-semibold transition-colors ${
                filter === f
                  ? "bg-accent text-accent-foreground"
                  : "border border-border bg-surface text-foreground hover:border-border-strong"
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {filtered.map((agent) => (
          <div
            key={agent.id}
            className="group relative rounded-xl border border-border bg-surface p-6 transition-all hover:border-accent/40 hover:-translate-y-0.5"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-start gap-3 min-w-0">
                <div className="h-11 w-11 shrink-0 rounded-[10px] bg-accent-tint border border-accent/20 flex items-center justify-center text-xl">
                  {agent.icon}
                </div>
                <div className="min-w-0">
                  <h3 className="text-[15px] font-semibold text-foreground truncate">
                    {agent.name}
                  </h3>
                  <p className="text-xs text-muted-foreground truncate">{agent.company}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <StatusBadge status={agent.status} />
                <div className="relative">
                  <button
                    onClick={() => setOpenMenu(openMenu === agent.id ? null : agent.id)}
                    className="h-7 w-7 rounded-md flex items-center justify-center text-muted-foreground opacity-0 group-hover:opacity-100 hover:bg-surface-muted hover:text-foreground transition-all"
                    aria-label="More"
                  >
                    <MoreVertical size={16} />
                  </button>
                  {openMenu === agent.id && (
                    <>
                      <div className="fixed inset-0 z-10" onClick={() => setOpenMenu(null)} />
                      <div className="af-fade-in absolute right-0 top-8 z-20 w-36 rounded-lg border border-border bg-surface shadow-lg py-1">
                        <button className="w-full px-3 py-1.5 text-left text-sm hover:bg-surface-muted">
                          Edit
                        </button>
                        <button className="w-full px-3 py-1.5 text-left text-sm hover:bg-surface-muted">
                          Duplicate
                        </button>
                        <button
                          onClick={() => {
                            setOpenMenu(null);
                            setConfirmDelete(agent);
                          }}
                          className="w-full px-3 py-1.5 text-left text-sm text-destructive hover:bg-destructive/10"
                        >
                          Delete
                        </button>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>

            <p className="text-[13px] leading-relaxed text-muted-foreground mb-4 line-clamp-2">
              {agent.purpose}
            </p>

            <div className="flex flex-wrap gap-1.5 mb-4">
              {agent.tools.map((t) => (
                <ToolBadge key={t}>{t}</ToolBadge>
              ))}
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-border">
              <span className="text-xs text-muted-foreground">Last used {agent.lastUsed}</span>
              <Link
                to="/agents/$id"
                params={{ id: agent.id }}
                className="inline-flex items-center rounded-md bg-accent px-4 py-1.5 text-[13px] font-semibold text-accent-foreground hover:bg-accent/90 transition-colors"
              >
                Open →
              </Link>
            </div>
          </div>
        ))}
      </div>

      <Modal
        open={!!confirmDelete}
        onClose={() => setConfirmDelete(null)}
        title={`Delete ${confirmDelete?.name}?`}
        destructive
      >
        <p className="text-sm text-muted-foreground">
          This will permanently delete the agent and all of its scheduled tasks and chat history.
          This action cannot be undone.
        </p>
        <div className="mt-6 flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setConfirmDelete(null)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDeleteAgent}>
            Delete Agent
          </Button>
        </div>
      </Modal>

      <Modal open={buildOpen} onClose={() => setBuildOpen(false)} title="Build New Agent">
        <form onSubmit={handleCreateAgent} className="space-y-4">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Agent Name</label>
            <input
              value={newAgentName}
              onChange={(e) => setNewAgentName(e.target.value)}
              placeholder="e.g. Sales Assistant"
              required
              className="mt-1 w-full rounded-lg border border-border bg-surface-muted px-3 py-2 text-sm focus:outline-none focus:border-accent"
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Description / Purpose</label>
            <textarea
              value={newAgentDesc}
              onChange={(e) => setNewAgentDesc(e.target.value)}
              placeholder="What exactly does this agent do?"
              required
              rows={3}
              className="mt-1 w-full rounded-lg border border-border bg-surface-muted p-3 text-sm focus:outline-none focus:border-accent"
            />
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Operational Scope</label>
              <input
                value={newAgentScope}
                onChange={(e) => setNewAgentScope(e.target.value)}
                placeholder="e.g. Internal sales data only"
                className="mt-1 w-full rounded-lg border border-border bg-surface-muted px-3 py-2 text-sm focus:outline-none focus:border-accent"
              />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Restrictions</label>
              <input
                value={newAgentRestr}
                onChange={(e) => setNewAgentRestr(e.target.value)}
                placeholder="e.g. Cannot send emails"
                className="mt-1 w-full rounded-lg border border-border bg-surface-muted px-3 py-2 text-sm focus:outline-none focus:border-accent"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Icon Emoji</label>
              <input
                value={newAgentIcon}
                onChange={(e) => setNewAgentIcon(e.target.value)}
                placeholder="🤖"
                className="mt-1 w-full rounded-lg border border-border bg-surface-muted px-3 py-2 text-sm focus:outline-none focus:border-accent"
              />
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Theme Color</label>
              <select
                value={newAgentTheme}
                onChange={(e) => setNewAgentTheme(e.target.value)}
                className="mt-1 w-full rounded-lg border border-border bg-surface-muted px-3 py-2 text-sm focus:outline-none focus:border-accent"
              >
                <option value="cyberpunk">Cyberpunk Dark</option>
                <option value="space">Deep Space Blue</option>
                <option value="nordic">Nordic Light</option>
              </select>
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-2">Enabled Tools</label>
            <div className="flex flex-wrap gap-2">
              {["RAG Knowledge Base", "Web Search", "Slack Output", "Email Output"].map((tool) => {
                const active = selectedTools.includes(tool);
                return (
                  <button
                    type="button"
                    key={tool}
                    onClick={() => toggleTool(tool)}
                    className={`rounded-full px-3 py-1 text-xs font-semibold transition-colors ${
                      active
                        ? "bg-accent text-accent-foreground"
                        : "border border-border bg-surface text-foreground hover:border-border-strong"
                    }`}
                  >
                    {tool}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="mt-6 flex justify-end gap-2 pt-2">
            <Button variant="secondary" type="button" onClick={() => setBuildOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Create Agent</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
