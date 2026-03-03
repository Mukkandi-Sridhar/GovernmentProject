"use client";

import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { listAnomalies } from "@/lib/api";

export default function AdminFlagsPage() {
  const query = useQuery({ queryKey: ["anomalies"], queryFn: listAnomalies });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Anomaly Alerts</h1>
      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-soft">
        {query.isLoading ? (
          <p>Loading anomalies...</p>
        ) : query.isError ? (
          <p>Failed to load anomalies.</p>
        ) : (query.data ?? []).length === 0 ? (
          <p>No active anomalies.</p>
        ) : (
          <ul className="space-y-2">
            {(query.data ?? []).map((row: Record<string, unknown>, idx: number) => (
              <li key={`${String(row.type)}-${idx}`} className="rounded-xl border border-slate-200 p-3 text-sm">
                <div className="mb-1 flex items-center gap-2">
                  <Badge>{String(row.type)}</Badge>
                  <span className="font-semibold">{String(row.scheme_id)}</span>
                </div>
                <pre className="overflow-auto text-xs text-slate-700">{JSON.stringify(row, null, 2)}</pre>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

