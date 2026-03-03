import { describe, expect, it } from "vitest";

import { ChatQueryRequestSchema } from "@ap-civic/contracts";

describe("contracts", () => {
  it("validates chat request payload", () => {
    const parsed = ChatQueryRequestSchema.parse({
      query: "Scholarship details",
      language: "en",
      conversation_id: "abc",
    });

    expect(parsed.language).toBe("en");
  });
});
