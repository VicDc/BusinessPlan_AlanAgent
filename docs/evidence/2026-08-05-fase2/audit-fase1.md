FASE 1 — AUDIT

Base: lettura codice + esecuzione reale. Ambiente: .venv Python 3.13.5, Windows 11.

---
A. FALSI — il codice fa il contrario di quanto dichiarato

┌─────┬───────────────────────────────────────────────┬────────────────────────────────────┐
│  #  │                 Claim README                  │               Realtà               │
├─────┼───────────────────────────────────────────────┼────────────────────────────────────┤
│ A1  │ python -m scripts.intake_cli lancia l'intake  │ Missing command, exit 2            │
├─────┼───────────────────────────────────────────────┼────────────────────────────────────┤
│ A2  │ Link a README.legacy.md                       │ File inesistente                   │
├─────┼───────────────────────────────────────────────┼────────────────────────────────────┤
│ A3  │ cd business-plan-ai                           │ Cartella reale BusinessPlan_Agent  │
├─────┼───────────────────────────────────────────────┼────────────────────────────────────┤
│ A4  │ OUTPUT_DIR da .env                            │ Ignorato da grafici e report       │
├─────┼───────────────────────────────────────────────────────┤
│ A5  │ SERPER_API_KEY da .env migliora i risultati   │ Ignorata: ramo Serper mai attivato │
├─────┼───────────────────────────────────────────────┼────────────────────────────────────┤ │ A6  │ Fallback a 3 livelli, "testato e funPlaywright morto  │
└─────┴───────────────────────────────────────────────┴────────────────────────────────────┘
                                                                                             Note

1. A1 — README:181 e README:389. scripts/intake_cli.py:27 crea un typer.Typer() con due comandi (run a riga 32, parse a riga 98): Typer esige il sottocomando. Output reale eseguito:
Usage: python -m scripts.intake_cli [OPTIONS] COMMAND [ARGS]...
Error: Missing command.        EXIT=2
1. Comando corretto: python -m scripts.intake_cli run. È il primo comando del quick start: chi clona si ferma qui.
2. A2 — README:20. git ls-files restituisce solo README.md.
3. A3 — README:171, 378, e i blocchi struttura README:143 / README:351.                      4. A4 — app/services/charts.py:15 e app/servgono os.getenv("OUTPUT_DIR", "output").os.getenv non legge .env: nessun load_dotenv in tutto il repo (grep su dotenv: 0 occorrenze in *.py), python-dotenv non è in requirements.txt (compare solo in business_plan_ai_spec.md:2080). Solo app/api/v1/resettings.OUTPUT_DIR, che invece .env lo legga concreta: con OUTPUT_DIR=out_custom in.env, orchestrator scrive in output/reports/ e l'endpoint GET /api/v1/report/{id} cerca in out_custom/reports/ → 404 sistematico. Stessa variabile, due fonti, esiti divergenti.
5. A5 — app/services/web_search.py:18 os.getenv("SERPER_API_KEY"). Stesso meccanismo di A4: la key messa in .env non arriva mai. README:45 e README:253 la presentano come opzione funzionante.
6. A6 — README:136 / README:344 e la nota privacy README:45. playwright non è installato nel list; a runtime: ModuleNotFoundError: No mod_search.py:44). La catena reale eseguita èSerper (skippato, key vuota) → Playwright (ImportError, catturato da web_search.py:25) → ddgs. Verifica eseguita: la ricerca funziona, 3 risultati reali in 7.6s — ma via ddgs, non Playwright. Anche dopo pip insil livello Playwright resta morto senza playdocumentato.
---
B. NON VERIFICABILI — plausibili, nessuna prova nel repo
                                                                                             ┌─────┬───────────────────────────────────────────┐
│  #  │                  Claim                  │     Perché non provabile     │
├─────┼─────────────────────────────────────────┼──────────────────────────────┤
│ B1  │ docker compose up --build               │ Non eseguito; sospetto rotto │
├─────┼─────────────────────────────────────────┼──────────────────────────────┤
│ B2  │ Stessa architettura di orgtransform-ai  │ Repo esterno                 │
├─────┼─────────────────────────────────────────┼──────────────────────────────┤
│ B3  │ Gemma satura il reasoning in 1 chiamata │ Nessuna misura               │
├─────┼─────────────────────────────────────────┼──────────────────────────────┤
│ B4  │ Pipeline end-to-end produce un piano    │ Zero run nel repo            │
└─────┴─────────────────────────────────────────┴──────────────────────────────┘
                                                                                             Note

