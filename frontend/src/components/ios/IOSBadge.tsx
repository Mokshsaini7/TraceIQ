import React from 'react';

export type IOSBadgeVariant =
  | 'blue'
  | 'green'
  | 'red'
  | 'orange'
  | 'purple'
  | 'teal'
  | 'gray';

interface IOSBadgeProps {
  children: React.ReactNode;
  variant?: IOSBadgeVariant;
  size?: 'sm' | 'md' | 'lg';
  dot?: boolean;
  className?: string;
  icon?: React.ReactNode;
}

export const IOSBadge: React.FC<IOSBadgeProps> = ({
  children,
  variant = 'blue',
  size = 'md',
  dot = false,
  className = '',
  icon,
}) => {
  const variantStyles: Record<IOSBadgeVariant, { bg: string; text: string; dot: string; border: string }> = {
    blue: {
      bg: 'bg-[#007AFF]/12 dark:bg-[#0A84FF]/18',
      text: 'text-[#007AFF] dark:text-[#64D2FF]',
      dot: 'bg-[#007AFF]',
      border: 'border-[#007AFF]/25',
    },
    green: {
      bg: 'bg-[#34C759]/12 dark:bg-[#30D158]/18',
      text: 'text-[#248A3D] dark:text-[#30D158]',
      dot: 'bg-[#34C759]',
      border: 'border-[#34C759]/25',
    },
    red: {
      bg: 'bg-[#FF3B30]/12 dark:bg-[#FF453A]/18',
      text: 'text-[#D70015] dark:text-[#FF453A]',
      dot: 'bg-[#FF3B30]',
      border: 'border-[#FF3B30]/25',
    },
    orange: {
      bg: 'bg-[#FF9500]/12 dark:bg-[#FF9F0A]/18',
      text: 'text-[#C93400] dark:text-[#FF9F0A]',
      dot: 'bg-[#FF9500]',
      border: 'border-[#FF9500]/25',
    },
    purple: {
      bg: 'bg-[#AF52DE]/12 dark:bg-[#BF5AF2]/18',
      text: 'text-[#8944AB] dark:text-[#BF5AF2]',
      dot: 'bg-[#AF52DE]',
      border: 'border-[#AF52DE]/25',
    },
    teal: {
      bg: 'bg-[#30B0C7]/12 dark:bg-[#40C8E0]/18',
      text: 'text-[#0071A4] dark:text-[#40C8E0]',
      dot: 'bg-[#30B0C7]',
      border: 'border-[#30B0C7]/25',
    },
    gray: {
      bg: 'bg-slate-200/60 dark:bg-zinc-800/80',
      text: 'text-slate-700 dark:text-zinc-300',
      dot: 'bg-slate-400 dark:bg-zinc-500',
      border: 'border-slate-300/40 dark:border-zinc-700/50',
    },
  };

  const sizeStyles = {
    sm: 'text-[11px] px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
    lg: 'text-sm px-3 py-1.5 gap-2',
  };

  const current = variantStyles[variant];

  return (
    <span
      className={`inline-flex items-center font-medium rounded-full border ${current.bg} ${current.text} ${current.border} ${sizeStyles[size]} ${className}`}
    >
      {dot && <span className={`w-1.5 h-1.5 rounded-full ${current.dot} animate-pulse`} />}
      {icon && <span className="w-3.5 h-3.5 flex items-center justify-center">{icon}</span>}
      <span>{children}</span>
    </span>
  );
};
