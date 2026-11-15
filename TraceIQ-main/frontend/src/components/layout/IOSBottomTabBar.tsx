import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { LayoutGrid, Sparkles, FileText, Database, Layers } from 'lucide-react';

export const IOSBottomTabBar: React.FC = () => {
  const location = useLocation();

  const tabs = [
    { name: 'Overview', path: '/', icon: LayoutGrid, exact: true },
    { name: 'Diagnose', path: '/submit', icon: Sparkles, highlight: true },
    { name: 'Reports', path: '/reports', icon: FileText },
    { name: 'KB Search', path: '/knowledge-base', icon: Database },
    { name: 'Arch', path: '/architecture', icon: Layers },
  ];

  return (
    <nav className="fixed bottom-0 inset-x-0 z-40 md:hidden bg-[#F2F2F7]/90 dark:bg-[#161618]/90 backdrop-blur-2xl border-t border-black/10 dark:border-white/10 pb-safe">
      <div className="flex items-center justify-around h-16 px-2 max-w-md mx-auto">
        {tabs.map((tab) => {
          const isActive = tab.exact
            ? location.pathname === tab.path
            : location.pathname.startsWith(tab.path);
          const Icon = tab.icon;

          return (
            <NavLink
              key={tab.path}
              to={tab.path}
              className={`flex flex-col items-center justify-center flex-1 h-full py-1 text-center transition-all ${
                isActive
                  ? 'text-blue-600 dark:text-blue-400 font-semibold'
                  : 'text-slate-500 dark:text-zinc-400 hover:text-slate-800 dark:hover:text-zinc-200'
              }`}
            >
              <div
                className={`relative flex items-center justify-center ${
                  tab.highlight
                    ? 'w-10 h-10 rounded-2xl bg-gradient-to-tr from-blue-600 to-cyan-500 text-white shadow-md shadow-blue-500/20 -mt-3'
                    : 'w-6 h-6'
                }`}
              >
                <Icon className={tab.highlight ? 'w-5 h-5' : 'w-5 h-5'} />
                {isActive && !tab.highlight && (
                  <span className="absolute -bottom-1 w-1 h-1 rounded-full bg-blue-500" />
                )}
              </div>
              <span className={`text-[10px] mt-1 tracking-tight ${tab.highlight ? 'font-bold' : ''}`}>
                {tab.name}
              </span>
            </NavLink>
          );
        })}
      </div>
    </nav>
  );
};
