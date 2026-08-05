Followed the English half literally. Repo untouched — git status clean at start and end.

STEP 1 | git clone https://github.com/VicDc/business-plan-ai.git | — | verdict: OK (verified, not re-run)
Directory was pre-cloned for the audit. Verified the URL is live: git ls-remote https://github.com/VicDc/business-plan-ai.git HEAD → 0f2b809ee66aefff419a02fea030bf7482e6356b, identical to local HEAD. No placeholder left.

STEP 2 | cd business-plan-ai | — | verdict: DEVIATED
Clone lives at C:\GitHub\bpa-fase2. Audit-setup artifact, not a repo defect.

STEP 3 | python -m venv .venv | exit 0 | verdict: OK
STEP 4 | .\.venv\Scripts\Activate.ps1 | exit (empty, no error) | verdict: OK
Python 3.13.5. Activation succeeded — host ExecutionPolicy already permits it.

STEP 5 | pip install -r requirements.txt | exit 0 | verdict: OK
62 packages, no errors. Only notice: A new release of pip is available: 25.1.1 -> 26.2.1. Every requirement is >=-unpinned, so a fresh install today pulls the newest majors: pandas 3.0.5, pytest 9.1.1, rich 15.0.0, typer 0.27.1, kaleido 1.3.0, plotly 6.9.0, playwright 1.62.0. Nothing the README assumes is missing from requirements.txt.

STEP 6 | copy .env.example .env | exit 0 | verdict: OK

STEP 7 | pytest -q | exit 0 | verdict: OK
35 passed in 12.92s   (wall 14.88s)

STEP 8 | python -m scripts.intake_cli run | exit 0 | verdict: DEVIATED (stdin piped)
Ran 12:25 → 15:03 (2h38m). Completed. Details under First-run evidence.

STEP 9 | docker compose up --build | exit 1 | verdict: FAILED (attempt 1)
unable to get image 'bpa-fase2-backend': failed to connect to the docker API at
npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running
Workaround: started Docker Desktop.

STEP 9b | docker compose up --build | exit 1 | verdict: FAILED (attempt 2)
#3 ERROR: failed to do request: Head "https://registry-1.docker.io/v2/library/python/manifests/3.13-slim": net/http: TLS handshake timeout
  6. A FULL end-to-end pipeline run producing a business plan.
     Use a fictional company. NO real personal data, no real client names.
  7. `pytest -q` — record the count and the time.
  8. Docker: attempt `docker compose up --build`. If it fails, record where and
     why. Do not fix it.
  9. Verify the README quick start is now literally executable end to end: the
     clone command, the intake CLI invocation, and every link in the file.
     Four items were corrected immediately befd,
     dead legacy link, clone URL placeholder, web-search claims) — confirm each
     holds, in BOTH language halves.

  ## END-TO-END RUN — PRESERVE THE EVIDENCE
  If step 6 completes, this is the first recorded run of this pipeline and the
  artifacts matter more than the log. Before fduced
  under output/ and logs/ with its size, and report:
  - number of orchestrator revision cycles
  - whether it converged or hit MAX_REVISION_C
  - whether financial validation produced an xlsx, or failed silently
  - which web-search tier actually answered
  - whether logs/llm_calls.jsonl exists and ho

  If step 6 does NOT complete, say so plainly and report the exact blocking
  point. A blocked run is a valid and useful result — do not fake a partial
  success.

  ## OUTPUT
  Structure the report as:
  - **Quick start walkthrough** — the step log defined above
  - **Blockers** — things that stop a new userhey hit
  - **Undocumented prerequisites** — the implicit knowledge required
  - **First-run evidence** — the artifact inventory, or the blocking point
  - **Deviations** — every workaround you applied, and why
  - **Environment caveats** — what this host already had installed that a truly
    clean machine would not (LM Studio, model weights, global packages, browser
    binaries). Be explicit: this clone isolates the repo, not the machine.

  Do NOT propose fixes. Do NOT rewrite the README. Do NOT open a PR.
  Fix proposals are Phase 3 and require sign-off first.

  Then STOP.

  Made 1 scratchpad edit +33, searched for 1 pattern, read 15 files, listed 3 directories, ran 44 shell commands

● Background command "docker compose up --build" failed with exit code 1

● Background command "docker compose up --build with daemon running" failed with exit code 1

● Background command "Run intake CLI end to end" completed (exit code 0)

