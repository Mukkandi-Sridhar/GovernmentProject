"use client";

import { useMemo, useState } from "react";
import { useMutation } from "@tanstack/react-query";

import { ChatBubble } from "@/components/chat/chat-bubble";
import { ChatHistory } from "@/components/chat/chat-history";
import { CitationList } from "@/components/chat/citation-list";
import { SchemeCard } from "@/components/chat/scheme-card";
import { TypingIndicator } from "@/components/chat/typing-indicator";
import { OutdatedDataBanner } from "@/components/layout/outdated-banner";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { queryChat } from "@/lib/api";

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [query, setQuery] = useState("");
  const [language, setLanguage] = useState<"en" | "te">("en");
  const [history, setHistory] = useState<string[]>([]);
  const [citations, setCitations] = useState<Array<{ source_url: string; version: number; last_updated: string }>>([]);
  const [cards, setCards] = useState<Array<{ scheme_name: string; department: string | null; eligibility_summary: string | null; income_limit: string | null; deadline: string | null; details_url: string }>>([]);

  const mutation = useMutation({
    mutationFn: queryChat,
    onSuccess: (data) => {
      setMessages((prev) => [...prev, { role: "assistant", text: data.answer_text }]);
      setCitations(data.citations as Array<{ source_url: string; version: number; last_updated: string }>);
      setCards(data.structured_cards as Array<{ scheme_name: string; department: string | null; eligibility_summary: string | null; income_limit: string | null; deadline: string | null; details_url: string }>);
    },
    onError: () => {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "I could not find official confirmation from government sources." },
      ]);
      setCitations([]);
      setCards([]);
    },
  });

  const isStale = useMemo(() => {
    if (!citations.length) return false;
    const now = Date.now();
    return citations.some((citation) => now - new Date(citation.last_updated).getTime() > 48 * 60 * 60 * 1000);
  }, [citations]);

  async function submit() {
    if (!query.trim() || mutation.isPending) return;
    const nextQuery = query.trim();

    setMessages((prev) => [...prev, { role: "user", text: nextQuery }]);
    setHistory((prev) => [nextQuery, ...prev].slice(0, 8));
    setQuery("");
    await mutation.mutateAsync({ query: nextQuery, language, conversation_id: "public-user" });
  }

  return (
    <div className="grid gap-4 xl:grid-cols-[280px_minmax(0,1fr)_320px]">
      <ChatHistory history={history} />

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-soft">
        <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
          <h1 className="text-xl font-bold">Public Assistant</h1>
          <div className="inline-flex rounded-xl border border-slate-200 p-1">
            <button
              type="button"
              className={`rounded-lg px-3 py-1 text-sm ${language === "en" ? "bg-primary text-white" : "text-slate-700"}`}
              onClick={() => setLanguage("en")}
            >
              English
            </button>
            <button
              type="button"
              className={`rounded-lg px-3 py-1 text-sm ${language === "te" ? "bg-primary text-white" : "text-slate-700"}`}
              onClick={() => setLanguage("te")}
            >
              Telugu
            </button>
          </div>
        </div>

        <OutdatedDataBanner stale={isStale} />

        <div className="mb-4 h-[420px] space-y-3 overflow-y-auto rounded-xl border border-slate-200 bg-slate-50 p-3">
          {messages.length === 0 ? (
            <p className="text-sm text-slate-500">
              Ask about any Andhra Pradesh student welfare scheme. Responses include source URL, version, and last update.
            </p>
          ) : (
            messages.map((msg, idx) => <ChatBubble key={`${msg.role}-${idx}`} role={msg.role} text={msg.text} />)
          )}
          {mutation.isPending ? <TypingIndicator /> : null}
        </div>

        {cards.length ? (
          <div className="mb-4 grid gap-3 md:grid-cols-2">
            {cards.map((card, idx) => (
              <SchemeCard key={`${card.scheme_name}-${idx}`} {...card} />
            ))}
          </div>
        ) : null}

        <div className="sticky bottom-0 flex gap-2 bg-white pt-2">
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") void submit();
            }}
            placeholder="Ask about eligibility, deadlines, required documents..."
            aria-label="Chat query"
          />
          <Button onClick={() => void submit()} disabled={mutation.isPending || !query.trim()}>
            Send
          </Button>
        </div>
      </section>

      <aside className="rounded-2xl border border-slate-200 bg-white p-4 shadow-soft">
        <h2 className="mb-3 text-sm font-semibold text-slate-700">Cited Sources</h2>
        <CitationList citations={citations} />
      </aside>
    </div>
  );
}

