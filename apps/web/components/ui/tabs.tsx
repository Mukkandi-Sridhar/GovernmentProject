"use client";

import { cn } from "@/lib/utils";
import { ReactNode, useState } from "react";

export function Tabs({
  tabs,
  defaultTab,
}: {
  tabs: Array<{ id: string; label: string; content: ReactNode }>;
  defaultTab?: string;
}) {
  const [active, setActive] = useState(defaultTab ?? tabs[0]?.id ?? "");

  return (
    <div>
      <div className="mb-4 flex flex-wrap gap-2">
        {tabs.map((tab) => (
            <button
              key={tab.id}
              className={cn(
                "rounded-xl px-4 py-2 text-sm font-medium transition",
                active === tab.id ? "bg-primary text-white" : "bg-white text-slate-700 hover:bg-slate-100",
              )}
              onClick={() => setActive(tab.id)}
              type="button"
              aria-pressed={active === tab.id}
            >
            {tab.label}
          </button>
        ))}
      </div>
      <div>{tabs.find((tab) => tab.id === active)?.content}</div>
    </div>
  );
}