1. B1 — Docker presente (v29.6.2), build non lanciata. Problema evidente da codice: docker-compose.yml monta env_file: .env con LLM_BASE_URL=http://localhost:1234/v1; dentro il container localhost è il container,Studio. Nessun extra_hosts: host.docker.intenoltre Dockerfile non esegue playwrightinstall. Il container espone solo l'API: l'intake CLI, unico entry point documentato, non è raggiungibile.
2. B3 — motivazione in app/agents/orchestrator.py:146-148; nessun benchmark nel repo.
3. B4 — logs/llm_calls.jsonl non esiste, python -m scripts.analyze_logs risponde Nessun log trovato. output/ vuota. logs/failed_responses/ contiene 4 file da 16 byte. Nessuna evidenza nel repo di un business plan completo mai generato.

---
C. INCOMPLETI — veri ma parziali o fuorvianti
                                                                                             ┌─────┬─────────────────────────┬───────────
│  #  │          Area           │             Problema             │
├─────┼─────────────────────────┼──────────────────────────────────┤                         │ C1  │ Privacy / PII           │ Istruzione
├─────┼─────────────────────────┼──────────────────────────────────┤
│ C2  │ Endpoint                │ /intake/template non documentato │
├─────┼─────────────────────────┼──────────────────────────────────┤
│ C3  │ Validazione finanziaria │ Fallisce in silenzio             │
├─────┼─────────────────────────┼──────────────────────────────────┤                         │ C4  │ Struttura progetto      │ File dimen
├─────┼─────────────────────────┼──────────────────────────────────┤
│ C5  │ Config                  │ 4 variabili orfane               │                         ├─────┼─────────────────────────┼───────────
│ C6  │ Commenti nel codice     │ Contraddicono il README (giusto) │
├─────┼─────────────────────────┼──────────────────────────────────┤                         │ C7  │ Test                    │ 35 verdi,
├─────┼─────────────────────────┼──────────────────────────────────┤
│ C8  │ Prerequisiti            │ 5 impliciti, mai scritti         │
└─────┴─────────────────────────┴──────────────────────────────────┘

