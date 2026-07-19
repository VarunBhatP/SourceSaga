# SourceSage Technical Guide

This document is a practical walkthrough of the `SourceSage` project so you can explain it confidently in technical interviews.

It covers:

- what the project does
- why it exists
- how the architecture works
- how each agent behaves
- how frontend and backend communicate
- how caching and persistence work
- what tradeoffs the current implementation makes
- how to explain the project clearly in interviews

## 1. Project Summary

`SourceSage` is a full-stack application that helps developers discover beginner-friendly open source issues and generate structured implementation guidance for them.

At a high level, the app:

1. takes a user’s skills as input
2. searches GitHub for matching `good first issue` tickets
3. lets the user select one or more issues
4. fetches issue details and comments
5. generates:
   - a solution plan
   - an explanation-style coding prompt
   - an optional GSOC proposal draft

Originally, the project used external LLM APIs for generation. In the current version, the generation pipeline has been refactored to use a **fully free local deterministic explainer** so the app can always show output without API credits.

## 2. Main Goal Of The Project

The product solves a real onboarding problem in open source:

- beginners often do not know which repository issue to pick
- even after choosing an issue, they may not understand the codebase or how to approach the fix
- proposal-style writing for programs like GSOC is time-consuming

`SourceSage` reduces that friction by combining:

- GitHub issue discovery
- structured issue analysis
- generated implementation guidance
- document export

In interview terms, this is a **developer productivity and onboarding assistant for open source contribution workflows**.

## 3. High-Level Architecture

The project is split into two main applications:

- `backend/`: FastAPI service with the agent workflow, GitHub integration, caching, and document generation
- `frontend/`: React + Vite UI for searching issues, selecting them, and viewing the generated analysis

### Backend stack

- `FastAPI` for REST endpoints
- `LangGraph` for agent orchestration
- `Motor + MongoDB` for caching
- `requests` for GitHub API access
- `python-docx` for downloadable proposal generation

### Frontend stack

- `React`
- `TypeScript`
- `Vite`
- `Framer Motion`
- `shadcn/ui` style component structure
- `axios` for HTTP requests

## 4. End-To-End Flow

The easiest way to explain the system is as a pipeline:

1. user enters skills in the frontend
2. frontend calls `POST /api/search-issues`
3. backend searches GitHub for matching `good first issue` tickets
4. backend returns a list of issues
5. user selects one or more issues
6. frontend calls `POST /api/analyze`
7. backend runs a sequential multi-agent workflow
8. backend returns:
   - issue context
   - solution plan
   - generated prompt
   - optional report download links
9. frontend renders the result and optionally downloads the generated `.docx`

## 5. Backend Entry Points

### `backend/app.py`

This is the FastAPI application bootstrap.

Responsibilities:

- creates the FastAPI app
- configures CORS
- connects to MongoDB during startup
- creates the `downloads/` directory
- registers the API router
- exposes a simple root health/info response

In interviews, you can say:

> The backend uses FastAPI with a lifespan hook to initialize infrastructure like MongoDB and the downloads directory before serving requests.

### `backend/api/routes.py`

This is the main API layer.

Important endpoints:

- `GET /api/health`
- `POST /api/search-issues`
- `POST /api/analyze`
- `GET /api/download/{filename}`
- `WebSocket /api/ws`

Key behavior:

- `/api/search-issues` checks cache first, then runs issue discovery
- `/api/analyze` checks cached analyses, regenerates incomplete ones, and runs the full analysis pipeline when needed
- proposal documents are served back via the download route

One useful design detail:

- `_is_analysis_complete()` prevents stale or partial cached analyses from being reused if `solution_plan` or `generated_prompt` is missing

That is a good interview talking point because it shows you handled a real production-style cache consistency issue.

## 6. Agent Workflow

The core intelligence of the backend is modeled as a sequence of agents.

### Workflow definition

The graph is defined in `backend/graph/workflow.py`.

The sequence is:

1. `find_issues`
2. `analyze_code`
3. `suggest_solutions`
4. `generate_prompts`
5. optionally `draft_reports`

This is a linear flow with a conditional branch at the end.

### Async execution

`backend/graph/async_workflow.py` provides async wrappers that run each agent in order using `asyncio.to_thread(...)`.

