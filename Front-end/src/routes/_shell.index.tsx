import { createFileRoute, Link } from "@tanstack/react-router";
import { useState, useRef, useEffect } from "react";
import {
  Bot,
  Clock,
  CheckCircle2,
  MessageSquare,
  ArrowRight,
  Send,
} from "lucide-react";
// Removed mock data imports
import {
  Button,
  ThinkingIndicator,
  ToolCallIndicator,
} from "@/components/agentforge/primitives";

export const Route = createFileRoute("/_shell/")({
  head: () => ({
    meta: [
      { title: "Dashboard — AgentForge" },
      { name: "description", content: "Build, schedule, and chat with your AI workforce." },
      { property: "og:title", content: "AgentForge — AI agent builder for teams" },
      { property: "og:description", content: "Build, schedule, and chat with your AI workforce." },
    ],
  }),
  component: DashboardPage,
});

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

type Msg = { from: "user" | "agent"; text: string; time: string };

const seedMessages: Msg[] = [
  { from: "user", text: "Build me an HR agent for Acme Corp", time: "10:24 AM" },
  {
    from: "agent",
    text:
      "I can help with that. What should the HR agent help employees with — leave policies, payroll, onboarding, or all of the above?",
    time: "10:24 AM",
  },
  {
    from: "agent",
    text: "Configure tools next: RAG for documents, fast-mcp for actions like leave requests.",
    time: "10:25 AM",
  },
];

const quickPrompts = [
  "🤖 Build an agent",
  "🔍 Search company docs",
  "⏰ Schedule a task",
  "📊 Analyze data",
  "🌐 Search the web",
];

