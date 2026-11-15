import React, { useState, useEffect } from 'react';
import {
  Settings,
  Activity,
  Database,
  Cpu,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Shield,
  Layers,
  Lock,
  Moon,
  Sun
} from 'lucide-react';
import { IOSBadge } from '../components/ios/IOSBadge';
import { IOSToggle } from '../components/ios/IOSToggle';
import { IOSSegmentedControl } from '../components/ios/IOSSegmentedControl';
import { api } from '../services/api';

export const SettingsPage: React.FC = () => {
  const [health, setHealth] = useState<any>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Settings state
  const [llmProvider, setLlmProvider] = useState('claude');
  const [autoRedactPII, setAutoRedactPII] = useState(true);
  const [hybridFusion, setHybridFusion] = useState(true);
  const [denseTopK, setDenseTopK] = useState(10);

  const loadSettings = async () => {
    try {
      const data = await api.getHealth();
      setHealth(data);
    } catch {
      setHealth({ status: 'unavailable', version: 'unknown', error: 'Backend health check failed.' });
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    loadSettings();
  }, []);

  const handleRefresh = () => {
    setIsRefreshing(true);
    loadSettings();
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 pb-16">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            System Settings & Preferences
          </h1>
          <p className="mt-1 text-sm text-slate-600 dark:text-zinc-400">
            View backend health and the services configured in the backend environment.
          </p>
        </div>

        <button
          type="button"
          onClick={handleRefresh}
          disabled={isRefreshing}
          className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 text-xs font-medium text-slate-700 dark:text-zinc-300 border border-black/5 dark:border-white/5 transition-all"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>Check Health</span>
        </button>
      </div>

      {/* Model & Reasoning Provider */}
      <div className="ios-card p-6 space-y-5">
        <div className="border-b border-black/5 dark:border-white/5 pb-3">
          <h3 className="font-bold text-base text-slate-900 dark:text-white flex items-center gap-2">
            <Cpu className="w-4 h-4 text-purple-500" />
            <span>LLM Inference & Agent Engine</span>
          </h3>
          <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
            Pluggable provider interface supporting Claude API and local Ollama models.
          </p>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-slate-700 dark:text-zinc-300 mb-2">
              Primary Agent Model
            </label>
            <IOSSegmentedControl
              value={llmProvider}
              onChange={setLlmProvider}
              options={[
                { value: 'claude', label: 'Optional Anthropic API (server configured)' },
                { value: 'ollama', label: 'Not configured' },
              ]}
            />
          </div>

          <div className="p-3.5 rounded-xl bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
            The core diagnosis pipeline uses deterministic Python agents. Optional Anthropic refinement is enabled only when ANTHROPIC_API_KEY is configured; ungrounded LLM output is rejected.
          </div>
        </div>
      </div>

      {/* Privacy & Redaction Settings */}
      <div className="ios-card p-6 space-y-5">
        <div className="border-b border-black/5 dark:border-white/5 pb-3">
          <h3 className="font-bold text-base text-slate-900 dark:text-white flex items-center gap-2">
            <Lock className="w-4 h-4 text-emerald-500" />
            <span>Enterprise Privacy & Zero Execution</span>
          </h3>
          <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
            Client-side data protection before network transmission.
          </p>
        </div>

        <div className="space-y-4">
          <IOSToggle
            checked={autoRedactPII}
            onChange={setAutoRedactPII}
            label="Client-Side PII & Token Masking"
            description="Automatically scrubs IPv4/IPv6, Bearer tokens, AWS secrets, and database credentials."
          />

          <IOSToggle
            checked={hybridFusion}
            onChange={setHybridFusion}
            label="Reciprocal Rank Fusion (RRF)"
            description="Combine compatible SentenceTransformer vectors with BM25 keyword search. Dense search is disabled when the real embedding model is unavailable."
          />
        </div>
      </div>

      {/* Vector Store Configuration */}
      <div className="ios-card p-6 space-y-4">
        <div className="border-b border-black/5 dark:border-white/5 pb-3">
          <h3 className="font-bold text-base text-slate-900 dark:text-white flex items-center gap-2">
            <Database className="w-4 h-4 text-blue-500" />
            <span>Vector Storage (PostgreSQL / pgvector)</span>
          </h3>
          <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
            Vector records are stored with PostgreSQL. The active database and embedding mode are shown in backend health.
          </p>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 dark:text-zinc-300 mb-1.5">
            Database configuration
          </label>
          <input
            type="text"
            value="Configured in backend/.env (DATABASE_URL)"
            readOnly
            className="w-full px-4 py-2 rounded-xl bg-slate-100 dark:bg-zinc-800/80 border border-black/5 dark:border-white/10 text-xs sm:text-sm text-slate-900 dark:text-white font-mono focus:outline-none focus:ring-2 focus:ring-blue-500/40"
          />
        </div>
      </div>
    </div>
  );
};