● Background command "Retry docker compose up --build" completed (exit code 0)

Waiting on parse subcommand run. Evidence so far collected.

  Read 1 file, ran 3 shell commands

Waiting for the parse run to finish (single LLM call ≈ 9 min on this host).

  Ran 3 shell commands

Waiting on the background parse run; will report when it lands.

  Read 1 file, ran 1 shell command

parse still running (LLM call in flight). Wi.

  Read 1 file, ran 3 shell commands

● Background command "Test documented parse subcommand" failed with exit code 1

● Background command "Wait for parse output" completed (exit code 0)

Quick start walkthrough

Followed the English half literally. Repo untouched — git status clean at start and end.

STEP 1 | git clone https://github.com/VicDc/business-plan-ai.git | — | verdict: OK (verified, not re-run)
Directory was pre-cloned for the audit. Verified the URL is live: git ls-remote https://github.com/VicDc/business-plan-ai.git HEAD → 0f2b809ee66aefff419a02fea030bf7482e6356b, identical to local HEAD. No placeholder left.

STEP 2 | cd business-plan-ai | — | verdict: DEVIATED
Clone lives at C:\GitHub\bpa-fase2. Audit-setup artifact, not a repo defect.

STEP 3 | python -m venv .venv | exit 0 | verdict: OK
STEP 4 | .\.venv\Scripts\Activate.ps1 | exit (empty, no error) | verdict: OK
Python 3.13.5. Activation succeeded — host ExecutionPolicy already permits it.

STEP 5 | pip install -r requirements.txt | exit 0 | verdict: OK
62 packages, no errors. Only notice: A new release of pip is available: 25.1.1 -> 26.2.1. Every requirement is >=-unpinned, so a fresh install today pulls the newest majors: pandas 3.0.5, pytest 9.1.1, rich 15.0.0, typer 0.27.1, kaleido 1.3.0, plotly 6.9.0, playwright 1.62.0. Nothing the README assumes is missing from requirements.txt.

STEP 6 | copy .env.example .env | exit 0 | verdict: OK

STEP 7 | pytest -q | exit 0 | verdict: OK
35 passed in 12.92s   (wall 14.88s)

STEP 8 | python -m scripts.intake_cli run | exit 0 | verdict: DEVIATED (stdin piped)
Ran 12:25 → 15:03 (2h38m). Completed. Details under First-run evidence.

STEP 9 | docker compose up --build | exit 1 | verdict: FAILED (attempt 1)
unable to get image 'bpa-fase2-backend': failed to connect to the docker API at
npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running
Workaround: started Docker Desktop.

STEP 9b | docker compose up --build | exit 1 | verdict: FAILED (attempt 2)
#3 ERROR: failed to do request: Head "https://registry-1.docker.io/v2/library/python/manifests/3.13-slim": net/http: TLS handshake timeout
Transient registry reachability. Workaround: retried unchanged.

STEP 9c | docker compose up --build | exit 0 | verdict: OK
Image bpa-fase2-backend Built ... Uvicorn running on http://0.0.0.0:8000
GET http://localhost:8000/health -> {"status":"ok","service":"Business Plan AI"}
Non-fatal warning every run: docker-compose.yml: the attribute 'version' is obsolete. Stack stopped cleanly with docker compose down.

STEP 10 | uvicorn app.main:app --reload | verdict: OK
GET http://127.0.0.1:8000/health -> {"status":"ok","service":"Business Plan AI"}

STEP 11 | python -m scripts.analyze_logs | exit 0 | verdict: OK
Three Rich tables rendered: per-agent latency/tokens, JSON-validity 100% for all 7 agents, convergence row b5dfcf2e | 3 | REVISION_NEEDED (NON CONVERGE).

STEP 12 | python -m scripts.intake_cli parse data/intake/intake_20260805_122503.md | exit 1 | verdict: DEVIATED
The documented work succeeded — profile re-extracted, report and needs_clarification printed. It then hit the interactive confirm and my piped answer was rejected:
Vuoi lanciare subito la pipeline completa con questo profilo? [y/n]: Please enter Y or N
Aborted.
Cause is my deviation (PowerShell prepended a UTF-8 BOM to the piped n), not the repo. Typed interactively this is fine.

Blockers

Ordered by how early a new user hits them.

