FROM node:24.9.0-bookworm-slim@sha256:3e69116c924bfcba6c6979aff60d966c37aef56d488ce091c69d442ebec9f103 AS node
FROM python:3.13.5-slim-bookworm@sha256:4c2cf9917bd1cbacc5e9b07320025bdb7cdf2df7b0ceaccb55e9dd7e30987419
RUN apt-get update && apt-get install -y --no-install-recommends libstdc++6 && rm -rf /var/lib/apt/lists/*
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules/npm /usr/local/lib/node_modules/npm
RUN ln -s /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm
WORKDIR /app
COPY backend/requirements.lock backend/requirements.lock
RUN pip install --no-cache-dir -r backend/requirements.lock
COPY agent/package.json agent/package-lock.json agent/
RUN npm ci --prefix agent --ignore-scripts --no-audit --no-fund
COPY backend backend
COPY eval eval
COPY agent/retrieval.ts agent/fixture.json agent/
COPY agent/conversation.ts agent/provider_policy.ts agent/
COPY agent/conversation_policy.ts agent/test_conversation_policy.ts agent/
COPY agent/essay.ts agent/application_advice.ts agent/
COPY agent/essay_format.ts agent/test_essay_format.ts agent/
COPY agent/skills/ship30 agent/skills/ship30
RUN useradd --uid 10001 --create-home evaluator && mkdir -p /app/evidence/private-chat && chown -R evaluator:evaluator /app/evidence && chmod 700 /app/evidence/private-chat
USER evaluator
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PI_TELEMETRY=0 PI_OFFLINE=1
EXPOSE 8000
CMD ["sh", "-c", "python -m backend.migrate && exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --no-access-log"]
