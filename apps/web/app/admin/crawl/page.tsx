"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Shimmer } from "@/components/ui/shimmer";
import { approveVersion, listCrawlJobs, listSchemes, runCrawl, runOpenSourcePull } from "@/lib/api";
import type { SchemeVersion } from "@ap-civic/contracts";

type CrawlJob = {
  job_id: string;
  status: string;
  progress_phase?: string;
  discovered?: number;
  updated?: number;
  failed?: number;
  started_at?: string;
  ended_at?: string | null;
  error?: string | null;
};

function formatTime(value?: string): string {
  if (!value) return "n/a";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.valueOf())) return "n/a";
  return parsed.toLocaleTimeString();
}

function formatElapsed(startedAt?: string, endedAt?: string | null): string {
  if (!startedAt) return "n/a";
  const start = new Date(startedAt).valueOf();
  if (Number.isNaN(start)) return "n/a";
  const end = endedAt ? new Date(endedAt).valueOf() : Date.now();
  const seconds = Math.max(0, Math.floor((end - start) / 1000));
  const minutes = Math.floor(seconds / 60);
  const rem = seconds % 60;
  return `${minutes}m ${rem}s`;
}

export default function AdminCrawlPage() {
  const jobsQuery = useQuery({
    queryKey: ["crawl-jobs"],
    queryFn: listCrawlJobs,
    refetchInterval: 5_000,
    refetchIntervalInBackground: true,
  });
  const crawlMutation = useMutation({ mutationFn: runCrawl, onSuccess: () => jobsQuery.refetch() });
  const openSourceMutation = useMutation({ mutationFn: runOpenSourcePull, onSuccess: () => jobsQuery.refetch() });
  const pendingSchemesQuery = useQuery({
    queryKey: ["pending-schemes-for-crawl-monitor"],
    queryFn: () => listSchemes("pending_review"),
    refetchInterval: 10_000,
    refetchIntervalInBackground: true,
  });
  const quickApproveMutation = useMutation({
    mutationFn: ({ schemeId, version }: { schemeId: string; version: number }) =>
      approveVersion(
        schemeId,
        version,
        "Quick approval from Crawl Monitor to publish verified official update.",
      ),
    onSuccess: () => {
      pendingSchemesQuery.refetch();
      jobsQuery.refetch();
    },
  });
  const jobs = (jobsQuery.data ?? []) as CrawlJob[];
  const runningJobs = jobs.filter((job) => ["queued", "running"].includes(String(job.status)));
  const pendingSchemes = (pendingSchemesQuery.data ?? []) as SchemeVersion[];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Crawl Monitor</h1>
        <div className="flex items-center gap-2">
          <Button onClick={() => crawlMutation.mutate()} disabled={crawlMutation.isPending || openSourceMutation.isPending}>
            Trigger Manual Re-crawl
          </Button>
          <Button
            variant="secondary"
            onClick={() => openSourceMutation.mutate()}
            disabled={crawlMutation.isPending || openSourceMutation.isPending}
          >
            Pull Open-Source Data + Rebuild Vectors
          </Button>
        </div>
      </div>
      <div className="rounded-2xl border border-slate-200 bg-white p-3 text-sm text-slate-600 shadow-soft">
        <p>Live polling every 5 seconds.</p>
        <p>Last refresh: {jobsQuery.dataUpdatedAt ? new Date(jobsQuery.dataUpdatedAt).toLocaleTimeString() : "n/a"}</p>
      </div>
      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-soft">
        <h2 className="mb-2 text-lg font-semibold">Running Process</h2>
        {runningJobs.length === 0 ? (
          <p className="text-sm text-slate-600">No active crawl job.</p>
        ) : (
          <ul className="space-y-2">
            {runningJobs.map((job) => (
              <li key={job.job_id} className="rounded-xl border border-emerald-200 bg-emerald-50 p-3 text-sm">
                <p className="font-semibold text-emerald-800">Job {job.job_id}</p>
                <p>
                  Status: <span className="font-medium">{job.status}</span> | Phase:{" "}
                  <span className="font-medium">{job.progress_phase ?? "running"}</span>
                </p>
                <p>
                  Started: {formatTime(job.started_at)} | Elapsed: {formatElapsed(job.started_at, job.ended_at)}
                </p>
                <p>
                  Discovered: {String(job.discovered ?? 0)} | Updated: {String(job.updated ?? 0)} | Failed:{" "}
                  {String(job.failed ?? 0)}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
      {openSourceMutation.isSuccess ? (
        <p className="text-sm text-slate-700">
          Open-source pull started. Provider: {openSourceMutation.data.embedding_provider}. Rebuilt chunks:{" "}
          {String(openSourceMutation.data.vector_chunks_rebuilt)}.
        </p>
      ) : null}
      {openSourceMutation.isError ? <p className="text-sm text-red-600">Open-source pull failed.</p> : null}
      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-soft">
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-semibold">Pending Review Queue</h2>
          <Button variant="secondary" onClick={() => pendingSchemesQuery.refetch()} disabled={pendingSchemesQuery.isFetching}>
            Refresh Pending
          </Button>
        </div>
        {pendingSchemesQuery.isLoading ? (
          <div className="space-y-2">
            <Shimmer className="h-10 w-full" />
            <Shimmer className="h-10 w-full" />
          </div>
        ) : pendingSchemesQuery.isError ? (
          <p className="text-sm text-red-600">Failed to load pending schemes.</p>
        ) : pendingSchemes.length === 0 ? (
          <p className="text-sm text-slate-600">No pending versions. All detected schemes are already moderated.</p>
        ) : (
          <ul className="space-y-2">
            {pendingSchemes.map((row) => (
              <li key={`${row.scheme_id}-${row.version}`} className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm">
                <p className="font-semibold">
                  {row.structured_data.scheme_name ?? row.scheme_id} (v{row.version})
                </p>
                <p>
                  Status: {row.status} | Confidence: {Math.round(row.confidence * 100)}%
                </p>
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  <Button
                    onClick={() => quickApproveMutation.mutate({ schemeId: row.scheme_id, version: row.version })}
                    disabled={quickApproveMutation.isPending}
                  >
                    Approve + Update Index
                  </Button>
                  <Link
                    href={`/admin/schemes/${encodeURIComponent(row.scheme_id)}`}
                    prefetch={false}
                    className="text-sm font-medium text-blue-700 hover:underline"
                  >
                    Open Details
                  </Link>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
      {quickApproveMutation.isSuccess ? (
        <p className="text-sm text-emerald-700">Pending version approved and vectors updated.</p>
      ) : null}
      {quickApproveMutation.isError ? (
        <p className="text-sm text-red-600">Approve/update failed. Open details to review manually.</p>
      ) : null}

      <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-soft">
        {jobsQuery.isLoading ? (
          <div className="space-y-2">
            <Shimmer className="h-10 w-full" />
            <Shimmer className="h-10 w-full" />
          </div>
        ) : jobsQuery.isError ? (
          <p>Failed to load crawl jobs.</p>
        ) : (
          <ul className="space-y-2">
            {jobs.map((job) => (
              <li key={job.job_id} className="rounded-xl border border-slate-200 p-3 text-sm">
                <p className="font-semibold">Job {job.job_id}</p>
                <p>
                  Status: {job.status} | Phase: {job.progress_phase ?? "n/a"}
                </p>
                <p>
                  Started: {formatTime(job.started_at)} | Ended: {formatTime(job.ended_at ?? undefined)} | Elapsed:{" "}
                  {formatElapsed(job.started_at, job.ended_at)}
                </p>
                <p>
                  Discovered: {String(job.discovered ?? 0)} | Updated: {String(job.updated ?? 0)} | Failed:{" "}
                  {String(job.failed ?? 0)}
                </p>
                {job.error ? <p className="text-red-600">Error: {job.error}</p> : null}
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

