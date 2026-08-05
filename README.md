[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![Docs](https://img.shields.io/badge/docs-README-blueviolet)](#readme)

# AI Code Engineer Agent
Professional, extensible multi-agent system for automated code editing, validation, and PR generation.

This README has been tailored for the Paritok Token Efficiency Hackathon. It preserves verified project facts from the codebase and adds the mandatory hackathon sections and guidance — without adding unsupported features or metrics.

Table of contents
- About
- Quick demo
- Key features
- Paritok — meaningful role & integration
- Architecture (high level)
- Screenshots & demo assets
- Setup (local)
- Environment variables (reference)
- Running (API, Streamlit, script)
- Benchmarks (how-to)
- Contributing & Code of Conduct
- Hackathon submission checklist
- License


About
-----
This repository contains an autonomous agent pipeline that:
- clones or updates a target repository
- extracts and indexes code blocks
- retrieves relevant code for a natural-language engineering prompt
- plans edits, generates patches, validates/executes changes, and can create GitHub commits/PRs

The implementation builds on:
- FastAPI backend with REST endpoints and WebSocket log streaming ([api/server.py](E:/repoagent.worktrees/update-readme-for-hackathon-requirements/api/server.py))
- A Streamlit control UI ([app.py](E:/repoagent.worktrees/update-readme-for-hackathon-requirements/app.py))
- A LangGraph-orchestrated workflow defined in [orchestrator/workflow.py](E:/repoagent.worktrees/update-readme-for-hackathon-requirements/orchestrator/workflow.py)
- A provider-routing layer at [utils/model_router.py](E:/repoagent.worktrees/update-readme-for-hackathon-requirements/utils/model_router.py)

This README does not claim support for providers or features not present in the code — it documents what exists and provides clear, non-invasive guidance for adding Paritok integration for the hackathon.

Quick demo
----------
Video demo (as included in repository):
(https://youtu.be/SSbz5QrGDWQ)

Screenshots
-----------
Placeholders for images are included below — add image files to the listed paths and they will render in the project documentation/UI.

- Architecture diagram (recommended): assets/architecture.png
- Streamlit run view: assets/streamlit-run.png
- API / logs view: assets/api-logs.png

Architecture (high level)
-------------------------
A concise diagram of the core pipeline:

[API / UI] -> [Orchestrator (LangGraph)] -> [Agents: Retriever, Planner, Editor, Validator, Tester] -> [Executor / Debugger] -> [GitHub Integration]

Key components and locations
- API server: [api/server.py](E:/repoagent.worktrees/update-readme-for-hackathon-requirements/api/server.py)
- Orchestrator/workflow: [orchestrator/workflow.py](E:/repoagent.worktrees/update-readme-for-hackathon-requirements/orchestrator/workflow.py)
- Streamlit UI: [app.py](E:/repoagent.worktrees/update-readme-for-hackathon-requirements/app.py)
- Model routing: [utils/model_router.py](E:/repoagent.worktrees/update-readme-for-hackathon-requirements/utils/model_router.py)
- RAG/indexing: [rag/repo_indexer.py](E:/repoagent.worktrees/update-readme-for-hackathon-requirements/rag/repo_indexer.py)

Key features (what is implemented)
- Repository cloning and refresh
- AST-based extraction + embedding indexing for retrieval
- Retrieval + reranking of relevant code blocks
- Planner that produces structured JSON plans (supports explain-only mode)
- Editor that produces file patches and applies them to the working copy
- Validator/Executor to run/compile and collect failure diagnostics
- Tester that can scaffold/run pytest-based tests
- Optional commit/push/PR automation under `github/`

Paritok — meaningful role & integration
--------------------------------------
Built with Paritok: This submission is being prepared for the Paritok Token Efficiency Hackathon and includes a clear plan for integrating Paritok as a meaningful, cost-sensitive provider.

What "meaningful integration" means here (non-invasive, verifiable):
- Use Paritok as one of the LLM providers in the provider routing layer so the planner/coder/debugger stages can use Paritok models.
- Use token usage and response-size controls to leverage Paritok's token-efficiency features for cost-sensitive stages (for example: planning and reranking use smaller models; code generation uses larger models only when needed).
- Measure token consumption per run and report tokens-per-stage in the run summary to demonstrate Paritok efficiency in the hackathon benchmarks.

Important: the repository currently includes a generic provider routing implementation ([utils/model_router.py](E:/repoagent.worktrees/update-readme-for-hackathon-requirements/utils/model_router.py)) for OpenRouter/Bedrock/Groq. The README documents how to add Paritok without assuming it's already present in code.

How to add Paritok support (recommended minimal steps)
1. Add environment variables for Paritok (see Environment variables section below).
2. Extend `utils/model_router.py` to recognize `LLM_PROVIDER=paritok` and map stages to Paritok model names and client calls.
3. Implement a small client wrapper for Paritok token reporting (so runs can collect tokens-used per-stage).
4. Run the provided benchmark steps and include token-efficiency measurements in the submission.

Environment variables (reference)
---------------------------------
The repo already documents many variables; the key ones to configure locally are listed here.

Required (example):
- OPENROUTER_API_KEY — primary OpenRouter key (if using OpenRouter)
- LLM_PROVIDER — one of `openrouter`, `bedrock`, `groq`, `auto`
- GITHUB_TOKEN — personal access token for commit/PR automation
- GITHUB_USERNAME — username for GitHub automation

Optional / role-specific overrides (examples in repo):
- OPENROUTER_MODEL, OPENROUTER_CODER_MODEL, OPENROUTER_PLANNER_MODEL, etc.
- BEDROCK_MODEL, BEDROCK_PLANNER_MODEL, BEDROCK_MAX_TOKENS, etc.
- GROQ_API_KEY, GROQ_MAX_RETRIES
- EDITOR_MAX_WORKERS, FORCE_REINDEX

Suggested Paritok variables to add for integration (not present by default):
- PARITOK_API_KEY — Paritok API key
- PARITOK_MODEL_PLANNER — Paritok model identifier for planning (token-efficient)
- PARITOK_MODEL_CODER — Paritok model identifier for coding
- PARITOK_MAX_TOKENS — per-call max tokens for Paritok
- PARITOK_REPORT_TOKENS=true — enable token reporting per-stage

Setup (local)
-------------
1. Create a Python virtualenv and activate it (tested with Python 3.11+):

```bash
python -m venv .venv
# macOS / Linux
source .venv/bin/activate
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Create a `.env` at repository root and populate required keys (see Environment variables).

4. Run the API server or Streamlit UI (examples in Running section).

Running (examples)
------------------
FastAPI (API) server

```bash
python -m uvicorn api.server:app --reload --port 8000
```

Streamlit UI

```bash
streamlit run app.py
```

Script-run (quick local flow)

```bash
python main.py
```

API: start a run (example)

```bash
curl -X POST http://127.0.0.1:8000/api/run \
  -H "Content-Type: application/json" \
  -d '{"repo_url":"https://github.com/revtiraman/fastapi","user_prompt":"Add logging to API routes"}'
```

Benchmarks (how-to, no invented metrics)
---------------------------------------
This repository does not publish pre-computed benchmarks. The benchmark section below is a reproducible procedure you can follow to measure performance and token-efficiency for the hackathon.

Recommended benchmark procedure
1. Choose a representative target repository and a small suite of prompts (planning, code change, debugging).
2. For each provider configuration (e.g., baseline provider vs Paritok):
   - Start a fresh run (reset workspace) and run the same prompts.
   - Collect per-stage timings and token usage (if available).
   - Record wall-clock time, tokens consumed, and observables such as number of edit/compile iterations.
3. Use a CSV/table to report results and include raw run logs and artifacts in your submission.

Table template (fill after running):

| Provider | Prompt | Wall time (s) | Tokens (stage-wise) | Iterations | Notes |
|---|---:|---:|---|---:|---|
| paritok | "Add logging" | 42 | planner:100 / coder:1200 / debug:300 | 2 | example note |

Notes:
- Do not publish tokens or metrics you cannot verify. The README provides the method; the submitter must produce measured values.

Contributing
------------
Contributions are welcome. To contribute:
1. Fork the repository and create a feature branch.
2. Open a pull request with a clear description of the change and testing notes.
3. Keep PRs focused and add unit/integration tests where applicable.

Suggested areas for contribution relevant to the hackathon:
- Add a Paritok provider implementation in `utils/model_router.py` and a lightweight client wrapper for token reporting.
- Add dashboarding or run-summary outputs that expose per-stage token usage.

Code of conduct
---------------
Follow respectful collaboration practices. Report harassment or policy violations to the maintainers.

Hackathon submission checklist
-----------------------------
For the Paritok Token Efficiency Hackathon, include the following in your submission:
- A public GitHub repository link (ensure the repo is public)
- A short demo video (hosted on YouTube or similar) demonstrating the run
- Screenshots: architecture diagram and at least two run screenshots
- A short README explaining the Paritok integration and how token-efficiency was measured
- Benchmark CSV or table with methodology and raw logs
- Instructions to reproduce (setup, env variables, exact commands used)

If this repository is used for submission, ensure the repository is made public and a LICENSE file is added (Apache 2.0 recommended) before submission.

Built with Paritok
------------------
This submission is being prepared for Paritok. Add the following small attribution in your project and submission materials:

"Built with Paritok — used as an LLM provider for cost-sensitive planning and code generation stages."

License
-------
Include the Apache 2.0 license for hackathon submission. Add a `LICENSE` file in the repository root containing the full Apache License 2.0 text, or include the standard SPDX header in source files:

SPDX-License-Identifier: Apache-2.0

For convenience, the Apache 2.0 license text is available at: https://www.apache.org/licenses/LICENSE-2.0

If you intend to make this repository public and open-source for the hackathon, create a `LICENSE` file before submission.

Support & contact
-----------------
For questions about this repository, open an issue or contact the maintainers via GitHub issues.


Thank you and good luck with the Paritok Token Efficiency Hackathon!
