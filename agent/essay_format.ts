// Plain drafting must omit the grammar parameters entirely, not request JSON/text grammar.
export function plainMarkdownPayload(payload:Record<string,unknown>){
  const result={...payload,tool_choice:'none'};
  delete result.response_format;delete result.grammar;delete result.format;
  return result;
}
