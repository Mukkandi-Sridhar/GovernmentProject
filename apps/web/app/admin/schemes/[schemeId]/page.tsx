"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useParams } from "next/navigation";

import { DiffView } from "@/components/admin/diff-view";
import { ModeratePanel } from "@/components/admin/moderate-panel";
import { Badge } from "@/components/ui/badge";
import { approveVersion, flagVersion, getSchemeDiff, listSchemeVersions } from "@/lib/api";

export default function AdminSchemeDetailPage() {
  const params = useParams<{ schemeId: string }>();
  const schemeId = params.schemeId;
  const queryClient = useQueryClient();

  const versionsQuery = useQuery({
    queryKey: ["admin-scheme-versions", schemeId],
    queryFn: () => listSchemeVersions(schemeId),
  });

  const latest = versionsQuery.data?.[0];

  const diffQuery = useQuery({
    queryKey: ["admin-scheme-diff", schemeId, latest?.version],
    queryFn: () => getSchemeDiff(schemeId, latest!.version),
    enabled: !!latest,
  });

  const approveMutation = useMutation({
    mutationFn: (reason: string) => approveVersion(schemeId, latest!.version, reason),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-scheme-versions", schemeId] });
    },
  });

  const flagMutation = useMutation({
    mutationFn: (reason: string) => flagVersion(schemeId, latest!.version, reason),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["admin-scheme-versions", schemeId] });
    },
  });

  if (versionsQuery.isLoading) return <p>Loading scheme versions...</p>;
  if (versionsQuery.isError || !latest) return <p>Unable to load scheme version data.</p>;

  return (
    <div className="space-y-4">
      <section className="rounded-2xl border border-slate-200 bg-white p-5 shadow-soft">
        <h1 className="text-2xl font-bold">{latest.structured_data.scheme_name ?? schemeId}</h1>
        <div className="mt-2 flex flex-wrap gap-2">
          <Badge>Version v{latest.version}</Badge>
          <Badge>{latest.status}</Badge>
          <Badge>{Math.round(latest.confidence * 100)}% confidence</Badge>
        </div>
      </section>

      <DiffView diff={diffQuery.data?.field_diff ?? {}} />

      <ModeratePanel
        onApprove={async (reason) => {
          await approveMutation.mutateAsync(reason);
        }}
        onFlag={async (reason) => {
          await flagMutation.mutateAsync(reason);
        }}
      />
    </div>
  );
}

