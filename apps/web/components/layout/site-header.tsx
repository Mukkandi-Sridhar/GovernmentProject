import Link from "next/link";

import { Badge } from "@/components/ui/badge";

export function SiteHeader() {
  return (
    <header className="sticky top-0 z-40 border-b border-slate-200 bg-white/95 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-primary" aria-hidden />
          <div>
            <p className="text-sm font-semibold text-slateText">Andhra Pradesh Welfare AI</p>
            <p className="text-xs text-slate-500">Official civic intelligence interface</p>
          </div>
        </div>
        <nav className="flex items-center gap-2">
          <Link className="rounded-xl px-3 py-2 text-sm text-slate-700 hover:bg-slate-100" href="/">
            Home
          </Link>
          <Link className="rounded-xl px-3 py-2 text-sm text-slate-700 hover:bg-slate-100" href="/chat">
            Chat
          </Link>
          <Link className="rounded-xl px-3 py-2 text-sm text-slate-700 hover:bg-slate-100" href="/admin/schemes">
            Admin
          </Link>
        </nav>
      </div>
      <div className="border-t border-slate-100 bg-slate-50/80 px-4 py-2 text-center text-xs text-slate-600">
        <Badge className="mr-2">Official Sources</Badge>
        Data sourced from official government portals.
      </div>
    </header>
  );
}

