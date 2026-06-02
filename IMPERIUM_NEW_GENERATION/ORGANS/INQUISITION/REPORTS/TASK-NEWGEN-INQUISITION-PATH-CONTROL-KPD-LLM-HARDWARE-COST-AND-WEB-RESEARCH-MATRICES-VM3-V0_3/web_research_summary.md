# Web Research Summary

    Accessed UTC: `2026-06-02T20:17:31Z`

    ## Findings

    1. Cost control starts with fewer requests, smaller routed models, and async/batch lanes for low-priority work.
    2. Repeated static prefixes should be kept identical and early in the prompt to exploit prompt/context/KV caching.
    3. Output tokens are a direct latency and cost driver; short final answers are legitimate only when detailed evidence is retained elsewhere.
    4. Structured outputs reduce malformed receipt retries and make validator-first workflows cheaper.
    5. Token estimates are useful preflight signals, but provider usage metadata is stronger evidence.
    6. RAG/indexing cost must account for build-time calls, query-time calls, chunking/top-k choices, and synthesis.
    7. Agent cost must include non-LLM work: retrieval, tool calls, local validators, SSH transfer, bundle construction, and manual Owner steps.
    8. Long context is not automatically good context; relevance placement and focused manifests matter.
    9. Observability platforms converge on trace-level cost attribution, which maps well to IMPERIUM organ-agent receipts.
    10. AI FinOps governance should tie spend to value and KPIs, not only to cheaper model usage.

    ## Direct IMPERIUM Applications

    - Add a task-start cost budget: expected context size, max output size, validator count, transfer size, and stop threshold.
    - Add static-prefix/dynamic-suffix manifests to every LLM context pack.
    - Add a cost ledger with LLM, retrieval, tool, local runtime, transfer, artifact retention, and Owner labor rows.
    - Run validators before expensive reasoning and reject evidence-loss "savings".
    - Use exact source-quality receipts for web research.

    ## Source Index

    - `SRC-001` OpenAI API cost optimization - https://developers.openai.com/api/docs/guides/cost-optimization
- `SRC-002` OpenAI prompt caching - https://developers.openai.com/api/docs/guides/prompt-caching
- `SRC-003` OpenAI latency optimization - https://developers.openai.com/api/docs/guides/latency-optimization
- `SRC-004` OpenAI Structured Outputs - https://developers.openai.com/api/docs/guides/structured-outputs
- `SRC-005` OpenAI token counting with tiktoken - https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
- `SRC-006` Anthropic Claude pricing and tool costs - https://platform.claude.com/docs/en/about-claude/pricing
- `SRC-007` Anthropic prompt caching - https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- `SRC-008` Google Vertex AI context caching overview - https://docs.cloud.google.com/vertex-ai/generative-ai/docs/context-cache/context-cache-overview
- `SRC-009` Amazon Bedrock prompt caching - https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-caching.html
- `SRC-010` LangSmith cost tracking - https://docs.langchain.com/langsmith/cost-tracking
- `SRC-011` Langfuse token and cost tracking - https://langfuse.com/docs/observability/features/token-and-cost-tracking
- `SRC-012` LlamaIndex cost analysis - https://developers.llamaindex.ai/python/framework/understanding/evaluating/cost_analysis/
- `SRC-013` vLLM Automatic Prefix Caching - https://docs.vllm.ai/en/v0.15.0/features/automatic_prefix_caching/
- `SRC-014` FinOps for AI - https://www.finops.org/framework/technology-categories/ai/
- `SRC-015` Lost in the Middle: How Language Models Use Long Contexts - https://arxiv.org/abs/2307.03172
- `SRC-016` LiteLLM getting started and proxy cost controls - https://docs.litellm.ai/