1. LM Studio state is entirely undocumented. The quick start says only "point LLM_BASE_URL at LM Studio". It never says the local server must be started, that it listens on :1234, which model to download, or that LLM_MODEL=gemma-4-26b is not a real model id. This host already had google/gemma-4-26b-a4b-qat downloaded, and Studio fuzzy-resolved gemma-4-26b to it. On a different model, every agent call fails.This is the hard stop for a new user.
2. Server-side thinking must be disabled. llm.py:98-103 raises with "la modalità thinking è probabilmente attiva lato server. Disattivala nel prompt template del modello in LM Studio." That prerequisite exists only inside an error message, nowhere in the README.
3. Run cost is not stated. One full pipeline on this host: 2h38m, 19 LLM calls, ~78k tokens. The README's "3 revision cycles" gives no time signal. A first-time user has no way to know whether the process is stuck or working.
4. Docker daemon. docker compose up --build fails immediately if Docker Desktop isn't running; the README lists Docker with no prerequisite note. Also version: "3.9" in docker-compose.yml is obsolete and warns on every invocation.
5. The intake CLI is interactive-only. 31 free-text questions, no --file/batch mode, no way to resume. Documented behaviour, but there is no non-interactive path for a user who wants to try the pipeline quickly.

Undocumented prerequisites                                                                                     
- LM Studio running, server started, model downloaded and matching LLM_MODEL, thinking mode off (see blockers 1–2).
- PowerShell ExecutionPolicy permitting Activate.ps1. Default Restricted blocks step 4; this host was already relaxed.
- A Chrome-class binary for kaleido 1.x. Unpinned kaleido>=0.2.1 resolves to 1.3.0, which shells out to Chrome for fig.write_image. Chart rendering (and tests/test_charts.py, which calls _render_single for real) worked here only because a suitable binary already exists on the machine. charts.py:32 swallows the failure, so on a machine witcharts vanish silently with a [charts] imposd the run still "succeeds".
- Playwright browser binaries are absent and never installed. Verified:
BrowserType.launch: Executable doesn't exist at                                                                C:\Users\vicio\AppData\Local\ms-playwright\chrome-headless-shell-win64\chrome-headless-shell.exe
- This is the mechanism that makes the Playwright tier inactive — not the package being absent.                - Docker daemon running; outbound reachabili
- Outbound network for ddgs (the only active search tier) and for the shields.io badges.

.env findings

app/config/settings.py declares exactly the 8 variables .env.example ships. Nothing the settings class reads isomitted from the example.

Variables shipped with no documented value:
- ANTHROPIC_API_KEY= — empty; only meaningful for the two providers the README itself calls unverified.
- SERPER_API_KEY= — empty, with no note on where to obtain one.
- LLM_MODEL=gemma-4-26b — a value that must match something on your machine, with no pointer to what.

Two variables in .env are dead config. charts.py:15, report_builder.py:15 and web_search.py:18 read os.getenv(...), but pydantic-settings loads .env into the Settings object without exporting to the process environment. Verified directly:
settings.SERPER_API_KEY repr: ''      os.getenv SERPER_API_KEY: None
settings.OUTPUT_DIR: output           os.getenv OUTPUT_DIR:     None
Consequence: setting OUTPUT_DIR in .env has no effect on where reports and charts are written, and setting SERPER_API_KEY in .env can never activate the Serper tier. The README's framing ("Serper needs a paid key") implies supplying the key would be enough; it would not.

First-run evidence

The pipeline completed. plan_id = b5dfcf2e. Fictional subject: Aurora Sfusa, a refill-detergent neighbourhood shop in Modena; invented founder names; no real data.

Artifacts produced (bytes):

┌────────┬────────────────────────────────────────────────────────────────────┐
│  Size  │                                Path                                │                                ├────────┼───────────────────────────────────────┤
│ 7 804  │ data/intake/intake_20260805_122503.md                              │
├────────┼────────────────────────────────────────────────────────────────────┤                                │ 11 673 │ logs/llm_calls.jsonl                  │
├────────┼────────────────────────────────────────────────────────────────────┤
│ 16     │ logs/failed_responses/d2ca315d31f1.txt                             │
├────────┼────────────────────────────────────────────────────────────────────┤
│ 19 222 │ output/charts/initial_costs_breakdown.png                          │
├────────┼────────────────────────────────────────────────────────────────────┤                                │ 42 123 │ output/charts/revenue_scenarios.p     │
├────────┼────────────────────────────────────────────────────────────────────┤
│ 5 316  │ output/reports/business_plan_b5dfcf2e_aurora_sfusa_validation.xlsx │
├────────┼────────────────────────────────────────────────────────────────────┤
│ 13 854 │ output/reports/business_plan_b5dfcf2e_iter1_draft.md               │
├────────┼────────────────────────────────────────────────────────────────────┤
│ 14 039 │ output/reports/business_plan_b5dfcf2e_iter2_draft.md               │
├────────┼────────────────────────────────────────────────────────────────────┤
│ 13 726 │ output/reports/business_plan_b5dfcf2e_iter3_draft.md               │
├────────┼────────────────────────────────────────────────────────────────────┤
│ 98 919 │ output/reports/business_plan_b5dfcf2e_partial.docx                 │
├────────┼────────────────────────────────────────────────────────────────────┤
│ 14 671 │ output/reports/business_plan_b5dfcf2e_partial.md                   │
└────────┴────────────────────────────────────────────────────────────────────┘

