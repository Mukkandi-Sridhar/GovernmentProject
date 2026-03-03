"use client";

import { useState } from "react";

import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

export function ModeratePanel({
  onApprove,
  onFlag,
}: {
  onApprove: (reason: string) => Promise<void>;
  onFlag: (reason: string) => Promise<void>;
}) {
  const [reason, setReason] = useState("");
  const [busy, setBusy] = useState(false);

  async function perform(action: "approve" | "flag") {
    if (reason.trim().length < 3) return;
    setBusy(true);
    try {
      if (action === "approve") {
        await onApprove(reason);
      } else {
        await onFlag(reason);
      }
      setReason("");
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-4 shadow-soft">
      <h3 className="mb-3 text-base font-semibold">Moderation Actions</h3>
      <Textarea
        value={reason}
        onChange={(e) => setReason(e.target.value)}
        placeholder="Enter moderation reason"
        className="mb-3"
        aria-label="Moderation reason"
      />
      <div className="flex gap-2">
        <Button onClick={() => void perform("approve")} disabled={busy || reason.trim().length < 3}>
          Approve Version
        </Button>
        <Button variant="danger" onClick={() => void perform("flag")} disabled={busy || reason.trim().length < 3}>
          Flag Version
        </Button>
      </div>
    </section>
  );
}

