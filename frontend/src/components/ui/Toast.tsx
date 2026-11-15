import React, { useEffect } from 'react';
import { CheckCircle2, AlertCircle, X, Info } from 'lucide-react';

export type ToastType = 'success' | 'error' | 'info';

export interface ToastMessage {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
}

interface ToastProps {
  toast: ToastMessage;
  onDismiss?: (id: string) => void;
  onClose?: () => void;
}

export const ToastItem: React.FC<ToastProps> = ({ toast, onDismiss, onClose }) => {
  const handleClose = () => {
    if (onDismiss) onDismiss(toast.id);
    if (onClose) onClose();
  };

  useEffect(() => {
    const timer = setTimeout(() => {
      handleClose();
    }, 4500);
    return () => clearTimeout(timer);
  }, [toast.id]);

  const icons = {
    success: <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />,
    error: <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />,
    info: <Info className="w-5 h-5 text-blue-400 shrink-0" />,
  };

  return (
    <div className="flex items-start gap-3 bg-[#1C1C1E]/95 text-white p-4 rounded-2xl shadow-2xl border border-white/15 min-w-[300px] sm:min-w-[340px] max-w-md backdrop-blur-2xl animate-fade-in select-none">
      {icons[toast.type]}
      <div className="flex-1 text-xs">
        <h4 className="font-semibold text-white tracking-tight">{toast.title}</h4>
        {toast.message && (
          <p className="text-zinc-300 text-[11px] mt-0.5 leading-relaxed">{toast.message}</p>
        )}
      </div>
      <button
        type="button"
        onClick={handleClose}
        className="text-zinc-400 hover:text-white p-0.5 transition-colors"
      >
        <X className="w-4 h-4" />
      </button>
    </div>
  );
};
