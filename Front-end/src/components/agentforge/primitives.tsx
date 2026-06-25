import { type ReactNode, type ButtonHTMLAttributes, useEffect } from "react";
import { X } from "lucide-react";

export function SectionLabel({ children, action }: { children: ReactNode; action?: ReactNode }) {
  return (
    <div className="flex items-center justify-between px-3 mb-2">
      <span className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
        {children}
      </span>
      {action}
    </div>
  );
}

export function StatusBadge({ status }: { status: "active" | "inactive" | "paused" }) {
  if (status === "active") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-success/20 bg-success-tint px-2 py-0.5 text-[11px] font-semibold text-success">
        <span className="h-1.5 w-1.5 rounded-full bg-success" />
        Active
      </span>
    );
  }
  if (status === "paused") {
    return (
      <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface-muted px-2 py-0.5 text-[11px] font-semibold text-muted-foreground">
        Paused
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface-muted px-2 py-0.5 text-[11px] font-semibold text-muted-foreground">
      <span className="h-1.5 w-1.5 rounded-full bg-muted-foreground/50" />
      Inactive
    </span>
  );
}

export function ToolBadge({ children }: { children: ReactNode }) {
  return (
    <span className="inline-flex items-center rounded-full border border-accent/20 bg-accent-tint px-2.5 py-0.5 text-[11px] font-semibold uppercase tracking-wide text-accent">
      {children}
    </span>
  );
}

export function Button({
  variant = "primary",
  className = "",
  children,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "ghost" | "danger" }) {
  const base =
    "inline-flex items-center justify-center gap-2 rounded-lg text-sm font-semibold transition-all duration-150 active:translate-y-0 disabled:opacity-50 disabled:pointer-events-none";
  const variants: Record<string, string> = {
    primary:
      "bg-accent text-accent-foreground px-4 py-2 hover:-translate-y-px hover:bg-accent/90 shadow-sm",
    secondary:
      "bg-surface text-foreground border border-border px-4 py-2 hover:-translate-y-px hover:border-border-strong",
    ghost: "text-foreground px-3 py-1.5 hover:bg-surface-muted",
    danger:
      "bg-destructive text-destructive-foreground px-4 py-2 hover:-translate-y-px hover:bg-destructive/90",
  };
  return (
    <button className={`${base} ${variants[variant]} ${className}`} {...rest}>
      {children}
    </button>
  );
}

export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-12 px-6">
      <div className="text-5xl opacity-60 mb-4">{icon}</div>
      <h3 className="text-base font-semibold text-foreground">{title}</h3>
      {description && <p className="mt-1 text-sm text-muted-foreground max-w-sm">{description}</p>}
      {action && <div className="mt-6">{action}</div>}
    </div>
  );
}

export function Modal({
  open,
  onClose,
  title,
  children,
  destructive,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  destructive?: boolean;
}) {
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);

  if (!open) return null;
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 af-fade-in">
      <div
        className="absolute inset-0 bg-foreground/40 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden
      />
      <div
        className={`relative af-modal-in w-[90vw] max-w-[480px] rounded-2xl border ${
          destructive ? "border-destructive/30" : "border-border"
        } bg-surface p-8 shadow-2xl`}
      >
        <div className="flex items-start justify-between mb-4">
          <h2 className={`text-xl font-bold ${destructive ? "text-destructive" : "text-foreground"}`}>
            {title}
          </h2>
          <button
            onClick={onClose}
            className="rounded-md p-1 text-muted-foreground hover:bg-surface-muted hover:text-foreground transition-colors"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}

export function ThinkingIndicator() {
  return (
    <div className="af-msg-in border-l-[3px] border-accent pl-4 py-2">
      <div className="flex items-center gap-1.5">
        <span className="h-2 w-2 rounded-full bg-accent af-bounce" style={{ animationDelay: "0s" }} />
        <span className="h-2 w-2 rounded-full bg-accent af-bounce" style={{ animationDelay: "0.15s" }} />
        <span className="h-2 w-2 rounded-full bg-accent af-bounce" style={{ animationDelay: "0.3s" }} />
      </div>
    </div>
  );
}

export function ToolCallIndicator({ label }: { label: string }) {
  return (
    <div className="af-msg-in mb-2 inline-block overflow-hidden rounded-md border border-accent/20 bg-accent-tint">
      <div className="px-3 py-1.5 text-xs font-medium text-accent">{label}</div>
      <div className="h-[2px] w-full bg-accent/10">
        <div className="h-full bg-accent af-progress" />
      </div>
    </div>
  );
}
