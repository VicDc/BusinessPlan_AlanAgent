# AGENTS.md — Guida di Build per Antigravity IDE
> Progetto: business-plan-ai
> Fonte di verità: `business_plan_ai_spec.md`

Questo file dice ad Antigravity **cosa costruire, in che ordine, e cosa è già
stato costruito** — per evitare che rigeneri file già completati durante run
successive.

---

## CURRENT BUILD STATUS

> Aggiorna questa sezione manualmente (o fai aggiornare ad Antigravity) dopo
> ogni checkpoint verificato con `pytest -q`. Finché una riga è TODO,
> Antigravity può generarla/modificarla liberamente; se è DONE, non deve
> rigenerarla senza istruzione esplicita.

### Struttura e configurazione
- [x] DONE — struttura cartelle repository (vedi spec)
- [x] DONE — `requirements.txt`, `.env.example`, `docker-compose.yml`, `Dockerfile`
- [x] DONE — `app/config/settings.py`

### Core
- [x] DONE — `app/core/types.py` (incluso `raw_intake_notes` e `IntakeReport`)
- [x] DONE — `app/core/prompts.py` (incluso `INTAKE_AGENT_PROMPT` e `REPORT_WRITER_PROMPT`)
- [x] DONE — `app/core/intake_questions.py`
- [x] DONE — `app/core/exceptions.py`

### Intake (precede gli agenti specialistici)
- [x] DONE — `app/agents/intake_agent.py`
- [x] DONE — `data/templates/business_idea_intake_template.md`
- [x] DONE — `scripts/intake_cli.py`
- [x] DONE — `app/api/v1/intake.py`

### Agenti
- [x] DONE — `app/agents/base.py`
- [x] DONE — `app/agents/vision_agent.py`
- [x] DONE — `app/agents/market_agent.py`
- [x] DONE — `app/agents/team_agent.py`
- [x] DONE — `app/agents/setup_agent.py`
- [x] DONE — `app/agents/financial_agent.py` (include charts_needed)
- [x] DONE — `app/agents/funding_agent.py`
- [x] DONE — `app/agents/orchestrator.py`

### Servizi
- [x] DONE — `app/services/llm.py` (multi-provider: local / claude_fast / claude_quality)
- [x] DONE — `app/services/llm_logging.py` (log JSONL chiamate LLM + esiti parsing)
- [x] DONE — `app/services/charts.py` (rendering deterministico, NON-LLM)
- [x] DONE — `app/services/web_search.py` (fallback Serper → Playwright → ddgs)
- [x] DONE — `app/services/report_builder.py` (DOCX/MD, tabelle/bold, sezioni agente)

### API e modelli
- [x] DONE — `app/models/requests.py`, `app/models/responses.py`
- [x] DONE — `app/api/v1/business_plan.py`
- [x] DONE — `app/api/v1/report.py`
- [x] DONE — `app/api/v1/health.py`
- [x] DONE — `app/main.py`

### Test
- [x] DONE — test suite base (`tests/`) con almeno: parsing JSON di ogni agente,
  rendering charts.py con spec valide/invalide, revision loop con mock LLM,
  consistency check dei 5 controlli dell'Orchestrator

---

## COME PROCEDERE (istruzioni per Antigravity)

1. Leggi interamente `business_plan_ai_spec.md` prima di generare qualsiasi file.
2. Genera i file **nell'ordine delle sezioni sopra** (struttura → core → intake →
   agenti specialistici → servizi → API → test). Non saltare avanti:
   `orchestrator.py` dipende da tutti gli agenti, `financial_agent.py` dipende
   da `charts.py` solo per il tipo di dato che produce (`charts_needed`), non
   per importazione diretta.
3. `IntakeAgent` **non eredita da `BaseAgent`**: non forzarlo in quella gerarchia
   solo per uniformità. La sua forma è diversa apposta — produce il profilo
   invece di consumarlo, e non partecipa al revision loop dell'Orchestrator.
3. Dopo ogni file o piccolo gruppo di file generato, fermati e segnala cosa hai
   creato. Non generare tutto in un unico blocco senza checkpoint intermedi.
4. Se un file elencato sopra è già marcato DONE, non modificarlo a meno che
   l'istruzione esplicita in chat non dica di farlo.
5. Il modulo `app/services/charts.py` **non deve mai chiamare l'LLM**: riceve
   solo `list[dict]` (le ChartSpec) e produce PNG con Plotly. Se ti viene in
   mente di far "descrivere" il grafico a Gemma in linguaggio naturale e poi
   parsare quella descrizione, non farlo — usa lo schema JSON già definito in
   `FINANCIAL_AGENT_PROMPT` (`charts_needed`), è già strutturato apposta.
6. Rispetta la separazione delle responsabilità tra agenti — non far scrivere
   a un agente output che appartengono a un altro (es. FinancialAgent non deve
   valutare le competenze del team, quello è compito di TeamAgent).

---

## VERIFICA (dopo ogni checkpoint)

Ambiente: Windows / PowerShell.

```powershell
.\.venv\Scripts\Activate.ps1
pytest -q
git status
```

Note ambiente (stesse di OrgTransform AI):
- `&&` non è valido in PowerShell — usa `;` o righe separate
- `curl` è alias di `Invoke-WebRequest`
- LM Studio deve essere avviato con Gemma 4 26B QAT sulla porta 1234 prima di
  eseguire test che coinvolgono l'LLM reale (i test unitari dovrebbero comunque
  usare un mock del client LLM, non dipendere da LM Studio in esecuzione)

---

## NOTE ARCHITETTURALI DA NON PERDERE

- Stesso pattern di `orgtransform-ai`: `BaseAgent` astratto + `Orchestrator` con
  revision loop esplicito (`MAX_REVISION_CYCLES`). Non introdurre CrewAI o altri
  framework di orchestrazione: l'obiettivo è coerenza architetturale tra i
  progetti, non solo funzionalità.
- I 6 controlli di coerenza dell'Orchestrator (ricavi vs mercato, costi
  gestionali completi, affermazioni non dimostrabili, competenze vs ambizione,
  fabbisogno vs copertura, fedeltà ai dati dell'utente) sono il cuore del
  sistema — non vanno semplificati o rimossi per "velocizzare" lo sviluppo.
- L'Orchestrator NON scrive più il business plan: fa solo i controlli di
  coerenza e la decisione APPROVED/REVISION_NEEDED. La scrittura del plan è
  delegata a un secondo agente (`REPORT_WRITER_PROMPT`), invocato solo dopo
  APPROVED. Motivo: il reasoning forzato di Gemma 4 saturava una singola
  chiamata che faceva entrambe le cose. Non riunire i due prompt.
- Ogni chiamata LLM passa da `LLMService.generate()` che logga su
  `logs/llm_calls.jsonl`. Il provider è scelto da `LLM_PROVIDER` in settings.
- Nessuna API esterna per la generazione dei grafici. Il rendering è sempre
  locale (Plotly/Matplotlib), coerente con la postura privacy-first del
  progetto gemello OrgTransform AI.
