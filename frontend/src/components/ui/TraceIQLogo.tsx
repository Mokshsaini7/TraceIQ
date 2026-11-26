import React from 'react';

interface TraceIQLogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showWordmark?: boolean;
  className?: string;
  badgeText?: string;
  showTagline?: boolean;
}

export const TraceIQLogo: React.FC<TraceIQLogoProps> = ({
  size = 'md',
  showWordmark = true,
  className = '',
  badgeText = 'v1.0 iOS',
  showTagline = true
}) => {
  const iconSizeClasses = {
    sm: 'w-7 h-7',
    md: 'w-9 h-9',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  const textSizeClasses = {
    sm: 'text-base',
    md: 'text-xl',
    lg: 'text-2xl',
    xl: 'text-3xl'
  };

  return (
    <div className={`inline-flex items-center gap-2 sm:gap-3 select-none ${className}`}>
      {/* iOS Squircle Icon Container */}
      <div
        className={`${iconSizeClasses[size]} relative rounded-[22%] bg-gradient-to-br from-[#0A1124] via-[#0F1B38] to-[#040814] p-0.5 shadow-lg shadow-blue-500/10 ring-1 ring-white/20 overflow-hidden flex items-center justify-center transition-all duration-300 group-hover:scale-105 group-hover:ring-blue-400/40`}
      >
        {/* Subtle Specular Top Arc */}
        <div className="absolute inset-x-0 top-0 h-1/2 bg-gradient-to-b from-white/25 via-white/5 to-transparent pointer-events-none" />

        {/* Scalable Vector Glyph */}
        <svg
          viewBox="0 0 100 100"
          className="w-full h-full p-1.5"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <defs>
            <linearGradient id="traceGradComponent" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#007AFF" />
              <stop offset="45%" stop-color="#00F0FF" />
              <stop offset="100%" stop-color="#5856D6" />
            </linearGradient>
            <filter id="glowComponent" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          </defs>

          {/* Radar Circles */}
          <circle cx="50" cy="50" r="32" stroke="rgba(0, 122, 255, 0.2)" strokeWidth="1" strokeDasharray="2 3" />
          <circle cx="50" cy="50" r="22" stroke="rgba(0, 240, 255, 0.15)" strokeWidth="1" />

          {/* T-Trace Glyph */}
          <g filter="url(#glowComponent)">
            <path
              d="M 22 28 C 22 25 24 23 27 23 L 73 23 C 76 23 78 25 78 28 C 78 31 76 33 73 33 L 27 33 C 24 33 22 31 22 28 Z"
              fill="url(#traceGradComponent)"
            />
            <path
              d="M 45 32 L 55 32 L 55 72 C 55 75 53 77 50 77 C 47 77 45 75 45 72 Z"
              fill="url(#traceGradComponent)"
            />
            <line x1="30" y1="48" x2="45" y2="48" stroke="#00F0FF" strokeWidth="2.5" strokeLinecap="round" />
            <line x1="55" y1="48" x2="70" y2="48" stroke="#5856D6" strokeWidth="2.5" strokeLinecap="round" />
            <line x1="35" y1="62" x2="45" y2="62" stroke="#007AFF" strokeWidth="2" strokeLinecap="round" />
            <line x1="55" y1="62" x2="65" y2="62" stroke="#00F0FF" strokeWidth="2" strokeLinecap="round" />
          </g>

          {/* Radar Nodes */}
          <circle cx="50" cy="48" r="3" fill="#FFFFFF" />
          <circle cx="50" cy="48" r="1.5" fill="#007AFF" />
          <circle cx="70" cy="48" r="2" fill="#00F0FF" />
          <circle cx="30" cy="48" r="2" fill="#5856D6" />
          <circle cx="50" cy="74" r="2" fill="#00F0FF" />
        </svg>
      </div>

      {/* Wordmark */}
      {showWordmark && (
        <div className="flex flex-col min-w-0">
          <div className="flex items-center gap-1.5 leading-none">
            <span className={`font-semibold tracking-tight text-slate-900 dark:text-white ${textSizeClasses[size]}`}>
              Trace<span className="font-bold bg-gradient-to-r from-blue-500 via-cyan-400 to-indigo-500 bg-clip-text text-transparent">IQ</span>
            </span>
            {badgeText && (
              <span className="hidden sm:inline text-[10px] uppercase font-semibold tracking-wider px-1.5 py-0.5 rounded-full bg-blue-500/10 text-blue-600 dark:text-blue-400 border border-blue-500/20">
                {badgeText}
              </span>
            )}
          </div>
          {showTagline && (
            <span className="text-[11px] font-medium tracking-tight text-slate-500 dark:text-slate-400 mt-0.5">
              Intelligent Defect Diagnosis & Remediation
            </span>
          )}
        </div>
      )}
    </div>
  );
};
