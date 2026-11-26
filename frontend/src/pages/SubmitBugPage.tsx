import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ArrowRight,
  Code2,
  FileText,
  ShieldCheck,
  Sparkles,
} from 'lucide-react';
import { IOSToggle } from '../components/ios/IOSToggle';
import { IOSBadge } from '../components/ios/IOSBadge';
import { ToastItem, ToastMessage } from '../components/ui/Toast';
import { api } from '../services/api';

export const SubmitBugPage: React.FC = () => {
  const navigate = useNavigate();

  // Keep an in-progress submission when the user navigates between Diagnose Studio,
  // Reports, Dashboard, and other routes. sessionStorage is tab-scoped and is not
  // sent to the backend until the user explicitly submits the form.
  const DRAFT_KEY = 'traceiq:diagnose-studio:draft:v1';
  const [restoredDraft] = useState(() => {
    try {
      const raw = sessionStorage.getItem(DRAFT_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });

  const [title, setTitle] = useState(restoredDraft?.title ?? '');
  const [bugDescription, setBugDescription] = useState(restoredDraft?.bugDescription ?? '');
  const [reportedSeverity, setReportedSeverity] = useState(restoredDraft?.reportedSeverity ?? 'medium');
  const [requestedPriority, setRequestedPriority] = useState(restoredDraft?.requestedPriority ?? 'p3');
  const [language, setLanguage] = useState(restoredDraft?.language ?? 'Java');
  const [sourceCode, setSourceCode] = useState(restoredDraft?.sourceCode ?? '');
  const [stackTrace, setStackTrace] = useState(restoredDraft?.stackTrace ?? '');
  const [terminalOutput, setTerminalOutput] = useState(restoredDraft?.terminalOutput ?? '');
  const [redactPII, setRedactPII] = useState(restoredDraft?.redactPII ?? true);

  const [isDiagnosing, setIsDiagnosing] = useState(false);
  const [activeAgentStep, setActiveAgentStep] = useState(0);
  const [agentLogs, setAgentLogs] = useState<string[]>([]);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [draftSaved, setDraftSaved] = useState(Boolean(restoredDraft));

  useEffect(() => {
    try {
      sessionStorage.setItem(DRAFT_KEY, JSON.stringify({
        title, bugDescription, reportedSeverity, requestedPriority, language,
        sourceCode, stackTrace, terminalOutput, redactPII,
        updatedAt: new Date().toISOString(),
      }));
      setDraftSaved(true);
    } catch {
      // Storage can be unavailable in private/restricted browser contexts.
      setDraftSaved(false);
    }
  }, [title, bugDescription, reportedSeverity, requestedPriority, language,
      sourceCode, stackTrace, terminalOutput, redactPII]);

  const clearDraft = () => {
    setTitle('');
    setBugDescription('');
    setReportedSeverity('medium');
    setRequestedPriority('p3');
    setLanguage('Java');
    setSourceCode('');
    setStackTrace('');
    setTerminalOutput('');
    setRedactPII(true);
    try { sessionStorage.removeItem(DRAFT_KEY); } catch { /* ignore unavailable storage */ }
    setDraftSaved(false);
  };

  const addToast = (
    type: 'success' | 'error' | 'info',
    toastTitle: string,
    message?: string,
  ) => {
    setToasts((previous) => [
      ...previous,
      { id: Math.random().toString(36).slice(2), type, title: toastTitle, message },
    ]);
  };

  const removeToast = (id: string) => {
    setToasts((previous) => previous.filter((toast) => toast.id !== id));
  };

  const scrubPII = (value: string) => {
    if (!redactPII) return value;

    return value
      .replace(
        /\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b/g,
        '[REDACTED_IP]',
      )
      .replace(
        /(?:bearer|token|apikey|password|secret|auth)[=:\s]+["']?([a-zA-Z0-9_\-.]{8,})["']?/gi,
        (match) => `${match.split(/[=:\s]/)[0]}=[REDACTED_SECRET]`,
      )
      .replace(
        /[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/g,
        '[REDACTED_EMAIL]',
      );
  };

  const agentSteps = [
    { title: 'Save bug report', agent: 'Submission API' },
    { title: 'Run Triage and Log Analysis automatically', agent: 'Intake orchestrator' },
    { title: 'Run downstream diagnosis agents', agent: 'Python orchestrator' },
    { title: 'Open diagnosis report', agent: 'Diagnosis API' },
  ];

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (title.trim().length < 5) {
      addToast('error', 'Bug title required', 'Enter a title containing at least 5 characters.');
      return;
    }

    if (bugDescription.trim().length < 10) {
      addToast('error', 'Bug description required', 'Describe the observed impact in at least 10 characters.');
      return;
    }

    // Stack traces and logs are optional; the intake agents return an explicit
    // incomplete-analysis state when technical evidence is absent.

    // Keep the reporter's impact description distinct from technical evidence.
    const safeSourceCode = scrubPII(sourceCode);
    const safeStackTrace = scrubPII(stackTrace);
    const safeTerminalOutput = scrubPII(terminalOutput);
    const analysisDescription = [
      scrubPII(bugDescription),
      safeSourceCode ? `Source code:\n${safeSourceCode}` : '',
    ].filter(Boolean).join('\n\n');

    setIsDiagnosing(true);
    setActiveAgentStep(0);
    setAgentLogs(['Saving your bug report...']);

    try {
      const created = await api.createSubmission({
        title: scrubPII(title),
        description: analysisDescription,
        stack_trace: safeStackTrace || undefined,
        error_logs: safeTerminalOutput || undefined,
        programming_language: language,
        // Reporter labels are context only; the triage agent independently reassesses them.
        severity: reportedSeverity,
        priority: requestedPriority,
      });

      setActiveAgentStep(1);
      setAgentLogs(['Bug report saved.', 'Triage Agent and Log Analysis Agent ran automatically.', 'Combined agent context persisted for downstream diagnosis.']);

      setActiveAgentStep(2);
      setAgentLogs((previous) => [
        ...previous,
        'Starting TraceIQ five-agent diagnosis...',
      ]);

      const diagnosis = await api.triggerDiagnosis(created.id);
      if (diagnosis.status !== 'completed') {
        throw new Error(
          diagnosis.error_message || 'The diagnosis pipeline did not complete successfully.',
        );
      }

      setActiveAgentStep(3);
      setAgentLogs((previous) => [...previous, 'Diagnosis completed. Opening report...']);
      try { sessionStorage.removeItem(DRAFT_KEY); } catch { /* ignore unavailable storage */ }
      navigate(`/reports/${created.id}`);
    } catch (error: any) {
      setIsDiagnosing(false);
      addToast(
        'error',
        'Diagnosis failed',
        error.response?.data?.detail ||
          error.message ||
          'Could not complete defect diagnosis.',
      );
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      <div className="fixed top-20 right-6 z-50 space-y-2 pointer-events-none">
        {toasts.map((toast) => (
          <div key={toast.id} className="pointer-events-auto">
            <ToastItem toast={toast} onClose={() => removeToast(toast.id)} />
          </div>
        ))}
      </div>

      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <div className="flex items-center gap-2 flex-wrap">
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-slate-900 dark:text-white">
              Diagnose Defect Studio
            </h1>
            <IOSBadge variant="blue" size="sm">TraceIQ Diagnosis</IOSBadge>
          </div>
          <p className="mt-1 text-sm text-slate-600 dark:text-zinc-400">
            Submit the affected source code and terminal output for evidence-based defect analysis.
          </p>
        </div>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-2 rounded-xl border border-emerald-500/15 bg-emerald-500/5 px-4 py-2.5">
        <div className="flex items-center gap-2 text-xs text-slate-600 dark:text-zinc-300">
          <ShieldCheck className="h-4 w-4 text-emerald-500" />
          <span>{draftSaved ? 'Draft autosaved in this browser tab. You can switch pages and return without losing these fields.' : 'Your draft will be saved automatically as you edit.'}</span>
        </div>
        <button type="button" onClick={clearDraft}
          className="text-xs font-semibold text-slate-500 hover:text-red-500 transition-colors">
          Clear draft
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <section className="ios-card p-6 space-y-5">
          <div className="flex items-center justify-between border-b border-black/5 dark:border-white/5 pb-3 gap-4">
            <h2 className="font-semibold text-slate-900 dark:text-white text-base flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-500" />
              <span>1. Bug Information</span>
            </h2>
            <IOSToggle
              checked={redactPII}
              onChange={setRedactPII}
              label="Sanitize PII"
              description="Mask IP addresses, tokens, and secrets"
            />
          </div>

          <div>
            <label htmlFor="bug-title" className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1.5">
              Defect Title / Summary *
            </label>
            <input
              id="bug-title"
              type="text"
              required
              minLength={5}
              maxLength={255}
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="e.g. NullPointerException in Workspace.save() during auto-build"
              className="w-full px-4 py-3 rounded-xl bg-slate-100/80 dark:bg-zinc-800/80 border border-black/5 dark:border-white/10 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            />
          </div>

          <div>
            <label htmlFor="bug-description" className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1.5">
              Observed Behaviour & Impact *
            </label>
            <textarea id="bug-description" required minLength={10} rows={4} value={bugDescription}
              onChange={(event) => setBugDescription(event.target.value)}
              placeholder="What failed, who is affected, how often it occurs, and whether a workaround exists..."
              className="w-full px-4 py-3 rounded-xl bg-slate-100/80 dark:bg-zinc-800/80 border border-black/5 dark:border-white/10 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40" />
          </div>

          <div className="grid sm:grid-cols-2 gap-4">
            <div>
              <label htmlFor="reported-severity" className="block text-xs font-semibold text-slate-600 dark:text-zinc-400 mb-1.5">Reported Severity (advisory)</label>
              <select id="reported-severity" value={reportedSeverity} onChange={(e) => setReportedSeverity(e.target.value)} className="w-full px-3 py-3 rounded-xl bg-slate-100/80 dark:bg-zinc-800/80 border border-black/5 dark:border-white/10 text-sm text-slate-900 dark:text-white">
                <option value="critical">Critical — widespread outage / severe security or data impact</option>
                <option value="high">High — major workflow or significant service failure</option>
                <option value="medium">Medium — limited functional defect</option>
                <option value="low">Low — cosmetic / minor impact</option>
              </select>
            </div>
            <div>
              <label htmlFor="requested-priority" className="block text-xs font-semibold text-slate-600 dark:text-zinc-400 mb-1.5">Requested Priority (advisory)</label>
              <select id="requested-priority" value={requestedPriority} onChange={(e) => setRequestedPriority(e.target.value)} className="w-full px-3 py-3 rounded-xl bg-slate-100/80 dark:bg-zinc-800/80 border border-black/5 dark:border-white/10 text-sm text-slate-900 dark:text-white">
                <option value="p1">P1 — Immediate response / active incident</option>
                <option value="p2">P2 — Urgent / major workflow blocked</option>
                <option value="p3">P3 — Normal development queue</option>
                <option value="p4">P4 — Schedule for later / cosmetic</option>
              </select>
            </div>
          </div>
          <p className="text-[11px] text-slate-500 dark:text-zinc-400">These are reporter suggestions, not final decisions. TraceIQ assigns its own severity and priority from impact, urgency, scope, and technical evidence.</p>

          <div className="max-w-sm">
            <label htmlFor="programming-language" className="block text-xs font-semibold text-slate-600 dark:text-zinc-400 mb-1.5">
              Programming Language
            </label>
            <select
              id="programming-language"
              value={language}
              onChange={(event) => setLanguage(event.target.value)}
              className="w-full px-3 py-3 rounded-xl bg-slate-100/80 dark:bg-zinc-800/80 border border-black/5 dark:border-white/10 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            >
              <option value="Java">Java</option>
              <option value="C++">C++</option>
              <option value="Python">Python</option>
              <option value="Scala">Scala</option>
              <option value="Rust">Rust</option>
              <option value="TypeScript">TypeScript / JavaScript</option>
              <option value="Go">Go</option>
              <option value="Other">Other</option>
            </select>
          </div>
        </section>

        <section className="ios-card p-6 space-y-5">
          <div className="flex items-center gap-2 border-b border-black/5 dark:border-white/5 pb-3">
            <Code2 className="w-4 h-4 text-cyan-500" />
            <h2 className="font-semibold text-slate-900 dark:text-white text-base">
              2. Technical Evidence & Logs
            </h2>
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label htmlFor="source-code" className="text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-zinc-300">
                Source Code (Optional)
              </label>
              <span className="text-[11px] text-zinc-400">Paste the relevant code directly</span>
            </div>
            <textarea
              id="source-code"
              rows={8}
              spellCheck={false}
              value={sourceCode}
              onChange={(event) => setSourceCode(event.target.value)}
              placeholder={'// Paste the code related to the defect here\npublic void save() {\n    workspace.getName();\n}'}
              className="w-full px-4 py-3 rounded-xl bg-[#0B0F19] border border-white/10 font-mono text-xs leading-6 text-zinc-200 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40 resize-y"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label htmlFor="stack-trace" className="text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-zinc-300">
                Stack Trace (Optional)
              </label>
              <span className="text-[11px] text-zinc-400">Paste the complete exception traceback</span>
            </div>
            <textarea id="stack-trace" rows={6} spellCheck={false} value={stackTrace}
              onChange={(event) => setStackTrace(event.target.value)}
              placeholder={'Traceback (most recent call last):\n  File "app.py", line 42, in save\n    raise RuntimeError("save failed")'}
              className="w-full px-4 py-3 rounded-xl bg-[#0B0F19] border border-white/10 font-mono text-xs leading-6 text-zinc-200 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40 resize-y" />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1.5">
              <label htmlFor="terminal-output" className="text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-zinc-300">
                Terminal Output / Error Logs
              </label>
              <span className="text-[11px] text-zinc-400">Paste the error produced when it fails</span>
            </div>
            <textarea
              id="terminal-output"
              rows={6}
              spellCheck={false}
              value={terminalOutput}
              onChange={(event) => setTerminalOutput(event.target.value)}
              placeholder={'java.lang.NullPointerException:\n    at com.traceiq.workspace.WorkspaceService.save(WorkspaceService.java:42)'}
              className="w-full px-4 py-3 rounded-xl bg-[#0B0F19] border border-white/10 font-mono text-xs leading-6 text-zinc-200 placeholder:text-zinc-500 focus:outline-none focus:ring-2 focus:ring-blue-500/40 resize-y"
            />
          </div>
        </section>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-1">
          <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-zinc-400">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            <span>On submission, Triage and Log Analysis run automatically; technical logs are optional.</span>
          </div>
          <button
            type="submit"
            disabled={isDiagnosing}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2.5 px-8 py-3.5 rounded-2xl bg-[#007AFF] hover:bg-[#0066D6] dark:bg-[#0A84FF] dark:hover:bg-[#0070E0] text-white font-semibold text-sm shadow-xl shadow-blue-500/25 active:scale-95 transition-all disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4" />
            <span>Start Intelligent Diagnosis</span>
            <ArrowRight className="w-4 h-4 ml-1" />
          </button>
        </div>
      </form>

      {isDiagnosing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-fade-in">
          <div className="w-full max-w-lg rounded-3xl bg-white dark:bg-[#1C1C1E] border border-black/10 dark:border-white/10 p-6 sm:p-8 shadow-2xl space-y-6">
            <div className="flex items-center justify-between border-b border-black/5 dark:border-white/5 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-blue-500/20 text-blue-500 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 animate-spin-slow" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 dark:text-white text-base">TraceIQ Multi-Agent Diagnosis</h3>
                  <p className="text-xs text-slate-500 dark:text-zinc-400">Running the backend diagnosis pipeline...</p>
                </div>
              </div>
              <IOSBadge variant="blue" size="sm" dot>Processing</IOSBadge>
            </div>

            <div className="space-y-3">
              {agentSteps.map((step, index) => {
                const isCurrent = index === activeAgentStep;
                const isDone = index < activeAgentStep;
                return (
                  <div
                    key={step.title}
                    className={`flex items-center justify-between p-3 rounded-2xl transition-all ${
                      isCurrent
                        ? 'bg-blue-500/10 dark:bg-blue-500/15 border border-blue-500/25'
                        : isDone
                          ? 'bg-emerald-500/5 border border-emerald-500/15 opacity-80'
                          : 'opacity-40'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${isDone ? 'bg-emerald-500 text-white' : isCurrent ? 'bg-blue-500 text-white animate-pulse' : 'bg-zinc-700 text-zinc-400'}`}>
                        {isDone ? '✓' : index + 1}
                      </div>
                      <div>
                        <div className="font-medium text-xs sm:text-sm text-slate-900 dark:text-white">{step.title}</div>
                        <div className="text-[10px] text-zinc-400 font-mono">{step.agent}</div>
                      </div>
                    </div>
                    <span className="text-[11px] font-mono text-zinc-400">{isDone ? 'Done' : isCurrent ? 'Running...' : 'Waiting'}</span>
                  </div>
                );
              })}
            </div>

            <div className="p-3 rounded-2xl bg-[#0B0F19] border border-white/10 font-mono text-[11px] text-zinc-300 max-h-28 overflow-y-auto space-y-1">
              {agentLogs.map((log, index) => <div key={`${index}-${log}`} className="text-cyan-400">{log}</div>)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
