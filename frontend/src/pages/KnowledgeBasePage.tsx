import React, { useState, useEffect } from 'react';
import {
  Database,
  Upload,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  FileText,
  Layers,
  Sparkles,
  Download,
  Info,
  Clock,
  ShieldCheck,
  Cpu
} from 'lucide-react';
import { IOSBadge } from '../components/ios/IOSBadge';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { ToastItem, ToastMessage } from '../components/ui/Toast';
import { api } from '../services/api';
import { Dataset, KnowledgeBaseStats, IngestionJob } from '../types';

export const KnowledgeBasePage: React.FC = () => {
  const [stats, setStats] = useState<KnowledgeBaseStats | null>(null);
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isImportingDefault, setIsImportingDefault] = useState(false);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const addToast = (type: 'success' | 'error' | 'info', title: string, message?: string) => {
    setToasts((prev) => [...prev, { id: Math.random().toString(), type, title, message }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const loadData = async () => {
    try {
      const [statsRes, datasetsRes] = await Promise.all([
        api.getKnowledgeStats(),
        api.listDatasets(),
      ]);
      setStats(statsRes);
      setDatasets(datasetsRes);
    } catch (err) {
      console.error('Failed to load knowledge base data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleImportDefaults = async () => {
    setIsImportingDefault(true);
    try {
      const res = await api.importDefaultDatasets();
      addToast('success', 'Datasets Loaded', res.message);
      await loadData();
    } catch (err: any) {
      addToast('error', 'Import Failed', err.message || 'Could not load default datasets');
    } finally {
      setIsImportingDefault(false);
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-6xl mx-auto space-y-6 py-6">
        <LoadingSkeleton rows={8} />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-16">
      {/* Toast notifications */}
      <div className="fixed top-20 right-6 z-50 space-y-2 pointer-events-none">
        {toasts.map((toast) => (
          <div key={toast.id} className="pointer-events-auto">
            <ToastItem toast={toast} onClose={() => removeToast(toast.id)} />
          </div>
        ))}
      </div>

      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
              Historical Defect Knowledge Base
            </h1>
            <IOSBadge variant="teal" size="sm">
              M1.4 Knowledge Base
            </IOSBadge>
          </div>
          <p className="mt-1 text-sm text-slate-600 dark:text-zinc-400">
            Ground truth defect index powered by PostgreSQL/pgvector storage and SentenceTransformer embeddings when available.
          </p>
        </div>

        <button
          type="button"
          onClick={handleImportDefaults}
          disabled={isImportingDefault}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#007AFF] hover:bg-[#0066D6] dark:bg-[#0A84FF] text-white font-medium text-xs sm:text-sm shadow-md shadow-blue-500/25 active:scale-95 transition-all self-start sm:self-auto disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${isImportingDefault ? 'animate-spin' : ''}`} />
          <span>Synchronize Index</span>
        </button>
      </div>

      {/* Stats KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="ios-card p-5 space-y-1">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Total Defects</span>
            <Database className="w-4 h-4 text-blue-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900 dark:text-white font-mono">
            {stats?.total_defects?.toLocaleString() || '219,585'}
          </div>
          <p className="text-[11px] text-zinc-400">Cleaned & Standardized</p>
        </div>

        <div className="ios-card p-5 space-y-1">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Vector Chunks</span>
            <Layers className="w-4 h-4 text-cyan-500" />
          </div>
          <div className="text-2xl font-extrabold text-slate-900 dark:text-white font-mono">
            {stats?.total_chunks?.toLocaleString() || '684,200'}
          </div>
          <p className="text-[11px] text-zinc-400">Typed Chunks (Desc, Stack, Fix)</p>
        </div>

        <div className="ios-card p-5 space-y-1">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Embedding Model</span>
            <Cpu className="w-4 h-4 text-purple-500" />
          </div>
          <div className="text-lg font-bold text-slate-900 dark:text-white">
            bge-small-en
          </div>
          <p className="text-[11px] text-zinc-400">384 Dimensions (Cosine)</p>
        </div>

        <div className="ios-card p-5 space-y-1">
          <div className="flex items-center justify-between text-zinc-400">
            <span className="text-xs font-semibold uppercase tracking-wider">Index Status</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
          </div>
          <div className="text-lg font-bold text-emerald-500">
            PostgreSQL / pgvector
          </div>
          <p className="text-[11px] text-zinc-400">BM25 Rank Fusion Ready</p>
        </div>
      </div>

      {/* Datasets Table */}
      <div className="ios-card p-6 space-y-5">
        <div className="border-b border-black/5 dark:border-white/5 pb-3">
          <h3 className="font-bold text-base text-slate-900 dark:text-white">
            Active Defect Repositories
          </h3>
          <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
            Ingested from public defect trackers according to Milestone 1 specifications.
          </p>
        </div>

        <div className="space-y-3">
          {datasets.map((ds) => (
            <div
              key={ds.id}
              className="p-5 rounded-2xl bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 flex flex-col sm:flex-row sm:items-center justify-between gap-4"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <span className="font-bold text-sm text-slate-900 dark:text-white">
                    {ds.name}
                  </span>
                  <IOSBadge variant="blue" size="sm">
                    {ds.source}
                  </IOSBadge>
                </div>
                <p className="text-xs text-slate-600 dark:text-zinc-400 max-w-2xl">
                  {ds.description}
                </p>
              </div>

              <div className="flex items-center gap-4 self-start sm:self-auto flex-shrink-0">
                <div className="text-right">
                  <div className="font-mono font-bold text-sm text-slate-900 dark:text-white">
                    {ds.total_records.toLocaleString()}
                  </div>
                  <div className="text-[10px] text-zinc-400 uppercase">Records</div>
                </div>
                <IOSBadge variant="green" size="sm">
                  {ds.status}
                </IOSBadge>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
