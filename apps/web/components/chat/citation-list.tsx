import { Badge } from "@/components/ui/badge";

export function CitationList({ citations }: { citations: Array<{ source_url: string; version: number; last_updated: string }> }) {
  if (!citations.length) {
    return <p className="text-sm text-slate-500">No citations available.</p>;
  }

  return (
    <ul className="space-y-2">
      {citations.map((citation, idx) => (
        <li key={`${citation.source_url}-${idx}`} className="rounded-xl border border-slate-200 bg-white p-3">
          <div className="mb-2 flex flex-wrap gap-2">
            <Badge>v{citation.version}</Badge>
            <Badge>Updated {new Date(citation.last_updated).toLocaleDateString()}</Badge>
          </div>
          <a href={citation.source_url} className="text-sm text-primary hover:underline" target="_blank" rel="noreferrer">
            {citation.source_url}
          </a>
        </li>
      ))}
    </ul>
  );
}

