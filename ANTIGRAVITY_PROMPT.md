# Prompt da incollare in Antigravity IDE

> Istruzioni: apri Antigravity nella cartella dove vuoi creare `business-plan-ai/`,
> assicurati che `business_plan_ai_spec.md`, `AGENTS.md` e `README.md` siano
> presenti nella root del workspace, poi incolla il prompt qui sotto.

---

```
Devi scaffoldare un nuovo progetto Python chiamato "business-plan-ai" seguendo
esattamente la specifica contenuta nel file business_plan_ai_spec.md presente
in questo workspace.

Prima di scrivere qualsiasi file:
1. Leggi per intero business_plan_ai_spec.md.
2. Leggi per intero AGENTS.md — contiene l'ordine di generazione e la sezione
   CURRENT BUILD STATUS che devi aggiornare (da TODO a DONE) man mano che
   completi ogni file, non tutto insieme alla fine.
3. Usa README.md solo come riferimento di alto livello per stack e struttura,
   non come fonte di dettagli implementativi (quelli sono in
   business_plan_ai_spec.md).

Regole di esecuzione:
- Segui l'ordine indicato in AGENTS.md: struttura/config → core (types,
  prompts, intake_questions) → intake (intake_agent.py, template md,
  intake_cli.py, api/v1/intake.py) → agenti (base.py per primo, poi i 6
  agenti specialistici, poi orchestrator.py per ultimo) → servizi (llm.py,
  charts.py, web_search.py, report_builder.py) → API/modelli restanti → test.
- IntakeAgent NON eredita da BaseAgent — non "correggerlo" per farlo rientrare
  in quella gerarchia. Ha una forma diversa di proposito: produce il profilo
  invece di consumarlo e non partecipa al revision loop dell'Orchestrator.
- Fermati dopo ogni gruppo logico di file (es. dopo core/, dopo agents/) e
  riporta cosa hai creato, prima di proseguire al gruppo successivo. Non
  generare l'intero repository in un solo blocco senza checkpoint.
- Il codice dei singoli agenti (vision_agent.py, market_agent.py, team_agent.py,
  setup_agent.py, funding_agent.py) deve seguire ESATTAMENTE il pattern
  mostrato per financial_agent.py nella spec (stessa struttura di classe,
  stesso modo di chiamare self.llm.generate, stesso error handling su
  json.JSONDecodeError) — cambia solo il prompt importato e il nome
  dell'agente.
- app/services/charts.py NON deve mai chiamare l'LLM. Riceve solo strutture
  dati (le ChartSpec/charts_needed prodotte da FinancialAgent) e produce PNG
  con Plotly. Se pensi che serva un modo "più intelligente" di generare i
  grafici (es. chiedere a Gemma di descriverli in linguaggio naturale), non
  farlo: lo schema JSON strutturato definito in FINANCIAL_AGENT_PROMPT è
  già pensato per essere consumato direttamente da codice deterministico.
- MarketAgent e FundingAgent devono ricevere in iniezione anche
  web_search_service (vedi services/web_search.py) — non implementarli senza
  quella dipendenza, anche se nella prima versione la userai in modo minimo.
- Non introdurre CrewAI, LangChain o altri framework di orchestrazione: la
  logica di orchestrazione è tutta in app/agents/orchestrator.py, scritta a
  mano, per coerenza con l'architettura di orgtransform-ai.
- Al termine di ogni gruppo di file, genera anche i test corrispondenti in
  tests/ (uso mock per il client LLM, non deve dipendere da LM Studio in
  esecuzione per i test unitari).

Quando hai finito tutti i gruppi:
- Esegui pytest -q e riportami l'esito.
- Aggiorna la sezione CURRENT BUILD STATUS in AGENTS.md segnando DONE tutto
  ciò che hai effettivamente completato e testato.
- Non aggiungere funzionalità non richieste nella spec (es. non implementare
  ora il meccanismo di "bozze di risposta suggerite" per l'intake — è
  esplicitamente rimandato a una fase futura nella spec).
```
