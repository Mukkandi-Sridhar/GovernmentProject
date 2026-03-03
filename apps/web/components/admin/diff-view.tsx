import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function DiffView({ diff }: { diff: Record<string, { from: unknown; to: unknown }> }) {
  const entries = Object.entries(diff);
  if (!entries.length) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Version Diff</CardTitle>
        </CardHeader>
        <CardContent>No field-level changes detected.</CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Version Diff</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {entries.map(([field, value]) => (
          <div key={field} className="rounded-xl border border-slate-200 p-3">
            <div className="mb-2 flex items-center justify-between">
              <p className="font-semibold text-slateText">{field}</p>
              <Badge>Changed</Badge>
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              <div className="rounded-lg border border-danger/30 bg-danger/10 p-2 text-xs">
                <p className="mb-1 font-semibold text-danger">Previous</p>
                <pre className="overflow-auto whitespace-pre-wrap">{JSON.stringify(value.from, null, 2)}</pre>
              </div>
              <div className="rounded-lg border border-accent/30 bg-accent/10 p-2 text-xs">
                <p className="mb-1 font-semibold text-accent">Current</p>
                <pre className="overflow-auto whitespace-pre-wrap">{JSON.stringify(value.to, null, 2)}</pre>
              </div>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