Note                                                                                         
1. C1 — claim di postura, il più delicato. README:45 / README:253: "Questo traffico non deve mai contenere dati sensibili sui soci". È una raccomandazione, non un'implementazione. Nessun PII guard esiste: app/services/web_search.py:6-9 lo dichiara euro ("se in futuro questo servizio ricevedati sensibili... va sanitizzato PRIMA"). Nel comportamento attuale i nomi dei soci non escono davvero, ma per costruzione della query, non per un filtro: market_agent.py:30-33 e funding_agent.py:30-33 compongono la qneed_addressed/idea_description + settore + . Classificazione: TODO presentato comegaranzia. Il testo suona come una policy applicata; non c'è codice che la applichi. Se domani qualcuno cambia la query, niente si accorge.
Il badge Privacy-first (README:9) eredita lo stesso problema: vero per il provider local, non sostenuto da alcun controllo.
2. C2 — GET /api/v1/intake/template esiste (app/api/v1/intake.py:10), assente dalle tabelle README:206-212 e README:414-419.
3. C3 — orchestrator.py:281-300: qualsiasi eccezione nella validazione ricade su (markdown invariato, "") print. Il report esce senza la tabella di veamante API riceve validation_xlsx_path=""senza distinguere "non calcolabile" da "crashato". README:114 / README:322 descrivono l'export come se avvenisse sempre.                                                                                                   4. C4 — README:146/354 elenca 3 file in app/ons.py non è importato da nessuna riga (grepsu tutto il repo: solo un nome di test omonimo) → codice morto. README:162/370 dice data/ runtime-generated e gitignored, ma data/templates/business_idea_intake_template.md è tracciato (git ls-files) ed è byte-identico (SHA256 2DFB31EB…) a business_idea_intake_template.md in root: due copie, nessuna delle due letta dal codice — le domande vengono da app/core/intake_questions.py. .gitignore:14 ignora solo data/intake/. Anche ANTIGRAVITY_PROMPT.md (3.6 KB) e business_plan_ai_spec.md (94 KB) sono puramente dichiarativi: nessuna riga di codice li apre; il README secondo, non il primo.
5. C5 — settings.py:20-22 dichiara APP_HOST, APP_PORT, LOG_LEVEL: mai lette (grep settings.[A-Z_]+ → solo OUTPUT_DIR, LLM_*, ANTHROPIC_API_KEY, MAX_REVISION_CYCLES). Sono anche in .env.example:12-14. Il .env locale contiene REDIS_URL=redis://localhost:6379/0, assente ple, mai usata da nessuna riga. Inoltre .envlocale non contiene LLM_PROVIDER, ANTHROPIC_API_KEY, LOG_LEVEL (funziona solo grazie ai default di settings.py).
6. C6 — orchestrator.py:49 commenta FASE 1: agenti paralleli mentre le righe 50-53 sono quaREADME:91 lo descrive correttamente). orchesui, dopo APPROVED per il rendering grafici,ma le righe 255-256 li renderizzano anche nel ramo parziale (di nuovo, il README è quello giusto). Il codice mente, non la doc.
7. C7 — pytest -q eseguito: 35 passed in 12.33s. Ripartizione: test_agents.py 13 funzioni, test_financial_validation.py 7 (di cui test_), test_charts.py 1. Non coperti:app/services/llm.py (nessun test del client HTTP né dei rami claude_*), app/services/web_search.py (zero test: i tre livelli di fallback non sono mai esercitati, solo mockati dall'esterno in test_agents.py:170), tutti gli endpoint in app/api/ (nessun TestClient), scripts/intake_cli.py, scripts/analyze_logs.py, scripts/clean_outputs.py, app/config/settings.py, app/core/prompts.py. Nessun test di integrazione con LLM reale: ogni test usa MockLLMService.
8. C8 — prerequisiti impliciti mai documentati:
  - LM Studio (o Ollama) installato, avviato, con modello caricato su :1234. Il README dice solo "punta LLM_BASE_URL a LM Studio", dandolo per esistente.
  - Thinking mode va disattivata lato server nel prompt template del modello. llm.py:98-103 solleva un errore esplicito su questo caso — è un fallimento no nel README.
  - playwright install chromium per il livello 2 della ricerca. Assente da README e da Dockerfile.
  - Nome modello: .env.example:5 dice gemma-a-4-26b-a4b-it-qat. Va allineato all'IDesatto esposto da LM Studio, altrimenti la chiamata fallisce.
  - Docker: serve rimappare l'host LLM (vedi B1).

---
D. VERIFICATI — confermati, con riferimento

┌───────────────────────────────────┬─────────────────────────────────────────┐
│               Claim               │               Riferimento               │
├───────────────────────────────────┼────────────┤
│ 6 agenti + Orchestrator           │ orchestrator.py:36-41                   │
├───────────────────────────────────┼────────────┤
│ ReportWriter = 2ª chiamata LLM    │ orchestrator.py:150-156                 │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ Fase 1 sequenziale, no gather     │ orchestrator.py:50-53                   │
├───────────────────────────────────┼────────────┤
ing        │ orchestrator.py:63, :68                 │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ Max 3 cicli, default              │ settings.py:25, orchestrator.py:80      │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ Report parziale + banner          │ orchestrator.py:240-265                 │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ 6 controlli di coerenza LLM       │ prompts.py:311-322                      │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ 5 check aritmetici, tolleranza 5% │ financial_validation.py:16, 137-266     │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ non_verificabile, mai eccezioni   │ financial_validation.py:111-112         │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ xlsx, righe incoerenti in rosso   │ financial_validation.py:308-320         │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ Report a 8 sezioni                │ prompts.py:367-374                      │
├───────────────────────────────────┼────────────┤
│ Grafici deterministici, zero LLM  │ charts.py (nessun import LLM)           │
├───────────────────────────────────┼────────────┤
│ Draft per iterazione              │ orchestrator.py:131-138                 │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ Log JSONL + risposte fallite      │ llm_logging.py:38, 121                  │
├───────────────────────────────────┼────────────┤
─────┼─────────────────────────────────────────┤
│ Nessuna dipendenza orfana         │ vedi nota                               │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ MIT + cover.png + Python 3.13     │ LICENSE, assets/cover.png, Dockerfile:1 │
├───────────────────────────────────┼─────────────────────────────────────────┤
│ analyze_logs / clean_outputs      │ eseguiti, output corretto               │
└───────────────────────────────────┴─────────────────────────────────────────┘

Note

1. ReportWriter — non è una classe agente (app/agents/report_writer.py non esiste): è un secondo llm.generate() con REPORT_WRITER_PROMPT. Il README lo chiama "a separate ReportWriter" e nel diagramma è un nodo: leggibile come agente. Riferimento vero: prompts.py:355 + orchestrator.py:150.
2. Dipendenze — tutte e 16 le voci di requirte: kaleido implicitamente da
: architettura, controlli, validazione aritmetica e grafici sono come descritti e testati. Il danno è concentrato altrove — il primo comando del quick start non parte, due variabili di .env sono lette da una fonte che .env non lo legge affatto, un livello della ricerca web è pubblicizzato come testato ed è assente dall'ambiente, e il claim privacy sui dati dei soci è una raccomandazione presentata come postura.

FERMO. Vado in Fase 2 (riproducibilità da zero)?