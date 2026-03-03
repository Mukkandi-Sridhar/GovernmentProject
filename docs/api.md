# API Guide

## Public
- `POST /api/v1/chat/query`
  - Request: `query`, `language` (`en`|`te`), `conversation_id`.
  - Response (existing): `answer_text`, `safe_failure`, `citations[]`, `structured_cards[]`, `unverified_fields[]`.
  - Response (optional additions): `intent`, `job_id`, `job_status`, `action_hint`.

- `GET /api/v1/schemes?status=approved|pending_review|flagged`
- `GET /api/v1/schemes/{scheme_id}`
- `GET /api/v1/schemes/{scheme_id}/versions`
- `GET /api/v1/schemes/{scheme_id}/versions/{version}/diff`
- `GET /api/v1/chat/jobs/{job_id}`

## Admin
Requires Firebase-authenticated token with `admin` or `reviewer` role.

- `POST /api/v1/admin/crawl/run`
- `POST /api/v1/admin/crawl/run-open-source`
- `GET /api/v1/admin/crawl/jobs`
- `POST /api/v1/admin/schemes/{scheme_id}/versions/{version}/approve`
- `POST /api/v1/admin/schemes/{scheme_id}/versions/{version}/flag`
- `POST /api/v1/admin/allowlist/hosts`
- `DELETE /api/v1/admin/allowlist/hosts/{host}`
- `GET /api/v1/admin/logs`
- `GET /api/v1/admin/anomalies`

