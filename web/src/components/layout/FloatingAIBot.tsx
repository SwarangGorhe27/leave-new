import { Bot } from 'lucide-react';
import { useUIStore } from '@store/uiStore';
import { cn } from '@utils/utils';

export function FloatingAIBot() {
  const setAiAssistantOpen = useUIStore((state) => state.setAiAssistantOpen);
  const aiAssistantOpen = useUIStore((state) => state.aiAssistantOpen);

  if (aiAssistantOpen) return null;

  return (
    <button
      type="button"
      onClick={() => setAiAssistantOpen(true)}
      className={cn(
        "fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-brand-600 text-white shadow-xl transition-all duration-300 hover:scale-110 hover:bg-brand-500 hover:shadow-brand-500/25 active:scale-95 dark:bg-brand-500 dark:hover:bg-brand-400",
        "group"
      )}
      aria-label="Open AI Assistant"
    >
      {/* Pulse effect */}
      <div className="absolute inset-0 rounded-full bg-brand-400 opacity-20 group-hover:animate-ping" />
      <Bot className="relative z-10 h-6 w-6 transition-transform group-hover:rotate-12" />
    </button>
  );
}
