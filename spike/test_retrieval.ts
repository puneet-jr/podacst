import assert from "node:assert/strict";
import test from "node:test";
import extension from "./retrieval.ts";

function setup() {
  let tool: any;
  let active: string[] = [];
  const events: Record<string, any> = {};
  const api = {
    registerTool: (value: any) => { tool = value; },
    on: (name: string, handler: any) => { events[name] = handler; },
    setActiveTools: (names: string[]) => { active = names; },
    getActiveTools: () => active,
  };
  extension(api as any);
  events.session_start();
  return { tool, events, active };
}

test("only a bounded query is exposed; deterministic read-only evidence", async () => {
  const { tool, active } = setup();
  assert.deepEqual(active, ["search_fixture"]);
  assert.deepEqual(Object.keys(tool.parameters.properties), ["query"]);
  assert.equal(tool.parameters.additionalProperties, false);
  assert.equal(tool.parameters.properties.query.maxLength, 160);
  const result = await tool.execute("id", { query: "retention review window evidence code" });
  assert.equal(result.details.source_id, "FIXTURE-B");
  assert.match(result.details.text, /17 days/);
});

test("invalid and ambiguous queries fail instead of returning invented evidence", async () => {
  for (const query of ["", "x".repeat(161), "arbitrary topic", "activation retention", "/etc/passwd"]) {
    const { tool } = setup();
    await assert.rejects(tool.execute("id", { query }));
  }
});

test("explicit fixture route anchors the query and rejects unsupported routes", () => {
  const { events } = setup();
  assert.match(events.before_agent_start({ prompt: "Question about retention" }).systemPrompt, /\{"query":"retention"\}/);
  assert.throws(() => events.before_agent_start({ prompt: "activation and retention" }), /one fixture topic/);
  assert.throws(() => events.before_agent_start({ prompt: "anything else" }), /one fixture topic/);
});

test("finite tool budget and cancellation", async () => {
  const { tool } = setup();
  await tool.execute("one", { query: "activation" });
  await tool.execute("two", { query: "retention" });
  await assert.rejects(tool.execute("three", { query: "activation" }), /budget/);
  const other = setup().tool;
  await assert.rejects(other.execute("cancel", { query: "activation" }, AbortSignal.abort()), /cancelled/);
});

test("local provider guard, tool policy and request budget", () => {
  const { events } = setup();
  assert.deepEqual(events.tool_call({ toolName: "bash" }), { block: true, reason: "tool not allowed" });
  const event = { payload: { tools: [{ function: { name: "search_fixture" } }] } };
  assert.throws(() => events.before_provider_request(event, { model: { provider: "cloud" } }), /local provider/);
  const ctx = { model: { provider: "ollama-local", id: "qwen3:0.6b", baseUrl: "http://127.0.0.1:11434/v1" } };
  const first = events.before_provider_request(event, ctx);
  assert.equal(first.max_tokens, 256);
  assert.equal(first.reasoning_effort, "none");
  assert.equal(first.tool_choice.function.name, "search_fixture");
  assert.equal(events.before_provider_request(event, ctx).tool_choice, "none");
  events.before_provider_request(event, ctx);
  assert.throws(() => events.before_provider_request(event, ctx), /budget/);
});
