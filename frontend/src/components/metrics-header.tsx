"use client";

import { useState } from "react";
import { usePositions } from "@/hooks/use-positions";
import { ArrowUpRight, ArrowDownRight, Wallet, Activity } from "lucide-react";
import { UploadRbcCsv } from "./upload-rbc-csv";

type BaseCurrency = "CAD" | "USD";

// ─── Module-level component (not inside render) ───────────────────────────────
function CurrencyToggle({
  baseCurrency,
  setBaseCurrency,
}: {
  baseCurrency: BaseCurrency;
  setBaseCurrency: (c: BaseCurrency) => void;
}) {
  return (
    <div className="flex items-center gap-1 rounded-xl bg-zinc-100 dark:bg-zinc-800 p-1">
      {(["CAD", "USD"] as BaseCurrency[]).map((c) => (
        <button
          key={c}
          onClick={() => setBaseCurrency(c)}
          className={`px-3 py-1 rounded-lg text-xs font-bold tracking-wider transition-all duration-200 ${
            baseCurrency === c
              ? "bg-white dark:bg-zinc-700 text-zinc-900 dark:text-zinc-50 shadow-sm"
              : "text-zinc-500 dark:text-zinc-400 hover:text-zinc-700 dark:hover:text-zinc-200"
          }`}
        >
          {c}
        </button>
      ))}
    </div>
  );
}

// ─── Main Component ──────────────────────────────────────────────────────────
export default function MetricsHeader() {
  const { data: res, isLoading, isError } = usePositions();
  const [baseCurrency, setBaseCurrency] = useState<BaseCurrency>("CAD");

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-pulse">
        <div className="h-36 rounded-3xl bg-zinc-200/50 dark:bg-zinc-800/50 backdrop-blur-md" />
        <div className="h-36 rounded-3xl bg-zinc-200/50 dark:bg-zinc-800/50 backdrop-blur-md" />
        <div className="h-36 rounded-3xl bg-zinc-200/50 dark:bg-zinc-800/50 backdrop-blur-md" />
      </div>
    );
  }

  const positions = res?.data || [];

  if (isError || !res) {
    return (
      <div className="p-6 rounded-2xl bg-red-500/10 border border-red-500/20 text-red-600 dark:text-red-400">
        <p className="font-medium">Error loading portfolio metrics. Is the API running?</p>
      </div>
    );
  }

  // Aggregate totals in the chosen base currency
  const totalMarketVal = positions.reduce(
    (acc, pos) => acc + (baseCurrency === "CAD" ? pos.market_val_cad : pos.market_val_usd),
    0
  );
  const totalOpenPnl = positions.reduce(
    (acc, pos) => acc + (baseCurrency === "CAD" ? pos.open_pnl_cad : pos.open_pnl_usd),
    0
  );
  const totalDayPnl = positions.reduce(
    (acc, pos) => acc + (baseCurrency === "CAD" ? pos.day_pnl_cad : pos.day_pnl_usd),
    0
  );

  const fmt = (val: number) =>
    new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: baseCurrency,
      maximumFractionDigits: 2,
    }).format(val);

  const isOpenPositive = totalOpenPnl >= 0;
  const isDayPositive  = totalDayPnl  >= 0;

  return (
    <div className="flex flex-col gap-4">
      {/* Top Controls: Upload RBC CSV and Currency Toggle */}
      <div className="flex items-center justify-between">
        <UploadRbcCsv />
        <div className="flex items-center gap-2">
          <span className="text-xs text-zinc-500 dark:text-zinc-400 font-medium">Base currency</span>
          <CurrencyToggle baseCurrency={baseCurrency} setBaseCurrency={setBaseCurrency} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Net Asset Value */}
        <div className="relative overflow-hidden rounded-3xl bg-white/60 dark:bg-zinc-900/40 border border-zinc-200 dark:border-zinc-800/50 shadow-sm backdrop-blur-xl hover:shadow-md hover:bg-white/80 dark:hover:bg-zinc-900/60 transition-all p-6 flex flex-col gap-2">
          <div className="absolute -right-4 -top-4 w-24 h-24 bg-indigo-500/10 dark:bg-indigo-500/5 rounded-full blur-[24px]" />
          <div className="flex items-center gap-2 text-zinc-500 dark:text-zinc-400">
            <Wallet className="w-4 h-4" />
            <h3 className="text-xs font-semibold tracking-widest uppercase">Net Asset Value</h3>
          </div>
          <p className="text-4xl font-bold tracking-tight text-zinc-900 dark:text-zinc-50 mt-1">
            {fmt(totalMarketVal)}
          </p>
          <p className="text-xs font-medium text-zinc-400 dark:text-zinc-500 mt-2">
            Combined global holdings · {baseCurrency}
          </p>
        </div>

        {/* Unrealized PnL */}
        <div className="relative overflow-hidden rounded-3xl bg-white/60 dark:bg-zinc-900/40 border border-zinc-200 dark:border-zinc-800/50 shadow-sm backdrop-blur-xl hover:shadow-md hover:bg-white/80 dark:hover:bg-zinc-900/60 transition-all p-6 flex flex-col gap-2">
          <div className={`absolute -right-4 -bottom-4 w-24 h-24 rounded-full blur-[24px] ${isOpenPositive ? "bg-emerald-500/10 dark:bg-emerald-500/5" : "bg-rose-500/10 dark:bg-rose-500/5"}`} />
          <div className="flex items-center gap-2 text-zinc-500 dark:text-zinc-400">
            <Activity className="w-4 h-4" />
            <h3 className="text-xs font-semibold tracking-widest uppercase">Unrealized PnL</h3>
          </div>
          <p className={`text-4xl font-bold tracking-tight mt-1 ${isOpenPositive ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}>
            {totalOpenPnl > 0 ? "+" : ""}{fmt(totalOpenPnl)}
          </p>
          <div className={`flex items-center gap-1.5 mt-2 text-xs font-medium ${isOpenPositive ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}>
            {isOpenPositive ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
            Open positions · {baseCurrency}
          </div>
        </div>

        {/* Daily PnL */}
        <div className="relative overflow-hidden rounded-3xl bg-white/60 dark:bg-zinc-900/40 border border-zinc-200 dark:border-zinc-800/50 shadow-sm backdrop-blur-xl hover:shadow-md hover:bg-white/80 dark:hover:bg-zinc-900/60 transition-all p-6 flex flex-col gap-2">
          <div className={`absolute -left-4 -top-4 w-24 h-24 rounded-full blur-[24px] ${isDayPositive ? "bg-emerald-500/10 dark:bg-emerald-500/5" : "bg-rose-500/10 dark:bg-rose-500/5"}`} />
          <div className="flex items-center gap-2 text-zinc-500 dark:text-zinc-400">
            <Activity className="w-4 h-4" />
            <h3 className="text-xs font-semibold tracking-widest uppercase">Daily PnL</h3>
          </div>
          <p className={`text-4xl font-bold tracking-tight mt-1 ${isDayPositive ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}>
            {totalDayPnl > 0 ? "+" : ""}{fmt(totalDayPnl)}
          </p>
          <div className={`flex items-center gap-1.5 mt-2 text-xs font-medium ${isDayPositive ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}>
            {isDayPositive ? <ArrowUpRight className="w-3.5 h-3.5" /> : <ArrowDownRight className="w-3.5 h-3.5" />}
            Today&apos;s movement · {baseCurrency}
          </div>
        </div>
      </div>
    </div>
  );
}
