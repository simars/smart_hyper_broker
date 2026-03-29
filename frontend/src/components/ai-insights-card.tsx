"use client";

import { Sparkles, BrainCircuit } from "lucide-react";

export default function AIInsightsCard() {
  return (
    <div className="flex flex-col gap-6">
      {/* Manager Thesis Validation Widget */}
      <div className="relative overflow-hidden rounded-3xl bg-indigo-50/50 dark:bg-indigo-950/20 border border-indigo-100 dark:border-indigo-900/50 shadow-sm p-6 group">
        <div className="absolute -right-4 -top-4 w-32 h-32 bg-indigo-500/10 rounded-full blur-[32px] group-hover:bg-indigo-500/20 transition-all duration-700" />
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 rounded-xl bg-indigo-100 dark:bg-indigo-900">
            <Sparkles className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
          </div>
          <h3 className="font-semibold text-indigo-900 dark:text-indigo-100">Manager Thesis</h3>
        </div>
        <div className="space-y-3">
          <div className="h-4 w-3/4 rounded bg-indigo-200/50 dark:bg-indigo-800/50 animate-pulse" />
          <div className="h-4 w-full rounded bg-indigo-200/50 dark:bg-indigo-800/50 animate-pulse" />
          <div className="h-4 w-5/6 rounded bg-indigo-200/50 dark:bg-indigo-800/50 animate-pulse" />
        </div>
        <p className="mt-6 text-sm text-indigo-700/70 dark:text-indigo-300/50 font-medium">
          Awaiting NotebookLM context injection via MCP interface.
        </p>
      </div>

      {/* Behavioral Bias Widget */}
      <div className="relative overflow-hidden rounded-3xl bg-emerald-50/50 dark:bg-emerald-950/20 border border-emerald-100 dark:border-emerald-900/50 shadow-sm p-6 group">
        <div className="absolute -left-4 -bottom-4 w-32 h-32 bg-emerald-500/10 rounded-full blur-[32px] group-hover:bg-emerald-500/20 transition-all duration-700" />
        <div className="flex items-center gap-2 mb-4">
          <div className="p-2 rounded-xl bg-emerald-100 dark:bg-emerald-900">
            <BrainCircuit className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
          </div>
          <h3 className="font-semibold text-emerald-900 dark:text-emerald-100">Behavioral Biases</h3>
        </div>
        <div className="space-y-3">
          <div className="h-4 w-2/3 rounded bg-emerald-200/50 dark:bg-emerald-800/50 animate-pulse" />
          <div className="h-4 w-full rounded bg-emerald-200/50 dark:bg-emerald-800/50 animate-pulse" />
          <div className="h-4 w-4/5 rounded bg-emerald-200/50 dark:bg-emerald-800/50 animate-pulse" />
        </div>
        <p className="mt-6 text-sm text-emerald-700/70 dark:text-emerald-300/50 font-medium">
          Awaiting deep behavioral scanning against open loss distributions.
        </p>
      </div>
    </div>
  );
}
