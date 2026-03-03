"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Table, TBody, TD, TH, THead } from "@/components/ui/table";
import type { SchemeVersion } from "@ap-civic/contracts";

function confidenceTone(value: number) {
  if (value >= 0.8) return "border-accent/40 bg-accent/10 text-accent";
  if (value >= 0.55) return "border-warning/40 bg-warning/10 text-warning";
  return "border-danger/40 bg-danger/10 text-danger";
}

export function SchemeTable({ rows }: { rows: SchemeVersion[] }) {
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");

  const filtered = useMemo(
    () =>
      rows.filter((row) => {
        const inSearch = `${row.scheme_id} ${row.structured_data.scheme_name ?? ""}`
          .toLowerCase()
          .includes(search.toLowerCase());
        const inStatus = status === "all" || row.status === status;
        return inSearch && inStatus;
      }),
    [rows, search, status],
  );

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-soft">
      <div className="mb-4 flex flex-col gap-3 sm:flex-row">
        <Input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search scheme name or id"
          aria-label="Search schemes"
          className="sm:max-w-sm"
        />
        <select
          className="h-10 rounded-xl border border-slate-300 px-3 text-sm"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          aria-label="Filter by status"
        >
          <option value="all">All statuses</option>
          <option value="pending_review">Pending</option>
          <option value="approved">Approved</option>
          <option value="flagged">Flagged</option>
        </select>
      </div>

      <div className="overflow-auto">
        <Table>
          <THead>
            <tr>
              <TH>Scheme</TH>
              <TH>Version</TH>
              <TH>Confidence</TH>
              <TH>Last Updated</TH>
              <TH>Status</TH>
              <TH>Action</TH>
            </tr>
          </THead>
          <TBody>
            {filtered.map((row) => (
              <tr key={`${row.scheme_id}-${row.version}`}>
                <TD>{row.structured_data.scheme_name ?? row.scheme_id}</TD>
                <TD>v{row.version}</TD>
                <TD>
                  <Badge className={confidenceTone(row.confidence)}>{Math.round(row.confidence * 100)}%</Badge>
                </TD>
                <TD>{new Date(row.last_verified).toLocaleString()}</TD>
                <TD>
                  <Badge>{row.status}</Badge>
                </TD>
                <TD>
                  <Link
                    href={`/admin/schemes/${encodeURIComponent(row.scheme_id)}`}
                    prefetch={false}
                    className="text-primary hover:underline"
                  >
                    Open
                  </Link>
                </TD>
              </tr>
            ))}
          </TBody>
        </Table>
      </div>
    </div>
  );
}