This keeps the FastAPI route async-friendly even though the actual agent functions are synchronous.

That is another strong interview point:

> I separated orchestration from transport. FastAPI stays async, while the agent logic runs in worker threads so blocking tasks like GitHub requests and document generation do not directly block the event loop.

## 7. Agent-By-Agent Breakdown

### Agent 1: Issue Finder

File: `backend/agents/issue_finder.py`

Purpose:

- takes user skills
- queries GitHub for matching `good first issue` tickets
- returns a normalized issue list

Input:

- `skills`

Output:

- `found_issues`
- `current_step = "issues_found"`

### Agent 2: Code Analyzer

File: `backend/agents/code_analyzer.py`

Purpose:

- fetches detailed issue information from GitHub
- gets issue body and recent comments
- compiles a unified context string

Input:

- `selected_issue_urls`
- `found_issues`

Output:

- `analyses`, where each analysis contains:
  - `issue_url`
  - `context`
  - empty `solution_plan`
  - empty `generated_prompt`

This is effectively the **context-building stage** of the pipeline.

### Agent 3: Solution Suggester

File: `backend/agents/solution_suggester.py`

Purpose:

- converts raw issue context into a deterministic step-by-step plan

Current implementation:

- no external model call
- uses `generate_solution_plan()` from `backend/utils/free_explainer.py`

Why this matters:

- the system always returns a result
- there is no dependency on LLM quota or API billing

### Agent 4: Prompt Generator

File: `backend/agents/prompt_generator.py`

Purpose:

- turns the issue context and solution plan into a structured prompt that can be copied into ChatGPT, Claude, or another assistant

Current implementation:

- uses `generate_coding_prompt()` from `backend/utils/free_explainer.py`

This stage is useful because it transforms raw guidance into a reusable developer-facing artifact.

### Agent 5: Report Drafter

File: `backend/agents/report_drafter.py`

Purpose:

- creates a GSOC-style proposal
- formats it into a `.docx`
- stores it in the `downloads/` folder
- returns a download URL

Current implementation:

- uses `generate_proposal()` from `backend/utils/free_explainer.py`
- uses `python-docx` to build the final document

This is the document-generation layer of the system.

## 8. The Local Free Explainer

File: `backend/utils/free_explainer.py`

This is now the most important generation utility in the project.

It replaces paid or quota-limited LLM calls with a deterministic, local text generation strategy.

It contains:

- `_extract_section()`
- `_extract_title_description_comments()`
- `generate_solution_plan()`
- `generate_coding_prompt()`
- `generate_proposal()`

How it works:

1. parses the structured issue context string
2. extracts title, description, and recent comments
3. uses templated text generation to create output artifacts

Tradeoff:

- output is less intelligent than an actual LLM
- but it is stable, free, deterministic, and demo-friendly

In interviews, frame this as:

> I adapted the generation layer from external model APIs to a local deterministic generator so the application could remain functional under zero-cost constraints while preserving the overall workflow design.

## 9. GitHub Integration

File: `backend/utils/github_client.py`

The GitHub client performs two main jobs.

### Search flow

`search_good_first_issues(skills, max_results=15)`:

- normalizes framework names into likely GitHub languages
- builds a GitHub search query
- filters by:
  - `is:issue`
  - `is:open`
  - `label:"good first issue"`
  - language tags

Example logic:

- `fastapi` becomes `python`
- `react` becomes `javascript`
- `angular` becomes `typescript`

This improves search relevance.

### Issue detail flow

`get_issue_details(issue_api_url)`:

- fetches issue title and body
- fetches recent comments
- returns a compact detail object used for analysis

This is the data ingestion layer of the backend.

## 10. State Management In The Agent Graph

File: `backend/graph/state.py`

The workflow passes around a shared `AgentState` typed dictionary.

Important fields:

- `skills`
- `found_issues`
- `selected_issue_urls`
- `analyses`
- `user_choice`
- `report_downloads`
- `current_step`
- `error`

Why this design is good:

- each agent reads from and writes to a shared contract
- it keeps agent boundaries explicit
- it makes orchestration easier to reason about

In interviews, you can say:

> I modeled the workflow state as an explicit typed shared object so each agent had a clear input/output contract instead of passing around loosely structured data ad hoc.

