TECH_STACK_FINAL.md

Universal Digital Employee (UDE) v3.0 — Полный производственный стек (FINAL)

Назначение.
Единственный источник правды для всех технических решений в проекте universal-digital-employee. QWEN и люди обязаны сверяться с этим документом перед выбором технологий, генерацией кода, конфигураций, созданием ADR/RFC, развертыванием и изменениями инфраструктуры.

Ключевое правило: этот файл — первичный источник по версиям, ролям компонентов, fallback-стратегиям, требованиям безопасности, SLO/SLA, strategy выбора LLM. Любое отклонение требует ADR + тестирования + одобрения владельцев.

Содержание (быстрый обзор)

Резюме ролей моделей (hosted vs local)

Языки и рантаймы, критические версии

RPC / API / контракты

Архитектурные парадигмы (microservices, orchestrator, event-driven, CQRS)

Сеть, API Gateway, Service Mesh, безопасность сетевого уровня

AuthN/AuthZ, секреты, KMS/Vault

Очереди и поток событий (Kafka, Debezium, Outbox)

Базы данных и хранилища (Postgres, ClickHouse, Weaviate, S3 и пр.)

ML / LLM / RAG — detailed policies и flow

Model selection policies, traceability, audit & governance

Observability & SRE (metrics, logs, tracing, SLOs)

DevOps, Infra-as-Code, GitOps, CI/CD, SBOM

Data governance, DLP, compliance (GDPR, etc.)

Security (runtime, container, infra)

DR / Backup / RTO-RPO

Cost management, token budgets, throttling + reports

Testing matrix (unit, integration, contract, e2e, synthetic, chaos)

Release & rollout strategies (canary, feature-flag, blue/green)

Operational policies (runbooks, maintenance, support tiers)

Governance: ADRs, RFCs, CHANGELOG, CODEOWNERS

Templates & snippets (model selection policy, ADR template, model card, PR checklist, prompt templates, commands)

Appendix: Hardware, capacity, glossary, contacts

0. Резюме (decisioning & models — кратко)

Primary decision engine (production, high-stakes user-facing): Hosted GPT-family (OpenAI — конкретные модели фиксируются в ml_config.yaml / require security approval). Hosted модели — источник финальных ответов для продаж/возражений/финансовых/юридических/безопасных сценариев.

Secondary / On-prem / Cost-optimized: Llama, Mistral, CodeLlama и т.п. (развёрнутые через vLLM/Triton/KServe). Используются как черновики, для приватных workloads, dev sandboxes, оффлайн inference. Не использовать локальные модели как единственный источник истины для high-stakes решений.

Embeddings primary: OpenAI text-embedding-3-small. Fallback: sentence-transformers/all-MiniLM-L6-v2.

Политика: hybrid flows, traceability, confidence scoring, human-in-the-loop при low confidence или policy violations.

1. ЯЗЫКИ, рантаймы и версии (фиксированные)

Python

Версия: 3.11.7+ (фиксировать minor/patch в infra manifests).

Основные фреймворки:

FastAPI 0.110.0+

Pydantic v2.5+

SQLAlchemy 2.0.25+

Alembic 1.13.0+

Celery 5.3.6+ (legacy compatibility only)

Критические библиотеки: numpy 1.24.3+, pandas 2.1.4+, scikit-learn 1.3.2+, openai 1.3.0+, httpx 0.26.0+, redis 5.0.1+, kafka-python 2.0.2+.

Go

Версия: 1.21.5+.

Использование: event router, auth proxy, high-throughput consumers, gRPC latency-critical.

Библиотеки: Gin 1.9.1+, gRPC-Go 1.59.0+, Sarama 1.42.1+, GORM 1.25.5+, Viper 1.18.1+.

Node/JS/TS (для UI/админки)

Node 20+. ESLint + Prettier, TypeScript где применимо.

Docker / Kubernetes

Docker client / engine: latest stable. Images: multi-stage builds, minimal base (distroless / slim).

K8s: 1.28+ recommended per cloud provider support matrices.

その他

