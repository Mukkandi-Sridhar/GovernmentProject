import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Shimmer({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "animate-pulse rounded-xl bg-gradient-to-r from-slate-200 via-slate-100 to-slate-200",
        className,
      )}
      {...props}
    />
  );
}