## 11. API Contracts

File: `backend/api/models.py`

The backend uses Pydantic models to validate requests and responses.

### Main request models

- `SearchIssuesRequest`
- `AnalyzeIssuesRequest`

### Main response models

- `SearchIssuesResponse`
- `AnalyzeIssuesResponse`
- `IssueAnalysis`

This gives you:

- input validation
- schema clarity
- better docs generation in FastAPI

Good interview phrasing:

> I used typed request/response schemas so the frontend and backend communicated through explicit contracts rather than implicit JSON assumptions.

## 12. Caching Strategy

Files:

- `backend/database/connection.py`
- `backend/database/cache.py`

MongoDB is used as a cache layer, not as a primary business database.

### What gets cached

- GitHub search results
- issue analysis results

### Why cache is useful

- reduces repeated GitHub API calls
- improves response speed
- avoids redoing analysis for the same issue repeatedly

### Cache TTLs

- issue search cache: `24 hours`
- analysis cache: `168 hours` (7 days)

### Design detail

If MongoDB is not configured, the app can still run in a degraded mode without caching.

That is a strong resilience point.

## 13. Frontend Architecture

The frontend is structured around a single-page flow.

Main page:

- `frontend/src/pages/Index.tsx`

Main UI components:

- `Header`
- `Hero`
- `SkillsForm`
- `IssuesList`
- `IssueCard`
- `AnalysisView`
- `Footer`

### `Index.tsx`

This is the main coordinator on the frontend.

It manages:

- theme state
- issue list state
- selected issues
- analysis result
- search loading state
- analysis loading state
- report generation toggle
- navigation between search view and analysis view

It sends requests to:

- `/api/search-issues`
- `/api/analyze`

It also maps backend responses into the frontend shape expected by `AnalysisView`.

## 14. Frontend User Journey

### Step 1: Enter skills

`SkillsForm.tsx`:

- user enters skills
- multiple skills are converted into removable badges
- submit triggers the issue search

### Step 2: Browse issues

`IssuesList.tsx` and `IssueCard.tsx`:

- issues are displayed as cards
- user can select multiple issues
- repo link can be opened separately
- selected issue URLs are stored in state

### Step 3: Analyze issues

`Index.tsx` calls `/api/analyze`

The backend returns analysis data and optional download links.

### Step 4: View results

`AnalysisView.tsx` shows:

- solution plan
- AI-ready prompt
- optional proposal download section

It also supports:

- copying the prompt
- toggling GSOC proposal generation
- going back to the issue list

## 15. Download Flow

The proposal generation and download flow works like this:

1. user enables report generation
2. backend creates a `.docx` in `downloads/`
3. backend returns a `download_url`
4. frontend creates a temporary anchor element
5. browser opens/downloads the generated file

This is a useful example of connecting generated backend artifacts to a frontend document download UX.

## 16. Error Handling And Resilience

The project contains several resilience mechanisms:

- graceful behavior when MongoDB is unavailable
- graceful behavior when GitHub token is missing
- cache-first reads for search and analysis
- regeneration of incomplete cached analyses
- deterministic local generation when external LLM APIs are not viable

This is worth emphasizing in interviews because it shows practical engineering beyond just happy-path implementation.

## 17. Why LangGraph Was A Good Fit

Even though the current generation is local, LangGraph is still useful here because the application is naturally a multi-stage workflow.

Why it fits:

- the workflow has clear sequential stages
- each stage transforms state
- the report draft step is conditional
- agent boundaries are explicit and easy to maintain

In other words, the graph abstraction keeps the system extensible.

If needed later, you could swap the local explainer back to real LLMs without rewriting the entire architecture.

## 18. Current Design Tradeoffs

### Strengths

- full-stack, end-to-end working product
- clear workflow-based backend architecture
- practical GitHub integration
- caching to reduce repeated work
- deterministic generation with zero API cost
- downloadable proposal output

### Limitations

- local explainer is template-based, so output quality is lower than real LLMs
- search results depend on GitHub label quality and repository metadata
- current async workflow still uses thread offloading for synchronous logic
- frontend is primarily single-page and stateful rather than route-based

Mentioning both strengths and limitations in interviews makes your explanation more credible.

