import { createFileRoute } from "@tanstack/react-router";
import { useState, useEffect } from "react";
import { Clock, Pause, Play, Trash2 } from "lucide-react";
import {
  Button,
  StatusBadge,
  EmptyState,
  Modal,
} from "@/components/agentforge/primitives";

export interface ScheduledTask {
  id: string;
  agentId: string;
  agentName?: string;
  task: string;
  frequency: string;
  nextRun: string;
  status: "active" | "paused";
}

export const Route = createFileRoute("/_shell/schedules")({
  head: () => ({
    meta: [
      { title: "Scheduled Tasks — AgentForge" },
      { name: "description", content: "Manage your scheduled AI tasks." },
    ],
  }),
  component: SchedulesPage,
});

function SchedulesPage() {
  const [agentsList, setAgentsList] = useState<any[]>([]);
  const [tasks, setTasks] = useState<ScheduledTask[]>([]);
  const [loading, setLoading] = useState(true);
  const [confirmDelete, setConfirmDelete] = useState<ScheduledTask | null>(null);
  const [scheduleOpen, setScheduleOpen] = useState(false);

  // Form states
  const [schedAgentId, setSchedAgentId] = useState("");
  const [schedTask, setSchedTask] = useState("");
  const [schedFreq, setSchedFreq] = useState("");
  const [schedDest, setSchedDest] = useState("");

  const fetchData = () => {
    setLoading(true);
    fetch("/api/agents")
      .then((res) => res.json())
      .then((agentsData) => {
        if (Array.isArray(agentsData)) {
          setAgentsList(agentsData);
          if (agentsData.length > 0) {
            setSchedAgentId(agentsData[0].id);
          }
        }
        return fetch("/api/schedules");
      })
      .then((res) => res.json())
      .then((schedulesData) => {
        if (Array.isArray(schedulesData)) {
          setTasks(schedulesData);
        }
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching schedules data", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchData();
  }, []);

  const togglePause = (id: string) => {
    const task = tasks.find((t) => t.id === id);
    if (!task) return;
    const newStatus = task.status === "active" ? "paused" : "active";
    const scheduleName = task.agentName || task.id;
    
    fetch(`/api/schedules/${scheduleName}/status`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ status: newStatus }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to toggle status");
        fetchData();
      })
      .catch((err) => console.error("Error toggling status:", err));
  };

  const handleScheduleTask = (e: React.FormEvent) => {
    e.preventDefault();
    if (!schedAgentId || !schedTask.trim() || !schedFreq.trim()) return;

    fetch("/api/schedules", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        agentId: schedAgentId,
        task: schedTask,
        frequency: schedFreq,
        destination: schedDest || "System Logs",
      }),
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to schedule task");
        return res.json();
      })
      .then(() => {
        setSchedTask("");
        setSchedFreq("");
        setSchedDest("");
        setScheduleOpen(false);
        fetchData();
      })
      .catch((err) => console.error("Error creating schedule:", err));
  };

  const handleDeleteTask = () => {
    if (!confirmDelete) return;
    const scheduleName = confirmDelete.agentName || confirmDelete.id;
    fetch(`/api/schedules/${scheduleName}`, {
      method: "DELETE",
    })
      .then((res) => {
        if (!res.ok) throw new Error("Failed to delete scheduled task");
        setConfirmDelete(null);
        fetchData();
      })
      .catch((err) => console.error("Error deleting schedule:", err));
  };

  const stats = [
    { label: "Active Schedules", value: tasks.filter((t) => t.status === "active").length, icon: "⏰" },
    { label: "Ran Today", value: tasks.filter((t) => t.status === "active").length * 6, icon: "✅" },
    { label: "Failed Today", value: 0, icon: "⚠️" },
  ];

  return (
    <div className="p-8 max-w-[1400px] mx-auto">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Scheduled Tasks</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Recurring jobs your agents run automatically
          </p>
        </div>
        <Button onClick={() => setScheduleOpen(true)}>Schedule New Task</Button>
      </div>

      <div className="mt-6 grid grid-cols-1 sm:grid-cols-3 gap-4">
        {stats.map((s) => (
          <div
            key={s.label}
            className="rounded-xl border border-border bg-surface p-5 transition-all hover:border-accent/40 hover:-translate-y-0.5"
          >
            <div className="flex items-center gap-2">
              <span className="text-base">{s.icon}</span>
              <span className="text-[12px] font-semibold uppercase tracking-wider text-muted-foreground">
                {s.label}
              </span>
            </div>
            <div className="mt-2 text-[32px] font-bold text-accent leading-none">{s.value}</div>
          </div>
        ))}
      </div>

      <div className="mt-6 rounded-xl border border-border bg-surface overflow-hidden">
        {tasks.length === 0 ? (
          <EmptyState
            icon="⏰"
            title="No scheduled tasks yet"
            description="Tell AgentForge to run something automatically"
            action={<Button onClick={() => setScheduleOpen(true)}>Schedule a task →</Button>}
          />
        ) : (
          <div className="overflow-x-auto af-scroll">
            <table className="w-full">
              <thead>
                <tr className="bg-surface-muted border-b border-border">
                  {["Agent", "Task", "Frequency", "Next Run", "Status", "Actions"].map((h) => (
                    <th
                      key={h}
                      className="px-6 py-3 text-left text-[11px] font-semibold uppercase tracking-wider text-muted-foreground"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {tasks.map((t) => {
                  const agent = agentsList.find((a) => a.id === t.agentId);
                  return (
                    <tr
                      key={t.id}
                      className="border-b border-border last:border-0 hover:bg-surface-muted/60 transition-colors"
                    >
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2.5">
                          <div className="h-7 w-7 rounded-full bg-accent-tint flex items-center justify-center text-sm">
                            {agent?.icon ?? "⏰"}
                          </div>
                          <span className="text-sm font-medium text-foreground">
                            {agent?.name ?? t.agentName ?? "Unknown"}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 max-w-[200px]">
                        <p className="text-sm text-muted-foreground truncate">{t.task}</p>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex rounded-full border border-accent/20 bg-accent-tint px-2.5 py-0.5 text-xs font-semibold text-accent">
                          {t.frequency}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm text-muted-foreground">{t.nextRun}</td>
                      <td className="px-6 py-4">
                        <StatusBadge status={t.status} />
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => togglePause(t.id)}
                            className="h-8 w-8 rounded-lg flex items-center justify-center text-muted-foreground hover:bg-surface-muted hover:text-accent transition-colors"
                            aria-label={t.status === "active" ? "Pause" : "Resume"}
                          >
                            {t.status === "active" ? <Pause size={15} /> : <Play size={15} />}
                          </button>
                          <button
                            onClick={() => setConfirmDelete(t)}
                            className="h-8 w-8 rounded-lg flex items-center justify-center text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors"
                            aria-label="Delete"
                          >
                            <Trash2 size={15} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <Modal
        open={!!confirmDelete}
        onClose={() => setConfirmDelete(null)}
        title="Delete scheduled task?"
        destructive
      >
        <p className="text-sm text-muted-foreground">
          "{confirmDelete?.task}" will stop running automatically. You can re-schedule it later.
        </p>
        <div className="mt-6 flex justify-end gap-2">
          <Button variant="secondary" onClick={() => setConfirmDelete(null)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDeleteTask}>
            Delete Task
          </Button>
        </div>
      </Modal>

      <Modal open={scheduleOpen} onClose={() => setScheduleOpen(false)} title="Schedule New Task">
        <form onSubmit={handleScheduleTask} className="space-y-4">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-1">
              Select Agent
            </label>
            <select
              value={schedAgentId}
              onChange={(e) => setSchedAgentId(e.target.value)}
              className="w-full rounded-lg border border-border bg-surface-muted px-3 py-2 text-sm focus:outline-none focus:border-accent"
            >
              {agentsList.map((a) => (
                <option key={a.id} value={a.id}>
                  {a.icon} {a.name}
                </option>
              ))}
            </select>
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-1">
              Task Description
            </label>
            <input
              value={schedTask}
              onChange={(e) => setSchedTask(e.target.value)}
              placeholder="e.g. Run competitor analysis report"
              required
              className="w-full rounded-lg border border-border bg-surface-muted px-3 py-2 text-sm focus:outline-none focus:border-accent"
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-1">
              Frequency (Cron expression or Interval in minutes)
            </label>
            <input
              value={schedFreq}
              onChange={(e) => setSchedFreq(e.target.value)}
              placeholder="e.g. 0 9 * * 1 (Every Mon 9am) or 60 (Every 60 mins)"
              required
              className="w-full rounded-lg border border-border bg-surface-muted px-3 py-2 text-sm focus:outline-none focus:border-accent"
            />
          </div>
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground block mb-1">
              Report Destination / Output Channel (Optional)
            </label>
            <input
              value={schedDest}
              onChange={(e) => setSchedDest(e.target.value)}
              placeholder="e.g. Slack channel or email"
              className="w-full rounded-lg border border-border bg-surface-muted px-3 py-2 text-sm focus:outline-none focus:border-accent"
            />
          </div>
          <div className="mt-6 flex justify-end gap-2 pt-2">
            <Button variant="secondary" type="button" onClick={() => setScheduleOpen(false)}>
              Cancel
            </Button>
            <Button type="submit">Schedule Task</Button>
          </div>
        </form>
      </Modal>

      <div className="hidden">
        <Clock />
      </div>
    </div>
  );
}
