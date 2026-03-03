"use client";

import { useQuery } from "@tanstack/react-query";

import { SchemeTable } from "@/components/admin/scheme-table";
import { listSchemes } from "@/lib/api";

export default function AdminSchemesPage() {
  const query = useQuery({
    queryKey: ["admin-schemes"],
    queryFn: async () => {
      const [pending, approved, flagged] = await Promise.all([
        listSchemes("pending_review"),
        listSchemes("approved"),
        listSchemes("flagged"),
      ]);
      return [...pending, ...approved, ...flagged];
    },
  });

  if (query.isLoading) return <p>Loading schemes...</p>;
  if (query.isError) return <p>Failed to load schemes.</p>;

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Detected Schemes</h1>
      <SchemeTable rows={query.data ?? []} />
    </div>
  );
}

