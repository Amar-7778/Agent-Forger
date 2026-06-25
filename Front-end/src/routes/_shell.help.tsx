import { createFileRoute } from "@tanstack/react-router";
import { HelpCircle, ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

export const Route = createFileRoute("/_shell/help")({
  head: () => ({
    meta: [{ title: "Help & Docs — AgentForge" }],
  }),
  component: HelpPage,
});

interface FAQItemProps {
  question: string;
  answer: string;
}

function FAQItem({ question, answer }: FAQItemProps) {
  const [open, setOpen] = useState(false);
  return (
    <div className="border border-border rounded-xl bg-surface overflow-hidden transition-all hover:border-accent/30">
      <button
        onClick={() => setOpen(!open)}
        className="w-full px-6 py-4 text-left flex justify-between items-center font-semibold text-sm text-foreground hover:bg-surface-muted/50 transition-colors"
      >
        <span>{question}</span>
        {open ? <ChevronUp size={16} className="text-accent" /> : <ChevronDown size={16} className="text-muted-foreground" />}
      </button>
      {open && (
        <div className="px-6 pb-5 pt-1 text-xs text-muted-foreground leading-relaxed border-t border-border/40 bg-surface-muted/30">
          {answer}
        </div>
      )}
    </div>
  );
}

function HelpPage() {
  const faqs = [
    {
      question: "How do I create a custom agent?",
      answer: "Go to the 'My Agents' page using the sidebar link, and click on the 'Build New Agent' button. Enter the agent's name, description/purpose, restrictions, select a color theme, and toggle any required toolsets (e.g. Web Search or RAG Knowledge Base). Click 'Create Agent' and it will instantly spawn in your workspace and appear in the sidebar.",
    },
    {
      question: "How does the RAG Knowledge Base work?",
      answer: "Go to the 'Knowledge Base' page via the sidebar link. Upload company documents (such as PDF, DOCX, TXT, or CSV files) and click 'Ingest Documents'. The files will be processed, parsed into text chunks, embedded using a local MiniLM machine learning model, and stored in a local vector database. Any custom agent built with the 'RAG Knowledge Base' tool enabled will automatically check this context search database when answering relevant queries.",
    },
    {
      question: "How do I schedule background tasks?",
      answer: "Go to the 'Scheduled Tasks' page and click 'Schedule New Task'. Select the agent you want to run, outline the task description (what it should execute), write down the recurrence frequency (as an interval in minutes, or as a standard Cron expression like '0 9 * * 1' for every Monday at 9am), and save. The scheduler daemon in the background will run jobs on schedule.",
    },
    {
      question: "How do I change the user interface theme?",
      answer: "Go to 'Settings' page. You will see visual cards for Cyberpunk Dark (default deep neon styling), Deep Space Blue (dark atmospheric blue styling), and Nordic Light (a clean bright white styling). Clicking any theme card will switch themes instantly. Theme choices are saved to your local browser storage.",
    },
    {
      question: "How do I delete an agent?",
      answer: "Go to 'Settings' page. Scroll down to the 'Registered Agents' section, locate the agent you want to delete, and click its 'Delete' button. A warning modal will pop up. Confirming deletion will remove the agent configuration, its scheduled automation schedules, and all associated chat logs permanently from the database.",
    },
  ];

  return (
    <div className="p-8 max-w-[900px] mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
          <HelpCircle size={28} className="text-accent" /> Help & Documentation
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Find answers and learn how to configure and execute agents within AgentForge.
        </p>
      </div>

      <div className="space-y-3 pt-2">
        {faqs.map((f, i) => (
          <FAQItem key={i} question={f.question} answer={f.answer} />
        ))}
      </div>
    </div>
  );
}
