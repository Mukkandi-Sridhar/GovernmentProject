import {
  ChatQueryRequestSchema,
  ChatQueryResponseSchema,
  ChatJobStatusResponseSchema,
  SchemeVersionSchema,
  type ChatJobStatusResponse,
  type ChatQueryRequest,
  type ChatQueryResponse,
  type SchemeVersion,
} from "@ap-civic/contracts";
import { z } from "zod";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit, schema?: z.ZodType<T>): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }

  const json = await response.json();
  return schema ? schema.parse(json) : json;
}

export function queryChat(payload: ChatQueryRequest): Promise<ChatQueryResponse> {
  ChatQueryRequestSchema.parse(payload);
  return request("/chat/query", { method: "POST", body: JSON.stringify(payload) }, ChatQueryResponseSchema);
}

export function getChatJobStatus(jobId: string): Promise<ChatJobStatusResponse> {
  return request(`/chat/jobs/${jobId}`, undefined, ChatJobStatusResponseSchema);
}

export function listSchemes(status = "approved"): Promise<SchemeVersion[]> {
  const schema = z.array(SchemeVersionSchema);
  return request(`/schemes?status=${status}`, undefined, schema);
}

export function getScheme(schemeId: string): Promise<SchemeVersion> {
  return request(`/schemes/${schemeId}`, undefined, SchemeVersionSchema);
}

export function listSchemeVersions(schemeId: string): Promise<SchemeVersion[]> {
  const schema = z.array(SchemeVersionSchema);
  return request(`/schemes/${schemeId}/versions`, undefined, schema);
}

export function getSchemeDiff(schemeId: string, version: number): Promise<{ field_diff: Record<string, { from: unknown; to: unknown }> }> {
  return request(`/schemes/${schemeId}/versions/${version}/diff`);
}

export function runCrawl(): Promise<{ job_id: string; status: string }> {
  return request("/admin/crawl/run", { method: "POST" });
}

export function runOpenSourcePull(): Promise<{
  job_id: string;
  status: string;
  embedding_provider: string;
  vector_chunks_rebuilt: number;
  seeded_hosts: string[];
}> {
  return request("/admin/crawl/run-open-source", { method: "POST" });
}

export function listCrawlJobs(): Promise<Array<Record<string, unknown>>> {
  return request("/admin/crawl/jobs");
}

export function listAuditLogs(): Promise<Array<Record<string, unknown>>> {
  return request("/admin/logs");
}

export function listAnomalies(): Promise<Array<Record<string, unknown>>> {
  return request("/admin/anomalies");
}

export function approveVersion(schemeId: string, version: number, reason: string): Promise<{ ok: boolean }> {
  return request(`/admin/schemes/${schemeId}/versions/${version}/approve`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export function flagVersion(schemeId: string, version: number, reason: string): Promise<{ ok: boolean }> {
  return request(`/admin/schemes/${schemeId}/versions/${version}/flag`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export function addHost(host: string): Promise<Record<string, unknown>> {
  return request("/admin/allowlist/hosts", {
    method: "POST",
    body: JSON.stringify({ host }),
  });
}

export function removeHost(host: string): Promise<{ ok: boolean }> {
  return request(`/admin/allowlist/hosts/${host}`, { method: "DELETE" });
}

