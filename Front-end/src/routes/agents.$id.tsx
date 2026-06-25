import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useState, useRef, useEffect } from "react";
import { Send, MoreVertical, Info } from "lucide-react";
import {
  StatusBadge,
  ToolBadge,
  ThinkingIndicator,
  ToolCallIndicator,
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

export const Route = createFileRoute("/agents/$id")({
  head: ({ params }) => ({
    meta: [{ title: `Chat — ${params.id}` }],
  }),
  component: AgentChatPage,
});

type Msg = { from: "user" | "agent"; text: string; time: string };

function AgentChatPage() {
  const { id } = Route.useParams();
  const navigate = useNavigate();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [loading, setLoading] = useState(true);
  const [showMoreMenu, setShowMoreMenu] = useState(false);
  const [input, setInput] = useState("");
  const [thinking, setThinking] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const taRef = useRef<HTMLTextAreaElement>(null);

  const fetchAgentDetails = () => {
    setLoading(true);
    fetch(`/api/agents/${id}`)
      .then((res) => {
        if (!res.ok) throw new Error("Agent not found");
        return res.json();
      })
      .then((data) => {
        setAgent(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching agent", err);
        setLoading(false);
      });
  };

  const fetchChatHistory = () => {
    fetch(`/api/chat/history/${id}`)
      .then((res) => res.json())
      .then((data) => {
        if (data && data.length > 0) {
          setMessages(data);
        } else {
          setMessages([
            {
              from: "agent",
              text: agent
                ? `Hi! I'm ${agent.name}. ${agent.purpose} How can I help?`
                : "Hi! How can I help you today?",
              time: "Just now",
            },
          ]);
        }
      })
      .catch((err) => console.error("Error fetching chat history", err));
  };

  useEffect(() => {
    fetchAgentDetails();
  }, [id]);

  useEffect(() => {
    if (agent) {
      fetchChatHistory();
    }
  }, [agent]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, thinking]);

  useEffect(() => {
    if (taRef.current) {
      taRef.current.style.height = "auto";
      taRef.current.style.height = Math.min(taRef.current.scrollHeight, 160) + "px";
    }
  }, [input]);

  const clearConversation = () => {
    fetch(`/api/chat/clear/${id}`, { method: "POST" })
      .then(() => {
        setMessages([
          {
            from: "agent",
            text: agent
              ? `Hi! I'm ${agent.name}. ${agent.purpose} How can I help?`
              : "Hi! How can I help you today?",
            time: "Just now",
          },
        ]);
        setShowMoreMenu(false);
      })
      .catch((err) => console.error("Error clearing chat history", err));
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-center p-8">
        <h1 className="text-xl font-semibold">Loading agent configuration...</h1>
      </div>
    );
  }

  if (!agent) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center text-center p-8">
        <h1 className="text-2xl font-bold">Agent not found</h1>
        <Link to="/agents" className="mt-4 text-accent hover:underline">
          ← Back to agents
        </Link>
      </div>
    );
  }

  const anyWordMatches = (str: string, words: string[]) => {
    const lowercase = str.toLowerCase();
    return words.some(w => lowercase.includes(w));
  };

  const send = (text: string) => {
    if (!text.trim()) return;
    const now = new Date().toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
    setMessages((m) => [...m, { from: "user", text, time: now }]);
    setInput("");
    
    let label = `${agent.name} is thinking...`;
    if (agent.tools && agent.tools.length > 0) {
      if (agent.tools.includes("RAG Knowledge Base") && anyWordMatches(text, ["search", "knowledge", "document", "policy", "info"])) {
        label = "Checking company documents (RAG)...";
      } else if (agent.tools.includes("Web Search") && anyWordMatches(text, ["web", "search", "google", "news"])) {
        label = "Searching the web...";
      }
    }
    setThinking(label);
    
    fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: text, agentName: id })
    })
      .then((res) => res.json())
      .then((data) => {
        setMessages((m) => [...m, data]);
        setThinking(null);
      })
      .catch((err) => {
        console.error("Error chatting with agent:", err);
        setMessages((m) => [
          ...m,
          { from: "agent", text: "Sorry, I encountered an error connecting to the agent's brain.", time: now }
        ]);
        setThinking(null);
      });
  };

  return (
    <div className="min-h-screen flex flex-col bg-background">
      {/* Top bar */}
      <div className="h-[60px] border-b border-border bg-surface flex items-center justify-between px-6 shrink-0">
        <div className="flex items-center gap-4 min-w-0">
          <button
            onClick={() => navigate({ to: "/" })}
            className="text-[13px] text-muted-foreground hover:text-foreground transition-colors"
          >
            ← Dashboard
          </button>
          <div className="h-5 w-px bg-border" />
          <div className="flex items-center gap-2.5 min-w-0">
            <div className="h-8 w-8 rounded-full bg-accent-tint flex items-center justify-center text-base shrink-0">
              {agent.icon}
            </div>
            <span className="text-base font-semibold text-foreground truncate">{agent.name}</span>
          </div>
        </div>
        <div className="hidden md:flex items-center gap-1.5 flex-wrap">
          {agent.tools.map((t) => (
            <ToolBadge key={t}>{t}</ToolBadge>
          ))}
        </div>
        <div className="flex items-center gap-3">
          <StatusBadge status={agent.status} />
          <div className="relative">
            <button
              onClick={() => setShowMoreMenu(!showMoreMenu)}
              className="h-8 w-8 rounded-lg flex items-center justify-center text-muted-foreground hover:bg-surface-muted hover:text-foreground transition-colors"
              aria-label="More"
            >
              <MoreVertical size={16} />
            </button>
            {showMoreMenu && (
              <>
                <div className="fixed inset-0 z-10" onClick={() => setShowMoreMenu(false)} />
                <div className="af-fade-in absolute right-0 top-10 z-20 w-48 rounded-lg border border-border bg-surface shadow-lg py-1">
                  <button
                    onClick={clearConversation}
                    className="w-full px-4 py-2 text-left text-sm text-destructive hover:bg-destructive/10 transition-colors"
                  >
                    Clear Conversation
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Info strip */}
      <div className="bg-accent-tint border-b border-accent/20 px-6 py-2.5 flex items-center justify-between gap-3">
        <div className="flex items-center gap-2 text-[13px] text-foreground/80 min-w-0">
          <Info size={14} className="text-accent shrink-0" />
          <span className="truncate">{agent.purpose}</span>
        </div>
        <span className="text-xs text-muted-foreground/70 hidden sm:block">
          Powered by AgentForge
        </span>
      </div>

      {/* Quick actions */}
      <div className="border-b border-border px-6 py-3 overflow-x-auto af-scroll shrink-0">
        <div className="flex gap-2 whitespace-nowrap">
          {agent.quickActions.map((q) => (
            <button
              key={q}
              onClick={() => send(q)}
              className="rounded-full border border-border bg-surface px-4 py-2 text-[13px] font-medium text-foreground hover:border-accent hover:text-accent transition-colors"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Chat */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto af-scroll">
        <div className="max-w-[800px] mx-auto px-8 py-6 space-y-5">
          <div className="flex justify-center">
            <span className="rounded-full border border-border bg-surface-muted px-3 py-1 text-[11px] text-muted-foreground">
              Today
            </span>
          </div>
          {messages.map((m, i) =>
            m.from === "user" ? (
              <div key={i} className="af-msg-in flex flex-col items-end">
                <div className="max-w-[70%] rounded-[12px_12px_2px_12px] border border-border bg-surface-muted px-4 py-3 text-sm text-foreground">
                  {m.text}
                </div>
                <span className="mt-1 text-[11px] text-muted-foreground">{m.time}</span>
              </div>
            ) : (
              <div key={i} className="af-msg-in max-w-[75%]">
                <div className="border-l-[3px] border-accent pl-4 text-sm leading-[1.7] text-foreground">
                  {m.text}
                </div>
                <span className="mt-1 ml-4 block text-[11px] text-muted-foreground">{m.time}</span>
              </div>
            )
          )}
          {thinking && (
            <div className="max-w-[75%] space-y-1">
              <ToolCallIndicator label={thinking} />
              <ThinkingIndicator />
            </div>
          )}
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-border shrink-0">
        <div className="max-w-[800px] mx-auto px-8 py-5">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
            className="relative"
          >
            <textarea
              ref={taRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send(input);
                }
              }}
              placeholder={`Ask ${agent.name}...`}
              rows={1}
              className="w-full resize-none rounded-xl border border-border bg-surface pl-5 pr-16 py-4 text-sm placeholder:text-muted-foreground focus:outline-none focus:border-accent focus:ring-4 focus:ring-accent/15 transition-all"
              style={{ minHeight: 52 }}
            />
            <button
              type="submit"
              className="absolute right-2.5 bottom-2.5 h-9 w-9 rounded-lg bg-accent text-accent-foreground flex items-center justify-center hover:bg-accent/90 transition-colors"
              aria-label="Send"
            >
              <Send size={15} />
            </button>
          </form>
          <p className="mt-2 text-center text-[12px] text-muted-foreground/70">
            {agent.name} can make mistakes. Verify important information.
          </p>
        </div>
      </div>
    </div>
  );
}
