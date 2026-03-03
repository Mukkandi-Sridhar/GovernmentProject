# Architecture

## Backend (FastAPI)
Modules:
- Crawler: host allowlist + sitemap + host-bounded traversal.
- Classifier: AI relevance classification for AP student welfare content.
- Structurer: deterministic extraction using `gpt-4o-mini` (temperature 0).
- Verifier: evidence matching; unsupported extracted fields are nullified.
- Versioning: immutable version docs + field-level diff.
- Embeddings: chunking (800/150), embedding (`text-embedding-3-small`), FAISS indexing.
  - Supports free Hugging Face inference embeddings (`BAAI/bge-m3`) via `EMBEDDING_PROVIDER=huggingface`.
- Retrieval + Chat: top-5 approved chunks, citation-first response, safe-failure fallback.
- Scheduler: daily ingestion + reindex + FAISS snapshot.

## Agent Orchestration (Feature-Flagged)
- `ENABLE_AGENT_ORCHESTRATION=false` (default): `POST /api/v1/chat/query` uses legacy direct `ChatService`.
- `ENABLE_AGENT_ORCHESTRATION=true`: request executes a LangGraph state machine.

Graph nodes:
1. `IntentRouterNode`
2. `GreetingAgentNode`
3. `ScopeGuardAgentNode`
4. `SchemeQAAgentNode`
5. `CollectLatestDataAgentNode`
6. `ResponseComposerNode`
7. `FailurePolicyNode`

State includes:
- `query`
- `language`
- `conversation_id`
- `intent`
- `retrieval_hits`
- `citations`
- `structured_cards`
- `job_id`
- `job_status`
- `safe_failure`
- `answer_text`
- `policy_flags`

Deterministic routing:
- `greeting -> GreetingAgentNode -> ResponseComposerNode`
- `out_of_scope -> ScopeGuardAgentNode -> ResponseComposerNode`
- `collect_latest -> CollectLatestDataAgentNode -> ResponseComposerNode`
- `scheme_qa -> SchemeQAAgentNode -> ResponseComposerNode`
- `ambiguous -> scheme_qa fallback`

Safety guarantees:
- Greeting and out-of-scope flows never call retrieval.
- Scheme QA retrieves `top_k=5` from FAISS and only uses admin-approved versions.
- No evidence returns exact refusal: `I could not find official confirmation from government sources.`
- Chat never uses unapproved scraped content.
- Collection intent enqueues a background crawl job and returns `job_id` immediately.
- Admin can trigger seeded open-source pull (`/api/v1/admin/crawl/run-open-source`) which:
  - Adds curated official public hosts to allowlist.
  - Runs ingestion crawl.
  - Rebuilds vectors for approved content using Hugging Face embeddings.

## Data model
Collections:
- `schemes`
- `embeddings`
- `conversations`
- `audit_logs`
- `crawl_jobs`
- `host_allowlist`

## Publish flow
1. Crawl allowlisted hosts.
2. AI classify.
3. Extract structured schema.
4. Verify evidence and null unsupported fields.
5. Hash and diff. If `content_hash` changed: full re-extract, field-by-field compare, immutable new version.
6. Write pending version.
7. Admin approves.
8. Embed + index approved version only.
9. Public chat retrieval includes only approved chunks.