Terraform 1.6+, Terragrunt 0.54+, ArgoCD 2.9+, Prometheus 2.47+, Grafana 9+, Jaeger/OpenTelemetry 1.0+.

2. RPC / API / контракты

gRPC / Protobuf v3 — internal high-throughput / model-serving / vector-proxy paths. HTTP/2 + mTLS обязательны для всех internal gRPC каналов. Protobuf schema versioning practice required.

REST / OpenAPI 3.1 — public APIs (90% сервисов). Use OpenAPI generator, automatic docs generation from FastAPI + pydantic models. HATEOAS for public APIs where fits. Semantic versioning in path /v1/, /v2/.

Contract testing & Consumer-driven contracts: обязательны; schema changes require contract tests and CI gating.

3. Архитектура и парадигмы

Microservice-first

1 бизнес-модуль = 1 K8s Deployment (stateless)

1 технический модуль (DB-backed stateful) = StatefulSet (если требуется)

Stateless-first design, sidecars only where necessary

Orchestrator pattern

Stateless Saga Orchestrator (Kafka-driven) — no central orchestration DB; compensation actions for eventual consistency; timeout management with automatic compensation.

Event-Driven

Event sourcing for domain state changes (where applicable). Event replay, event versioning with migration plans and snapshots for large aggregates.

CQRS

Separate write/read models, materialized views for complex read queries, read-replicas for heavy analytics.

Multi-tenancy

Tenant_id mandatory in schemas and requests. PostgreSQL RLS enforced. Network isolation and resource quotas per tenant.

4. Сеть, Service Mesh, API Gateway, Load Balancing

Service Mesh

Istio 1.21+ recommended. Functions: mTLS, traffic control, retries, circuit breakers, fault injection, observability.

API Gateway

Kong Enterprise 3.4+ or equivalent: JWT verification, rate-limiting (1-minute windows), request/response transformations, bot detection, DDoS mitigation.

Load balancing

L7 via Kong, L4 via k8s Services + Istio. Custom healthchecks endpoints; circuit breaker patterns applied.

5. Аутентификация и авторизация

AuthN: Keycloak 22.0+

OAuth2/OIDC, SAML2, social logins, MFA (TOTP/WebAuthn), session management, brute-force protection.

AuthZ: OPA 0.60+ (Rego)

RBAC + ABAC hybrid. Resource-based permissions, temporal/location-based constraints. Policies versioned and stored in repo.

Secrets Management: HashiCorp Vault 1.15+

KV v2 for static secrets, DB secrets engine for dynamic credentials, PKI and Transit for encryption. Root keys via cloud KMS (AWS/GCP).

Key rotation: automate rotation schedules (e.g., monthly keys, shorter for high-risk credentials).

6. События и очереди

Event Bus: Apache Kafka (Confluent Cloud / AWS MSK), Kafka 3.5+

Topics: retention 30 days, compression zstd, replication factor 3. Schema Registry (Confluent) with Avro/JSON Schema compatibility set to BACKWARD. Versioning via semantic version.

Consumer group config: cooperative-sticky rebalancing, session timeout 45s, heartbeat 3s.

Dead Letter Queues: automatic DLQ after 3 retries, alerting + admin UI for reprocessing.

CDC & Outbox: Debezium 2.4+, Outbox pattern in Postgres with transactional guarantees for event delivery and exactly-once semantics when possible.

Caches: Redis 7.2+ cluster for sessions (RedisJSON), rate-limiting (RedisCell), distributed locks (Redlock), pub/sub notifications. Persistence via AOF every second + hourly RDB snapshots.

7. Хранилища данных

Primary OLTP: PostgreSQL 15+

RLS enforced, logical replication for CDC, PgBouncer for pooling, read replicas for heavy queries, partitioning. Extensions: pgvector 0.5.0+, postgis 3.3+, pg_cron 1.5+, timescaledb 2.11+ for timeseries.

OLAP: ClickHouse 23.8+

MergeTree, materialized views, replication for analytics.

Timeseries: TimescaleDB 2.11+ for metrics and forecast snapshots.

