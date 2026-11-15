import React, { useState, useEffect } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Navbar } from './Navbar';
import { Sidebar } from './Sidebar';
import { Footer } from './Footer';
import { IOSBottomTabBar } from './IOSBottomTabBar';
import { Search, X, Sparkles, Database, FileText, Cpu, ArrowRight } from 'lucide-react';
import { BUG_PRESETS } from '../../data/mockData';

export const AppLayout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const isLandingPage = location.pathname === '/';

  // Global keyboard shortcut ⌘K or Ctrl+K for search
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsSearchOpen((prev) => !prev);
      }
      if (e.key === 'Escape') {
        setIsSearchOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const handleSelectQuickResult = (path: string) => {
    setIsSearchOpen(false);
    navigate(path);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F2F2F7] dark:bg-[#000000] text-slate-900 dark:text-zinc-100 transition-colors">
      <Navbar onOpenSearch={() => setIsSearchOpen(true)} />

      {isLandingPage ? (
        /* Full-width container for Apple Keynote-style Landing Page */
        <main className="flex-1 w-full pb-20 md:pb-8">
          <Outlet />
        </main>
      ) : (
        /* App workspace container with sidebar on desktop */
        <div className="flex-1 max-w-7xl w-full mx-auto flex">
          {/* Desktop Sidebar (hidden on mobile, shown on lg+) */}
          <div className="hidden lg:block">
            <Sidebar />
          </div>

          {/* Main Content Area */}
          <main className="flex-1 p-4 sm:p-6 lg:p-8 min-w-0 pb-24 md:pb-8">
            <Outlet />
          </main>
        </div>
      )}

      <Footer />

      {/* Floating Cupertino Bottom Tab Bar for Mobile */}
      <IOSBottomTabBar />

      {/* Quick Search Modal (⌘K) */}
      {isSearchOpen && (
        <div
          className="fixed inset-0 z-50 flex items-start justify-center p-4 pt-20 bg-black/60 backdrop-blur-md animate-fade-in"
          onClick={() => setIsSearchOpen(false)}
        >
          <div
            className="w-full max-w-xl rounded-2xl bg-white dark:bg-[#1C1C1E] border border-black/10 dark:border-white/10 shadow-2xl p-4 space-y-4"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Search Input */}
            <div className="relative flex items-center border-b border-black/5 dark:border-white/10 pb-3">
              <Search className="w-5 h-5 text-zinc-400 absolute left-2" />
              <input
                type="text"
                autoFocus
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search defects, stack traces, or run agent diagnosis (⌘K)..."
                className="w-full pl-10 pr-10 py-2 bg-transparent text-sm font-medium text-slate-900 dark:text-white placeholder-zinc-400 focus:outline-none"
              />
              <button
                type="button"
                onClick={() => setIsSearchOpen(false)}
                className="p-1 rounded-lg text-zinc-400 hover:text-white"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Quick Actions & Presets */}
            <div className="space-y-2 text-xs">
              <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-2">
                Quick Navigation & Presets
              </div>

              <div
                onClick={() => handleSelectQuickResult('/submit')}
                className="p-2.5 rounded-xl bg-black/5 dark:bg-white/5 hover:bg-blue-500/10 cursor-pointer flex items-center justify-between transition-colors"
              >
                <div className="flex items-center gap-2.5 text-slate-800 dark:text-zinc-200">
                  <Sparkles className="w-4 h-4 text-blue-500" />
                  <span className="font-semibold">Launch Diagnose Studio</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-zinc-400" />
              </div>

              <div
                onClick={() => handleSelectQuickResult('/reports')}
                className="p-2.5 rounded-xl bg-black/5 dark:bg-white/5 hover:bg-blue-500/10 cursor-pointer flex items-center justify-between transition-colors"
              >
                <div className="flex items-center gap-2.5 text-slate-800 dark:text-zinc-200">
                  <FileText className="w-4 h-4 text-emerald-500" />
                  <span className="font-semibold">Bug Reports & Diagnoses</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-zinc-400" />
              </div>

              <div
                onClick={() => handleSelectQuickResult('/search')}
                className="p-2.5 rounded-xl bg-black/5 dark:bg-white/5 hover:bg-blue-500/10 cursor-pointer flex items-center justify-between transition-colors"
              >
                <div className="flex items-center gap-2.5 text-slate-800 dark:text-zinc-200">
                  <Database className="w-4 h-4 text-cyan-500" />
                  <span className="font-semibold">Semantic & BM25 Defect Search</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-zinc-400" />
              </div>

              <div
                onClick={() => handleSelectQuickResult('/architecture')}
                className="p-2.5 rounded-xl bg-black/5 dark:bg-white/5 hover:bg-blue-500/10 cursor-pointer flex items-center justify-between transition-colors"
              >
                <div className="flex items-center gap-2.5 text-slate-800 dark:text-zinc-200">
                  <Cpu className="w-4 h-4 text-purple-500" />
                  <span className="font-semibold">Five-Agent Python Architecture</span>
                </div>
                <ArrowRight className="w-3.5 h-3.5 text-zinc-400" />
              </div>

              <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-2 pt-2">
                Sample Test Cases
              </div>
              {BUG_PRESETS.map((p) => (
                <div
                  key={p.id}
                  onClick={() => handleSelectQuickResult(`/submit?preset=${p.id}`)}
                  className="p-2.5 rounded-xl bg-black/5 dark:bg-white/5 hover:bg-black/10 dark:hover:bg-white/10 cursor-pointer flex items-center justify-between transition-colors"
                >
                  <div className="flex items-center gap-2 text-slate-800 dark:text-zinc-200">
                    <span>{p.icon}</span>
                    <span className="font-medium">{p.name}</span>
                  </div>
                  <span className="text-[10px] text-blue-500 font-mono font-semibold">Load Preset</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
