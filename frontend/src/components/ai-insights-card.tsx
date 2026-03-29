"use client";

import { Sparkles, BrainCircuit, RefreshCw, CheckCircle2, Info, AlertTriangle, AlertCircle } from "lucide-react";
import { useManagerThesis, useBehavioralBias } from "@/hooks/use-insights";
import { InsightFinding, InsightReport, FindingType } from "@/lib/api";

// ─── Finding type config ──────────────────────────────────────────────────────
const findingConfig: Record<FindingType, { icon: React.ReactNode; pill: string; text: string }> = {
  success: {
    icon: <CheckCircle2 className="w-3.5 h-3.5 shrink-0 mt-0.5" />,
    pill: "bg-emerald-500/10 text-emerald-700 dark:text-emerald-400 border-emerald-500/20",
    text: "text-emerald-800 dark:text-emerald-300",
  },
  info: {
    icon: <Info className="w-3.5 h-3.5 shrink-0 mt-0.5" />,
    pill: "bg-blue-500/10 text-blue-700 dark:text-blue-400 border-blue-500/20",
    text: "text-blue-800 dark:text-blue-300",
  },
  caution: {
    icon: <AlertCircle className="w-3.5 h-3.5 shrink-0 mt-0.5" />,
    pill: "bg-amber-500/10 text-amber-700 dark:text-amber-400 border-amber-500/20",
    text: "text-amber-800 dark:text-amber-300",
  },
  warning: {
    icon: <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />,
    pill: "bg-rose-500/10 text-rose-700 dark:text-rose-400 border-rose-500/20",
    text: "text-rose-800 dark:text-rose-300",
  },
};

// ─── Single finding row ───────────────────────────────────────────────────────
function FindingRow({ finding }: { finding: InsightFinding }) {
  const cfg = findingConfig[finding.type] ?? findingConfig.info;
  return (
    <div className={`flex gap-2.5 rounded-xl border p-3 ${cfg.pill}`}>
      {cfg.icon}
      <div className="flex flex-col gap-0.5 min-w-0">
        <p className="text-[11px] font-bold tracking-wide leading-tight">{finding.title}</p>
        <p className="text-[11px] leading-relaxed opacity-80">{finding.detail}</p>
      </div>
    </div>
  );
}

// ─── Skeleton loader ──────────────────────────────────────────────────────────
function InsightSkeleton({ lines = 3 }: { lines?: number }) {
  return (
    <div className="space-y-2.5 mt-1">
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="h-14 rounded-xl bg-zinc-200/60 dark:bg-zinc-800/60 animate-pulse" />
      ))}
    </div>
  );
}

// ─── Insight card shell ───────────────────────────────────────────────────────
function InsightCard({
  title, icon, accentClass, glowClass, report, isLoading, isError, error, onRefresh, refetching,
}: {
  title: string;
  icon: React.ReactNode;
  accentClass: string;
  glowClass: string;
  report: InsightReport | undefined;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  onRefresh: () => void;
  refetching: boolean;
}) {
  const generatedAt = report?.generated_at
    ? new Date(report.generated_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
    : null;

  return (
    <div className={`relative overflow-hidden rounded-3xl border shadow-sm p-5 group ${accentClass}`}>
      {/* Ambient glow */}
      <div className={`absolute -right-6 -top-6 w-36 h-36 rounded-full blur-[40px] transition-all duration-700 ${glowClass}`} />

      {/* Header */}
      <div className="flex items-center justify-between mb-4 relative">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-xl bg-white/60 dark:bg-zinc-900/60 shadow-sm">{icon}</div>
          <div>
            <h3 className="font-semibold text-sm tracking-tight">{title}</h3>
            {generatedAt && (
              <p className="text-[10px] text-zinc-400 dark:text-zinc-500 mt-0.5">Updated {generatedAt}</p>
            )}
          </div>
        </div>
        <button
          onClick={onRefresh}
          disabled={refetching || isLoading}
          title="Re-generate"
          className="p-1.5 rounded-lg hover:bg-zinc-100 dark:hover:bg-zinc-800/60 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors disabled:opacity-40"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${refetching ? "animate-spin" : ""}`} />
        </button>
      </div>

      {/* Body */}
      <div className="relative flex flex-col gap-2">
        {isLoading ? (
          <InsightSkeleton />
        ) : isError ? (
          <div className="rounded-xl bg-rose-500/10 border border-rose-500/20 p-3 text-xs text-rose-700 dark:text-rose-400">
            {error?.message ?? "Failed to load insights."}
          </div>
        ) : report?.findings?.length ? (
          report.findings.map((f, i) => <FindingRow key={i} finding={f} />)
        ) : (
          <p className="text-xs text-zinc-400 dark:text-zinc-500 py-4 text-center">No findings available.</p>
        )}
      </div>
    </div>
  );
}

// ─── Main export ──────────────────────────────────────────────────────────────
export default function AIInsightsCard() {
  const thesis  = useManagerThesis();
  const biases  = useBehavioralBias();

  return (
    <div className="flex flex-col gap-5">
      <InsightCard
        title="Manager Thesis"
        icon={<Sparkles className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />}
        accentClass="bg-indigo-50/50 dark:bg-indigo-950/20 border-indigo-100 dark:border-indigo-900/50"
        glowClass="bg-indigo-500/10 dark:bg-indigo-500/5 group-hover:bg-indigo-500/20"
        report={thesis.data}
        isLoading={thesis.isLoading}
        isError={thesis.isError}
        error={thesis.error}
        onRefresh={() => thesis.refetch()}
        refetching={thesis.isFetching && !thesis.isLoading}
      />
      <InsightCard
        title="Behavioral Biases"
        icon={<BrainCircuit className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />}
        accentClass="bg-emerald-50/50 dark:bg-emerald-950/20 border-emerald-100 dark:border-emerald-900/50"
        glowClass="bg-emerald-500/10 dark:bg-emerald-500/5 group-hover:bg-emerald-500/20"
        report={biases.data}
        isLoading={biases.isLoading}
        isError={biases.isError}
        error={biases.error}
        onRefresh={() => biases.refetch()}
        refetching={biases.isFetching && !biases.isLoading}
      />
    </div>
  );
}
