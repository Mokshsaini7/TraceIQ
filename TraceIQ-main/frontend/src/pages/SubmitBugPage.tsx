import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Upload,
  AlertCircle,
  FileCode,
  CheckCircle2,
  X,
  FileText,
  Sparkles,
  Info,
  ShieldCheck,
  Terminal,
  Activity,
  Cpu,
  GitBranch,
  Layers,
  ArrowRight,
  Eye,
  EyeOff
} from 'lucide-react';
import { IOSSegmentedControl } from '../components/ios/IOSSegmentedControl';
import { IOSToggle } from '../components/ios/IOSToggle';
import { IOSBadge } from '../components/ios/IOSBadge';
import { ToastItem, ToastMessage } from '../components/ui/Toast';
import { api } from '../services/api';
import { BUG_PRESETS } from '../data/mockData';

const ALLOWED_EXTENSIONS = ['.txt', '.log', '.json', '.csv', '.md', '.py', '.java', '.cpp', '.cc', '.h', '.xml', '.yaml', '.yml'];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export const SubmitBugPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();

  // Mode: Paste vs Upload vs Presets
  const [inputMode, setInputMode] = useState<'paste' | 'upload'>('paste');

  // Form State
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [stackTrace, setStackTrace] = useState('');
  const [errorLogs, setErrorLogs] = useState('');
  const [language, setLanguage] = useState('Java');
  const [framework, setFramework] = useState('');
  const [severity, setSeverity] = useState('critical');
  const [priority, setPriority] = useState('p1');
  const [reproductionSteps, setReproductionSteps] = useState('');
  const [expectedBehavior, setExpectedBehavior] = useState('');
  const [actualBehavior, setActualBehavior] = useState('');

  // Enterprise Privacy & PII Redaction
  const [redactPII, setRedactPII] = useState(true);
  const [showRedactedPreview, setShowRedactedPreview] = useState(false);

  // Files
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [fileErrors, setFileErrors] = useState<string[]>([]);

  // Agent Pipeline Execution State
  const [isDiagnosing, setIsDiagnosing] = useState(false);
  const [activeAgentStep, setActiveAgentStep] = useState(0);
  const [agentLogs, setAgentLogs] = useState<string[]>([]);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  // Load preset if specified in URL query
  useEffect(() => {
    const presetId = searchParams.get('preset');
    if (presetId) {
      const found = BUG_PRESETS.find((p) => p.id === presetId);
      if (found) {
        loadPreset(found);
      }
    }
  }, [searchParams]);

  const loadPreset = (preset: (typeof BUG_PRESETS)[0]) => {
    setTitle(preset.title);
    setDescription(preset.description);
    setStackTrace(preset.stack_trace);
    setErrorLogs(preset.error_logs);
    setLanguage(preset.language);
    setFramework(preset.framework);
    setSeverity(preset.severity);
    setPriority(preset.priority);
    setReproductionSteps(
      '1. Trigger background resource sync / high-throughput event\n2. Observe thread contention\n3. Exception is thrown with stack trace'
    );
    setExpectedBehavior('Operation completes gracefully or returns bounded error status');
    setActualBehavior('Process abruptly fails or unhandled runtime exception terminates thread');
    addToast('info', `Loaded ${preset.name}`, 'Preset fields populated. Ready for agent diagnosis.');
  };

  const addToast = (type: 'success' | 'error' | 'info', title: string, message?: string) => {
    setToasts((prev) => [...prev, { id: Math.random().toString(), type, title, message }]);
  };

  const removeToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Real-time stack detection
  const detectedException = React.useMemo(() => {
    if (!stackTrace) return null;
    const match = stackTrace.match(/([a-zA-Z0-9_.]+(?:Exception|Error|SIGSEGV|SIGABRT|Fault))/);
    return match ? match[1] : null;
  }, [stackTrace]);

  const scrubPII = (text: string) => {
    if (!redactPII) return text;
    return text
      .replace(/\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b/g, '[REDACTED_IP]')
      .replace(/(?:bearer|token|apikey|password|secret|auth)[=:\s]+["']?([a-zA-Z0-9_\-\.]{8,})["']?/gi, '$1=[REDACTED_SECRET]')
      .replace(/[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+/g, '[REDACTED_EMAIL]');
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const files = Array.from(e.target.files);
    const valid: File[] = [];
    const errors: string[] = [];

    files.forEach((file) => {
      const ext = '.' + file.name.split('.').pop()?.toLowerCase();
      if (!ALLOWED_EXTENSIONS.includes(ext)) {
        errors.push(`File "${file.name}" has an unsupported format.`);
        return;
      }
      if (file.size > MAX_FILE_SIZE) {
        errors.push(`File "${file.name}" exceeds 10MB limit.`);
        return;
      }
      valid.push(file);

      // Read text content of first file if description or stack is empty
      if (files.length === 1 && !stackTrace) {
        const reader = new FileReader();
        reader.onload = (event) => {
          const content = event.target?.result as string;
          if (content) {
            setStackTrace(content.slice(0, 5000));
            setTitle(title || `Defect report parsed from ${file.name}`);
            setDescription(description || `Attached diagnostic log: ${file.name}`);
          }
        };
        reader.readAsText(file);
      }
    });

    setFileErrors(errors);
    setSelectedFiles((prev) => [...prev, ...valid]);
  };

  const removeFile = (index: number) => {
    setSelectedFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const agentSteps = [
    { title: 'Save bug report', agent: 'API', time: 'Backend request' },
    { title: 'Upload diagnostic attachments', agent: 'File Service', time: 'Backend request' },
    { title: 'Run the five-agent diagnosis pipeline', agent: 'Python Orchestrator', time: 'Actual backend execution' },
    { title: 'Open the saved diagnosis report', agent: 'Report API', time: 'Backend response' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim()) {
      addToast('error', 'Title is required', 'Please provide a descriptive title for this defect.');
      return;
    }
    if (!description.trim() && !stackTrace.trim() && selectedFiles.length === 0) {
      addToast('error', 'Missing Defect Evidence', 'Please provide a description, stack trace, or attach a log file.');
      return;
    }

    setIsDiagnosing(true);
    setActiveAgentStep(0);
    setAgentLogs(['Saving your bug report...']);

    try {
      const created = await api.createSubmission({
        title: scrubPII(title),
        description: scrubPII(description || 'See attached diagnostic files.'),
        stack_trace: stackTrace ? scrubPII(stackTrace) : undefined,
        error_logs: errorLogs ? scrubPII(errorLogs) : undefined,
        programming_language: language,
        framework,
        severity,
        priority,
        reproduction_steps: reproductionSteps ? scrubPII(reproductionSteps) : undefined,
        expected_behavior: expectedBehavior ? scrubPII(expectedBehavior) : undefined,
        actual_behavior: actualBehavior ? scrubPII(actualBehavior) : undefined,
      });

      setActiveAgentStep(1);
      setAgentLogs(['Bug report saved. Uploading attachments...']);
      for (const file of selectedFiles) {
        await api.uploadAttachment(created.id, file);
      }

      setActiveAgentStep(2);
      setAgentLogs(['Attachments saved. Running the real TraceIQ diagnosis pipeline...']);
      const diagnosis = await api.triggerDiagnosis(created.id);
      if (diagnosis.status !== 'completed') {
        throw new Error(diagnosis.error_message || 'The diagnosis pipeline did not complete successfully.');
      }

      setActiveAgentStep(3);
      setAgentLogs(['Diagnosis completed. Opening the report...']);
      navigate(`/reports/${created.id}`);
    } catch (err: any) {
      setIsDiagnosing(false);
      addToast('error', 'Diagnosis Failed', err.response?.data?.detail || err.message || 'Could not complete defect diagnosis.');
    }
  };


  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
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
              Diagnose Defect Studio
            </h1>
            <IOSBadge variant="blue" size="sm">
              M1.3 Submission Module
            </IOSBadge>
          </div>
          <p className="mt-1 text-sm text-slate-600 dark:text-zinc-400">
            Submit a raw crash report or stack trace. The five-agent diagnosis pipeline will diagnose root causes and recommend grounded fixes.
          </p>
        </div>

        {/* Input Mode Segmented Control */}
        <IOSSegmentedControl
          value={inputMode}
          onChange={(val) => setInputMode(val as any)}
          options={[
            { value: 'paste', label: 'Paste Trace / Text', icon: <Terminal className="w-3.5 h-3.5" /> },
            { value: 'upload', label: 'Upload Files', icon: <Upload className="w-3.5 h-3.5" /> },
          ]}
        />
      </div>

      {/* Quick 1-Click Preset Pills */}
      <div className="p-4 rounded-2xl bg-white/70 dark:bg-zinc-800/70 border border-black/5 dark:border-white/5 backdrop-blur-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-xs font-semibold text-slate-700 dark:text-zinc-300">
            <Sparkles className="w-4 h-4 text-blue-500" />
            <span>Preloaded Enterprise Test Cases:</span>
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {BUG_PRESETS.map((p) => (
              <button
                key={p.id}
                type="button"
                onClick={() => loadPreset(p)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 text-xs font-medium text-slate-800 dark:text-zinc-200 border border-black/5 dark:border-white/5 transition-all active:scale-95"
              >
                <span>{p.icon}</span>
                <span>{p.name}</span>
                <span className="text-[10px] text-blue-500 dark:text-blue-400 font-mono">({p.project})</span>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Form Container */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Card 1: Core Defect Details */}
        <div className="ios-card p-6 space-y-5">
          <div className="flex items-center justify-between border-b border-black/5 dark:border-white/5 pb-3">
            <h3 className="font-semibold text-slate-900 dark:text-white text-base flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-500" />
              <span>1. Defect Information & Context</span>
            </h3>

            {/* PII Redactor Toggle */}
            <div className="flex items-center gap-3">
              <IOSToggle
                checked={redactPII}
                onChange={setRedactPII}
                label="Sanitize PII"
                description="Mask IP addresses, tokens, and secrets"
              />
            </div>
          </div>

          {/* Title */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1.5">
              Defect Title / Summary *
            </label>
            <input
              type="text"
              required
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. NullPointerException in Workspace.save() during auto-build"
              className="w-full px-4 py-2.5 rounded-xl bg-slate-100/80 dark:bg-zinc-800/80 border border-black/5 dark:border-white/10 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1.5">
              Description & Reproduction Symptoms *
            </label>
            <textarea
              rows={3}
              required
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Describe the failure, trigger conditions, and observed system behavior..."
              className="w-full px-4 py-2.5 rounded-xl bg-slate-100/80 dark:bg-zinc-800/80 border border-black/5 dark:border-white/10 text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40"
            />
          </div>

          {/* Metadata Row: Language, Framework, Severity, Priority */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs font-semibold text-slate-600 dark:text-zinc-400 mb-1">
                Language
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-100/80 dark:bg-zinc-800/80 border border-black/5 dark:border-white/10 text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              >
                <option value="Java">Java</option>
                <option value="C++">C++</option>
                <option value="Python">Python</option>
                <option value="Scala">Scala</option>
                <option value="Rust">Rust</option>
                <option value="TypeScript">TypeScript / JS</option>
                <option value="Go">Go</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 dark:text-zinc-400 mb-1">
                Framework / Subsystem
              </label>
              <input
                type="text"
                value={framework}
                onChange={(e) => setFramework(e.target.value)}
                placeholder="e.g. Gecko IPC, Spark 3.4"
                className="w-full px-3 py-2 rounded-xl bg-slate-100/80 dark:bg-zinc-800/80 border border-black/5 dark:border-white/10 text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 dark:text-zinc-400 mb-1">
                Severity
              </label>
              <select
                value={severity}
                onChange={(e) => setSeverity(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-100/80 dark:bg-zinc-800/80 border border-black/5 dark:border-white/10 text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              >
                <option value="critical">Critical / Blocker</option>
                <option value="high">High / Major</option>
                <option value="medium">Medium / Normal</option>
                <option value="low">Low / Minor</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-600 dark:text-zinc-400 mb-1">
                Priority
              </label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full px-3 py-2 rounded-xl bg-slate-100/80 dark:bg-zinc-800/80 border border-black/5 dark:border-white/10 text-xs sm:text-sm text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              >
                <option value="p1">P1 - Highest</option>
                <option value="p2">P2 - High</option>
                <option value="p3">P3 - Medium</option>
                <option value="p4">P4 - Low</option>
              </select>
            </div>
          </div>
        </div>

        {/* Card 2: Stack Trace & Logs (Paste Mode) */}
        {inputMode === 'paste' && (
          <div className="ios-card p-6 space-y-5">
            <div className="flex items-center justify-between border-b border-black/5 dark:border-white/5 pb-3">
              <div className="flex items-center gap-2">
                <Terminal className="w-4 h-4 text-cyan-500" />
                <h3 className="font-semibold text-slate-900 dark:text-white text-base">
                  2. Stack Trace & Runtime Forensics
                </h3>
              </div>

              {detectedException && (
                <IOSBadge variant="purple" size="sm">
                  Detected: {detectedException}
                </IOSBadge>
              )}
            </div>

            <div>
              <div className="flex items-center justify-between mb-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-zinc-300">
                  Raw Stack Trace
                </label>
                <span className="text-[11px] text-zinc-400">
                  Address offsets and line numbers will be normalized for RAG retrieval
                </span>
              </div>
              <textarea
                rows={6}
                value={stackTrace}
                onChange={(e) => setStackTrace(e.target.value)}
                placeholder="Paste exception stack trace here (e.g. java.lang.NullPointerException at com.example... or #0 0x7fff... in C++)"
                className="w-full px-4 py-2.5 rounded-xl bg-[#0B0F19] border border-white/10 font-mono text-xs text-zinc-200 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-slate-700 dark:text-zinc-300 mb-1.5">
                Error Logs & Terminal Output (Optional)
              </label>
              <textarea
                rows={3}
                value={errorLogs}
                onChange={(e) => setErrorLogs(e.target.value)}
                placeholder="Paste relevant terminal logs, stdout/stderr timestamps, or error codes..."
                className="w-full px-4 py-2.5 rounded-xl bg-[#0B0F19] border border-white/10 font-mono text-xs text-zinc-200 focus:outline-none focus:ring-2 focus:ring-blue-500/40"
              />
            </div>
          </div>
        )}

        {/* Card 3: File Uploads */}
        {inputMode === 'upload' && (
          <div className="ios-card p-6 space-y-5">
            <div className="border-b border-black/5 dark:border-white/5 pb-3">
              <h3 className="font-semibold text-slate-900 dark:text-white text-base flex items-center gap-2">
                <Upload className="w-4 h-4 text-emerald-500" />
                <span>2. Upload Diagnostic Logs & Files</span>
              </h3>
              <p className="text-xs text-slate-500 dark:text-zinc-400 mt-0.5">
                Supported formats: .txt, .log, .json, .csv, .md, .xml, .yaml (Max 10MB per file)
              </p>
            </div>

            {/* Drag & Drop Area */}
            <div className="border-2 border-dashed border-slate-300 dark:border-zinc-700 rounded-2xl p-8 text-center hover:border-blue-500/50 transition-colors">
              <Upload className="w-8 h-8 text-blue-500 mx-auto mb-2" />
              <p className="text-sm font-semibold text-slate-800 dark:text-zinc-200">
                Drag and drop log files here, or{' '}
                <label className="text-blue-500 hover:underline cursor-pointer">
                  browse files
                  <input
                    type="file"
                    multiple
                    onChange={handleFileChange}
                    className="hidden"
                    accept=".txt,.log,.json,.csv,.md,.py,.java,.cpp,.xml,.yaml"
                  />
                </label>
              </p>
              <p className="text-xs text-zinc-400 mt-1">Zero-Execution Sandbox: Files are scanned as text only.</p>
            </div>

            {/* Selected Files List */}
            {selectedFiles.length > 0 && (
              <div className="space-y-2">
                <div className="text-xs font-semibold text-slate-700 dark:text-zinc-300">
                  Attached Files ({selectedFiles.length}):
                </div>
                {selectedFiles.map((f, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 rounded-xl bg-black/5 dark:bg-white/5 border border-black/5 dark:border-white/5 text-xs"
                  >
                    <div className="flex items-center gap-2">
                      <FileCode className="w-4 h-4 text-blue-500" />
                      <span className="font-mono text-slate-800 dark:text-zinc-200">{f.name}</span>
                      <span className="text-zinc-400 font-mono">({Math.round(f.size / 1024)} KB)</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeFile(idx)}
                      className="text-zinc-400 hover:text-red-500 p-1"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Submit Actions */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
          <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-zinc-400">
            <ShieldCheck className="w-4 h-4 text-emerald-500" />
            <span>5 Specialized Agents will analyze this submission against historical defect records currently loaded.</span>
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

      {/* Interactive 5-Agent Pipeline Live Modal / Overlay */}
      {isDiagnosing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-md animate-fade-in">
          <div className="w-full max-w-lg rounded-3xl bg-white dark:bg-[#1C1C1E] border border-black/10 dark:border-white/10 p-6 sm:p-8 shadow-2xl space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-black/5 dark:border-white/5 pb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-2xl bg-blue-500/20 text-blue-500 flex items-center justify-center">
                  <Sparkles className="w-5 h-5 animate-spin-slow" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-900 dark:text-white text-base">
                    TraceIQ Multi-Agent Swarm
                  </h3>
                  <p className="text-xs text-slate-500 dark:text-zinc-400">
                    Executing the backend diagnosis pipeline...
                  </p>
                </div>
              </div>
              <IOSBadge variant="blue" size="sm" dot>
                Live Orchestration
              </IOSBadge>
            </div>

            {/* Agent Steps Timeline */}
            <div className="space-y-3">
              {agentSteps.map((step, idx) => {
                const isCurrent = idx === activeAgentStep;
                const isDone = idx < activeAgentStep;
                return (
                  <div
                    key={idx}
                    className={`flex items-center justify-between p-3 rounded-2xl transition-all ${
                      isCurrent
                        ? 'bg-blue-500/10 dark:bg-blue-500/15 border border-blue-500/25'
                        : isDone
                        ? 'bg-emerald-500/5 border border-emerald-500/15 opacity-80'
                        : 'opacity-40'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold ${
                          isDone
                            ? 'bg-emerald-500 text-white'
                            : isCurrent
                            ? 'bg-blue-500 text-white animate-pulse'
                            : 'bg-zinc-700 text-zinc-400'
                        }`}
                      >
                        {isDone ? '✓' : idx + 1}
                      </div>
                      <div>
                        <div className="font-medium text-xs sm:text-sm text-slate-900 dark:text-white">
                          {step.title}
                        </div>
                        <div className="text-[10px] text-zinc-400 font-mono">
                          {step.agent}
                        </div>
                      </div>
                    </div>
                    <span className="text-[11px] font-mono text-zinc-400">
                      {isDone ? 'Done' : isCurrent ? 'Running...' : step.time}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Streaming Logs Terminal */}
            <div className="p-3 rounded-2xl bg-[#0B0F19] border border-white/10 font-mono text-[11px] text-zinc-300 max-h-28 overflow-y-auto space-y-1">
              {agentLogs.map((log, i) => (
                <div key={i} className="text-cyan-400">
                  {log}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
