import React from 'react';
import { Sparkles, Shield, Database, Cpu, Layers } from 'lucide-react';
import { TraceIQLogo } from '../ui/TraceIQLogo';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-[#E5E5EA]/70 dark:bg-[#121214]/90 border-t border-black/5 dark:border-white/10 text-slate-600 dark:text-zinc-400 py-12 transition-colors">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          {/* Brand & Summary */}
          <div className="space-y-3">
            <TraceIQLogo size="sm" />
            <p className="text-xs text-slate-500 dark:text-zinc-400 leading-relaxed">
              Enterprise-grade bug diagnosis platform integrating a five-agent Python pipeline, optional dense retrieval, and BM25 hybrid search.
            </p>
          </div>

          {/* 5-Agent Architecture */}
          <div>
            <h4 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-3">
              5-Agent Architecture
            </h4>
            <ul className="space-y-1.5 text-xs text-slate-500 dark:text-zinc-400">
              <li>1. Triage Agent (Classification)</li>
              <li>2. Log Analysis Agent (Stack Forensics)</li>
              <li>3. Duplicate Detection Agent (RRF)</li>
              <li>4. Root Cause Agent (Causal Inference)</li>
              <li>5. Remediation Agent (Grounded Fixes)</li>
            </ul>
          </div>

          {/* Knowledge Repositories */}
          <div>
            <h4 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-3">
              Defect Knowledge Base
            </h4>
            <ul className="space-y-1.5 text-xs text-slate-500 dark:text-zinc-400">
              <li>Mozilla sample defect records</li>
              <li>Eclipse sample defect records</li>
              <li>Apache sample defect records</li>
              <li>Embeddings: all-MiniLM-L6-v2 (when available)</li>
            </ul>
          </div>

          {/* Security & Roadmap */}
          <div>
            <h4 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-3">
              Milestone 1 Scope
            </h4>
            <p className="text-xs text-slate-500 dark:text-zinc-400 mb-3 leading-relaxed">
              Foundation & Bug Understanding — designed to show real API results and clearly label uncertain findings.
            </p>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 bg-black/5 dark:bg-white/5 rounded-full border border-black/5 dark:border-white/10 text-[11px] text-blue-600 dark:text-blue-400">
              <Shield className="w-3.5 h-3.5" />
              <span>Development Build</span>
            </div>
          </div>
        </div>

        {/* Bottom bar */}
        <div className="pt-6 border-t border-black/5 dark:border-white/10 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-500 dark:text-zinc-500 gap-3">
          <p>© 2026 TraceIQ Platform. All rights reserved.</p>
          <div className="flex items-center gap-4 text-[11px] font-mono">
            <span>FastAPI + PostgreSQL/pgvector</span>
            <span>React 18 + TypeScript</span>
            <span>Python Agent Orchestrator</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
