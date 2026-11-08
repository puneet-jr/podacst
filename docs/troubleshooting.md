# Operational troubleshooting

Use the visible request reference and saved session/run ID to correlate safe JSON events. Do not paste keys, full prompts, transcripts or raw RPC traces into reports. Refresh readiness and saved state before retrying; never switch provider automatically.

| Symptom | Diagnosis / recovery | This phase's evidence |
| --- | --- | --- |
| Selected cloud unavailable | `cloud_key_missing`: configure the key server-side or explicitly return to Ollama, then bootstrap/refresh. No writes/process start on key absence. | Actual isolated API503, UI fixture and recovery; cloud inference blocked |
| Ollama unavailable | Start the existing host daemon; verify container-to-host connectivity and readiness. On Linux check bridge bind/host-gateway. | Actual unreachable loopback target then recovery; normal daemon not stopped |
| Local model missing | Check `ollama list` against configured names; assess memory/disk before an authorized pull. No substitution/fallback. | Real tag check with deliberately absent configured name gives readiness503; restore config200 |
| Model timeout | Saved run `answer_timeout`/essay timeout; refresh, then bounded retry using the same saved question. Reduce scope/context or reassess hardware after measured failures. | Real mock subprocess timeout/reaping, bridge closure and same-ID retry; live local smoke separate |
| Empty corpus/evidence | Counts/status are empty; ingest/refresh the correct pinned corpus, or narrow to a supported question. Do not treat nearby matches as proof. | Actual isolated corpus state and recovery; existing empty-answer contracts |
| PostgreSQL unavailable | Liveness remains200, readiness/API503 `database_unavailable`; restore the configured DB connection, preserve volumes, refresh/retry. | Real refused test endpoint and recovered SQL request; normal DB never stopped |
| Embedding/index mismatch | Configured model/digest/dimensions must match stored identity. Restore correct config or plan an explicit re-index. Never rename vectors to suppress mismatch. | Actual model dimension check, retrieval identity tests and recovery |
| Interrupted stream/cancel | Refresh the saved run before retrying. Same request identity prevents duplicate messages. | Actual stream-generator disconnect and cancel with real mock process/bridge cleanup; UI fixture states separate |
| Malformed/oversized artifact | Safe422 `artifact_too_large`, correlated rendering code. Restore/recreate from the owned accepted reply; arbitrary new HTML remains sanitized/isolated. | Actual isolated stored-artifact mutation/recovery and existing hostile renderer/browser tests |
| Bootstrap fails | Check Docker/Compose and port ownership, safe `.env` validation and available disk. Do not print resolved secret configuration. | Warm existing-stack rehearsal6.60s, `.env`/corpus preserved; cold clone/other OS unverified |

Nonfatal psycopg ResourceWarnings occurred at contract-process shutdown; passing assertions do not prove all teardown warnings resolved. Production engine disposal is in app lifespan, and model-process/bridge cleanup has explicit tests. Report repeatable leaks instead of suppressing warnings.

Current Git publication deliberately excludes earlier runtime prerequisites: the full local tree works, but origin/main alone is incomplete. Obtain explicit publication authorization before changing that scope. One public cited OpenRouter smoke passed after removing follow-up JSON response mode alongside tool history; see phase-09-openrouter-diagnosis.md. Keep all keys configured out of band; never send them through chat.