Vector DB (Primary): Weaviate 1.23+

Multi-tenant indices, hybrid ranking, daily snapshots, automatic sharding. Modules: text2vec-openai, qna-openai, generative-openai. Fallbacks: Qdrant 1.7.0+, pgvector (emergency). Use vector abstraction layer for switching.

Object Storage: AWS S3 primary (versioning enabled, SSE encryption). Lifecycle policies: move to Glacier after 90 days, delete after 7 years. Secondary: Cloudflare R2 for CDN/cost-optimization.

8. ML / LLM / RAG (детально)
8.1 Роли моделей (policy)

Production decisioning (customer-facing, high-stakes): Hosted GPT-family (OpenAI). Final answers must pass hosted validation before delivery.

Local/on-prem (private, cost): Llama/Mistral/CodeLlama via vLLM/Triton/KServe for offline, sandbox, tenant-isolated workloads. Must not directly reply for critical flows without hosted validation/human approval.

Embeddings: OpenAI text-embedding-3-small primary; fallback to sentence-transformers.

Hybrid: local quick draft → hosted validation OR hosted draft → local re-ranker for business rules.

8.2 Model serving & infra

Hosted: vendor APIs wrapped by gateway; auditing, token budgeting, retries, rate limiting.

On-prem: vLLM 0.3.0+ for Llama/Mistral, Triton for other frameworks. Use GPU instances: NVIDIA A100/H100 recommended for large models; memory/throughput sizing per model. Use continuous batching, tensor parallelism where needed.

KServe: SKLearn, XGBoost, PyTorch serving with canary deployment support.

Feature store: Feast 0.31+ — online + offline feature serving with point-in-time correctness.

Experiment tracking: MLflow 2.9+.

Monitoring: Evidently AI, Arize AI for model performance & drift.

8.3 RAG orchestration

Hybrid retrieval (semantic + keyword), re-ranking with cross-encoders, citation + source tracking mandatory for factual claims. Context window optimization and chunking per pipeline config.

8.4 Embeddings pipeline & vector ops

Chunking max window 512 tokens (configurable). Metadata schema: source_path, source_type, created_at, tenant_id, sensitivity_level. Quality scoring + reindexing workflows with cost estimates. Retention defaults: sensitive data ≤ 90 days unless tenant policy stricter.

8.5 Safety & hallucination mitigation

Redact PII before embedding. Cross-check factual claims against canonical sources (DBs, knowledge base). OPA policy evaluation on outputs. Confidence thresholds; human-in-the-loop gating on low-confidence.

9. Model selection, traceability, auditing

Model selection config stored in ml_config.yaml and enforced by QWEN. Example snippet in Templates section.

Traceability: every model call logs: model_type, model_id, model_version, prompt_hash, prompt_snippet (truncated), token_usage, latency, correlation_id, tenant_id, user_id (if consent), decision_rationale_id, confidence_score. Store prompt hashes + metadata by default; full prompt storage requires data residency and consent checks.

Audit: immutable append-only audit logs for model decisions kept per compliance rules.

10. Observability, logging, tracing, SLOs

Metrics: Prometheus 2.47+ — scrape 15s, retention 30d. Business & technical metrics defined per service.
Logging: Grafana Loki 2.9+ — structured JSON logs; retention 90d; mandatory fields: tenant_id, user_id, correlation_id, service_name, timestamp.
Tracing: OpenTelemetry 1.0+ → Jaeger for traces. Sampling: head-based 10% prod, tail-based 100% for errors.
Alerting: Alertmanager 0.25+ — PagerDuty for critical, Slack for warnings.
SLOs: Availability 99.9% (primary services), latency p95 < 800ms (where applicable), freshness < 5 minutes for real-time data. Error budgets, auto-remediation triggers.
Synthetic & canary tests: e2e synthetic users and smoke tests in CI/CD pipeline.

11. DevOps, IaC, GitOps, CI/CD

