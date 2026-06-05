import * as Dialog from '@radix-ui/react-dialog';
import * as VisuallyHidden from '@radix-ui/react-visually-hidden';
import { AnimatePresence, motion } from 'framer-motion';
import { Bot, CornerDownLeft, Loader2, Sparkles, X } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { useUIStore } from '@store/uiStore';
import { useAuthStore } from '@store/authStore';

/* ------------------------------------------------------------------ */
/*  Types                                                              */
/* ------------------------------------------------------------------ */
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  pending?: boolean;
}

let msgId = 0;
function nextId() { return String(++msgId); }

/* ------------------------------------------------------------------ */
/*  Streaming via EventSource                                          */
/* ------------------------------------------------------------------ */
function streamAI(prompt: string, onChunk: (text: string) => void, onDone: () => void, onError: () => void) {
  const url = `/api/ai/chat/stream?prompt=${encodeURIComponent(prompt)}`;
  const es = new EventSource(url);

  es.addEventListener('message', (e) => {
    try {
      const data = JSON.parse(e.data) as { text: string };
      if (data.text) onChunk(data.text);
    } catch { /* ignore parse errors */ }
  });

  es.addEventListener('done', () => {
    es.close();
    onDone();
  });

  es.onerror = () => {
    es.close();
    onError();
  };

  return () => es.close();
}

/* ------------------------------------------------------------------ */
/*  Suggested prompts                                                  */
/* ------------------------------------------------------------------ */
const SUGGESTIONS = [
  'What is the leave policy?',
  'How do I apply for leave?',
  'Show me this month\'s attendance summary',
  'What are my payroll details?',
  'How do I update my profile?',
];

/* ------------------------------------------------------------------ */
/*  Message bubble                                                     */
/* ------------------------------------------------------------------ */
function MessageBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      {/* Avatar */}
      <div
        className={`flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold ${
          isUser
            ? 'bg-brand-500 text-white'
            : 'bg-gradient-to-br from-violet-500 to-brand-600 text-white'
        }`}
      >
        {isUser ? 'U' : <Sparkles className="h-3.5 w-3.5" />}
      </div>

      {/* Bubble */}
      <div
        className={`max-w-[80%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed ${
          isUser
            ? 'rounded-tr-sm bg-brand-500 text-white'
            : 'rounded-tl-sm bg-surface-100 text-surface-800 dark:bg-white/10 dark:text-white/90'
        }`}
      >
        {msg.pending ? (
          <span className="flex items-center gap-2 text-surface-500 dark:text-white/50">
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
            Thinking…
          </span>
        ) : (
          msg.content
        )}
      </div>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main AI Assistant panel                                            */
