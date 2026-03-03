"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Activity, Flag, FolderKanban, ListChecks, RefreshCw } from "lucide-react";

import { cn } from "@/lib/utils";

const nav = [
  { href: "/admin/schemes", label: "Schemes", icon: FolderKanban },
  { href: "/admin/crawl", label: "Crawl Monitor", icon: RefreshCw },
  { href: "/admin/logs", label: "Update Logs", icon: ListChecks },
  { href: "/admin/flags", label: "Flags", icon: Flag },
  { href: "/chat", label: "Public Chat", icon: Activity },
];

export function AdminSidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-full rounded-2xl border border-slate-200 bg-white p-3 shadow-soft lg:w-72">
      <p className="px-3 pb-2 text-xs font-semibold uppercase tracking-wider text-slate-500">Admin Console</p>
      <nav className="space-y-1">
        {nav.map((item) => {
          const active = pathname.startsWith(item.href);
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-2 rounded-xl px-3 py-2 text-sm transition",
                active ? "bg-primary text-white" : "text-slate-700 hover:bg-slate-100",
              )}
            >
              <Icon className="h-4 w-4" />
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

