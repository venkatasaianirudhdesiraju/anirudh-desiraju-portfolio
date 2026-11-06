"use client";

import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Cpu, Loader2, Send, Sparkles, WifiOff, X } from "lucide-react";
import ReactMarkdown from "react-markdown";
import { profile } from "@/lib/data";

type Role = "user" | "assistant";
type Message = { role: Role; content: string };

type OllamaStatus = "checking" | "online" | "offline";

const SUGGESTIONS = [
  "What's his strongest tech stack?",
  "Tell me about the Lab tools.",
  "What did he do at Intel?",
  "Is he open to new roles?",
];

export default function ChatWidget() {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<OllamaStatus>("checking");
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    setStatus("checking");
    fetch("/api/ollama-status")
      .then((r) => r.json())
      .then((d: { online: boolean; hasModel: boolean }) => {
        setStatus(d.online && d.hasModel ? "online" : "offline");
      })
      .catch(() => setStatus("offline"));
  }, [open]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, streaming]);

  async function send(text: string) {
    const content = text.trim();
    if (!content || streaming) return;

    const next: Message[] = [...messages, { role: "user", content }];
    setMessages(next);
    setInput("");
    setStreaming(true);
    setMessages((m) => [...m, { role: "assistant", content: "" }]);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: next }),
      });

      if (!res.ok || !res.body) {
        const errText = await res.text();
        setMessages((m) => {
          const copy = [...m];
          copy[copy.length - 1] = { role: "assistant", content: `⚠️ ${errText}` };
          return copy;
        });
        setStatus("offline");
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let acc = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        acc += decoder.decode(value, { stream: true });
        setMessages((m) => {
          const copy = [...m];
          copy[copy.length - 1] = { role: "assistant", content: acc };
          return copy;
        });
      }
    } catch {
      setMessages((m) => {
        const copy = [...m];
        copy[copy.length - 1] = {
          role: "assistant",
          content: "⚠️ Lost connection to the local model. Is Ollama still running?",
        };
        return copy;
      });
    } finally {
      setStreaming(false);
    }
  }

  return (
    <>
      <motion.button
        onClick={() => setOpen((o) => !o)}
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 1.2, type: "spring", stiffness: 260, damping: 20 }}
        whileHover={{ scale: 1.06 }}
        whileTap={{ scale: 0.95 }}
        className="fixed bottom-6 right-6 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-accent text-[#0a0a0a] shadow-lg shadow-accent/30"
        aria-label="Open AI chat"
      >
        <AnimatePresence mode="wait" initial={false}>
          <motion.span
            key={open ? "close" : "open"}
            initial={{ rotate: -45, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            exit={{ rotate: 45, opacity: 0 }}
            transition={{ duration: 0.2 }}
          >
            {open ? <X className="h-5 w-5" /> : <Sparkles className="h-5 w-5" />}
          </motion.span>
        </AnimatePresence>
      </motion.button>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 24, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 24, scale: 0.96 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="glass fixed bottom-24 right-6 z-50 flex h-[32rem] w-[22rem] flex-col overflow-hidden rounded-2xl border border-border shadow-2xl sm:w-[24rem]"
          >
            <div className="flex items-center justify-between border-b border-border px-4 py-3">
              <div className="flex items-center gap-2">
                <Cpu className="h-4 w-4 text-accent" />
                <div>
                  <div className="text-sm font-medium">Ask about {profile.shortName}</div>
                  <div className="font-mono text-[10px] text-muted">
                    {status === "checking" && "checking local model…"}
                    {status === "online" && "llama3.1:8b · running on this desktop"}
                    {status === "offline" && "local model offline"}
                  </div>
                </div>
              </div>
              <span
                className={`h-2 w-2 rounded-full ${
                  status === "online"
                    ? "bg-emerald-400"
                    : status === "checking"
                      ? "animate-pulse bg-muted"
                      : "bg-red-400"
                }`}
              />
            </div>

            <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-4 py-4">
              {status === "offline" && messages.length === 0 && (
                <div className="flex flex-col items-center gap-2 rounded-xl border border-dashed border-border p-5 text-center">
                  <WifiOff className="h-5 w-5 text-muted" />
                  <p className="text-xs text-muted">
                    This chat runs on a local Llama 3.1 8B model via Ollama on {profile.shortName}
                    &apos;s desktop. It&apos;s offline right now — start it with:
                  </p>
                  <code className="rounded-md bg-background px-2 py-1 font-mono text-[11px] text-accent">
                    ollama serve
                  </code>
                </div>
              )}

              {messages.length === 0 && status !== "offline" && (
                <div className="space-y-2">
                  <p className="text-xs text-muted">Try asking:</p>
                  {SUGGESTIONS.map((s) => (
                    <button
                      key={s}
                      onClick={() => send(s)}
                      className="block w-full rounded-lg border border-border bg-surface/50 px-3 py-2 text-left text-xs text-foreground/85 transition-colors hover:border-accent/50"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              )}

              {messages.map((m, i) => (
                <div
                  key={i}
                  className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[85%] rounded-xl px-3 py-2 text-sm leading-relaxed ${
                      m.role === "user"
                        ? "bg-accent text-[#0a0a0a]"
                        : "border border-border bg-surface/70"
                    }`}
                  >
                    {m.content ? (
                      <div className="prose-chat">
                        <ReactMarkdown>{m.content}</ReactMarkdown>
                      </div>
                    ) : (
                      <Loader2 className="h-3.5 w-3.5 animate-spin text-muted" />
                    )}
                  </div>
                </div>
              ))}
            </div>

            <form
              onSubmit={(e) => {
                e.preventDefault();
                send(input);
              }}
              className="flex items-center gap-2 border-t border-border p-3"
            >
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={status === "offline" ? "Start Ollama to chat…" : "Ask a question…"}
                disabled={status === "offline" || streaming}
                className="flex-1 rounded-lg border border-border bg-background/60 px-3 py-2 text-sm outline-none transition-colors focus:border-accent disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={status === "offline" || streaming || !input.trim()}
                className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-accent text-[#0a0a0a] transition-opacity disabled:opacity-40"
                aria-label="Send"
              >
                {streaming ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
