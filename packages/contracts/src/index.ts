import { z } from "zod";

export const SchemeStructuredDataSchema = z.object({
  scheme_name: z.string().nullable(),
  department: z.string().nullable(),
  year: z.string().nullable(),
  eligible_castes: z.array(z.string()).nullable(),
  income_limit: z.string().nullable(),
  education_levels: z.array(z.string()).nullable(),
  special_conditions: z.array(z.string()).nullable(),
  required_documents: z.array(z.string()).nullable(),
  application_deadline: z.string().nullable(),
  application_mode: z.string().nullable(),
  official_source_url: z.string().url().nullable(),
});

export const SchemeVersionSchema = z.object({
  scheme_id: z.string(),
  version: z.number().int().positive(),
  status: z.enum(["pending_review", "approved", "flagged"]),
  structured_data: SchemeStructuredDataSchema,
  source_url: z.string().url(),
  content_hash: z.string(),
  confidence: z.number().min(0).max(1),
  scraped_at: z.string(),
  last_verified: z.string(),
  previous_version: z.number().int().nullable(),
  field_diff: z.record(z.object({ from: z.any().nullable(), to: z.any().nullable() })),
});

export const CitationSchema = z.object({
  source_url: z.string().url(),
  scheme_id: z.string(),
  version: z.number().int().positive(),
  last_updated: z.string(),
  snippet: z.string(),
});

export const StructuredCardSchema = z.object({
  scheme_name: z.string(),
  department: z.string().nullable(),
  eligibility_summary: z.string().nullable(),
  income_limit: z.string().nullable(),
  deadline: z.string().nullable(),
  details_url: z.string().url(),
});

export const ChatQueryRequestSchema = z.object({
  query: z.string().min(1),
  language: z.enum(["en", "te"]),
  conversation_id: z.string().optional(),
});

export const ChatQueryResponseSchema = z.object({
  answer_text: z.string(),
  language: z.enum(["en", "te"]),
  safe_failure: z.boolean(),
  citations: z.array(CitationSchema),
  structured_cards: z.array(StructuredCardSchema),
  unverified_fields: z.array(z.string()),
  intent: z
    .enum(["greeting", "scheme_qa", "collect_latest", "out_of_scope", "ambiguous"])
    .nullable()
    .optional(),
  job_id: z.string().nullable().optional(),
  job_status: z.string().nullable().optional(),
  action_hint: z.string().nullable().optional(),
});

export const ChatJobStatusResponseSchema = z.object({
  job_id: z.string(),
  status: z.string(),
  progress_phase: z.string(),
  started_at: z.string(),
  ended_at: z.string().nullable().optional(),
  discovered: z.number(),
  updated: z.number(),
  failed: z.number(),
  error: z.string().nullable().optional(),
});

export type SchemeStructuredData = z.infer<typeof SchemeStructuredDataSchema>;
export type SchemeVersion = z.infer<typeof SchemeVersionSchema>;
export type ChatQueryRequest = z.infer<typeof ChatQueryRequestSchema>;
export type ChatQueryResponse = z.infer<typeof ChatQueryResponseSchema>;
export type ChatJobStatusResponse = z.infer<typeof ChatJobStatusResponseSchema>;

export const DEFAULT_SAFE_FAILURE_MESSAGE = "I could not find official confirmation from government sources.";

