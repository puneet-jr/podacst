import { readFileSync } from "node:fs";
import { Type } from "typebox";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

// A fixed read of our own reviewed fixture, never a model-supplied path.
const fixture = JSON.parse(readFileSync(new URL("./fixture.json", import.meta.url), "utf8"));
export default function (pi: ExtensionAPI) {
  let calls = 0;
  let requests = 0;
  pi.registerTool({
    name: "search_fixture",
    label: "Read synthetic evidence",
    description: "Search the synthetic evidence for the one experiment named by the user.",
    parameters: Type.Object({ query: Type.String({ description: "The experiment topic from the user's question", minLength: 1, maxLength: 160 }) }, { additionalProperties: false }),
    async execute(_id, args, signal) {
      if (signal?.aborted) throw new Error("cancelled");
      if (++calls > 2) throw new Error("fixture tool budget exhausted");
      if (typeof args.query !== "string" || args.query.length < 1 || args.query.length > 160) throw new Error("invalid query");
      const matches = [...new Set(args.query.toLowerCase().match(/\b(activation|retention)\b/g) ?? [])];
      if (matches.length !== 1) throw new Error("query must identify one supported fixture topic");
      const evidence = fixture[matches[0]];
      console.error(JSON.stringify({ event: "fixture_read", query: args.query, source_id: evidence.source_id }));
      return { content: [{ type: "text", text: JSON.stringify(evidence) }], details: evidence };
    },
  });
  pi.on("session_start", () => {
    calls = 0; requests = 0;
    pi.setActiveTools(["search_fixture"]);
    console.error(JSON.stringify({ event: "tool_policy", active: pi.getActiveTools() }));
  });
  pi.on("tool_call", event => {
    if (event.toolName !== "search_fixture") return { block: true, reason: "tool not allowed" };
  });
  pi.on("before_agent_start", event => {
    // A deliberately explicit two-topic route, not a general intent classifier.
    const topics = [...new Set((event.prompt ?? "").toLowerCase().match(/\b(activation|retention)\b/g) ?? [])];
    if (topics.length !== 1) throw new Error("request must name one fixture topic");
    return { systemPrompt: `First call search_fixture with exactly {"query":"${topics[0]}"}. After its result, report its review window and evidence code. /no_think` };
  });
  pi.on("before_provider_request", (event, ctx) => {
    if (ctx.model?.provider !== "ollama-local" || ctx.model?.baseUrl !== process.env.LENNY_OLLAMA_BASE_URL) throw new Error("local provider required");
    if (++requests > 3) throw new Error("provider request budget exhausted");
    const payload = event.payload as Record<string, unknown>;
    console.error(JSON.stringify({ event: "provider_request", provider: ctx.model.provider, model: ctx.model.id, request: requests, max_tokens: 256,
      tools: (payload.tools as any[])?.map(t => t.function?.name), tool_choice: requests === 1 ? "search_fixture" : "none" }));
    // The 0.6b model skipped optional tools in the recorded failed batch.
    // This spike is explicitly retrieval-first, not a proof of autonomous routing.
    return { ...payload, max_tokens: 256, temperature: 0, reasoning_effort: "none",
      tool_choice: requests === 1 ? { type: "function", function: { name: "search_fixture" } } : "none" };
  });
}