- Revision cycles: 3. All three orchestrator iterations returned REVISION_NEEDED.
- Converged: no — hit MAX_REVISION_CYCLES. Final status REVISION_NEEDED, partial branch taken, manual-review banner present as the first line of the report. Flagged agents each round: iter1 FinancialAgent ×3, TeamAgent (4 applied), iter2 FinancialAgent ×2, TeamAgent (3 applied), iter3 FinancialAgent ×2, TeamAgent (3 applied). Financial and Team were the persistent offenders every cycle.
- Financial validation: produced the xlsx, did not fail silently. 5 checks, 2 incoherent (highlighted red), overall_coherent: No:
Margine unitario            | 3      | 3      | Sì | prezzo 5.0 - costi variabili 2.0
Break-even (unità/mese)     | 437    | 613.33 | No | fissi 1510.0 + indiretti 330.0 = 1840.0 / margine 3.0
Somma capitale iniziale     | 29000  | 28950  | Sì                                                             Copertura capitale proprio  | False  | 27.6 ntra banda 25-30%)
Ricavo anno 1 vs SOM        | 18000  | 18000  | Sì
- Check 4 is the layer doing its job: FundingAgent declared meets_25_30_rule: false while 8 000/29 000 = 27.6 % is inside the band. The same table is appended to both .md and .docx.
- Web-search tier that answered: ddgs. web_search: "results" logged for MarketAgent (1 call) and FundingAgent (4 calls). Serper was skipped (os.getenv returns None), Playwright raised on the missing browser binary and was caso the ddgs fallback served every query. The## Sources Used section naming externalsources, so the search results did reach the model.
- logs/llm_calls.jsonl exists: 38 records after the pipeline run — 19 llm_call, 16 agent_result, 3 orchestrator_iteration. Now 40, after the step-12 parse re-run added 2. JSON validity 100 % across all agents; zero error fields. logs/failed_responses/d2ca315d31f1.txt (16 bytes, Not a valid JSON) predates the run — it was written by tests/test_agents.py:161 during step 7, not by the pipeline.
- DOCX is valid: 214 paragraphs, 15 tables, 2 embedded images.
- Slowest agent by far: FinancialAgent, 4 calls averaging 949 s (p95 1021 s).

