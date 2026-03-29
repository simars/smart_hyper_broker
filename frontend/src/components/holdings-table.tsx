"use client";

import { useState, useMemo } from "react";
import { usePositions } from "@/hooks/use-positions";
import { BrokerAuthError, Position } from "@/lib/api";
import {
  ArrowUpRight, ArrowDownRight, Globe,
  TriangleAlert, RefreshCw,
  ArrowUp, ArrowDown, ChevronsUpDown,
  Search, X, Layers, List,
} from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────
type SortKey = "symbol" | "qty" | "average_buying_price" | "market_val" | "open_pnl" | "day_pnl";
type SortDir = "asc" | "desc" | "none";

interface AccountSlot {
  broker: string;
  account_type: string;
  account_id: string;
}

/** A single row in grouped view — one entry per unique symbol. */
interface GroupedPosition {
  symbol: string;
  qty: number;
  average_buying_price: number; // qty-weighted average
  market_val: number;
  open_pnl: number;
  day_pnl: number;
  currency: string; // "MIX" if positions have different native currencies
  brokers: string[]; // unique, ordered
  accounts: AccountSlot[];
  rowCount: number;
}

// ─── Grouping logic ───────────────────────────────────────────────────────────
function groupBySymbol(positions: Position[]): GroupedPosition[] {
  const map = new Map<string, GroupedPosition>();

  for (const pos of positions) {
    const existing = map.get(pos.symbol);
    if (!existing) {
      map.set(pos.symbol, {
        symbol: pos.symbol,
        qty: pos.qty,
        average_buying_price: pos.average_buying_price, // will be recalculated below
        market_val: pos.market_val,
        open_pnl: pos.open_pnl,
        day_pnl: pos.day_pnl,
        currency: pos.currency,
        brokers: [pos.broker],
        accounts: [{ broker: pos.broker, account_type: pos.account_type, account_id: pos.account_id }],
        rowCount: 1,
        // store running weighted qty×price for avg calculation
        ..._wtotal(pos.qty, pos.average_buying_price),
      });
    } else {
      const newQty = existing.qty + pos.qty;
      // qty-weighted average entry price
      const prevWTotal = existing._wtotal ?? existing.qty * existing.average_buying_price;
      const newWTotal = prevWTotal + pos.qty * pos.average_buying_price;

      existing.qty = newQty;
      existing.average_buying_price = newQty > 0 ? newWTotal / newQty : 0;
      existing._wtotal = newWTotal;
      existing.market_val += pos.market_val;
      existing.open_pnl += pos.open_pnl;
      existing.day_pnl += pos.day_pnl;
      existing.currency = existing.currency === pos.currency ? pos.currency : "MIX";
      existing.rowCount += 1;
      if (!existing.brokers.includes(pos.broker)) existing.brokers.push(pos.broker);
      existing.accounts.push({ broker: pos.broker, account_type: pos.account_type, account_id: pos.account_id });
    }
  }

  return Array.from(map.values());
}

// Internal: attach _wtotal to initialise the weighted-average accumulator.
function _wtotal(qty: number, price: number) {
  return { _wtotal: qty * price } as { _wtotal: number };
}

// ─── Fuzzy match ──────────────────────────────────────────────────────────────
function fuzzyMatch(target: string, query: string): boolean {
  if (!query) return true;
  const t = target.toLowerCase();
  const q = query.toLowerCase().replace(/\s+/g, "");
  let ti = 0;
  for (let qi = 0; qi < q.length; qi++) {
    while (ti < t.length && t[ti] !== q[qi]) ti++;
    if (ti >= t.length) return false;
    ti++;
  }
  return true;
}

// ─── Sort helpers ─────────────────────────────────────────────────────────────
function nextDir(current: SortDir): SortDir {
  if (current === "none") return "asc";
  if (current === "asc") return "desc";
  return "none";
}

function sortRows<T extends { [k: string]: unknown }>(
  rows: T[], key: SortKey, dir: SortDir
): T[] {
  if (dir === "none") return rows;
  return [...rows].sort((a, b) => {
    const av = a[key];
    const bv = b[key];
    if (typeof av === "string" && typeof bv === "string")
      return dir === "asc" ? av.localeCompare(bv) : bv.localeCompare(av);
    return dir === "asc"
      ? (av as number) - (bv as number)
      : (bv as number) - (av as number);
  });
}

