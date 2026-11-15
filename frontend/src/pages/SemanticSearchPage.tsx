import React, { useState } from 'react';
import {
  Search,
  Sparkles,
  ExternalLink,
  ShieldCheck,
  BarChart2,
  CheckCircle2,
  Cpu,
  Layers,
  ArrowRight,
  Terminal
} from 'lucide-react';
import { IOSBadge } from '../components/ios/IOSBadge';
import { IOSSegmentedControl } from '../components/ios/IOSSegmentedControl';
import { LoadingSkeleton } from '../components/ui/LoadingSkeleton';
import { api } from '../services/api';
import { SearchResultItem, EvaluationMetrics } from '../types';

export const SemanticSearchPage: React.FC = () => {
  const [query, setQuery] = useState('NullPointer in Workspace save during auto-build');
  const [method, setMethod] = useState<'hybrid' | 'semantic' | 'bm25'>('hybrid');
  const [sourceFilter, setSourceFilter] = useState('all');
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [executionTimeMs, setExecutionTimeMs] = useState<number | null>(null);
  const [isSearching, setIsSearching] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setIsSearching(true);
    setHasSearched(true);
    try {
      const data = await api.searchHistoricalDefects({
        query,
        method,
        top_k: 8,
        source_filter: sourceFilter,
      });
      setResults(data.results);
      setExecutionTimeMs(data.execution_time_ms);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setIsSearching(false);
    }
  };

  // Run initial search on mount
  React.useEffect(() => {
    handleSearch();
  }, [method, sourceFilter]);

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-16">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            Hybrid Semantic & BM25 Defect Search
          </h1>
          <IOSBadge variant="blue" size="sm">
            RAG Retrieval Engine
          </IOSBadge>
        </div>
        <p className="mt-1 text-sm text-slate-600 dark:text-zinc-400">
          Search the historical defect records loaded into your knowledge base. Retrieval uses compatible dense embeddings when available and BM25 keyword matching.
        </p>
      </div>

      {/* Search Input Bar */}
      <form onSubmit={handleSearch} className="ios-card p-4 sm:p-5 space-y-4">
        <div className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-zinc-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Query symptoms, exception classes, or stack frames (e.g. Workspace.save NPE)..."
              className="w-full pl-10 pr-4 py-3 rounded-xl bg-slate-100 dark:bg-zinc-800/80 border border-black/5 dark:border-white/10 text-sm text-slate-900 dark:text-white placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            />
          </div>

          <button
            type="submit"
            disabled={isSearching}
            className="inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-[#007AFF] hover:bg-[#0066D6] dark:bg-[#0A84FF] text-white font-semibold text-xs sm:text-sm shadow-md shadow-blue-500/25 active:scale-95 transition-all disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            <span>{isSearching ? 'Searching...' : 'Search Defect DB'}</span>
          </button>
        </div>

        {/* Filter Bar with iOS Segmented Controls */}
        <div className="flex flex-col xl:flex-row xl:items-center justify-between gap-3 pt-2 border-t border-black/5 dark:border-white/5">
          <div className="flex items-center gap-2 min-w-0">
            <span className="text-xs font-semibold text-slate-600 dark:text-zinc-400 mr-1 flex-shrink-0">
              Mode:
            </span>
            <IOSSegmentedControl
              value={method}
              onChange={(v) => setMethod(v as any)}
              size="sm"
              options={[
                { value: 'hybrid', label: 'Hybrid RRF' },
                { value: 'semantic', label: 'Dense Vector (bge)' },
                { value: 'bm25', label: 'Sparse BM25' },
              ]}
            />
          </div>

          <div className="flex items-center gap-2 min-w-0">
            <span className="text-xs font-semibold text-slate-600 dark:text-zinc-400 mr-1 flex-shrink-0">
              Repo:
            </span>
            <IOSSegmentedControl
              value={sourceFilter}
              onChange={setSourceFilter}
              size="sm"
              options={[
                { value: 'all', label: 'All Trackers' },
                { value: 'mozilla', label: 'Mozilla' },
                { value: 'eclipse', label: 'Eclipse' },
                { value: 'apache', label: 'Apache' },
              ]}
            />
          </div>
        </div>
      </form>

      {/* Results Header */}
      {hasSearched && (
        <div className="flex items-center justify-between text-xs text-slate-500 dark:text-zinc-400 px-1">
          <span>
            Found <strong className="text-slate-900 dark:text-white">{results.length}</strong> matching historical defects
          </span>
          {executionTimeMs !== null && (
            <span className="font-mono">
              Retrieval latency: {executionTimeMs} ms
            </span>
          )}
        </div>
      )}

      {/* Results List */}
      {isSearching ? (
        <LoadingSkeleton rows={5} />
      ) : results.length === 0 ? (
        <div className="p-12 text-center ios-card">
          <p className="text-sm font-semibold text-slate-700 dark:text-zinc-300">No matching defects found</p>
          <p className="text-xs text-zinc-400 mt-1">Try broadening your query keywords or selecting "All Trackers".</p>
        </div>
      ) : (
        <div className="space-y-4">
          {results.map((res) => (
            <div
              key={res.defect_id}
              className="ios-card p-5 space-y-3 hover:border-blue-500/30 transition-all"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <span className="font-mono font-bold text-sm text-blue-600 dark:text-blue-400">
                    {res.defect_id}
                  </span>
                  <IOSBadge variant="blue" size="sm">
                    {res.source_repo}
                  </IOSBadge>
                  {res.resolution && (
                    <IOSBadge variant="green" size="sm">
                      {res.resolution}
                    </IOSBadge>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <span className="text-xs font-mono text-zinc-400">RRF Score:</span>
                  <span className="text-xs font-mono font-bold text-cyan-400">
                    {res.similarity_score.toFixed(3)}
                  </span>
                </div>
              </div>

              <h3 className="font-bold text-base text-slate-900 dark:text-white">
                {res.title}
              </h3>

              <p className="text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
                {res.description}
              </p>

              {res.stack_trace && (
                <div className="p-3 rounded-xl bg-[#090D16] border border-white/10 font-mono text-[11px] text-zinc-300 overflow-x-auto">
                  <pre>{res.stack_trace}</pre>
                </div>
              )}

              {res.matched_chunk && (
                <div className="text-[11px] text-zinc-400 flex items-center gap-1.5 pt-1">
                  <span className="font-semibold text-slate-700 dark:text-zinc-300">Matched Chunk:</span>
                  <span>{res.matched_chunk}</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
