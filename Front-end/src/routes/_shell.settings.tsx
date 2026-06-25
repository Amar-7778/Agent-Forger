import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { Settings, Check, Trash2, ShieldAlert } from "lucide-react";
import { Button, Modal } from "@/components/agentforge/primitives";

export const Route = createFileRoute("/_shell/settings")({
  head: () => ({
    meta: [{ title: "Platform Settings — AgentForge" }],
  }),
  component: SettingsPage,
});

type ThemeType = "cyberpunk" | "space" | "nordic";

interface Agent {
  id: string;
  name: string;
  icon: string;
  purpose: string;
}

function SettingsPage() {
  const [activeTheme, setActiveTheme] = useState<ThemeType>("cyberpunk");
  const [agents, setAgents] = useState<Agent[]>([]);
  const [confirmDelete, setConfirmDelete] = useState<Agent | null>(null);
  const [successMsg, setSuccessMsg] = useState("");

  const loadTheme = () => {
    const saved = localStorage.getItem("theme") as ThemeType;
    if (saved) {
      setActiveTheme(saved);
    }
  };

  const fetchAgents = () => {
    fetch("/api/agents")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setAgents(data);
        }
      })
      .catch((err) => console.error("Error fetching agents in Settings", err));
  };

  useEffect(() => {
    loadTheme();
    fetchAgents();
  }, []);

  const changeTheme = (theme: ThemeType) => {
    setActiveTheme(theme);
    localStorage.setItem("theme", theme);
    
    // Apply theme
    const root = document.documentElement;
    root.classList.remove("dark", "theme-cyberpunk", "theme-space", "theme-nordic");
    if (theme === "cyberpunk") {
      root.classList.add("dark", "theme-cyberpunk");
    } else if (theme === "space") {
      root.classList.add("dark", "theme-space");
    } else if (theme === "nordic") {
      root.classList.add("theme-nordic");
    }
    
    // Custom page refresh event so sidebar updates theme state if needed
    window.dispatchEvent(new Event("storage"));
  };

  const handleDeleteAgent = () => {
    if (!confirmDelete) return;
    
    fetch(`/api/agents/${confirmDelete.name}`, {
      method: "DELETE",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to delete agent");
        return res.json();
      })
      .then(() => {
        setSuccessMsg(`Agent "${confirmDelete.name}" deleted successfully.`);
        setConfirmDelete(null);
        fetchAgents();
        setTimeout(() => setSuccessMsg(""), 4000);
      })
      .catch((err) => console.error("Error deleting agent in settings", err));
  };

  const themes = [
    {
      id: "cyberpunk" as ThemeType,
      name: "Cyberpunk Dark",
      desc: "Default sleek neon look with vibrant purple accents.",
      colors: ["#7C3AED", "#1E1B4B", "#000000"],
    },
    {
      id: "space" as ThemeType,
      name: "Deep Space Blue",
      desc: "Deep atmospheric blue styling for celestial focus.",
      colors: ["#3B82F6", "#0F172A", "#020617"],
    },
    {
      id: "nordic" as ThemeType,
      name: "Nordic Light",
      desc: "Clean, light theme with premium soft-focus aesthetics.",
      colors: ["#10B981", "#EBF5FF", "#FFFFFF"],
    },
  ];

  return (
    <div className="p-8 max-w-[900px] mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
          <Settings size={28} className="text-accent" /> Platform Settings
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Configure interface theme options and manage your registered custom agents.
        </p>
      </div>

      {successMsg && (
        <div className="rounded-lg border border-success/20 bg-success-tint px-4 py-3 text-sm text-success flex items-center gap-2 af-fade-in">
          <Check size={16} /> {successMsg}
        </div>
      )}

      {/* Theme Section */}
      <div className="rounded-xl border border-border bg-surface p-6 space-y-4 shadow-sm">
        <div>
          <h2 className="text-[17px] font-bold text-foreground">🎨 User Interface Theme</h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Select the active visual stylesheet for your AgentForge operations dashboard.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          {themes.map((t) => {
            const active = activeTheme === t.id;
            return (
              <button
                key={t.id}
                onClick={() => changeTheme(t.id)}
                className={`text-left rounded-xl border p-4 transition-all duration-200 cursor-pointer flex flex-col justify-between h-[140px] hover:border-accent/40 ${
                  active
                    ? "border-accent bg-accent-tint/30 shadow-[0_0_12px_var(--color-accent-tint)]"
                    : "border-border bg-surface-muted hover:bg-surface-muted/80"
                }`}
              >
                <div className="flex justify-between items-start w-full">
                  <div>
                    <h3 className="text-sm font-semibold text-foreground">{t.name}</h3>
                    <p className="text-[11px] text-muted-foreground mt-1 leading-normal pr-2">
                      {t.desc}
                    </p>
                  </div>
                  {active && (
                    <span className="h-5 w-5 rounded-full bg-accent text-accent-foreground flex items-center justify-center">
                      <Check size={12} strokeWidth={3} />
                    </span>
                  )}
                </div>
                
                <div className="flex gap-1.5 mt-auto">
                  {t.colors.map((c, i) => (
                    <span
                      key={i}
                      className="h-4 w-4 rounded-full border border-border/10"
                      style={{ backgroundColor: c }}
                    />
                  ))}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Agents Management Section */}
      <div className="rounded-xl border border-border bg-surface p-6 space-y-4 shadow-sm">
        <div>
          <h2 className="text-[17px] font-bold text-foreground">🤖 Registered Agents</h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            View all custom AI workforce instances and delete them permanently when no longer required.
          </p>
        </div>

        <div className="divide-y divide-border pt-2">
          {agents.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4">No custom agents registered yet.</p>
          ) : (
            agents.map((agent) => (
              <div key={agent.id} className="flex items-center justify-between py-3.5 first:pt-0 last:pb-0">
                <div className="flex items-center gap-3">
                  <div className="h-9 w-9 rounded-lg bg-accent-tint flex items-center justify-center text-lg border border-accent/20">
                    {agent.icon}
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-foreground">{agent.name}</h4>
                    <p className="text-xs text-muted-foreground line-clamp-1">{agent.purpose}</p>
                  </div>
                </div>
                
                <Button
                  variant="secondary"
                  onClick={() => setConfirmDelete(agent)}
                  className="flex items-center gap-1.5 h-8 px-2.5 hover:text-destructive hover:bg-destructive/10 hover:border-destructive/30"
                >
                  <Trash2 size={13} /> Delete
                </Button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Warning/Modal */}
      <Modal
        open={!!confirmDelete}
        onClose={() => setConfirmDelete(null)}
        title="Delete agent?"
        destructive
      >
        <div className="space-y-4 pt-2">
          <div className="flex items-start gap-3 rounded-lg border border-destructive/20 bg-destructive/5 p-3.5">
            <ShieldAlert className="text-destructive shrink-0" size={18} />
            <div className="text-xs leading-normal text-muted-foreground">
              <strong>Warning:</strong> Deleting <span className="text-foreground font-semibold">"{confirmDelete?.name}"</span> will permanently clear its registered configuration, all history logs, and schedules. This action is irreversible.
            </div>
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="secondary" onClick={() => setConfirmDelete(null)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDeleteAgent}>
              Confirm Delete
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