/* ------------------------------------------------------------------ */
export function AIAssistant() {
  const open = useUIStore((state) => state.aiAssistantOpen);
  const setOpen = useUIStore((state) => state.setAiAssistantOpen);
  const user = useAuthStore((state) => state.user);

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const cleanupRef = useRef<(() => void) | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Scroll to bottom on new message
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when opened
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 150);
    }
  }, [open]);

  // Cleanup on unmount
  useEffect(() => () => { cleanupRef.current?.(); }, []);

  function addMessage(role: 'user' | 'assistant', content: string, pending = false): string {
    const id = nextId();
    setMessages((prev) => [...prev, { id, role, content, pending }]);
    return id;
  }

  function updateMessage(id: string, updates: Partial<Message>) {
    setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, ...updates } : m)));
  }

  function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || streaming) return;

    setInput('');
    addMessage('user', trimmed);
    const replyId = addMessage('assistant', '', true);
    setStreaming(true);

    let accumulated = '';

    cleanupRef.current = streamAI(
      trimmed,
      (chunk) => {
        accumulated += chunk;
        updateMessage(replyId, { content: accumulated, pending: false });
      },
      () => {
        setStreaming(false);
        if (!accumulated) {
          updateMessage(replyId, { content: 'Sorry, I couldn\'t get a response. Please try again.', pending: false });
        }
      },
      () => {
        setStreaming(false);
        // If AI service not running, show a helpful fallback
        if (!accumulated) {
          updateMessage(replyId, {
            content: 'AI service is not available right now. Start the AI service with: `uvicorn main:app --port 8001` in the ai-service directory.',
            pending: false,
          });
        }
      },
    );
  }

  function onKeyDown(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  }

  function handleClose() {
    cleanupRef.current?.();
    setOpen(false);
  }

  return (
    <Dialog.Root open={open} onOpenChange={(v) => !v && handleClose()}>
      <AnimatePresence>
        {open && (
          <Dialog.Portal forceMount>
            <Dialog.Overlay asChild>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 z-50 bg-black/30 backdrop-blur-sm"
              />
            </Dialog.Overlay>

            <Dialog.Content asChild>
              <motion.div
                initial={{ opacity: 0, x: 40, scale: 0.97 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, x: 40, scale: 0.97 }}
                transition={{ duration: 0.2, ease: 'easeOut' }}
                className="fixed bottom-4 right-4 top-4 z-50 flex w-[380px] max-w-[calc(100vw-2rem)] flex-col overflow-hidden rounded-3xl border border-surface-200/70 bg-surface-0 shadow-2xl dark:border-white/10 dark:bg-surface-950"
              >
                <VisuallyHidden.Root>
                  <Dialog.Title>AI Assistant</Dialog.Title>
                </VisuallyHidden.Root>

                {/* Header */}
                <div className="flex items-center gap-3 border-b border-surface-200/70 px-4 py-3.5 dark:border-white/10">
                  <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-brand-600 shadow-sm">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-surface-900 dark:text-white">HRMS AI Assistant</p>
                    <p className="text-xs text-surface-500 dark:text-white/40">Ask me anything about HR policies</p>
                  </div>
                  <Dialog.Close asChild>
                    <button
                      type="button"
                      onClick={handleClose}
                      className="flex h-7 w-7 items-center justify-center rounded-lg text-surface-400 transition-colors hover:bg-surface-100 hover:text-surface-600 dark:text-white/40 dark:hover:bg-white/10 dark:hover:text-white/70"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </Dialog.Close>
                </div>

                {/* Messages */}
                <div className="flex-1 space-y-4 overflow-y-auto px-4 py-4">
                  {messages.length === 0 ? (
                    <div className="space-y-4">
                      <div className="flex flex-col items-center py-6 text-center">
                        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-100 to-brand-100 dark:from-violet-900/30 dark:to-brand-900/30">
                          <Sparkles className="h-5 w-5 text-brand-600 dark:text-brand-400" />
                        </div>
                        <p className="mt-3 text-sm font-medium text-surface-700 dark:text-white/70">
                          Hi {user.name.split(' ')[0]}, how can I help?
                        </p>
                        <p className="mt-1 text-xs text-surface-400 dark:text-white/30">
                          Ask about policies, attendance, payroll, or anything HR.
                        </p>
                      </div>

                      {/* Suggestions */}
                      <div className="space-y-2">
                        <p className="text-xs font-medium text-surface-400 dark:text-white/30">Suggested questions</p>
                        {SUGGESTIONS.map((s) => (
                          <button
                            key={s}
                            type="button"
                            onClick={() => send(s)}
                            className="w-full rounded-xl border border-surface-200/70 bg-surface-50 px-3 py-2.5 text-left text-xs text-surface-700 transition-colors hover:border-brand-300 hover:bg-brand-50/50 hover:text-brand-700 dark:border-white/10 dark:bg-white/5 dark:text-white/60 dark:hover:border-brand-500 dark:hover:text-brand-400"
                          >
                            {s}
                          </button>
                        ))}
                      </div>
                    </div>
                  ) : (
                    messages.map((msg) => <MessageBubble key={msg.id} msg={msg} />)
                  )}
                  <div ref={bottomRef} />
                </div>

                {/* Input */}
                <div className="border-t border-surface-200/70 p-4 dark:border-white/10">
                  <div className="flex items-end gap-2 rounded-2xl border border-surface-300/70 bg-surface-50 px-3 py-2 focus-within:border-brand-400 dark:border-white/10 dark:bg-white/5">
                    <textarea
                      ref={inputRef}
                      rows={1}
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={onKeyDown}
                      placeholder="Ask a question…"
                      disabled={streaming}
                      className="flex-1 resize-none bg-transparent text-sm text-surface-900 placeholder-surface-400 focus:outline-none dark:text-white dark:placeholder-white/30"
                      style={{ maxHeight: '120px' }}
                    />
                    <button
                      type="button"
                      onClick={() => send(input)}
                      disabled={!input.trim() || streaming}
                      className="mb-0.5 flex h-7 w-7 items-center justify-center rounded-lg bg-brand-500 text-white transition-colors hover:bg-brand-600 disabled:opacity-40"
                    >
                      {streaming ? (
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                      ) : (
                        <CornerDownLeft className="h-3.5 w-3.5" />
                      )}
                    </button>
                  </div>
                  <p className="mt-1.5 text-center text-2xs text-surface-400 dark:text-white/25">
                    Press Enter to send · Shift+Enter for newline
                  </p>
                </div>
              </motion.div>
            </Dialog.Content>
          </Dialog.Portal>
        )}
      </AnimatePresence>
    </Dialog.Root>
  );
}
