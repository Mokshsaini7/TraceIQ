import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Cpu,
  Database,
  Layers,
  FileCode,
  CheckCircle2,
  Search,
  Zap,
  GitBranch,
  Activity,
  Terminal,
  Lock,
  ExternalLink,
  ChevronRight
} from 'lucide-react';
import { TraceIQLogo } from '../components/ui/TraceIQLogo';
import { IOSBadge } from '../components/ios/IOSBadge';
import { BUG_PRESETS } from '../data/mockData';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();

  const handleSelectPreset = (presetId: string) => {
    navigate(`/submit?preset=${presetId}`);
  };

  const agents = [
    {
      id: 'triage',
      step: '01',
      name: 'Triage Agent',
      role: 'Taxonomy & Severity',
      desc: 'Classifies defect category, computes severity (Blocker to Trivial), priority (P1–P4), and audits report completeness.',
      tag: 'Classification',
      icon: Activity,
      color: 'blue' as const,
    },
    {
      id: 'log',
      step: '02',
      name: 'Log Analysis Agent',
      role: 'Stack Forensics',
      desc: 'Parses multi-language stack traces, extracts error signatures, normalizes memory frames, and establishes an event timeline.',
      tag: 'Stack Forensics',
      icon: Terminal,
      color: 'teal' as const,
    },
    {
      id: 'duplicate',
      step: '03',
      name: 'Duplicate Detection Agent',
      role: 'Deduplication',
      desc: 'Executes hybrid retrieval across the historical records loaded into the knowledge base to pinpoint high-confidence duplicates with RRF fusion.',
      tag: 'Deduplication',
      icon: GitBranch,
      color: 'purple' as const,
    },
    {
      id: 'root-cause',
      step: '04',
      name: 'Root Cause Agent',
      role: 'Causal Reasoner',
      desc: 'Synthesizes runtime log evidence with historical resolution context to formulate ranked hypotheses with confidence scores.',
      tag: 'Causal Inference',
      icon: Cpu,
      color: 'orange' as const,
    },
    {
      id: 'remediation',
      step: '05',
      name: 'Remediation Agent',
      role: 'Actionable Patches',
      desc: 'Mines resolved defect commits to generate grounded code patches, step-by-step verification steps, and mandatory citations.',
      tag: 'Fix Recommendations',
      icon: Sparkles,
      color: 'green' as const,
    },
  ];

  const datasets = [
    {
      name: 'Mozilla Bugzilla Defect Archive',
      count: '119,585 bugs',
      desc: 'Curated Mozilla Core, Firefox, and Gecko bugs with comments, stack traces, and patch links from BugsRepo & MSR.',
      badge: 'C++ / Rust / JS',
    },
    {
      name: 'Eclipse Platform Repository',
      count: '68,000 defects',
      desc: 'Eclipse JDT, Platform, and Modeling Framework defect tracking reports with detailed stack frames and lifecycle states.',
      badge: 'Java / OSGi',
    },
    {
      name: 'Apache Software Foundation',
      count: '32,000 issues',
      desc: 'Jira issue traces from Cassandra, Hadoop, HBase, and Spark with mapped schemas and duplicate pair labels.',
      badge: 'Distributed Systems',
    },
  ];

  return (
    <div className="space-y-16 sm:space-y-24 pb-16">
      {/* Hero Section */}
      <section className="relative pt-6 sm:pt-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center">
        {/* Subtle Ambient Apple iOS Glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[340px] sm:w-[600px] h-[340px] sm:h-[400px] bg-gradient-to-tr from-blue-500/15 via-cyan-400/10 to-indigo-500/15 blur-3xl rounded-full pointer-events-none -z-10" />

        {/* Top Floating Capsule Announcement */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-white/70 dark:bg-zinc-800/80 border border-black/10 dark:border-white/10 shadow-sm backdrop-blur-xl mb-6">
          <IOSBadge variant="blue" size="sm" dot>
            TraceIQ 1.0 Ready
          </IOSBadge>
          <span className="text-xs font-medium text-slate-700 dark:text-zinc-300">
            Multi-Agent RAG Defect Diagnosis Platform
          </span>
          <ChevronRight className="w-3.5 h-3.5 text-zinc-400" />
        </div>

        {/* Hero Title */}
        <h1 className="text-3xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white max-w-4xl mx-auto leading-tight">
          Intelligent Bug Diagnosis.{' '}
          <span className="bg-gradient-to-r from-blue-600 via-cyan-500 to-indigo-600 dark:from-blue-400 dark:via-cyan-300 dark:to-indigo-400 bg-clip-text text-transparent">
            Grounded in Defect History.
          </span>
        </h1>

        {/* Subtitle */}
        <p className="mt-5 text-base sm:text-lg text-slate-600 dark:text-zinc-300 max-w-3xl mx-auto leading-relaxed">
          Paste a raw crash log or stack trace. A five-agent Python pipeline examines the submitted evidence and searches the historical records currently loaded into the knowledge base. Recommendations are guidance and must be reviewed.
        </p>

        {/* Action Buttons */}
        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link
            to="/submit"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-6 py-3 rounded-2xl bg-[#007AFF] hover:bg-[#0066D6] dark:bg-[#0A84FF] dark:hover:bg-[#0070E0] text-white font-semibold text-sm sm:text-base shadow-lg shadow-blue-500/25 active:scale-95 transition-all"
          >
            <Sparkles className="w-4 h-4" />
            <span>Launch Diagnose Studio</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </Link>

          <Link
            to="/knowledge-base"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-6 py-3 rounded-2xl bg-white/80 dark:bg-zinc-800/80 hover:bg-white dark:hover:bg-zinc-700 text-slate-800 dark:text-zinc-100 font-medium text-sm sm:text-base border border-black/10 dark:border-white/10 shadow-sm backdrop-blur-xl active:scale-95 transition-all"
          >
            <Database className="w-4 h-4 text-blue-500" />
            <span>Explore Historical Defect Archive</span>
          </Link>
        </div>

        {/* Quick 1-Click Preset Crash Reports */}
        <div className="mt-8 pt-6 border-t border-black/5 dark:border-white/5 flex flex-wrap items-center justify-center gap-2 text-xs">
          <span className="text-slate-500 dark:text-zinc-400 font-medium mr-1">
            Try 1-Click Sample Crashes:
          </span>
          {BUG_PRESETS.map((preset) => (
            <button
              key={preset.id}
              onClick={() => handleSelectPreset(preset.id)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/60 dark:bg-zinc-800/60 hover:bg-white dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-300 border border-black/5 dark:border-white/10 shadow-sm transition-all active:scale-95"
            >
              <span>{preset.icon}</span>
              <span className="font-semibold">{preset.name}</span>
              <span className="text-[10px] text-zinc-400 uppercase font-mono">({preset.badge})</span>
            </button>
          ))}
        </div>
      </section>

      {/* Interactive iOS Floating Preview Window */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto">
        <div className="relative rounded-3xl p-1 bg-gradient-to-b from-white/40 via-white/10 to-transparent dark:from-white/15 dark:via-white/5 dark:to-transparent shadow-2xl">
          <div className="rounded-[22px] bg-white/90 dark:bg-[#1C1C1E]/90 border border-black/10 dark:border-white/10 backdrop-blur-2xl overflow-hidden">
            {/* macOS / iOS Window Header */}
            <div className="px-4 py-3 bg-black/5 dark:bg-white/5 border-b border-black/5 dark:border-white/10 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-[#FF5F56] border border-[#E0443E]" />
                <span className="w-3 h-3 rounded-full bg-[#FFBD2E] border border-[#DEA123]" />
                <span className="w-3 h-3 rounded-full bg-[#27C93F] border border-[#1AAB29]" />
                <span className="ml-2 text-xs font-semibold text-slate-500 dark:text-zinc-400 font-mono">
                  TraceIQ Diagnostic Inspector — Report #sub-moz-8910
                </span>
              </div>
              <div className="flex items-center gap-2">
                <IOSBadge variant="red" size="sm" dot>
                  Blocker (P1)
                </IOSBadge>
                <IOSBadge variant="blue" size="sm">
                  94.2% Duplicate Found
                </IOSBadge>
              </div>
            </div>

            {/* Inner Inspector Body */}
            <div className="p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column: Triage & Root Cause */}
              <div className="lg:col-span-2 space-y-4">
                <div className="p-4 rounded-2xl bg-blue-500/5 dark:bg-blue-500/10 border border-blue-500/15">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-bold uppercase tracking-wider text-blue-600 dark:text-blue-400 flex items-center gap-1.5">
                      <Sparkles className="w-3.5 h-3.5" />
                      Root Cause Identified (Confidence 92%)
                    </span>
                    <span className="text-[11px] font-mono text-zinc-400">Cited: MOZ-1482910</span>
                  </div>
                  <h3 className="font-semibold text-sm sm:text-base text-slate-900 dark:text-white">
                    Buffer overrun in IPC message deserializer during dense canvas updates
                  </h3>
                  <p className="mt-1 text-xs text-slate-600 dark:text-zinc-300 leading-relaxed">
                    Boundary check verified (offset &gt; buffer_size) instead of (offset + size &gt; buffer_size), causing an out-of-bounds pointer read when payload exactly reaches the 1MB buffer edge.
                  </p>
                </div>

                {/* Code Diff Preview */}
                <div className="rounded-2xl bg-[#090D16] border border-white/10 p-3 sm:p-4 text-xs font-mono text-zinc-300 overflow-x-auto">
                  <div className="flex items-center justify-between text-[11px] text-zinc-400 mb-2 border-b border-white/10 pb-1.5">
                    <span>Verified Code Patch (Remediation Agent)</span>
                    <span className="text-emerald-400">Grounded Citation</span>
                  </div>
                  <pre className="text-[11px] leading-relaxed">
                    <span className="text-zinc-500">--- a/dom/ipc/ContentChild.cpp</span>{'\n'}
                    <span className="text-zinc-500">+++ b/dom/ipc/ContentChild.cpp</span>{'\n'}
                    <span className="text-cyan-400">@@ -309,7 +309,9 @@ bool ContentChild::RecvUpdate(...) @@</span>{'\n'}
                    <span className="text-emerald-400">+   // Guard against buffer overrun when payload approaches mapped limit</span>{'\n'}
                    <span className="text-emerald-400">+   if (MOZ_UNLIKELY(payload.offset + payload.size &gt; mSharedBuffer-&gt;Size())) &#123;</span>{'\n'}
                    <span className="text-emerald-400">+       NS_WARNING("Refusing to read beyond SharedMemory boundary");</span>{'\n'}
                    <span className="text-emerald-400">+       return false;</span>{'\n'}
                    <span className="text-emerald-400">+   &#125;</span>{'\n'}
                    <span className="text-rose-400">-   mSharedBuffer-&gt;ReadBuffer(payload.offset, payload.size);</span>{'\n'}
                    <span className="text-emerald-400">+   mSharedBuffer-&gt;ReadBufferSafe(payload.offset, payload.size);</span>
                  </pre>
                </div>
              </div>

              {/* Right Column: Multi-Agent Telemetry */}
              <div className="space-y-3">
                <div className="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400 px-1">
                  5-Agent Pipeline Execution
                </div>

                <div className="space-y-2">
                  <div className="p-2.5 rounded-xl bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-400" />
                      <span className="font-medium text-slate-800 dark:text-zinc-200">Triage Agent</span>
                    </div>
                    <span className="font-mono text-[11px] text-zinc-400">340ms • P1 Blocker</span>
                  </div>

                  <div className="p-2.5 rounded-xl bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-400" />
                      <span className="font-medium text-slate-800 dark:text-zinc-200">Log Analysis</span>
                    </div>
                    <span className="font-mono text-[11px] text-zinc-400">580ms • SIGSEGV</span>
                  </div>

                  <div className="p-2.5 rounded-xl bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-400" />
                      <span className="font-medium text-slate-800 dark:text-zinc-200">Duplicate Check</span>
                    </div>
                    <span className="font-mono text-[11px] text-blue-400">94.2% match</span>
                  </div>

                  <div className="p-2.5 rounded-xl bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-400" />
                      <span className="font-medium text-slate-800 dark:text-zinc-200">Root Cause</span>
                    </div>
                    <span className="font-mono text-[11px] text-purple-400">0.92 confidence</span>
                  </div>

                  <div className="p-2.5 rounded-xl bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 flex items-center justify-between text-xs">
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-400" />
                      <span className="font-medium text-slate-800 dark:text-zinc-200">Remediation</span>
                    </div>
                    <span className="font-mono text-[11px] text-emerald-400">Patch Verified</span>
                  </div>
                </div>

                <Link
                  to="/reports/sub-moz-8910"
                  className="w-full mt-2 inline-flex items-center justify-center gap-1.5 py-2 rounded-xl bg-blue-500/10 hover:bg-blue-500/20 text-blue-600 dark:text-blue-400 text-xs font-semibold transition-all"
                >
                  <span>Open Full Diagnostic Report</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 5-Agent Architecture Section */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="text-center max-w-3xl mx-auto mb-12">
          <IOSBadge variant="purple" size="sm">
            Python Orchestrated
          </IOSBadge>
          <h2 className="mt-3 text-2xl sm:text-4xl font-bold tracking-tight text-slate-900 dark:text-white">
            The 5 Specialized Diagnostic Agents
          </h2>
          <p className="mt-2 text-sm sm:text-base text-slate-600 dark:text-zinc-400">
            Rather than asking a single LLM to guess, TraceIQ deploys specialized agents running in parallel and sequential state branches.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
          {agents.map((agent) => {
            const Icon = agent.icon;
            return (
              <div
                key={agent.id}
                className="ios-card p-6 flex flex-col justify-between hover:border-blue-500/30 transition-all group"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-10 h-10 rounded-2xl bg-blue-500/10 text-blue-600 dark:text-blue-400 flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Icon className="w-5 h-5" />
                    </div>
                    <IOSBadge variant={agent.color} size="sm">
                      {agent.step} {agent.tag}
                    </IOSBadge>
                  </div>

                  <h3 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
                    {agent.name}
                  </h3>
                  <p className="text-xs font-medium text-blue-600 dark:text-blue-400 mt-0.5">
                    {agent.role}
                  </p>
                  <p className="mt-3 text-xs sm:text-sm text-slate-600 dark:text-zinc-400 leading-relaxed">
                    {agent.desc}
                  </p>
                </div>

                <div className="mt-6 pt-4 border-t border-black/5 dark:border-white/5 flex items-center justify-between text-[11px] text-zinc-400">
                  <span>Input: BugReport State</span>
                  <span className="text-emerald-500 font-mono">Pydantic Validated</span>
                </div>
              </div>
            );
          })}

          {/* Architecture Card */}
          <div className="ios-card p-6 flex flex-col justify-between bg-gradient-to-br from-blue-500/10 via-indigo-500/5 to-transparent border-blue-500/20">
            <div>
              <div className="w-10 h-10 rounded-2xl bg-blue-500/20 text-blue-600 dark:text-blue-400 flex items-center justify-center mb-4">
                <Layers className="w-5 h-5" />
              </div>
              <h3 className="text-lg font-bold text-slate-900 dark:text-white tracking-tight">
                Inspect System Architecture
              </h3>
              <p className="mt-2 text-xs sm:text-sm text-slate-600 dark:text-zinc-300 leading-relaxed">
                Explore the complete technical topology: FastAPI backend, PostgreSQL/pgvector storage and sequential Python agents, and PostgreSQL relational schemas.
              </p>
            </div>
            <Link
              to="/architecture"
              className="mt-6 inline-flex items-center gap-2 text-xs font-semibold text-blue-600 dark:text-blue-400 hover:underline"
            >
              <span>View System Architecture & Specs</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Historical Knowledge Base Datasets Section */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="rounded-3xl p-6 sm:p-10 bg-white/60 dark:bg-[#1C1C1E]/60 border border-black/10 dark:border-white/10 backdrop-blur-2xl">
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-8">
            <div>
              <IOSBadge variant="teal" size="sm">
                Historical Defect Records
              </IOSBadge>
              <h2 className="mt-2 text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
                Historical Defect Knowledge Base
              </h2>
              <p className="mt-1 text-sm text-slate-600 dark:text-zinc-400">
                Using historical records as supporting references; suggested fixes are not presented as tested patches.
              </p>
            </div>
            <Link
              to="/search"
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-blue-500/10 hover:bg-blue-500/20 text-blue-600 dark:text-blue-400 text-xs sm:text-sm font-semibold transition-all self-start md:self-auto"
            >
              <Search className="w-4 h-4" />
              <span>Query Defect Search Engine</span>
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {datasets.map((ds) => (
              <div
                key={ds.name}
                className="p-5 rounded-2xl bg-white/80 dark:bg-zinc-800/80 border border-black/5 dark:border-white/5 space-y-3"
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-blue-600 dark:text-blue-400 font-mono">
                    {ds.count}
                  </span>
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-black/5 dark:bg-white/10 text-zinc-400 font-medium">
                    {ds.badge}
                  </span>
                </div>
                <h4 className="font-semibold text-sm text-slate-900 dark:text-white">
                  {ds.name}
                </h4>
                <p className="text-xs text-slate-600 dark:text-zinc-400 leading-relaxed">
                  {ds.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Security & Non-Functional Guarantees */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl bg-white/60 dark:bg-[#1C1C1E]/60 border border-black/5 dark:border-white/10 backdrop-blur-xl">
            <ShieldCheck className="w-6 h-6 text-emerald-500 mb-3" />
            <h4 className="text-sm font-bold text-slate-900 dark:text-white">Zero Execution Sandbox</h4>
            <p className="mt-1 text-xs text-slate-600 dark:text-zinc-400 leading-relaxed">
              Uploaded files and logs are statically parsed as text only. No code or script is ever executed.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white/60 dark:bg-[#1C1C1E]/60 border border-black/5 dark:border-white/10 backdrop-blur-xl">
            <Lock className="w-6 h-6 text-blue-500 mb-3" />
            <h4 className="text-sm font-bold text-slate-900 dark:text-white">Client PII Redactor</h4>
            <p className="mt-1 text-xs text-slate-600 dark:text-zinc-400 leading-relaxed">
              Integrated pattern scrubber masks API keys, IP addresses, JWT tokens, and credentials before transmission.
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white/60 dark:bg-[#1C1C1E]/60 border border-black/5 dark:border-white/10 backdrop-blur-xl">
            <CheckCircle2 className="w-6 h-6 text-cyan-500 mb-3" />
            <h4 className="text-sm font-bold text-slate-900 dark:text-white">Mandatory Citation Rule</h4>
            <p className="mt-1 text-xs text-slate-600 dark:text-zinc-400 leading-relaxed">
              Every diagnosis claim and code patch must explicitly cite a historical defect ID (e.g. MOZ-1482910).
            </p>
          </div>

          <div className="p-5 rounded-2xl bg-white/60 dark:bg-[#1C1C1E]/60 border border-black/5 dark:border-white/10 backdrop-blur-xl">
            <Zap className="w-6 h-6 text-amber-500 mb-3" />
            <h4 className="text-sm font-bold text-slate-900 dark:text-white">Hybrid Rank Fusion</h4>
            <p className="mt-1 text-xs text-slate-600 dark:text-zinc-400 leading-relaxed">
              Reciprocal Rank Fusion merges dense semantic embeddings with BM25 sparse keyword token matching.
            </p>
          </div>
        </div>
      </section>

      {/* Call to Action Banner */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto text-center">
        <div className="rounded-3xl p-8 sm:p-12 bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 text-white shadow-2xl relative overflow-hidden">
          <div className="relative z-10 space-y-4">
            <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight">
              Ready to Accelerate Bug Triage & Root Cause Analysis?
            </h2>
            <p className="text-sm sm:text-base text-blue-100 max-w-2xl mx-auto leading-relaxed">
              Submit your stack trace, run the five-agent diagnosis pipeline, and receive grounded fix recommendations in seconds.
            </p>
            <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-3">
              <Link
                to="/submit"
                className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-white text-blue-600 font-bold text-sm shadow-md hover:bg-blue-50 active:scale-95 transition-all"
              >
                Start Intelligent Diagnosis
              </Link>
              <Link
                to="/dashboard"
                className="w-full sm:w-auto px-6 py-3 rounded-2xl bg-white/20 hover:bg-white/30 text-white font-medium text-sm backdrop-blur-md active:scale-95 transition-all"
              >
                View Live Dashboard
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
