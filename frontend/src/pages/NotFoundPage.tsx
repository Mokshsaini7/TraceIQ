import React from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle, ArrowLeft, Home, Sparkles, Database, Layers } from 'lucide-react';
import { IOSBadge } from '../components/ios/IOSBadge';

export const NotFoundPage: React.FC = () => {
  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center p-6 space-y-5 max-w-lg mx-auto">
      <div className="w-16 h-16 rounded-3xl bg-blue-500/15 text-blue-500 flex items-center justify-center shadow-lg">
        <AlertCircle className="w-8 h-8" />
      </div>
      <div>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-slate-900 dark:text-white font-mono">404</h1>
        <h2 className="text-lg font-bold text-slate-800 dark:text-zinc-200 mt-1">Page Not Found</h2>
        <p className="text-xs sm:text-sm text-slate-500 dark:text-zinc-400 mt-2 leading-relaxed">
          The requested route was not found on the TraceIQ defect platform. Choose an option below to return to the active platform features.
        </p>
      </div>

      <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
        <Link
          to="/"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/15 text-xs font-semibold text-slate-800 dark:text-zinc-200 transition-all"
        >
          <Home className="w-4 h-4" />
          <span>Overview Home</span>
        </Link>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-[#007AFF] text-white text-xs font-semibold shadow-md transition-all"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Dashboard</span>
        </Link>
        <Link
          to="/submit"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-purple-500/10 hover:bg-purple-500/20 text-purple-600 dark:text-purple-400 text-xs font-semibold transition-all"
        >
          <Sparkles className="w-4 h-4" />
          <span>Diagnose Bug</span>
        </Link>
      </div>
    </div>
  );
};
