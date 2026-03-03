"use client";

import { AlertTriangle } from "lucide-react";

import { Badge } from "@/components/ui/badge";

export function OutdatedDataBanner({ stale }: { stale: boolean }) {
  if (!stale) return null;

  return (
    <div className="mb-4 flex items-center gap-2 rounded-2xl border border-warning/30 bg-warning/10 px-4 py-3 text-sm text-slate-800" role="alert">
      <AlertTriangle className="h-4 w-4 text-warning" />
      <Badge className="border-warning/30 bg-warning/20 text-warning">Warning</Badge>
      Data may be outdated. Please verify with the latest official notification.
    </div>
  );
}

