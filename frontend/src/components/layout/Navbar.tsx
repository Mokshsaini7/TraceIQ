import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Sparkles,
  Sun,
  Moon,
  Search,
  Menu,
  X,
  LayoutDashboard,
  Bug,
  Database,
  Cpu,
  Settings,
  Terminal,
  ChevronRight,
  ArrowRight
} from 'lucide-react';
import { TraceIQLogo } from '../ui/TraceIQLogo';
import { IOSDynamicIsland } from '../ios/IOSDynamicIsland';
import { IOSBadge } from '../ios/IOSBadge';
import { api } from '../../services/api';
import { BUG_PRESETS } from '../../data/mockData';

interface NavbarProps {
  onOpenSearch?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenSearch }) => {
  const location = useLocation();
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() =>
    document.documentElement.classList.contains('dark')
  );

  useEffect(() => {
    // Check backend health
    api.getHealth()
      .then((data) => setIsBackendHealthy(data.status === 'healthy'))
      .catch(() => setIsBackendHealthy(false));
  }, []);

  // Close mobile drawer when route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  const toggleTheme = () => {
    const root = document.documentElement;
    if (isDarkMode) {
      root.classList.remove('dark');
      setIsDarkMode(false);
      localStorage.setItem('traceiq-theme', 'light');
    } else {
      root.classList.add('dark');
      setIsDarkMode(true);
      localStorage.setItem('traceiq-theme', 'dark');
    }
  };

  const navLinks = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Diagnose Studio', path: '/submit', icon: Sparkles, highlight: true },
    { name: 'Bug Reports', path: '/reports', icon: Bug },
    { name: 'Knowledge Base', path: '/knowledge-base', icon: Database },
    { name: 'Semantic Search', path: '/search', icon: Search },
    { name: 'Architecture', path: '/architecture', icon: Cpu },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <>
      <header className="sticky top-0 z-40 w-full border-b border-black/10 dark:border-white/10 bg-[#F5F4ED]/85 dark:bg-[#1f1e1d]/85 backdrop-blur-xl transition-colors">
        <div className="max-w-screen-2xl mx-auto px-3 sm:px-6 lg:px-8 h-14 flex items-center gap-2 sm:gap-4">
          {/* Brand */}
          <Link to="/" className="flex-shrink-0 min-w-0 rounded-lg cl-focus" aria-label="TraceIQ home">
            <TraceIQLogo size="md" showTagline={false} />
          </Link>

          {/* Status pill (2xl+): fixed slot, expands as an overlay so it never reflows the bar */}
          <div className="hidden 2xl:block relative w-[200px] h-9 flex-shrink-0 mr-4">
            <div className="absolute left-0 top-0 w-full">
              <IOSDynamicIsland isBackendHealthy={isBackendHealthy} />
            </div>
          </div>

          {/* Primary navigation (xl+) */}
          <nav className="hidden xl:flex items-center gap-0.5 flex-1 min-w-0 justify-center" aria-label="Primary">
            {navLinks.slice(0, 6).map((link) => {
              const isActive = location.pathname.startsWith(link.path);
              return (
                <Link
                  key={link.path}
                  to={link.path}
                  aria-current={isActive ? 'page' : undefined}
                  className="cl-nav-link"
                >
                  {link.name}
                </Link>
              );
            })}
          </nav>

          {/* Spacer below xl so actions stay right-aligned */}
          <div className="flex-1 xl:hidden" />

          {/* Actions */}
          <div className="flex items-center gap-1 sm:gap-1.5 flex-shrink-0">
            <button
              type="button"
              onClick={onOpenSearch}
              className="cl-icon-btn sm:cl-btn-secondary sm:w-auto sm:!px-3 text-[#5e5d59] dark:text-[#b8b6ac]"
              title="Search defect database (⌘K)"
              aria-label="Search defect database"
            >
              <Search className="w-4 h-4" />
              <span className="hidden 2xl:inline">Search</span>
              <kbd className="cl-kbd">⌘K</kbd>
            </button>

            <button
              type="button"
              onClick={toggleTheme}
              className="cl-icon-btn"
              aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
              title={isDarkMode ? 'Light mode' : 'Dark mode'}
            >
              {isDarkMode ? <Sun className="w-[18px] h-[18px]" /> : <Moon className="w-[18px] h-[18px]" />}
            </button>

            <Link to="/settings" className="cl-icon-btn hidden xl:inline-flex" aria-label="Settings" title="Settings">
              <Settings className="w-[18px] h-[18px]" />
            </Link>

            <Link to="/submit" className="cl-btn-primary hidden md:inline-flex ml-1">
              <Sparkles className="w-4 h-4" />
              <span>Diagnose</span>
            </Link>

            <button
              type="button"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="cl-icon-btn xl:hidden"
              aria-label={isMobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'}
              aria-expanded={isMobileMenuOpen}
            >
              {isMobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </header>

      {/* iOS Slide-Over Navigation Sheet (Mobile & Tablet) */}
      {isMobileMenuOpen && (
        <div
          className="fixed inset-0 z-50 xl:hidden bg-black/60 backdrop-blur-md animate-fade-in"
          onClick={() => setIsMobileMenuOpen(false)}
        >
          <div
            className="fixed inset-y-0 right-0 w-[300px] max-w-[88vw] bg-[#F5F4ED] dark:bg-[#262624] backdrop-blur-2xl border-l border-black/10 dark:border-white/10 p-5 flex flex-col justify-between shadow-2xl animate-spring-up overflow-y-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="space-y-6">
              {/* Drawer Header */}
              <div className="flex items-center justify-between border-b border-black/5 dark:border-white/10 pb-4">
                <TraceIQLogo size="sm" />
                <button
                  type="button"
                  onClick={() => setIsMobileMenuOpen(false)}
                  className="cl-icon-btn"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>

              {/* Navigation Links */}
              <div>
                <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-zinc-500 mb-2">
                  TraceIQ Platform Pages
                </p>
                <div className="space-y-1">
                  {navLinks.map((link) => {
                    const isActive =
                      link.path === '/'
                        ? location.pathname === '/'
                        : location.pathname.startsWith(link.path);
                    const Icon = link.icon;

                    return (
                      <Link
                        key={link.path}
                        to={link.path}
                        className={`flex items-center justify-between h-11 px-3 rounded-lg text-sm font-medium transition-colors ${
                          isActive
                            ? 'bg-black/[.06] dark:bg-white/10 text-[#141413] dark:text-white'
                            : 'text-[#3d3d3a] dark:text-[#d6d4ca] hover:bg-black/[.05] dark:hover:bg-white/[.07]'
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <Icon className="w-4 h-4" />
                          <span>{link.name}</span>
                        </div>
                        <ChevronRight className="w-4 h-4 opacity-70" />
                      </Link>
                    );
                  })}
                </div>
              </div>

              {/* Sample Enterprise Crashes */}
              <div className="pt-2 border-t border-black/5 dark:border-white/10">
                <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-zinc-500 mb-2">
                  Sample Bug Presets
                </p>
                <div className="space-y-1.5">
                  {BUG_PRESETS.map((p) => (
                    <Link
                      key={p.id}
                      to={`/submit?preset=${p.id}`}
                      className="p-2.5 rounded-lg border border-black/10 dark:border-white/10 hover:bg-black/[.04] dark:hover:bg-white/[.06] flex items-center justify-between text-xs transition-colors"
                    >
                      <div className="flex items-center gap-2">
                        <span>{p.icon}</span>
                        <span className="font-medium text-slate-800 dark:text-zinc-200">{p.name}</span>
                      </div>
                      <span className="text-[10px] text-[#C6613F] font-medium">Load</span>
                    </Link>
                  ))}
                </div>
              </div>
            </div>

            {/* Bottom Status Card in Drawer */}
            <div className="pt-4 border-t border-black/5 dark:border-white/10 text-xs">
              <div className="flex items-center justify-between text-slate-500 dark:text-zinc-400 mb-2">
                <span>Core Engine:</span>
                <span className="text-emerald-500 font-semibold font-mono">5 Agents Online</span>
              </div>
              <Link
                to="/submit"
                className="cl-btn-primary w-full h-10"
              >
                <Sparkles className="w-4 h-4" />
                <span>Launch Diagnose Studio</span>
              </Link>
            </div>
          </div>
        </div>
      )}
    </>
  );
};
