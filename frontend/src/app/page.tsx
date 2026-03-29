import { ModeToggle } from "@/components/mode-toggle";
// We will build these React components shortly:
import MetricsHeader from "@/components/metrics-header";
import HoldingsTable from "@/components/holdings-table";
import AIInsightsCard from "@/components/ai-insights-card";

export default function Home() {
  return (
    <div className="min-h-screen bg-zinc-50 dark:bg-zinc-950 font-sans text-zinc-900 dark:text-zinc-100 transition-colors duration-300 antialiased selection:bg-indigo-500/30">
      {/* Background Glassmorphism Gradients */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden select-none">
        <div className="absolute top-0 right-0 -mr-[20%] -mt-[10%] w-[50%] h-[50%] rounded-full bg-indigo-500/10 dark:bg-indigo-500/5 blur-[120px]" />
        <div className="absolute bottom-0 left-0 -ml-[20%] -mb-[10%] w-[50%] h-[50%] rounded-full bg-emerald-500/10 dark:bg-emerald-500/5 blur-[120px]" />
      </div>

      {/* Main Container */}
      <div className="relative z-10 mx-auto max-w-screen-2xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Top Navbar Area */}
        <header className="flex items-center justify-between mb-10 border-b border-zinc-200 dark:border-zinc-800/50 pb-6">
          <div className="flex flex-col">
            <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-zinc-800 to-zinc-500 dark:from-zinc-100 dark:to-zinc-400 bg-clip-text text-transparent">
              Smart Hyper Broker
            </h1>
            <p className="text-sm font-medium text-zinc-500 dark:text-zinc-400 mt-1">Multi-Gateway Portfolio Intelligence</p>
          </div>
          <ModeToggle />
        </header>

        {/* Dynamic Interactive Surfaces */}
        <div className="flex flex-col gap-10">
          {/* Top Level Aggregate Metrics */}
          <section className="animate-in fade-in slide-in-from-bottom-4 duration-700">
            <MetricsHeader />
          </section>

          {/* Core Layout Split */}
          <div className="grid grid-cols-1 lg:grid-cols-[1fr_400px] gap-8">
            {/* Holdings Matrix Grid */}
            <section className="space-y-6 animate-in fade-in slide-in-from-bottom-6 duration-700 delay-150 fill-mode-both">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold tracking-tight">Active Portfolios</h2>
              </div>
              <HoldingsTable />
            </section>

            {/* AI Insights Sidebar */}
            <section className="space-y-6 animate-in fade-in slide-in-from-bottom-8 duration-700 delay-300 fill-mode-both">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold tracking-tight flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                  MCP Insights Layer
                </h2>
              </div>
              <AIInsightsCard />
            </section>
          </div>
        </div>
      </div>
    </div>
  );
}
