import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  PlusCircle,
  Bug,
  Database,
  Search,
  Cpu,
  Settings,
  ShieldCheck,
  Sparkles
} from 'lucide-react';
import { IOSBadge } from '../ios/IOSBadge';

export const Sidebar: React.FC = () => {
  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Diagnose Studio', path: '/submit', icon: Sparkles, highlight: true },
    { label: 'Bug Reports', path: '/reports', icon: Bug },
    { label: 'Knowledge Base', path: '/knowledge-base', icon: Database },
    { label: 'Semantic Search', path: '/search', icon: Search },
    { label: 'Architecture & Agents', path: '/architecture', icon: Cpu },
    { label: 'System Settings', path: '/settings', icon: Settings },
  ];

  const agentSwarm = [
    { name: 'Triage Agent', role: 'Severity & Category', color: 'bg-blue-500' },
    { name: 'Log Analysis Agent', role: 'Stack Forensics', color: 'bg-cyan-500' },
    { name: 'Duplicate Detection', role: 'pgvector + BM25', color: 'bg-purple-500' },
    { name: 'Root Cause Agent', role: 'Causal Synthesis', color: 'bg-orange-500' },
    { name: 'Remediation Agent', role: 'Patch Mining', color: 'bg-emerald-500' },
  ];

  return (
    <aside className="w-64 ios-glass border-r border-black/5 dark:border-white/10 min-h-[calc(100vh-4rem)] flex flex-col justify-between p-4 shrink-0 rounded-r-3xl my-2">
      <div className="space-y-6">
        {/* Navigation */}
        <div>
          <p className="px-3 text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-zinc-500 mb-2">
            Analysis Platform
          </p>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs sm:text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-[#007AFF] text-white shadow-md shadow-blue-500/25 font-semibold'
                        : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-white hover:bg-black/5 dark:hover:bg-white/5'
                    }`
                  }
                >
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* 5-Agent Swarm Status */}
        <div className="pt-4 border-t border-black/5 dark:border-white/5">
          <div className="flex items-center justify-between px-3 mb-2">
            <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-zinc-500">
              Agent Swarm (M2)
            </p>
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
          </div>

          <div className="space-y-2 px-1">
            {agentSwarm.map((agent) => (
              <div
                key={agent.name}
                className="flex items-center justify-between p-2 rounded-xl bg-black/5 dark:bg-white/5 text-xs"
              >
                <div className="flex items-center gap-2">
                  <span className={`w-2 h-2 rounded-full ${agent.color}`} />
                  <span className="font-medium text-slate-800 dark:text-zinc-200 text-[11px]">
                    {agent.name}
                  </span>
                </div>
                <span className="text-[10px] text-zinc-400 font-mono">Ready</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Zero Execution Sandbox Box */}
      <div className="p-3.5 rounded-2xl bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 space-y-1.5 text-xs">
        <div className="flex items-center gap-2 font-semibold text-slate-900 dark:text-white">
          <ShieldCheck className="w-4 h-4 text-emerald-500" />
          <span>Zero-Execution Sandbox</span>
        </div>
        <p className="text-slate-500 dark:text-zinc-400 text-[11px] leading-relaxed">
          Log files & stack traces are scanned as static text only. No arbitrary code execution is permitted.
        </p>
      </div>
    </aside>
  );
};