// ─── Display helpers ──────────────────────────────────────────────────────────
function formatCurrency(val: number, cur: string): string {
  try {
    const safe = cur && cur.length === 3 && cur !== "N/A" && cur !== "MIX"
      ? cur.toUpperCase() : "USD";
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: safe,
      currencyDisplay: "narrowSymbol",
    }).format(val);
  } catch {
    return `$${Number(val).toFixed(2)}`;
  }
}

function CurrencyBadge({ cur }: { cur: string }) {
  const label = cur && cur.length === 3 && cur !== "N/A" ? cur.toUpperCase() : "USD";
  return (
    <span className="ml-1.5 text-[10px] font-semibold text-zinc-400 dark:text-zinc-500 tracking-wider">
      {label}
    </span>
  );
}

function BrokerBadge({ broker }: { broker: string }) {
  const isMoomoo = broker.toLowerCase() === "moomoo";
  return (
    <span className={`inline-flex items-center px-1.5 py-0.5 rounded-sm text-[10px] uppercase font-bold tracking-wider ${
      isMoomoo
        ? "bg-orange-500/10 text-orange-600 dark:text-orange-400 border border-orange-500/20"
        : "bg-green-500/10 text-green-600 dark:text-green-400 border border-green-500/20"
    }`}>
      {broker}
    </span>
  );
}

function SortIcon({ col, sortKey, sortDir }: { col: SortKey; sortKey: SortKey; sortDir: SortDir }) {
  if (col !== sortKey || sortDir === "none") return <ChevronsUpDown className="w-3.5 h-3.5 opacity-30" />;
  return sortDir === "asc"
    ? <ArrowUp className="w-3.5 h-3.5 text-indigo-500" />
    : <ArrowDown className="w-3.5 h-3.5 text-indigo-500" />;
}

function ColHeader({ col, label, sortKey, sortDir, onSort }: {
  col: SortKey; label: string;
  sortKey: SortKey; sortDir: SortDir;
  onSort: (col: SortKey) => void;
}) {
  return (
    <th
      className="px-6 py-4 font-semibold text-right cursor-pointer select-none hover:text-zinc-700 dark:hover:text-zinc-200 transition-colors"
      onClick={() => onSort(col)}
    >
      <div className="flex items-center justify-end gap-1.5">
        {label}
        <SortIcon col={col} sortKey={sortKey} sortDir={sortDir} />
      </div>
    </th>
  );
}

// ─── Shared table chrome ──────────────────────────────────────────────────────
function TableHeader({ sortKey, sortDir, onSort }: {
  sortKey: SortKey; sortDir: SortDir; onSort: (c: SortKey) => void;
}) {
  return (
    <thead className="bg-zinc-50/50 dark:bg-zinc-900/50 border-b border-zinc-200 dark:border-zinc-800/50 text-zinc-500 dark:text-zinc-400">
      <tr>
        <th
          className="px-6 py-4 font-semibold cursor-pointer select-none hover:text-zinc-700 dark:hover:text-zinc-200 transition-colors"
          onClick={() => onSort("symbol")}
        >
          <div className="flex items-center gap-1.5">
            Asset Node
            <SortIcon col="symbol" sortKey={sortKey} sortDir={sortDir} />
          </div>
        </th>
        <ColHeader col="qty"                  label="Volume"       sortKey={sortKey} sortDir={sortDir} onSort={onSort} />
        <ColHeader col="average_buying_price" label="Avg Entry"    sortKey={sortKey} sortDir={sortDir} onSort={onSort} />
        <ColHeader col="market_val"           label="Market Value" sortKey={sortKey} sortDir={sortDir} onSort={onSort} />
        <ColHeader col="open_pnl"             label="Open PnL"     sortKey={sortKey} sortDir={sortDir} onSort={onSort} />
        <ColHeader col="day_pnl"              label="Day PnL"      sortKey={sortKey} sortDir={sortDir} onSort={onSort} />
      </tr>
    </thead>
  );
}

