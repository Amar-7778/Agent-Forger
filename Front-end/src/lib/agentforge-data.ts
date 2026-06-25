export type AgentStatus = "active" | "inactive";

export interface Agent {
  id: string;
  name: string;
  icon: string;
  company: string;
  status: AgentStatus;
  purpose: string;
  tools: string[];
  lastUsed: string;
  quickActions: string[];
}

export const agents: Agent[] = [
  {
    id: "hr-assistant",
    name: "HR Assistant",
    icon: "👥",
    company: "Acme Corp",
    status: "active",
    purpose: "Answers employee HR queries about leave, payroll, and onboarding",
    tools: ["RAG", "fast-mcp"],
    lastUsed: "2h ago",
    quickActions: [
      "📅 Check leave balance",
      "💰 Payroll question",
      "📚 Onboarding docs",
      "🏥 Benefits overview",
      "📝 Submit request",
    ],
  },
  {
    id: "sales-summarizer",
    name: "Sales Summarizer",
    icon: "📊",
    company: "Acme Corp",
    status: "active",
    purpose: "Pulls weekly sales data and posts summaries to Slack every Monday",
    tools: ["Tavily", "Slack MCP", "fast-mcp"],
    lastUsed: "4h ago",
    quickActions: [
      "📈 This week's report",
      "🔍 Top performers",
      "📊 Pipeline review",
      "💬 Post to Slack",
      "📅 Schedule digest",
    ],
  },
  {
    id: "support-bot",
    name: "Support Bot",
    icon: "🎧",
    company: "Acme Corp",
    status: "inactive",
    purpose: "Handles tier-1 customer support queries from the knowledge base",
    tools: ["RAG", "fast-mcp"],
    lastUsed: "3d ago",
    quickActions: [
      "🔎 Search KB",
      "🎫 Create ticket",
      "📊 Ticket trends",
      "💡 Suggest article",
      "📨 Reply draft",
    ],
  },
];

export interface ScheduledTask {
  id: string;
  agentId: string;
  task: string;
  frequency: string;
  nextRun: string;
  status: "active" | "paused";
}

export const scheduledTasks: ScheduledTask[] = [
  {
    id: "t1",
    agentId: "sales-summarizer",
    task: "Weekly Sales Report",
    frequency: "Every Monday 9am",
    nextRun: "in 3 hours",
    status: "active",
  },
  {
    id: "t2",
    agentId: "support-bot",
    task: "Inventory Check",
    frequency: "Every 30 minutes",
    nextRun: "in 12 min",
    status: "active",
  },
  {
    id: "t3",
    agentId: "sales-summarizer",
    task: "Competitor Digest",
    frequency: "Every Friday 5pm",
    nextRun: "Friday 5:00 PM",
    status: "active",
  },
];

export const metrics = {
  totalAgents: { value: 3, delta: "+1 this week" },
  activeSchedules: { value: 3, delta: "no change" },
  tasksThisWeek: { value: 47, delta: "+12% vs last week" },
  messagesToday: { value: 128, delta: "+24 since yesterday" },
};

export function getAgent(id: string) {
  return agents.find((a) => a.id === id);
}
