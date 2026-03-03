"use client";

import { useQuery } from "@tanstack/react-query";

import { listAuditLogs } from "@/lib/api";

export default function AdminLogsPage() {
  const query = useQuery({ queryKey: ["audit-logs"], queryFn: listAuditLogs });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Extraction & Update Logs</h1>
      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-soft">
        {query.isLoading ? (
          <p>Loading logs...</p>
        ) : query.isError ? (
          <p>Failed to load logs.</p>
        ) : (
          <ul className="space-y-2">
            {(query.data ?? []).map((log: Record<string, unknown>, idx: number) => (
              <li key={`${String(log.scheme_id)}-${idx}`} className="rounded-xl border border-slate-200 p-3 text-sm">
                <p className="font-semibold">{String(log.scheme_id)}</p>
                <p>{String(log.change_summary)}</p>
                <p className="text-xs text-slate-500">{String(log.timestamp)}</p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