// ─── Root component ───────────────────────────────────────────────────────────
export default function HoldingsTable() {
  const { data: positions, isLoading, error, refetch, isFetching } = usePositions();
  const [sortKey,  setSortKey]  = useState<SortKey>("symbol");
  const [sortDir,  setSortDir]  = useState<SortDir>("none");
  const [search,   setSearch]   = useState("");
  const [grouped,  setGrouped]  = useState(false); // default: ungrouped

  if (isLoading) {
    return (
      <div className="w-full rounded-3xl bg-white/60 dark:bg-zinc-900/40 border border-zinc-200 dark:border-zinc-800/50 backdrop-blur-xl p-8 h-[500px] flex items-center justify-center">
        <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
      </div>
    );
  }

  if (error) {
    const isAuthError = error instanceof BrokerAuthError;
    const brokerName  = isAuthError ? (error as BrokerAuthError).broker : "broker";
    return (
      <div className="w-full rounded-3xl bg-amber-50/60 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800/50 backdrop-blur-xl p-8">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-2xl bg-amber-100 dark:bg-amber-900/50 shrink-0">
            <TriangleAlert className="w-6 h-6 text-amber-600 dark:text-amber-400" />
          </div>
          <div className="flex flex-col gap-2 flex-1">
            <h3 className="font-bold text-lg text-amber-900 dark:text-amber-100 capitalize">
              {brokerName} Authentication Required
            </h3>
            <p className="text-sm text-amber-800/80 dark:text-amber-200/70 leading-relaxed">{error.message}</p>
            {isAuthError && (
              <ol className="mt-3 text-sm text-amber-800/70 dark:text-amber-200/60 space-y-1 list-decimal list-inside">
                <li>Open <strong>Questrade App Hub</strong> and log in.</li>
                <li>Navigate to <strong>API Access</strong> → generate a new <strong>Personal API Token</strong>.</li>
                <li>Paste the refresh token into <code className="text-xs bg-amber-200/50 dark:bg-amber-800/50 px-1 py-0.5 rounded">.env</code> as <code className="text-xs bg-amber-200/50 dark:bg-amber-800/50 px-1 py-0.5 rounded">QUESTRADE_REFRESH_TOKEN</code>.</li>
                <li>The backend picks it up automatically on the next request.</li>
              </ol>
            )}
            <button
              onClick={() => refetch()}
              disabled={isFetching}
              className="mt-4 self-start flex items-center gap-2 px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-700 text-white text-sm font-semibold transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 ${isFetching ? "animate-spin" : ""}`} />
              {isFetching ? "Retrying…" : "Retry Connection"}
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!positions || positions.length === 0) {
    return (
      <div className="w-full rounded-3xl bg-white/60 dark:bg-zinc-900/40 border border-zinc-200 dark:border-zinc-800/50 backdrop-blur-xl p-8 text-center text-zinc-500">
        <p>No active positions currently detected.</p>
      </div>
    );
  }

  return (
    <TableContent
      positions={positions}
      sortKey={sortKey}   setSortKey={setSortKey}
      sortDir={sortDir}   setSortDir={setSortDir}
      search={search}     setSearch={setSearch}
      grouped={grouped}   setGrouped={setGrouped}
    />
  );
}

// ─── Table content (renders after data is confirmed available) ────────────────
function TableContent({
  positions, sortKey, setSortKey, sortDir, setSortDir, search, setSearch, grouped, setGrouped,
}: {
  positions: Position[];
  sortKey: SortKey;   setSortKey: (k: SortKey) => void;
  sortDir:  SortDir;  setSortDir: (d: SortDir) => void;
  search:   string;   setSearch:  (s: string)  => void;
  grouped:  boolean;  setGrouped: (g: boolean) => void;
}) {
  const handleSort = (col: SortKey) => {
    if (col === sortKey) setSortDir(nextDir(sortDir));
    else { setSortKey(col); setSortDir("asc"); }
  };

  // ── Ungrouped pipeline ────────────────────────────────────────────────────
  const filteredIndividual = useMemo(() =>
    positions.filter(p => fuzzyMatch(`${p.symbol} ${p.broker} ${p.account_type}`, search)),
    [positions, search]
  );
  const sortedIndividual = useMemo(
    () => sortRows(filteredIndividual, sortKey, sortDir),
    [filteredIndividual, sortKey, sortDir]
  );

  // ── Grouped pipeline ──────────────────────────────────────────────────────
  const allGrouped = useMemo(() => groupBySymbol(positions), [positions]);
  const filteredGrouped = useMemo(() =>
    allGrouped.filter(g => fuzzyMatch(g.symbol, search)),
    [allGrouped, search]
  );
  const sortedGrouped = useMemo(
    () => sortRows(filteredGrouped, sortKey, sortDir),
    [filteredGrouped, sortKey, sortDir]
  );

  const displayCount = grouped ? sortedGrouped.length : sortedIndividual.length;
  const totalCount   = grouped ? allGrouped.length   : positions.length;

  return (
    <div className="w-full flex flex-col gap-4">
      {/* Toolbar */}
      <div className="flex items-center gap-3">
        {/* Fuzzy search */}
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-400" />
          <input
            id="holdings-search"
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search symbol, broker, account type…"
            className="w-full pl-10 pr-10 py-2.5 rounded-2xl bg-white/70 dark:bg-zinc-900/50 border border-zinc-200 dark:border-zinc-800/50 text-sm text-zinc-800 dark:text-zinc-200 placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/30 backdrop-blur-sm transition-all"
          />
          {search && (
            <button
              onClick={() => setSearch("")}
              className="absolute right-3.5 top-1/2 -translate-y-1/2 text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-300 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Result count */}
        <span className="text-xs text-zinc-500 dark:text-zinc-400 whitespace-nowrap font-medium">
          {displayCount} / {totalCount} {grouped ? "symbols" : "positions"}
        </span>

        {/* Group toggle */}
        <button
          id="group-by-symbol-toggle"
          onClick={() => setGrouped(!grouped)}
          title={grouped ? "Show individual positions" : "Group by symbol"}
          className={`flex items-center gap-2 px-3 py-2 rounded-xl text-xs font-semibold tracking-wide transition-all duration-200 border ${
            grouped
              ? "bg-indigo-500 text-white border-indigo-600 shadow-sm shadow-indigo-500/20"
              : "bg-white/70 dark:bg-zinc-900/50 text-zinc-600 dark:text-zinc-400 border-zinc-200 dark:border-zinc-800/50 hover:border-indigo-400 hover:text-indigo-600"
          }`}
        >
          {grouped
            ? <><Layers className="w-3.5 h-3.5" /> Grouped</>
            : <><List  className="w-3.5 h-3.5" /> Group by Symbol</>
          }
        </button>
      </div>

      {/* Table */}
      <div className="w-full relative overflow-hidden rounded-3xl bg-white/60 dark:bg-zinc-900/40 border border-zinc-200 dark:border-zinc-800/50 shadow-sm backdrop-blur-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left whitespace-nowrap">
            <TableHeader sortKey={sortKey} sortDir={sortDir} onSort={handleSort} />
            <tbody className="divide-y divide-zinc-200 dark:divide-zinc-800/50">
              {grouped
                ? /* ── Grouped rows ─────────────────────────────────────────────────── */
                  sortedGrouped.length === 0
                    ? <EmptyRow search={search} />
                    : sortedGrouped.map((g) => {
                        const isOpenPos = g.open_pnl >= 0;
                        const isDayPos  = g.day_pnl  >= 0;
                        const cur = g.currency;
                        return (
                          <tr key={g.symbol} className="hover:bg-zinc-50/50 dark:hover:bg-zinc-800/20 transition-colors">
                            {/* Asset Node — grouped */}
                            <td className="px-6 py-4">
                              <div className="flex flex-col gap-1.5">
                                <div className="flex items-center gap-2 flex-wrap">
                                  <span className="font-bold text-base text-zinc-900 dark:text-zinc-50">{g.symbol}</span>
                                  {g.brokers.map(b => <BrokerBadge key={b} broker={b} />)}
                                  {g.rowCount > 1 && (
                                    <span className="px-1.5 py-0.5 rounded-full bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 text-[10px] font-bold border border-indigo-500/20">
                                      ×{g.rowCount}
                                    </span>
                                  )}
                                </div>
                                {/* Account breakdown sub-line */}
                                <div className="flex items-center gap-1.5 flex-wrap text-[11px] text-zinc-400 dark:text-zinc-500">
                                  {g.accounts.map((acc, i) => (
                                    <span key={`${acc.account_id}-${i}`} className="flex items-center gap-1">
                                      {i > 0 && <span className="text-zinc-300 dark:text-zinc-700">·</span>}
                                      <Globe className="w-2.5 h-2.5" />
                                      <span className="uppercase font-medium">{acc.account_type}</span>
                                      <span className="font-mono">{acc.account_id}</span>
                                    </span>
                                  ))}
                                </div>
                              </div>
                            </td>
                            {/* Volume */}
                            <td className="px-6 py-4 text-right font-medium text-zinc-700 dark:text-zinc-300">
                              {g.qty.toLocaleString()}
                            </td>
                            {/* Avg Entry (weighted) */}
                            <td className="px-6 py-4 text-right font-medium text-zinc-700 dark:text-zinc-300">
                              {cur === "MIX" ? <span className="text-zinc-400">—</span> : <>{formatCurrency(g.average_buying_price, cur)}<CurrencyBadge cur={cur} /></>}
                            </td>
                            {/* Market Value */}
                            <td className="px-6 py-4 text-right font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
                              {cur === "MIX" ? <span className="text-zinc-400">—</span> : <>{formatCurrency(g.market_val, cur)}<CurrencyBadge cur={cur} /></>}
                            </td>
                            {/* Open PnL */}
                            <td className={`px-6 py-4 text-right font-bold tracking-tight ${isOpenPos ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}>
                              <div className="flex items-center justify-end gap-1">
                                {isOpenPos ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                                {cur === "MIX" ? "—" : <>{formatCurrency(g.open_pnl, cur)}<CurrencyBadge cur={cur} /></>}
                              </div>
                            </td>
                            {/* Day PnL */}
                            <td className={`px-6 py-4 text-right font-bold tracking-tight ${isDayPos ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}>
                              {cur === "MIX" ? "—" : <>{isDayPos ? "+" : ""}{formatCurrency(g.day_pnl, cur)}<CurrencyBadge cur={cur} /></>}
                            </td>
                          </tr>
                        );
                      })
                : /* ── Individual rows ──────────────────────────────────────────────── */
                  sortedIndividual.length === 0
                    ? <EmptyRow search={search} />
                    : sortedIndividual.map((pos, i) => {
                        const isOpenPos = pos.open_pnl >= 0;
                        const isDayPos  = pos.day_pnl  >= 0;
                        return (
                          <tr key={`${pos.symbol}-${pos.account_id}-${i}`} className="hover:bg-zinc-50/50 dark:hover:bg-zinc-800/20 transition-colors">
                            {/* Asset Node — individual */}
                            <td className="px-6 py-4">
                              <div className="flex flex-col gap-1.5">
                                <div className="flex items-center gap-2">
                                  <span className="font-bold text-base text-zinc-900 dark:text-zinc-50">{pos.symbol}</span>
                                  <BrokerBadge broker={pos.broker} />
                                </div>
                                <div className="flex items-center gap-2 text-xs text-zinc-500">
                                  <Globe className="w-3 h-3" />
                                  <span className="uppercase">{pos.account_type || "Standard"}</span>
                                  <span className="text-zinc-300 dark:text-zinc-700">•</span>
                                  <span className="font-mono">{pos.account_id}</span>
                                </div>
                              </div>
                            </td>
                            <td className="px-6 py-4 text-right font-medium text-zinc-700 dark:text-zinc-300">{pos.qty}</td>
                            <td className="px-6 py-4 text-right font-medium text-zinc-700 dark:text-zinc-300">
                              {formatCurrency(pos.average_buying_price, pos.currency)}<CurrencyBadge cur={pos.currency} />
                            </td>
                            <td className="px-6 py-4 text-right font-bold tracking-tight text-zinc-900 dark:text-zinc-50">
                              {formatCurrency(pos.market_val, pos.currency)}<CurrencyBadge cur={pos.currency} />
                            </td>
                            <td className={`px-6 py-4 text-right font-bold tracking-tight ${isOpenPos ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}>
                              <div className="flex items-center justify-end gap-1">
                                {isOpenPos ? <ArrowUpRight className="w-4 h-4" /> : <ArrowDownRight className="w-4 h-4" />}
                                {formatCurrency(pos.open_pnl, pos.currency)}<CurrencyBadge cur={pos.currency} />
                              </div>
                            </td>
                            <td className={`px-6 py-4 text-right font-bold tracking-tight ${isDayPos ? "text-emerald-600 dark:text-emerald-400" : "text-rose-600 dark:text-rose-400"}`}>
                              {isDayPos ? "+" : ""}{formatCurrency(pos.day_pnl, pos.currency)}<CurrencyBadge cur={pos.currency} />
                            </td>
                          </tr>
                        );
                      })
              }
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function EmptyRow({ search }: { search: string }) {
  return (
    <tr>
      <td colSpan={6} className="px-6 py-12 text-center text-zinc-400 dark:text-zinc-500">
        {search ? <>No positions match &quot;{search}&quot;</> : "No positions to display."}
      </td>
    </tr>
  );
}
