import { ReactNode } from "react";

import { AdminSidebar } from "@/components/layout/admin-sidebar";

export default function AdminLayout({ children }: { children: ReactNode }) {
  return (
    <div className="grid gap-4 lg:grid-cols-[280px_minmax(0,1fr)]">
      <AdminSidebar />
      <div>{children}</div>
    </div>
  );
}