function DashboardPage() {
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState<null | string>(null);
  const [liveMetrics, setLiveMetrics] = useState<any>(null);
  const [recentAgents, setRecentAgents] = useState<any[]>([]);
  const [recentSchedules, setRecentSchedules] = useState<any[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // 1. Fetch metrics
    fetch("/api/metrics")
      .then((res) => res.json())
      .then(setLiveMetrics)
      .catch((err) => console.error("Error fetching metrics", err));

    // 2. Fetch agents
    fetch("/api/agents")
      .then((res) => res.json())
      .then(setRecentAgents)
      .catch((err) => console.error("Error fetching agents", err));

    // 3. Fetch schedules
    fetch("/api/schedules")
      .then((res) => res.json())
      .then(setRecentSchedules)
      .catch((err) => console.error("Error fetching schedules", err));

    // 4. Fetch chat history
    fetch("/api/chat/history/master-agent")
      .then((res) => res.json())
      .then((data) => {
        if (data && data.length > 0) {
          setMessages(data);
        } else {
          setMessages([
            {
              from: "agent",
              text: "Hi! I am the AgentForge Operations Director. How can I help you automate or coordinate tasks today?",
              time: "Just now",
            },
          ]);
        }
      })
      .catch((err) => {
        console.error("Error fetching chat history", err);
        setMessages([
          {
            from: "agent",
            text: "Hi! I am the AgentForge Operations Director. How can I help you automate or coordinate tasks today?",
            time: "Just now",
          },
        ]);
      });
  }, []);

  const send = (text: string) => {
    if (!text.trim()) return;
    const now = new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
    setMessages((m) => [...m, { from: "user", text, time: now }]);
    setInput("");
    setThinking("Operations Director checking intent...");
    
    fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: text, agentName: "master-agent" })
    })
      .then((res) => res.json())
      .then((data) => {
        setMessages((m) => [...m, data]);
        setThinking(null);
        
        // Refresh metrics, schedules, and agents
        fetch("/api/metrics").then((res) => res.json()).then(setLiveMetrics);
        fetch("/api/schedules").then((res) => res.json()).then(setRecentSchedules);
        fetch("/api/agents").then((res) => res.json()).then(setRecentAgents);
      })
      .catch((err) => {
        console.error("Error chatting with master-agent", err);
        setMessages((m) => [
          ...m,
          { from: "agent", text: "Sorry, I encountered an error connecting to the backend API.", time: now }
        ]);
        setThinking(null);
      });
  };

  const metricCards = [
    { icon: "🤖", label: "Total Agents", value: liveMetrics?.totalAgents?.value ?? 0, delta: liveMetrics?.totalAgents?.delta ?? "...", IconC: Bot },
    { icon: "⏰", label: "Active Schedules", value: liveMetrics?.activeSchedules?.value ?? 0, delta: liveMetrics?.activeSchedules?.delta ?? "...", IconC: Clock },
    { icon: "✅", label: "Tasks This Week", value: liveMetrics?.tasksThisWeek?.value ?? 0, delta: liveMetrics?.tasksThisWeek?.delta ?? "...", IconC: CheckCircle2 },
    { icon: "💬", label: "Messages Today", value: liveMetrics?.messagesToday?.value ?? 0, delta: liveMetrics?.messagesToday?.delta ?? "...", IconC: MessageSquare },
  ];

  return (
    <div className="p-8 max-w-[1400px] mx-auto">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">
            {greeting()} <span className="inline-block">👋</span>
          </h1>
          <p className="mt-1 text-sm text-muted-foreground">
            What would you like to automate today?
          </p>
        </div>
        <Link to="/agents">
          <Button>Build Agent</Button>
        </Link>
      </div>

      {/* Metrics */}
      <div className="mt-6 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metricCards.map((m) => (
          <div
            key={m.label}
            className="rounded-xl border border-border bg-surface p-5 transition-all hover:border-accent/40 hover:-translate-y-0.5"
          >
            <div className="flex items-center gap-2">
              <span className="text-base">{m.icon}</span>
              <span className="text-[12px] font-semibold uppercase tracking-wider text-muted-foreground">
                {m.label}
              </span>
            </div>
            <div className="mt-2 text-[32px] font-bold leading-none text-accent">{m.value}</div>
            <div className="mt-2 text-xs text-muted-foreground">{m.delta}</div>
          </div>
        ))}
      </div>

      {/* Main row */}
      <div className="mt-6 grid grid-cols-1 lg:grid-cols-[1.6fr_1fr] gap-6">
        {/* Chat */}
        <div className="rounded-xl border border-border bg-surface flex flex-col h-[520px] overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4 border-b border-border">
            <div>
              <h3 className="text-[15px] font-semibold text-foreground">AgentForge Assistant</h3>
              <p className="text-xs text-muted-foreground">
                Ask anything or say build me an agent
              </p>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <span className="h-2 w-2 rounded-full bg-success af-pulse" />
              Online
            </div>
          </div>

          <div ref={scrollRef} className="flex-1 overflow-y-auto af-scroll px-6 py-5 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center pt-14">
                <div className="text-5xl">🤖</div>
                <p className="mt-4 text-base font-semibold text-foreground">
                  How can I help you today?
                </p>
                <p className="mt-1 text-sm text-muted-foreground">
                  Ask a question, build an agent, or schedule a task
                </p>
              </div>
            ) : (
              messages.map((m, i) =>
                m.from === "user" ? (
                  <div key={i} className="af-msg-in flex flex-col items-end">
                    <div className="max-w-[75%] rounded-[12px_12px_2px_12px] border border-border bg-surface-muted px-3.5 py-2.5 text-sm text-foreground">
                      {m.text}
                    </div>
                    <span className="mt-1 text-[11px] text-muted-foreground">{m.time}</span>
                  </div>
                ) : (
                  <div key={i} className="af-msg-in max-w-[80%]">
                    <div className="border-l-[3px] border-accent pl-4 text-sm leading-relaxed text-foreground">
                      {m.text}
                    </div>
                    <span className="mt-1 ml-4 block text-[11px] text-muted-foreground">
                      {m.time}
                    </span>
                  </div>
                )
              )
            )}
            {thinking && (
              <div className="max-w-[80%] space-y-1">
                <ToolCallIndicator label={thinking} />
                <ThinkingIndicator />
              </div>
            )}
          </div>

          <div className="px-6 py-3 border-t border-border overflow-x-auto af-scroll">
            <div className="flex gap-2 whitespace-nowrap">
              {quickPrompts.map((q) => (
                <button
                  key={q}
                  onClick={() => send(q.replace(/^[^\s]+\s/, ""))}
                  className="rounded-full border border-border bg-surface px-3.5 py-1.5 text-xs font-medium text-foreground hover:border-accent hover:text-accent transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          <div className="px-5 py-4 border-t border-border">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                send(input);
              }}
              className="relative"
            >
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Message AgentForge Assistant..."
                className="w-full rounded-[10px] border border-border bg-surface-muted pl-4 pr-14 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-accent focus:ring-4 focus:ring-accent/15 transition-all"
              />
              <button
                type="submit"
                className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 rounded-md bg-accent text-accent-foreground flex items-center justify-center hover:bg-accent/90 transition-colors"
                aria-label="Send"
              >
                <Send size={14} />
              </button>
            </form>
          </div>
        </div>

        {/* Right column */}
        <div className="flex flex-col gap-6">
          <div className="rounded-xl border border-border bg-surface p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[15px] font-semibold text-foreground">Recent Agents</h3>
              <Link to="/agents" className="text-xs font-semibold text-accent hover:underline">
                View all →
              </Link>
            </div>
            <div className="divide-y divide-border">
              {recentAgents.length === 0 ? (
                <p className="text-xs text-muted-foreground py-3">No custom agents created yet.</p>
              ) : (
                recentAgents.slice(0, 3).map((a) => (
                  <div key={a.id} className="flex items-center gap-3 py-3">
                    <div className="h-8 w-8 rounded-full bg-accent-tint flex items-center justify-center text-sm">
                      {a.icon}
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold text-foreground truncate">{a.name}</p>
                      <p className="text-xs text-muted-foreground truncate">{a.company}</p>
                    </div>
                    <Link
                      to="/agents/$id"
                      params={{ id: a.id }}
                      className="text-xs font-semibold text-accent hover:underline whitespace-nowrap"
                    >
                      Open →
                    </Link>
                  </div>
                ))
              )}
            </div>
          </div>

          <div className="rounded-xl border border-border bg-surface p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-[15px] font-semibold text-foreground">Scheduled Tasks</h3>
              <Link to="/schedules" className="text-xs font-semibold text-accent hover:underline">
                View all →
              </Link>
            </div>
            <div className="divide-y divide-border">
              {recentSchedules.length === 0 ? (
                <p className="text-xs text-muted-foreground py-3">No scheduled tasks yet.</p>
              ) : (
                recentSchedules.slice(0, 3).map((t) => (
                  <div key={t.id} className="flex items-center gap-3 py-3">
                    <div className="h-8 w-8 rounded-full bg-accent-tint flex items-center justify-center">
                      <Clock size={14} className="text-accent" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-semibold text-foreground truncate">{t.task}</p>
                      <p className="text-xs text-muted-foreground truncate">Next: {t.nextRun}</p>
                    </div>
                    <span className="rounded-full border border-accent/20 bg-accent-tint px-2 py-0.5 text-[11px] font-semibold text-accent whitespace-nowrap">
                      {t.frequency.split(" ")[0]}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Keep ArrowRight import used (lint)
void ArrowRight;