## 19. Suggested Interview Pitch

Use something like this:

> SourceSage is a full-stack developer productivity tool that helps users find beginner-friendly open source issues and generates structured implementation guidance for them. The frontend is built in React and talks to a FastAPI backend. On the backend, I modeled the analysis pipeline as a LangGraph workflow with separate agents for issue discovery, context building, planning, prompt generation, and optional proposal drafting. GitHub data is fetched through the GitHub API, and MongoDB is used as a cache layer for searches and analyses. I initially used external LLM APIs for generation, but later replaced that with a deterministic local explainer so the app could run reliably without API credits. That change preserved the architecture while improving reliability and cost efficiency for demos and evaluation.

## 20. Good Technical Interview Talking Points

- **Architecture**: I split the app into a React frontend and FastAPI backend with clear API contracts.
- **Workflow design**: I used LangGraph because the problem is naturally a staged agent workflow.
- **Data modeling**: I used a shared typed workflow state and Pydantic request/response models.
- **Caching**: I added MongoDB-based caching for both GitHub search results and issue analyses.
- **Reliability**: I handled incomplete cache records by forcing regeneration instead of trusting stale data.
- **Cost optimization**: I replaced quota-based LLM calls with a local deterministic generator to keep the product functional for free.
- **UX**: I built a flow where the user searches, selects issues, gets analysis, copies prompts, and downloads generated documents.

## 21. Questions You May Be Asked

### Why did you choose FastAPI?

Because it provides fast API development, built-in validation via Pydantic, automatic docs, and works well with async endpoints.

### Why use LangGraph instead of plain function calls?

Because the system is a stateful multi-step workflow. LangGraph makes each stage explicit and keeps the pipeline extensible.

### Why MongoDB?

MongoDB was used mainly as a flexible cache store. The cached objects are naturally document-shaped, so MongoDB fits well.

### Why move away from external LLM APIs?

For cost and reliability reasons. The local explainer guarantees output for every request without credits or API rate limits.

### What would you improve next?

- add real repository code understanding beyond issue text
- improve prompt/report quality with better local heuristics or optional pluggable models
- add authentication and saved user sessions
- introduce proper background jobs for long-running analysis/report generation
- improve frontend routing and state management

## 22. How To Explain Your Contribution In One Minute

> I built an AI-style workflow system that helps developers discover and understand beginner-friendly GitHub issues. The backend uses FastAPI, LangGraph, GitHub API integration, and MongoDB caching. The frontend lets users search by skills, select issues, view a structured solution plan, copy an implementation prompt, and download a GSOC-style proposal. One of the key engineering decisions I made was replacing paid model-based generation with a local deterministic explainer so the project remains fully functional without external API quotas.

## 23. File Map For Quick Revision

If you want to revise fast before an interview, focus on these files:

- `backend/app.py`: FastAPI startup and app wiring
- `backend/api/routes.py`: main request lifecycle
- `backend/api/models.py`: API contracts
- `backend/graph/workflow.py`: agent graph definition
- `backend/graph/async_workflow.py`: async orchestration wrapper
- `backend/agents/issue_finder.py`: GitHub issue discovery
- `backend/agents/code_analyzer.py`: issue context creation
- `backend/agents/solution_suggester.py`: solution plan generation
- `backend/agents/prompt_generator.py`: coding prompt generation
- `backend/agents/report_drafter.py`: proposal generation and document export
- `backend/utils/github_client.py`: GitHub API integration
- `backend/utils/free_explainer.py`: current fully free local generation layer
- `backend/database/cache.py`: caching strategy
- `frontend/src/pages/Index.tsx`: main frontend orchestration
- `frontend/src/components/SkillsForm.tsx`: user input flow
- `frontend/src/components/IssueCard.tsx`: issue selection and repo navigation
- `frontend/src/components/AnalysisView.tsx`: displaying outputs and downloads

## 24. Final Interview Summary

If you remember only five points, remember these:

1. `SourceSage` helps users find and understand open source issues.
2. It is a React + FastAPI full-stack application.
3. The backend is organized as a LangGraph multi-agent workflow.
4. GitHub API and MongoDB caching are key backend integrations.
5. The generation layer now uses a fully free local explainer instead of paid LLM APIs.
