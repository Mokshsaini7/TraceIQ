import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Sparkles,
  AlertTriangle,
  CheckCircle,
  Clock,
  Database,
  Activity,
  Layers,
  ArrowUpRight,
  RefreshCw,
  Search,
  ShieldCheck,
  ChevronRight
} from 'lucide-react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip
} from 'recharts';
import { IOSBadge } from '../components/ios/IOSBadge';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { api } from '../services/api';
import { BugSubmission, KnowledgeBaseStats } from '../types';

export const DashboardPage: React.FC = () => {
  const [submissions, setSubmissions] = useState<BugSubmission[]>([]);
  const [kbStats, setKbStats] = useState<KnowledgeBaseStats | null>(null);
  const [systemHealth, setSystemHealth] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const loadData = async () => {
    try {
      const [subsRes, statsRes, healthRes] = await Promise.all([
        api.listSubmissions({ page: 1, page_size: 50 }),
        api.getKnowledgeStats().catch(() => null),
        api.getHealth().catch(() => null),
      ]);
      setSubmissions(subsRes.items);
      setKbStats(statsRes);
      setSystemHealth(healthRes);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleRefresh = async () => {
    setIsRefreshing(true);
    await loadData();
  };

  const severityData = [
    { name: 'Critical', value: submissions.filter((item) => item.severity === 'critical').length, color: '#FF3B30' },
    { name: 'High', value: submissions.filter((item) => item.severity === 'high').length, color: '#FF9500' },
    { name: 'Medium', value: submissions.filter((item) => item.severity === 'medium').length, color: '#007AFF' },
    { name: 'Low', value: submissions.filter((item) => item.severity === 'low').length, color: '#30B0C7' },
  ].filter((item) => item.value > 0);

  const sourceData = Object.entries(kbStats?.by_source || {}).map(([name, value]) => ({ name, value }));

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto space-y-6 py-6">
        <LoadingSkeleton rows={8} />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
              Platform Intelligence Dashboard
            </h1>
            <IOSBadge variant="blue" size="sm">
              Live Overview
            </IOSBadge>
          </div>
          <p className="mt-1 text-sm text-slate-600 dark:text-zinc-400">
            Real-time telemetry across submissions, five-agent Python orchestration, and vector knowledge indices.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-xl bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 text-xs font-medium text-slate-700 dark:text-zinc-300 border border-black/5 dark:border-white/5 transition-all"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>

          <Link
            to="/submit"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-[#007AFF] hover:bg-[#0066D6] dark:bg-[#0A84FF] text-white text-xs sm:text-sm font-semibold shadow-md shadow-blue-500/25 active:scale-95 transition-all"
          >
            <Sparkles className="w-4 h-4" />
            <span>Diagnose Bug</span>
          </Link>
        </div>
      </div>

      {/* KPI Metric Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="ios-card p-5 space-y-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
            Active Submissions
          </span>
          <div className="text-2xl font-extrabold text-slate-900 dark:text-white font-mono">
            {submissions.length}
          </div>
          <p className="text-[11px] text-zinc-400">Under Analysis</p>
        </div>

        <div className="ios-card p-5 space-y-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
            Knowledge Base
          </span>
          <div className="text-2xl font-extrabold text-blue-600 dark:text-blue-400 font-mono">
            {kbStats ? kbStats.total_defects.toLocaleString() : 'Unavailable'}
          </div>
          <p className="text-[11px] text-zinc-400">Historical Bugs Indexed</p>
        </div>

        <div className="ios-card p-5 space-y-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
            Indexed Embeddings
          </span>
          <div className="text-2xl font-extrabold text-purple-600 dark:text-purple-400 font-mono">
            {kbStats ? `${kbStats.total_embeddings.toLocaleString()}` : '—'}
          </div>
          <p className="text-[11px] text-zinc-400">Indexed embeddings</p>
        </div>

        <div className="ios-card p-5 space-y-1">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
            System Core
          </span>
          <div className="text-lg font-bold text-emerald-500 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>{systemHealth?.status === 'healthy' ? 'Healthy' : systemHealth?.status === 'degraded' ? 'Degraded' : 'Unknown'}</span>
          </div>
          <p className="text-[11px] text-zinc-400">5 Agents Orchestrated</p>
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Severity Distribution */}
        <div className="ios-card p-6 space-y-4">
          <h3 className="font-bold text-sm sm:text-base text-slate-900 dark:text-white">
            Defect Severity Breakdown
          </h3>
          <div className="h-60 w-full flex items-center justify-center">
            {severityData.length === 0 ? <p className="text-sm text-zinc-400">No submission data available yet.</p> : <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={severityData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={85}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {severityData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>}
          </div>
          <div className="flex items-center justify-around text-xs text-slate-600 dark:text-zinc-400 pt-2 border-t border-black/5 dark:border-white/5">
            {severityData.map((s) => (
              <div key={s.name} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: s.color }} />
                <span>{s.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Knowledge Base Volume */}
        <div className="ios-card p-6 space-y-4">
          <h3 className="font-bold text-sm sm:text-base text-slate-900 dark:text-white">
            Historical Defect Lake Distribution
          </h3>
          <div className="h-60 w-full">
            {sourceData.length === 0 ? <p className="h-full flex items-center justify-center text-sm text-zinc-400">No indexed source breakdown available.</p> : <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sourceData}>
                <XAxis dataKey="name" stroke="#888888" fontSize={11} />
                <YAxis stroke="#888888" fontSize={11} />
                <Tooltip />
                <Bar dataKey="value" fill="#007AFF" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>}
          </div>
          <div className="text-xs text-center text-zinc-400 pt-2 border-t border-black/5 dark:border-white/5">
            Source counts returned by the connected TraceIQ knowledge base.
          </div>
        </div>
      </div>

      {/* Recent Submissions List */}
      <div className="ios-card p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-black/5 dark:border-white/5 pb-3">
          <h3 className="font-bold text-sm sm:text-base text-slate-900 dark:text-white">
            Recent Diagnostic Reports
          </h3>
          <Link
            to="/reports"
            className="text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
          >
            <span>View All</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="space-y-2">
          {submissions.slice(0, 4).map((sub) => (
            <Link
              key={sub.id}
              to={`/reports/${sub.id}`}
              className="p-3.5 rounded-2xl bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 flex items-center justify-between gap-3 transition-all"
            >
              <div className="space-y-1 min-w-0">
                <div className="flex items-center gap-2">
                  <IOSBadge
                    variant={sub.severity === 'critical' ? 'red' : 'orange'}
                    size="sm"
                  >
                    {sub.severity.toUpperCase()}
                  </IOSBadge>
                  <span className="font-mono text-[11px] text-zinc-400">{sub.id}</span>
                </div>
                <h4 className="font-semibold text-xs sm:text-sm text-slate-900 dark:text-white truncate">
                  {sub.title}
                </h4>
              </div>

              <div className="flex items-center gap-2 flex-shrink-0">
                <span className="text-[11px] text-zinc-400 hidden sm:inline">
                  {new Date(sub.created_at).toLocaleDateString()}
                </span>
                <ChevronRight className="w-4 h-4 text-zinc-400" />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
};