IaC: Terraform 1.6+ modules with remote state (S3/GCS) and state locking (DynamoDB). Terragrunt for env management.
Kubernetes: EKS/GKE/AKS 1.28+, use Cilium 1.14+ for CNI/eBPF. Use spot+on-demand mix for cost efficiency. Velero for backups.
GitOps: ArgoCD 2.9+ with ApplicationSets for auto-discovery and multi-cluster deployments.
CI/CD: GitHub Actions / GitLab CI. Stages: build, unit test, integration, security scans, sbom generation, deploy (ArgoCD). Tools in pipeline: Trivy/Snyk (SCA), OWASP ZAP (security), Syft (SBOM).
Artifacts: SBOM, vulnerability reports, test coverage artefacts.
Pre-commit: black, isort, ruff, mypy/pyright configured.

12. Security & Compliance

Runtime security: Falco 0.36+ rules for privilege escalation, FS anomalies. Container image scanning with Trivy, runtime protection with Falco, network policies with Cilium.
Audit & Compliance: immutable audit trails, append-only storage for critical logs. GDPR: right-to-forget, portability. Data Processing Agreements and DPO workflow integration. SOC2 / ISO controls to be followed per enterprise requirements.
Secrets: always via Vault; no secrets in repo; enforce git-secrets scanning; CI SAST/SCA to run on PR.
DLP: Microsoft Presidio for PII detection; redaction before embedding.
Access control: least privilege, regular access reviews, MFA enabled, session timeout 15 minutes.

13. Data governance & quality

Quality tools: Great Expectations 0.18+, Soda Core 3.0+. Expectations: freshness, schema validation, statistical distributions, referential integrity. Quarantine bad data; automated remediation where safe.
Schema governance: Confluent Schema Registry (default backward compatibility), schema migrations via Alembic (Postgres) and custom migrator for vector DBs. Zero-downtime migrations emphasized.
Retention policies: policy-based, automated archiving, secure deletion and audit trails.

14. Disaster Recovery & Backups

Postgres: PITR, logical backups daily, WAL archiving, cross-region replication.
Kafka: topic replication across AZs, consumer offset tracking, schema registry backups.
VectorDB: Weaviate daily snapshots, metadata exports, index rebuild playbooks.
RTO/RPO: Critical services RTO < 15 min, RPO < 5 min. Standard services RTO < 1 h, RPO < 15 min. Batch RTO < 4 h, RPO < 1 h. Quarterly DR drills & automated recovery verification.

15. Cost management & ML cost controls

Token budgets per tenant, auto-throttling and fallback to cheaper models on overuse. Real-time spending dashboards and budget alerts (80%, 100%, 120%). Resource tagging for cost allocation. Spot instances for batch, reserved instances for stable production. Idle resource detection & right-sizing recommendations.

16. Testing & quality gates

Unit tests: pytest, coverage.
Integration tests: docker-compose lightweight stacks or testcontainers (Postgres, Redis, Kafka).
Contract tests: consumer-driven tests for OpenAPI/AsyncAPI/Protobuf.
E2E & synthetic: simulate user journeys.
Performance: load testing (k6/jmeter), performance baselines and regression.
Security tests: SAST/SCA/DAST in pipeline.
Model quality tests: hallucination rate, relevance, precision/recall where applicable; human-in-the-loop review for 1% of outputs or 200 samples monthly.

17. Release & rollout strategies

Default: feature flag + canary rollout.

Critical infra changes: blue/green only if necessary.

DB migrations: staging -> canary -> full; reversible migrations mandatory.

Model rollouts: ADR + A/B testing on small % traffic; monitor hallucination and accuracy metrics.

18. Operational policies & runbooks

Runbooks stored in docs/runbooks/ with triage steps, mitigation, owners, timelines.

Incident response: page owners, runbook, postmortem with RCA.

Maintenance windows announced 2 weeks prior for scheduled downtime.

19. Governance (ADRs, RFCs, CODEOWNERS)

All architectural changes: ADRs under docs/ADRs/ with status, motivation, alternatives, decision, rollback.

RFCs for large initiatives in docs/RFCs/.

