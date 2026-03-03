# Operations Runbook

## Daily pipeline
- Cron runs ingestion.
- Pending versions created for changed content.
- FAISS index refreshed for approved chunks.
- Snapshot persisted locally and optionally to GCS.

## Alert policy
Alert on:
- Crawl failures > threshold.
- Validation mismatch spikes.
- No successful crawl in 24h.
- Stale scheme data.
- FAISS snapshot load/save failures.

## Incident checks
1. Check `/health/ready` and `/metrics`.
2. Inspect `audit_logs` and `crawl_jobs`.
3. Verify host allowlist.
4. Validate OpenAI/Firebase/GCP credentials.
5. Trigger manual crawl from admin dashboard.

