import React from 'react';

export interface SegmentOption<T extends string = string> {
  value: T;
  label: string;
  icon?: React.ReactNode;
  badge?: string | number;
}

interface IOSSegmentedControlProps<T extends string = string> {
  options: SegmentOption<T>[];
  value: T;
  onChange: (val: T) => void;
  className?: string;
  size?: 'sm' | 'md';
}

export function IOSSegmentedControl<T extends string = string>({
  options,
  value,
  onChange,
  className = '',
  size = 'md',
}: IOSSegmentedControlProps<T>) {
  const sizeStyles = {
    sm: 'p-0.5 text-xs',
    md: 'p-1 text-xs sm:text-sm',
  };

  const itemPadding = {
    sm: 'px-2.5 py-1',
    md: 'px-3.5 py-1.5',
  };

  return (
    <div
      role="tablist"
      className={`inline-flex max-w-full overflow-x-auto no-scrollbar items-center rounded-xl bg-slate-200/60 dark:bg-zinc-800/80 p-1 border border-black/5 dark:border-white/5 select-none transition-all ${className}`}
    >
      {options.map((opt) => {
        const isActive = opt.value === value;
        return (
          <button
            key={opt.value}
            role="tab"
            aria-selected={isActive}
            type="button"
            onClick={() => onChange(opt.value)}
            className={`flex flex-shrink-0 whitespace-nowrap items-center gap-1.5 rounded-lg ${itemPadding[size]} font-medium transition-all duration-200 ${
              isActive
                ? 'bg-white dark:bg-zinc-700/90 text-slate-900 dark:text-white shadow-[0_2px_8px_rgba(0,0,0,0.08)] font-semibold'
                : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-200'
            }`}
          >
            {opt.icon && <span className="w-3.5 h-3.5 flex items-center justify-center">{opt.icon}</span>}
            <span>{opt.label}</span>
            {opt.badge !== undefined && (
              <span
                className={`ml-1 px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
                  isActive
                    ? 'bg-blue-500/15 text-blue-600 dark:text-blue-400'
                    : 'bg-black/10 dark:bg-white/10 text-slate-500 dark:text-zinc-400'
                }`}
              >
                {opt.badge}
              </span>
            )}
          </button>
        );
      })}
    </div>
  );
}
