import React, { useState } from 'react';
import { Activity, ShieldCheck, Database, Cpu, ChevronDown, CheckCircle2, Sparkles, AlertCircle } from 'lucide-react';

interface IOSDynamicIslandProps {
  isBackendHealthy: boolean | null;
  activeAgentName?: string | null;
  isProcessing?: boolean;
  progressPercent?: number;
}

export const IOSDynamicIsland: React.FC<IOSDynamicIslandProps> = ({
  isBackendHealthy,
  activeAgentName,
  isProcessing = false,
  progressPercent = 0,
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <div className="relative z-50 flex justify-center">
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        className={`group cursor-pointer border backdrop-blur-2xl transition-all duration-300 ease-out select-none ${
          isExpanded
            ? 'px-5 py-3 w-[340px] sm:w-[420px] rounded-2xl bg-[#262624] text-white border-white/15 shadow-2xl'
            : 'h-9 px-3 w-full flex items-center whitespace-nowrap rounded-lg bg-black/[.04] dark:bg-white/[.06] hover:bg-black/[.07] dark:hover:bg-white/10 text-slate-700 dark:text-zinc-200 border-black/10 dark:border-white/10'
        }`}
      >
        {/* Collapsed Pill State */}
        {!isExpanded && (
          <div className="flex w-full items-center justify-between gap-3 text-xs whitespace-nowrap">
            <div className="flex items-center gap-2">
              {isProcessing ? (
                <div className="relative flex items-center justify-center">
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-400 animate-ping absolute" />
                  <span className="w-2.5 h-2.5 rounded-full bg-blue-500" />
                </div>
              ) : (
                <span
                  className={`w-2 h-2 rounded-full ${
                    isBackendHealthy === null
                      ? 'bg-amber-400 animate-pulse'
                      : isBackendHealthy
                      ? 'bg-[#34C759]'
                      : 'bg-blue-400'
                  }`}
                />
              )}
              <span className="font-medium tracking-tight truncate">
                {isProcessing
                  ? activeAgentName || 'Agent Swarm Reasoning...'
                  : 'Intelligence Core'}
              </span>
            </div>

            <div className="flex items-center gap-2 text-[11px] text-slate-500 dark:text-zinc-400 font-mono">
              {isProcessing ? (
                <span className="text-cyan-400 font-bold">{Math.round(progressPercent)}%</span>
              ) : (
                <span className="text-slate-500 dark:text-zinc-400">5 agents</span>
              )}
              <ChevronDown className="w-3.5 h-3.5 text-slate-400 group-hover:text-slate-700 dark:group-hover:text-white transition-colors" />
            </div>
          </div>
        )}

        {/* Expanded Telemetry Modal State */}
        {isExpanded && (
          <div className="space-y-3 animate-fade-in text-xs">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-white/10 pb-2">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 rounded-lg bg-blue-500/20 text-blue-400 flex items-center justify-center">
                  <Sparkles className="w-3.5 h-3.5" />
                </div>
                <div>
                  <h4 className="font-semibold text-white text-sm">System Telemetry</h4>
                  <p className="text-[10px] text-zinc-400">Milestone 1 Foundation + M2 Agent Pipeline</p>
                </div>
              </div>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setIsExpanded(false);
                }}
                className="text-zinc-400 hover:text-white px-2 py-1 text-[11px] rounded-full bg-white/10"
              >
                Done
              </button>
            </div>

            {/* Grid of Micro Services */}
            <div className="grid grid-cols-2 gap-2 pt-1">
              <div className="p-2.5 rounded-xl bg-white/5 border border-white/5 flex items-center gap-2.5">
                <Database className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                <div>
                  <div className="text-[11px] text-zinc-400">Knowledge Base</div>
                  <div className="text-xs font-semibold text-white">PostgreSQL / pgvector</div>
                </div>
              </div>

              <div className="p-2.5 rounded-xl bg-white/5 border border-white/5 flex items-center gap-2.5">
                <Cpu className="w-4 h-4 text-cyan-400 flex-shrink-0" />
                <div>
                  <div className="text-[11px] text-zinc-400">Embeddings</div>
                  <div className="text-xs font-semibold text-white">bge-small-en (384d)</div>
                </div>
              </div>

              <div className="p-2.5 rounded-xl bg-white/5 border border-white/5 flex items-center gap-2.5">
                <Activity className="w-4 h-4 text-purple-400 flex-shrink-0" />
                <div>
                  <div className="text-[11px] text-zinc-400">Orchestrator</div>
                  <div className="text-xs font-semibold text-white">Python 5-Agent</div>
                </div>
              </div>

              <div className="p-2.5 rounded-xl bg-white/5 border border-white/5 flex items-center gap-2.5">
                <ShieldCheck className="w-4 h-4 text-blue-400 flex-shrink-0" />
                <div>
                  <div className="text-[11px] text-zinc-400">Operational DB</div>
                  <div className="text-xs font-semibold text-white">PostgreSQL 16</div>
                </div>
              </div>
            </div>

            {/* Status Line */}
            <div className="flex items-center justify-between text-[11px] text-zinc-400 pt-1">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400" />
                {isBackendHealthy ? 'Connected to FastAPI Backend' : 'Client Intelligence Simulator Active'}
              </span>
              <span className="font-mono text-zinc-300">Loaded Defects</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
