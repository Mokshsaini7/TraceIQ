import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  PlusCircle,
  FileCode,
  Calendar,
  Sparkles,
  ArrowRight,
  ChevronRight,
  Filter,
  CheckCircle2
} from 'lucide-react';
import { IOSBadge } from '../components/ios/IOSBadge';
import { IOSSegmentedControl } from '../components/ios/IOSSegmentedControl';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { api } from '../services/api';
import { BugSubmission } from '../types';

export const BugReportsPage: React.FC = () => {
  const [submissions, setSubmissions] = useState<BugSubmission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');

  const loadSubmissions = async () => {
    setIsLoading(true);
    try {
      const data = await api.listSubmissions({
        search: search || undefined,
        severity: severityFilter !== 'all' ? severityFilter : undefined,
        priority: priorityFilter !== 'all' ? priorityFilter : undefined,
      });
      setSubmissions(data.items);
    } catch (err) {
      console.error('Failed to load bug reports:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSubmissions();
  }, [search, severityFilter, priorityFilter]);

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
              Defect Reports & Diagnoses
            </h1>
            <IOSBadge variant="blue" size="sm">
              {submissions.length} Total
            </IOSBadge>
          </div>
          <p className="mt-1 text-sm text-slate-600 dark:text-zinc-400">
            Historical submissions analyzed by TraceIQ's 5-Agent RAG pipeline.
          </p>
        </div>

        <Link
          to="/submit"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#007AFF] hover:bg-[#0066D6] dark:bg-[#0A84FF] text-white font-medium text-xs sm:text-sm shadow-md shadow-blue-500/25 active:scale-95 transition-all self-start sm:self-auto"
        >
          <Sparkles className="w-4 h-4" />
          <span>New Diagnosis</span>
        </Link>
      </div>

      {/* Search & Filter Bar */}
      <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3">
        {/* iOS Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-zinc-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search reports by title, exception, or component..."
            className="w-full pl-10 pr-4 py-2 rounded-xl bg-slate-200/60 dark:bg-zinc-800/80 border border-black/5 dark:border-white/5 text-xs sm:text-sm text-slate-900 dark:text-white placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-blue-500/30"
          />
        </div>

        {/* Severity Filter Segmented Control */}
        <IOSSegmentedControl
          value={severityFilter}
          onChange={setSeverityFilter}
          options={[
            { value: 'all', label: 'All Severities' },
            { value: 'critical', label: 'Critical' },
            { value: 'high', label: 'High' },
            { value: 'medium', label: 'Medium' },
            { value: 'low', label: 'Low' },
          ]}
        />
        <select aria-label="Filter by priority" value={priorityFilter} onChange={(event) => setPriorityFilter(event.target.value)}
          className="px-3 py-2 rounded-xl bg-slate-200/60 dark:bg-zinc-800/80 border border-black/5 dark:border-white/5 text-xs text-slate-900 dark:text-white">
          <option value="all">All Priorities</option>
          <option value="p1">P1 — Immediate</option>
          <option value="p2">P2 — Urgent</option>
          <option value="p3">P3 — Normal</option>
          <option value="p4">P4 — Later</option>
        </select>
      </div>

      {/* Submissions List */}
      {isLoading ? (
        <LoadingSkeleton rows={6} />
      ) : submissions.length === 0 ? (
        <div className="p-12 text-center ios-card">
          <p className="text-sm font-semibold text-slate-700 dark:text-zinc-300">No defect reports found</p>
          <p className="text-xs text-zinc-400 mt-1">Try modifying your search or submit a new bug.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {submissions.map((sub) => {
            const isCritical = sub.severity === 'critical';
            const isHigh = sub.severity === 'high';

            return (
              <Link
                key={sub.id}
                to={`/reports/${sub.id}`}
                className="ios-card p-5 block hover:border-blue-500/30 transition-all group"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                  <div className="space-y-1.5 flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2">
                      <IOSBadge
                        variant={isCritical ? 'red' : isHigh ? 'orange' : 'blue'}
                        size="sm"
                        dot
                      >
                        {sub.severity.toUpperCase()}
                      </IOSBadge>

                      <IOSBadge variant={sub.priority === 'p1' ? 'red' : sub.priority === 'p2' ? 'orange' : 'blue'} size="sm">
                        {sub.priority.toUpperCase()}
                      </IOSBadge>

                      <span className="text-[11px] font-mono text-zinc-400">
                        {sub.id}
                      </span>

                      {sub.programming_language && (
                        <span className="text-[11px] px-2 py-0.5 rounded-full bg-black/5 dark:bg-white/10 font-mono text-slate-600 dark:text-zinc-400">
                          {sub.programming_language}
                        </span>
                      )}

                      <span className="text-[11px] text-zinc-400">
                        {new Date(sub.created_at).toLocaleDateString()}
                      </span>
                    </div>

                    <h3 className="font-bold text-sm sm:text-base text-slate-900 dark:text-white truncate group-hover:text-blue-500 transition-colors">
                      {sub.title}
                    </h3>

                    <p className="text-xs text-slate-600 dark:text-zinc-400 line-clamp-1">
                      {sub.description}
                    </p>
                  </div>

                  <div className="flex items-center gap-3 self-end sm:self-center">
                    <IOSBadge
                      variant={sub.status === 'analyzed' ? 'green' : sub.status === 'failed' ? 'red' : 'blue'}
                      size="sm"
                    >
                      {sub.status === 'analyzed' ? 'Analyzed' : sub.status === 'failed' ? 'Failed' : sub.status === 'analyzing' ? 'Analyzing' : sub.status === 'pending' ? 'Pending' : sub.status}
                    </IOSBadge>
                    <ChevronRight className="w-4 h-4 text-zinc-400 group-hover:text-blue-500 transition-colors" />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
};
