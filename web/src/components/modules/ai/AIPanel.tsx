import { useEffect, useRef, useState } from 'react';
import { CornerDownLeft, Loader2, RotateCcw, Sparkles } from 'lucide-react';
import { cn } from '@utils/utils';
import { useAuthStore } from '@store/authStore';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  pending?: boolean;
}

let _id = 0;
function nextId() { return String(++_id); }

function streamAI(prompt: string, onChunk: (text: string) => void, onDone: () => void, onError: () => void) {
  const url = `/api/ai/chat/stream?prompt=${encodeURIComponent(prompt)}`;
  const es = new EventSource(url);
  es.addEventListener('message', (e) => {
    try {
      const data = JSON.parse(e.data) as { text: string };
      if (data.text) onChunk(data.text);
    } catch { /* ignore */ }
  });
  es.addEventListener('done', () => { es.close(); onDone(); });
  es.onerror = () => { es.close(); onError(); };
  return () => es.close();
}

const SUGGESTIONS = [
  'Summarize today\'s attendance',
  'Who is on leave this week?',
  'Generate this month\'s payroll report',
  'Show pending leave approvals',
  'What is the leave encashment policy?',
  'List employees joining this month',
];

function MessageBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === 'user';
  return (
    <div className={cn('flex gap-3', isUser ? 'flex-row-reverse' : 'flex-row')}>
      <div className={cn(
        'flex h-7 w-7 shrink-0 items-center justify-center rounded-full text-xs font-semibold',
        isUser ? 'bg-brand-500 text-white' : 'bg-gradient-to-br from-violet-500 to-brand-600 text-white',
      )}>
        {isUser ? 'U' : <Sparkles className="h-3.5 w-3.5" />}
      </div>
      <div className={cn(
        'max-w-[80%] rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed',
        isUser
          ? 'rounded-tr-sm bg-brand-500 text-white'
          : 'rounded-tl-sm bg-surface-100 text-surface-800 dark:bg-white/10 dark:text-white/90',
      )}>
        {msg.pending ? (
          <span className="flex items-center gap-2 text-surface-500 dark:text-white/50">
            <Loader2 className="h-3.5 w-3.5 animate-spin" /> Thinking…
          </span>
        ) : msg.content}
      </div>
    </div>
  );
}

export function AIPanel() {
  const user = useAuthStore((s) => s.user);
  const firstName = user?.name?.split(' ')[0] ?? 'there';
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const cleanupRef = useRef<(() => void) | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  function send(text?: string) {
    const prompt = (text ?? input).trim();
    if (!prompt || streaming) return;
    setInput('');

    const userMsg: Message = { id: nextId(), role: 'user', content: prompt };
    const asstMsg: Message = { id: nextId(), role: 'assistant', content: '', pending: true };
    setMessages((prev) => [...prev, userMsg, asstMsg]);
    setStreaming(true);

    let accumulated = '';
    cleanupRef.current = streamAI(
      prompt,
      (chunk) => {
        accumulated += chunk;
        setMessages((prev) =>
          prev.map((m) => m.id === asstMsg.id ? { ...m, content: accumulated, pending: false } : m),
        );
      },
      () => {
        setStreaming(false);
        setMessages((prev) =>
          prev.map((m) => m.id === asstMsg.id ? { ...m, pending: false } : m),
        );
      },
      () => {
        setStreaming(false);
        setMessages((prev) =>
          prev.map((m) => m.id === asstMsg.id
            ? { ...m, content: 'Something went wrong. Please try again.', pending: false } : m),
        );
      },
    );
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send(); }
  }

  function clearChat() {
    cleanupRef.current?.();
    setMessages([]);
    setStreaming(false);
    inputRef.current?.focus();
  }

  return (
    <div className="flex h-[calc(100vh-220px)] min-h-[480px] flex-col rounded-2xl border border-surface-200/70 bg-surface-0 shadow-xs dark:border-white/10 dark:bg-surface-900">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-surface-100 px-4 py-3 dark:border-white/5">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-brand-600 text-white">
            <Sparkles className="h-4 w-4" />
          </div>
          <div>
            <p className="text-sm font-semibold text-surface-900 dark:text-white">HRMS AI Assistant</p>
            <p className="text-xs text-surface-400 dark:text-white/30">Powered by your HR data</p>
          </div>
        </div>
        {messages.length > 0 && (
          <button
            type="button"
            onClick={clearChat}
            className="flex items-center gap-1.5 rounded-lg border border-surface-200 px-2.5 py-1.5 text-xs font-medium text-surface-600 hover:bg-surface-50 dark:border-white/10 dark:text-white/50 dark:hover:bg-white/5"
          >
            <RotateCcw className="h-3 w-3" /> Clear
          </button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center gap-6 pt-8">
            <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-violet-500/20 to-brand-600/20">
              <Sparkles className="h-8 w-8 text-violet-500" />
            </div>
            <div className="text-center">
              <p className="text-base font-semibold text-surface-900 dark:text-white">
                Hi {firstName}! How can I help?
              </p>
              <p className="mt-1 text-sm text-surface-500 dark:text-white/40">
                Ask me anything about HR, attendance, payroll, or policies.
              </p>
            </div>
            <div className="grid w-full max-w-lg grid-cols-1 gap-2 sm:grid-cols-2">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  type="button"
                  onClick={() => send(s)}
                  className="rounded-xl border border-surface-200 bg-surface-50 px-3 py-2.5 text-left text-xs text-surface-700 transition-colors hover:border-brand-300 hover:bg-brand-50 hover:text-brand-700 dark:border-white/10 dark:bg-white/5 dark:text-white/60 dark:hover:border-brand-500 dark:hover:bg-brand-900/20 dark:hover:text-brand-400"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {messages.map((msg) => <MessageBubble key={msg.id} msg={msg} />)}
            <div ref={bottomRef} />
          </div>
        )}
      </div>

      {/* Input */}
      <div className="border-t border-surface-100 p-3 dark:border-white/5">
        <div className="flex items-end gap-2 rounded-2xl border border-surface-200 bg-surface-50 px-3 py-2 focus-within:border-brand-400 dark:border-white/10 dark:bg-white/5">
          <textarea
            ref={inputRef}
            rows={1}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything… (Enter to send)"
            disabled={streaming}
            className="flex-1 resize-none bg-transparent text-sm text-surface-900 placeholder-surface-400 focus:outline-none dark:text-white dark:placeholder-white/30"
            style={{ maxHeight: '120px' }}
          />
          <button
            type="button"
            onClick={() => send()}
            disabled={!input.trim() || streaming}
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-brand-600 text-white transition-colors hover:bg-brand-700 disabled:opacity-40"
          >
            {streaming ? <Loader2 className="h-4 w-4 animate-spin" /> : <CornerDownLeft className="h-4 w-4" />}
          </button>
        </div>
        <p className="mt-1.5 text-center text-xs text-surface-400 dark:text-white/25">
          Shift+Enter for new line · Responses are AI-generated
        </p>
      </div>
    </div>
  );
}
