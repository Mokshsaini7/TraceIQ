import React, { useState, useEffect } from 'react';
import {
  Cpu,
  Layers,
  Database,
  ArrowRight,
  ShieldCheck,
  CheckCircle2,
  GitBranch,
  Terminal,
  FileCode,
  HardDrive,
  Sparkles,
  ExternalLink,
  ZoomIn
} from 'lucide-react';
import { IOSBadge } from '../components/ios/IOSBadge';
import { api } from '../services/api';
import { SystemArchitecture } from '../types';

export const ArchitecturePage: React.FC = () => {
  const [arch, setArch] = useState<SystemArchitecture | null>(null);
  const [isImageZoomed, setIsImageZoomed] = useState(false);

  useEffect(() => {
    api.getArchitecture()
      .then(setArch)
      .catch((err) => console.error('Failed to load architecture:', err));
  }, []);

  const layers = [
    {
      title: 'Presentation Layer',
      tech: 'React 18 + Vite 6 + TypeScript + Tailwind CSS',
      desc: 'iOS System-inspired interface with responsive mobile Cupertino bar, live agent execution timeline, and grounded fix inspector.',
      badge: 'Frontend',
      color: 'blue' as const,
    },
    {
      title: 'Backend / API Layer',
      tech: 'Python 3.11 + FastAPI + Pydantic v2',
      desc: 'Asynchronous REST API handling multipart uploads, regex & AST stack normalization, schema validation, and Python orchestrator hooks.',
      badge: 'Core Service',
      color: 'teal' as const,
    },
    {
      title: 'AI Agent Layer',
      tech: 'Sequential Python Agent Orchestrator + optional Anthropic refinement',
      desc: '5 specialized Python agents (Triage, Log Analysis, Root Cause, Duplicate Detection, Remediation) running in a sequential pipeline.',
      badge: 'Multi-Agent',
      color: 'purple' as const,
    },
    {
      title: 'RAG Retrieval Engine',
      tech: 'PostgreSQL pgvector (when compatible) + BM25 / RRF',
      desc: 'SentenceTransformer embeddings are used when available; otherwise search safely falls back to BM25 over the records actually loaded.',
      badge: 'Vector DB',
      color: 'orange' as const,
    },
    {
      title: 'Operational & Defect Data Stores',
      tech: 'PostgreSQL / SQLite + CSV and JSON defect samples',
      desc: 'Relational storage for submissions, attachments, diagnoses, and the imported historical defect records.',
      badge: 'Storage',
      color: 'green' as const,
    },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-16">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2">
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
            System Architecture & Technical Design
          </h1>
          <IOSBadge variant="blue" size="sm">
            Milestone 1 Specification
          </IOSBadge>
        </div>
        <p className="mt-1 text-sm text-slate-600 dark:text-zinc-400">
          TraceIQ multi-agent defect diagnosis platform architectural specification and topology.
        </p>
      </div>

      {/* Architecture Diagram Card */}
      <div className="ios-card p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-black/5 dark:border-white/5 pb-3">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-blue-500" />
            <h3 className="font-bold text-base text-slate-900 dark:text-white">
              System Topology (Milestone 1 Architecture Diagram)
            </h3>
          </div>
          <button
            type="button"
            onClick={() => setIsImageZoomed(!isImageZoomed)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-black/5 dark:bg-white/5 text-xs font-medium text-slate-700 dark:text-zinc-300 hover:bg-black/10 dark:hover:bg-white/10 transition-all"
          >
            <ZoomIn className="w-3.5 h-3.5" />
            <span>{isImageZoomed ? 'Reset View' : 'Enlarge Diagram'}</span>
          </button>
        </div>

        {/* Diagram Image */}
        <div
          className={`rounded-2xl overflow-hidden border border-black/10 dark:border-white/10 bg-white dark:bg-zinc-900 transition-all cursor-pointer ${
            isImageZoomed ? 'p-2 max-w-full' : 'p-4 max-h-[500px] flex items-center justify-center'
          }`}
          onClick={() => setIsImageZoomed(!isImageZoomed)}
        >
          <img
            src="/architecture.png"
            alt="Intelligent Bug Diagnosis Platform - System Architecture"
            className="w-full h-auto object-contain rounded-xl shadow-sm"
          />
        </div>
        <p className="text-xs text-center text-zinc-400">
          Figure 1: Full system architecture depicting Presentation, FastAPI, Python Agent Layer, PostgreSQL/pgvector, and Defect Lake.
        </p>
      </div>

      {/* Layer Breakdown Grid */}
      <div className="space-y-4">
        <h3 className="text-lg font-bold text-slate-900 dark:text-white">
          Architectural Layers & Components
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {layers.map((layer) => (
            <div
              key={layer.title}
              className="ios-card p-5 space-y-2 hover:border-blue-500/30 transition-all"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-sm text-slate-900 dark:text-white">
                  {layer.title}
                </span>
                <IOSBadge variant={layer.color} size="sm">
                  {layer.badge}
                </IOSBadge>
              </div>

              <div className="font-mono text-xs text-blue-600 dark:text-blue-400 font-semibold">
                {layer.tech}
              </div>

              <p className="text-xs text-slate-600 dark:text-zinc-400 leading-relaxed pt-1">
                {layer.desc}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Tech Stack Matrix */}
      {arch?.tech_stack && (
        <div className="ios-card p-6 space-y-4">
          <h3 className="text-base font-bold text-slate-900 dark:text-white border-b border-black/5 dark:border-white/5 pb-3">
            Technology Stack Mapping
          </h3>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(arch.tech_stack).map(([key, val]) => (
              <div
                key={key}
                className="p-3.5 rounded-xl bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 space-y-1"
              >
                <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500 dark:text-zinc-400">
                  {key}
                </div>
                <div className="text-xs font-medium text-slate-900 dark:text-white font-mono">
                  {val}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
