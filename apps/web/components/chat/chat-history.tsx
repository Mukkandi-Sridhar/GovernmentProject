"use client";

import { Clock3 } from "lucide-react";

export function ChatHistory({ history }: { history: string[] }) {
  return (
    <aside className="hidden w-72 shrink-0 rounded-2xl border border-slate-200 bg-white p-4 shadow-soft xl:block">
      <h2 className="mb-3 text-sm font-semibold text-slate-700">Recent Searches</h2>
      <ul className="space-y-2">
        {history.length ? (
          history.map((item, idx) => (
            <li key={`${item}-${idx}`} className="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs text-slate-700">
              {item}
            </li>
          ))
        ) : (
          <li className="rounded-xl border border-dashed border-slate-200 px-3 py-4 text-xs text-slate-500">
            <Clock3 className="mb-2 h-4 w-4" />
            Your recent questions appear here.
          </li>
        )}
      </ul>
    </aside>
  );
}

