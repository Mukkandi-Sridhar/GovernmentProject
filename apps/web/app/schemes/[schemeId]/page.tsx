"use client";

import { useQuery } from "@tanstack/react-query";
import { useParams } from "next/navigation";

import { Tabs } from "@/components/ui/tabs";
import { getScheme, listSchemeVersions } from "@/lib/api";

export default function SchemeDetailPage() {
  const params = useParams<{ schemeId: string }>();
  const schemeId = params.schemeId;

  const schemeQuery = useQuery({
    queryKey: ["scheme", schemeId],
    queryFn: () => getScheme(schemeId),
  });

  const versionsQuery = useQuery({
    queryKey: ["scheme-versions", schemeId],
    queryFn: () => listSchemeVersions(schemeId),
  });

  if (schemeQuery.isLoading) return <p>Loading scheme...</p>;
  if (schemeQuery.isError || !schemeQuery.data) return <p>Unable to load scheme details.</p>;

  const scheme = schemeQuery.data;
  const versions = versionsQuery.data ?? [];

  return (
    <div className="space-y-6">
      <header className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
        <h1 className="text-2xl font-bold">{scheme.structured_data.scheme_name ?? scheme.scheme_id}</h1>
        <p className="mt-1 text-sm text-slate-600">{scheme.structured_data.department ?? "Department not explicitly stated"}</p>
        <div className="mt-3 flex flex-wrap gap-3 text-xs text-slate-600">
          <span>Version v{scheme.version}</span>
          <span>Last updated {new Date(scheme.last_verified).toLocaleString()}</span>
          <a className="text-primary hover:underline" href={scheme.source_url} target="_blank" rel="noreferrer">
            Official Source
          </a>
        </div>
      </header>

      <Tabs
        tabs={[
          {
            id: "eligibility",
            label: "Eligibility",
            content: (
              <div className="rounded-2xl border border-slate-200 bg-white p-5">
                <p className="mb-2 text-sm text-slate-700">Caste categories: {(scheme.structured_data.eligible_castes ?? []).join(", ") || "Not officially confirmed"}</p>
                <p className="mb-2 text-sm text-slate-700">Education levels: {(scheme.structured_data.education_levels ?? []).join(", ") || "Not officially confirmed"}</p>
                <p className="text-sm text-slate-700">Special conditions: {(scheme.structured_data.special_conditions ?? []).join(", ") || "Not officially confirmed"}</p>
              </div>
            ),
          },
          {
            id: "documents",
            label: "Documents Required",
            content: (
              <div className="rounded-2xl border border-slate-200 bg-white p-5 text-sm text-slate-700">
                {(scheme.structured_data.required_documents ?? []).length
                  ? scheme.structured_data.required_documents?.map((doc) => <p key={doc}>• {doc}</p>)
                  : "No officially confirmed document list found."}
              </div>
            ),
          },
          {
            id: "deadlines",
            label: "Deadlines",
            content: (
              <div className="rounded-2xl border border-slate-200 bg-white p-5 text-sm text-slate-700">
                <p>Application deadline: {scheme.structured_data.application_deadline ?? "Not officially confirmed"}</p>
                <p className="mt-2">Application mode: {scheme.structured_data.application_mode ?? "Not officially confirmed"}</p>
              </div>
            ),
          },
          {
            id: "source",
            label: "Official Source",
            content: (
              <div className="rounded-2xl border border-slate-200 bg-white p-5 text-sm">
                <a className="text-primary hover:underline" href={scheme.source_url} target="_blank" rel="noreferrer">
                  {scheme.source_url}
                </a>
              </div>
            ),
          },
          {
            id: "versions",
            label: "Version History",
            content: (
              <div className="rounded-2xl border border-slate-200 bg-white p-5">
                <ol className="space-y-3">
                  {versions.map((version) => (
                    <li key={`${version.scheme_id}-${version.version}`} className="rounded-xl border border-slate-200 p-3">
                      <p className="text-sm font-semibold">v{version.version}</p>
                      <p className="text-xs text-slate-500">{new Date(version.last_verified).toLocaleString()}</p>
                      <p className="mt-2 text-xs text-slate-700">Changed fields: {Object.keys(version.field_diff).join(", ") || "None"}</p>
                    </li>
                  ))}
                </ol>
              </div>
            ),
          },
        ]}
      />
    </div>
  );
}

