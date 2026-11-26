import React from 'react';

type BadgeVariant = 'default' | 'cyan' | 'navy' | 'critical' | 'high' | 'medium' | 'low' | 'success' | 'warning' | 'purple';

interface BadgeProps {
  children: React.ReactNode;
  variant?: BadgeVariant;
  className?: string;
  size?: 'sm' | 'md';
}

const variantStyles: Record<BadgeVariant, string> = {
  default: 'bg-slate-100 text-slate-700 border-slate-200',
  cyan: 'bg-cyan-light text-cyan-hover border-cyan/30 font-semibold',
  navy: 'bg-navy-900 text-cyan-light border-navy-light',
  critical: 'bg-red-50 text-red-700 border-red-200 font-medium',
  high: 'bg-orange-50 text-orange-700 border-orange-200 font-medium',
  medium: 'bg-amber-50 text-amber-700 border-amber-200 font-medium',
  low: 'bg-blue-50 text-blue-700 border-blue-200 font-medium',
  success: 'bg-emerald-50 text-emerald-700 border-emerald-200 font-medium',
  warning: 'bg-yellow-50 text-yellow-800 border-yellow-200 font-medium',
  purple: 'bg-purple-50 text-purple-700 border-purple-200 font-medium',
};

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  className = '',
  size = 'md',
}) => {
  const sizeStyle = size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-2.5 py-1 text-xs';
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${sizeStyle} ${variantStyles[variant]} ${className}`}
    >
      {children}
    </span>
  );
};
