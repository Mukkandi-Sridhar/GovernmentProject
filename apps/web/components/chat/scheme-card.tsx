import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export function SchemeCard({
  scheme_name,
  department,
  eligibility_summary,
  income_limit,
  deadline,
  details_url,
}: {
  scheme_name: string;
  department: string | null;
  eligibility_summary: string | null;
  income_limit: string | null;
  deadline: string | null;
  details_url: string;
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{scheme_name}</CardTitle>
        <CardDescription>{department ?? "Department not explicitly stated"}</CardDescription>
      </CardHeader>
      <CardContent>
        <dl className="space-y-2 text-sm text-slate-700">
          <div className="flex justify-between gap-4">
            <dt className="font-semibold">Eligibility</dt>
            <dd className="text-right">{eligibility_summary ?? "Not officially confirmed"}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="font-semibold">Income Limit</dt>
            <dd className="text-right">{income_limit ?? "Not officially confirmed"}</dd>
          </div>
          <div className="flex justify-between gap-4">
            <dt className="font-semibold">Deadline</dt>
            <dd className="text-right">{deadline ?? "Not officially confirmed"}</dd>
          </div>
        </dl>
        <a href={details_url} target="_blank" rel="noreferrer" className="mt-4 inline-block text-sm font-semibold text-primary hover:underline">
          View Details
        </a>
      </CardContent>
    </Card>
  );
}