CODEOWNERS defines module owners. QWEN must tag relevant owners on PRs.

20. Templates, snippets и обязательные артефакты
20.1 Model selection policy (YAML snippet)
model_selection:
  rules:
    - when:
        sensitivity: high
        tenant_residency: eu_only
      use: on_prem
    - when:
        sensitivity: high
        tenant_residency: not_eu
      use: hosted
    - when:
        task_type: low_cost_batch
      use: local_fallback
  default: hosted

20.2 PR checklist (обязательный — вставлять в PR body)

 Описание + acceptance criteria

 Ссылка на используемые разделы TECH_STACK_FINAL.md

 Unit tests + coverage (>=80% for new code)

 Integration/contract tests (if API changed)

 Lint/format/typecheck passed (pre-commit hooks)

 Security scan (SCA/SAST) passed or remediation plan

 No secrets (use {{VAULT://...}} placeholders)

 Migrations reversible + deployment plan described

 Cost estimate if ML/infra impacted (token budgets, fallback)

 Owners assigned and relevant teams tagged

20.3 ADR template (short)

Title, Status, Context, Decision, Consequences, Alternatives, Rollback plan, Date, Authors.

20.4 Model Card template (ML)

Model name, version, trainer, dataset summary, metrics (accuracy, latency), intended uses, limitations, privacy considerations, Fallback models, Audit logs location.

20.5 Prompt templates (global)

select-model-prompt: ask QWEN to evaluate sensitivity/ residency/latency and pick model per policy.

decision-rationale-prompt: produce short rationale (3–5 bullets) for logging.

hosted-validation-prompt: validate a draft (from local) against hosted model and produce final content OR reasons to escalate.

20.6 Commands / CLI (examples)

generate-from-template --module catalog-service --model fastapi

validate-module-structure --path modules/catalog-inventory/product-catalog

ai-development-helper.py --task-file tasks/create_catalog.json

21. Security toolchain & scans

Container/image scanning: Trivy

Dependency SCA: Snyk / GitHub Dependabot

Static analysis: ruff/flake8, mypy/pyright, golangci-lint

Secrets scanning: git-secrets + pre-commit hooks

DAST: OWASP ZAP (periodic scans)

SBOM generation: Syft during build stage

22. Hardware & capacity guidance (ML & infra)

GPU: NVIDIA A100 / H100 for large models; V100/T4 for smaller tasks. Use GPU autoscaling and batch inference to optimize cost.

vLLM: tuned for A100/H100; ensure NVLINK & sufficient host RAM (2–3x model size).

Storage: high IOPS for DBs; object storage for models (S3).

Networking: 25–100 Gbps in model-serving clusters for high throughput.

23. Vector DB operational procedures

Daily snapshots for Weaviate; weekly test restores.

Reindexing procedure with cost estimates — require confirmation on large reindex jobs.

Metadata exports for offline audits.

Index rebuild playbooks for emergency.

24. Data residency & privacy rules

EU-only tenants: do not send raw PII to third-party hosted vendors. Use on-premise models or pseudonymization. Data residency flags live in tenant metadata and enforced at infra/config layer. All flows must check tenant policy before sending data externally.

25. Fallback chain & offline policies

Hosted primary (OpenAI)

Local fallback (vLLM Llama/Mistral)

Rule-based templates (deterministic)

Human escalation queue

When switching to fallback due to vendor outage, show banner and log fallback_mode=true with escalation flag.

26. Human-in-the-loop & escalation

Auto-escalate when: policy violation, low confidence, sensitive operation, payment or data deletion actions. L2/L3 on-call teams defined in governance/ and must be notified by PagerDuty.

27. Compliance & audits

Maintain audit trails for model decisions and data flows. Regular compliance checks and evidence in evidence/ directory (terraform plans, backups, security scans). Maintain DPIAs and DSAR processes.

28. Change process & versioning

Changes to TECH_STACK_FINAL.md require RFC + approval by architecture committee. Version bump and changelog entry mandatory. Use semver for modules where applicable.

29. Appendix A — Example model_call log schema (JSON)
{
  "timestamp": "2025-10-30T12:34:56Z",
  "correlation_id": "req-12345",
  "tenant_id": "tenant-xyz",
  "user_id": "user-abc",
  "service": "faq-service",
  "model": {
    "type": "hosted",
    "provider": "openai",
    "model_id": "gpt-5-thinking-mini",
    "version": "2025-10-01"
  },
  "prompt_hash": "sha256:...",
  "prompt_truncated": "System: ... User: ...",
  "token_usage": {"prompt": 120, "completion": 80, "total": 200},
  "latency_ms": 320,
  "confidence_score": 0.87,
  "decision_rationale_id": "dr-456",
  "escalated": false
}

30. Appendix B — PR шаблон (содержимое .github/PULL_REQUEST_TEMPLATE.md)

(см. prompts/ и .github/ — шаблон включает обязательный PR checklist, model metadata fields)

31. Appendix C — Model selection policy (full)

(см. ml_config.yaml в repo — держать в sync с этим документом; любые изменения — через ADR).

32. Appendix D — Model evaluation & metrics

Offline benchmarks: accuracy, F1, latency, throughput, memory footprint, token cost per request.

Online metrics: hallucination rate, rollback rate, human escalation rate, user satisfaction, conversion uplift (for sales flows).

Minimum acceptance before production: offline benchmarks + canary A/B with metrics within delta threshold.

33. Appendix E — Glossary (коротко)

Hosted — модель у вендора (OpenAI).

Local — модель развёрнут на вашей infra (vLLM/Triton).

RAG — retrieval-augmented generation.

vLLM — high-performance LLM serving.

SLO/SLI — service-level objectives/indicators.

PII — personally identifiable information.

34. Contacts и владельцы

Архитектура / CODEOWNERS: docs/governance/CODEOWNERS

Security owner: указан в SECURITY_POLICY.md

ML owner: ml-governance (см. modules/analytics-ml/ml-governance/)
(Добавить реальные контакты в production repo)

35. Последовательность при столкновении с несогласованностью

Свериться с TECH_STACK_FINAL.md.

Если конфликт — открыть ADR с 3 вариантами + рекомендованным выбором + rollback планом.

Если security-related — требовать human-approval от security OWNER.

36. Примеры быстрых действий (QWEN обязан)

Перед генерацией: QWEN -> validate model_selection(policy) -> log selection -> produce plan (3–6 шагов) -> generate scaffolding -> create tests -> open PR w/ model metadata & links to TECH_STACK_FINAL.md.

При отклонении стека: QWEN -> generate ADR template -> attach cost delta & benchmarks -> create RFC.

37. Closing notes (обязательные)

QWEN обязан ссылаться на конкретный раздел TECH_STACK_FINAL.md в каждом PR/ADR, который зависит от стека.

Любая автоматизация, которая меняет этот документ (или версии внутри него), должна проходить ревью архитектуры и governance workflow.

Этот документ считается живым — обновления через RFC/ADR, но пока изменения не задокументированы — использовать текущую версию.

38. Change log (place for edits)

Версии и изменения должны попадать в CHANGELOG.md в репо, с указанием причин и файлов impacted.

39. Дополнения, которые могут быть добавлены позже (TODO)

Полный matrix hardware cost per region / example cost estimation for model serving at X qps.

Полные policy snippets OPA/Rego для model selection & output filtering.

Predefined benchmark suites + synthetic datasets для каждлого сервиса.

## Quantum Compute Integration
- **Quantum Backend**: IBM Quantum, AWS Braket, Azure Quantum (vendor-agnostic abstraction)
- **Billing Unit**: `QUANTUM_COMPUTE_SECONDS` tracked per tenant in `tenant_budgets`
- **Cost Controls**: real-time throttling, fallback to classical when budget exceeded
- **Hardware Registry**: dynamic catalog of available quantum processors with fidelity, qubit count, calibration status
- **Validation**: statistical significance testing for quantum advantage (classical vs quantum runtime)
- **Fallback**: classical algorithms must be available for all quantum workloads