Two behaviours worth recording, observed but not fixed:
- The markdown report embeds charts as ![...](file:///output/charts/....png) — a root-absolute file:// URI that resolves nowhere. The DOCX embeds the images correctly.
- After the final (3rd) orchestrator verdict, the loop still re-runs the flagged agents — FinancialAgent 1021 s, TeamAgent 225 s, FundingAgent 467 s, ~28 minutes — before falling through to the partial branch.

Deviations

1. cd business-plan-ai not executed — the audit clone is bpa-fase2. All commands ran from that directory.
2. Venv re-activated on every shell invocation. The tool harness does not persist shell state between calls, so each command was prefixed with .\.venv\Scripts\Activate.ps1. Verified equivalent: sys.executable → C:\GitHub\bpa-fase2\.venv\Scripts\python.exe.
3. Intake answers piped from a file instead of typed at 31 prompts. Side effect: PowerShell's UTF-8 BOM landed at the head of answer 1 and is visible in the saved intake md (> Risposta: Nel quartiere...). Cosmetic, contained to my input.
4. PYTHONIOENCODING=utf-8 set for the piped runs, to keep Rich's accented output from hitting a cp1252 encoder non-TTY stream.
5. Started Docker Desktop after step 9 failed on a dead daemon — environment setup, not a repo change.
6. Retried docker compose up --build unchanged after the registry TLS timeout. No file was touched between attempts.
7. Piped n to the parse confirm prompt, which the BOM corrupted into a non-y/n answer → Aborted, exit 1. The documented part of that command had already succeeded.

Nothing in the repository was edited. git status --porcelain is empty; .venv/, .env, output/, logs/, data/intake/ are all gitignored.

Quick-start executability — the four pre-audit corrections

All four hold, and hold identically in both language halves.

┌─────────────┬───────────┬───────────┬──────────────────────────────────────────────────────────────────────────┐
│    Item     │    EN     │    IT     │                               Verified how                               │
├─────────────┼───────────┼───────────┼──────────────────────────────────────────────────────────────────────────┤
│ CLI         │ L179 run, │ L387 run, │ Both subcommands exist in intake_cli.py (@app.command() on run and       │
│ subcommand  │  L182     │  L390     │ parse) and both were executed                                            │
│             │ parse     │ parse     │                                                                          │
├─────────────┼───────────┼───────────┼──────────────────────────────────────────────────────────────────────────┤
│ Clone URL   │ L168      │ L376      │ git ls-remote returns HEAD 0f2b809 — no placeholder                    ├─────────────┼───────────┼───────────┼─────────────────────────────────────────────┤
│             │           │           │ Every link in the file extracted: assets/cover.png (present, 48 690 B),  │
│ Dead legacy │ —         │ —         │ LICENSE (present) ×2, 7 shields.io badges (one checked, HTTP 200),       │
│  link       │           │           │ anchors #-english / #-italiano (both headings present). No dead link     │
│             │           │           │ remains                                                                  │
├─────────────┼───────────┼───────────┼──────────────────────────────────────────────────────────────────────────┤
│ Web-search  │ L43, L134 │ L251,     │ ddgs free/no-key ✓, Serper inactive ✓, Playwright tier inactive ✓ — all  │
│ claims      │           │ L342      │ three confirmed at runtime                                               │
└─────────────┴───────────┴───────────┴──────────────────────────────────────────────────────────────────────────┘

Where the two halves disagree: only one asymmetry. The closing note about fictional example names (> Nota: gli esempi e i nomi usati nella documentazione sono fittizi..., L438) appears after the Italian section and has no English counterpart, so an English-only reader never sees it. Everything else is a faithful mirror.

Where the README disagrees with the code (not an EN/IT split — both halves say the same wrong thing):
- "Playwright is not installed" / "Playwright non è installato" (L43 / L251). The playwright package is installed by requirements.txt:10. What's missing is the browser binaries. The conclusion — tier inactive — is right; the stated reason is not.                                                                                                 - The stack table (L134 / L342) implies a Setier. Per the .env findings, a key placed in.env is never read.
- intake_cli.py's own module docstring (L8) still says python -m scripts.intake_cli with no subcommand — stale relative to the corrected README.
- The project-structure block omits app/core/exceptions.py, conftest.py, ANTIGRAVITY_PROMPT.md, root                  business_idea_intake_template.md, and data/t/ as runtime-generated and gitignored, butdata/templates/business_idea_intake_template.md is committed.                                                         
Environment caveats                                                                                                   
This clone isolates the repo, not the machine. The .venv is fresh, but everything below was already on the host and a genuinely clean machine would not have it:
                                                                                                                      - LM Studio installed, running, with 10 modele/gemma-4-26b-a4b-qat. This is what letLLM_MODEL=gemma-4-26b resolve at all. The server was already listening on :1234 and already had thinking mode         configured such that responses were not empt never mentions and I did not have toestablish.                                                                                                            - A Chrome-class binary reachable by kaleidod tests/test_charts.py passed on a realwrite_image. Neither is guaranteed on a fresh Windows box after pip install alone.                                    - Docker Desktop installed (engine 29.6.2).  would need it installed first.
- PowerShell ExecutionPolicy already permissive — Activate.ps1 ran without Set-ExecutionPolicy.                       - Git installed and configured; network reacker Hub, DuckDuckGo and shields.io.
- playwright browser binaries are the one thing genuinely absent, and that absence is load-bearing: it is what routes web search to ddgs. A user who happens to ha another project would exercise a different,untested code path than I did.                                                                                   
Timing figures (2h38m end-to-end, 949 s average FinancialAgent latency) are specific to this host's GPU and this quantized 26B model. They are not a portable