# Business Plan AI — Sistema Multi-Agente per la Creazione di Business Plan
> Spec file per Antigravity IDE — generazione agentica dello scaffold
> Autore: Vicio Di Cara
> Versione: 1.0
> Architettura riusata da: `orgtransform_ai_spec.md` (BaseAgent + Orchestrator + revision loop)

---

## PANORAMICA DEL PROGETTO

Sistema multi-agente **locale e privacy-first** che replica il lavoro di un consulente
che affianca un aspirante imprenditore nella costruzione di un business plan completo,
partendo da un'idea grezza fino ad un documento pronto per essere presentato a
Invitalia, banche o investitori.

Il sistema prende in input un profilo di idea imprenditoriale (`BusinessIdeaProfile`)
e produce: analisi del bisogno e proposta di valore, analisi di mercato e concorrenza,
mappa delle competenze del team, inquadramento legale/operativo, piano economico-
finanziario con grafici, e piano di copertura finanziaria — assemblati in un business
plan finale (Markdown → DOCX) da un Orchestratore che verifica la coerenza incrociata
tra gli output.

**Stack:** Python, FastAPI, Pydantic v2, httpx, Plotly + Matplotlib (grafici),
python-docx (export), Redis (opzionale, memoria sessione), Docker Compose,
LM Studio / Ollama (LLM locale — Gemma 4 26B QAT, stesso modello di OrgTransform AI)

**Pattern architetturale:** identico a OrgTransform AI — pipeline multi-agente
sequenziale + parallela, con Orchestratore che implementa un revision loop
strutturato (REVISION_NEEDED → correzione mirata → nuova esecuzione → convergenza).

**Differenza chiave rispetto a `strategic-consulting-crew` (CrewAI):** qui non si usa
CrewAI. Si riusa la stessa architettura custom di OrgTransform AI (BaseAgent astratto +
Orchestrator con revision loop esplicito), per coerenza tra i tuoi progetti e perché
ti dà controllo diretto sul consistency-check, che è il cuore del meccanismo.

---

## NOTA IMPORTANTE — GENERAZIONE DEI GRAFICI

Gemma 4 26B (o qualsiasi altro LLM testuale locale) **non genera immagini**. Può
generare solo una *specifica strutturata* del grafico desiderato (tipo, etichette,
serie di valori, titolo) in formato JSON, esattamente come già fa per il resto dei
suoi output.

Il rendering effettivo (i pixel del PNG) è delegato a un modulo deterministico,
`app/services/charts.py`, che usa Plotly/Matplotlib — la stessa libreria già prevista
in `scaffold_consulting_crew.py`. Questo significa:

- **Nessuna API esterna necessaria.** Tutto gira in locale, coerente con la
  postura GDPR di OrgTransform AI (nessun dato esce dalla macchina).
- **Nessun rischio di "grafici allucinati".** L'LLM decide *quali* grafici servono
  e *quali numeri* mostrare (i numeri li ha già calcolati lui), ma il disegno è
  codice puro e deterministico — stesso principio del tuo `_strip_code_fence()`:
  non ti fidi ciecamente dell'output del modello, lo validi e lo processi.
- **Responsabilità assegnata al FinancialAgent**, perché è l'agente che già produce
  i numeri (break-even, scenari, costi) — è quello con più contesto per decidere
  quali grafici siano utili, e chi già portava questa mansione nel vecchio README.

---

## NOTA — INTAKE GUIDATO E FILE MD DI ORIGINE

Prima dei 6 agenti specialistici c'è un passo 0: la raccolta dei requisiti.
Invece di presentare all'utente un JSON vuoto da compilare, un **IntakeAgent**
dedicato pone la serie di domande approfondite (raggruppate per area — Vision,
Market, Team, Setup, Financial, Funding) tramite una CLI interattiva, e
raccoglie le risposte in un file Markdown strutturato.

Questo file `.md` è l'origine di verità grezza: da lì, lo stesso IntakeAgent
(via LLM) estrae un `BusinessIdeaProfile` strutturato — gli stessi campi che
già consumano i 6 agenti — più delle note di sezione a testo libero
(`raw_intake_notes`) per dare a ciascun agente più contesto di quanto
entrerebbe nei campi fissi del dataclass.

**Perché un agente dedicato e non un semplice form:**
- Le risposte umane sono disordinate (frasi lunghe, elenchi non uniformi,
  numeri scritti in modi diversi) — serve un LLM per normalizzarle, non un
  parser regex fragile.
- L'IntakeAgent rilascia anche un **report di intake**: un breve markdown che
  riassume cosa ha capito e segnala esplicitamente le domande lasciate vuote o
  troppo vaghe (`needs_clarification`). Questo è un cancello di verifica
  esplicito prima di lanciare la pipeline a 6 agenti (che è più lenta e più
  costosa in token) — coerente con il tuo modo di lavorare a checkpoint
  verificati uno alla volta.
- L'IntakeAgent **non fa parte del revision loop** dell'Orchestrator: il suo
  lavoro finisce prima che la pipeline principale inizi. Non eredita da
  `BaseAgent` per questo motivo — ha una forma diversa (non riceve
  `correction_context` da un supervisore, produce esso stesso l'input per gli
  altri).

---

## STRUTTURA DEL REPOSITORY

```
business-plan-ai/
├── app/
│   ├── main.py                      # FastAPI entry point
│   ├── dependencies.py
│   │
│   ├── agents/
│   │   ├── base.py                  # BaseAgent ABC (identico a OrgTransform)
│   │   ├── intake_agent.py          # Raccolta requisiti: parse md → profile + report
│   │   ├── orchestrator.py          # Pipeline + revision loop
│   │   ├── vision_agent.py          # Idea, bisogno, proposta di valore
│   │   ├── market_agent.py          # TAM/SAM/SOM, competitor, SWOT
│   │   ├── team_agent.py            # Competenze, gap, allocazione ruoli
│   │   ├── setup_agent.py           # Forma giuridica, autorizzazioni
│   │   ├── financial_agent.py       # Numeri + specifiche grafici
│   │   └── funding_agent.py         # Fabbisogno, copertura, bandi
│   │
│   ├── api/v1/
│   │   ├── intake.py                 # POST /api/v1/intake/parse
│   │   ├── business_plan.py         # POST /api/v1/business-plan
│   │   ├── report.py                # GET /api/v1/report/{plan_id}
│   │   └── health.py                # GET /health
│   │
│   ├── core/
│   │   ├── types.py                 # Dataclass di dominio
│   │   ├── prompts.py               # Tutti i system prompt (fonte unica)
│   │   └── exceptions.py
│   │
│   ├── models/
│   │   ├── requests.py              # DTO input Pydantic
│   │   └── responses.py             # DTO output Pydantic
│   │
│   ├── services/
│   │   ├── llm.py                   # Client LM Studio/Ollama (riuso da OrgTransform)
│   │   ├── charts.py                # Rendering deterministico Plotly/Matplotlib
│   │   ├── web_search.py            # Serper/DuckDuckGo per Market e Funding
│   │   ├── report_builder.py        # Markdown → DOCX (python-docx)
│   │   └── memory.py                # Redis sessione (opzionale)
│   │
│   └── config/
│       └── settings.py              # pydantic-settings da .env
│
├── data/
│   ├── knowledge_base/              # Framework statici: BMC, SWOT, Porter, ADKAR
│   ├── templates/
│   │   └── business_idea_intake_template.md   # Domande + hint, per riferimento
│   └── intake/                      # File .md compilati dall'utente (uno per progetto)
│
├── scripts/
│   └── intake_cli.py                # CLI interattiva: fa le domande, scrive l'md,
│                                     # chiama IntakeAgent.parse_brief(), mostra il report
│
├── output/
│   ├── charts/                      # PNG generati da services/charts.py
│   └── reports/                     # DOCX finali
│
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements.txt
├── AGENTS.md                        # Build guide per Antigravity (status tracking)
└── README.md
```

---

## DOMAIN TYPES — app/core/types.py

```python
from dataclasses import dataclass, field
from enum import Enum


class ProductType(str, Enum):
    PHYSICAL = "physical"
    SERVICE = "service"
    MIXED = "mixed"


class RevisionStatus(str, Enum):
    APPROVED = "APPROVED"
    REVISION_NEEDED = "REVISION_NEEDED"
    REJECTED = "REJECTED"


@dataclass
class FounderProfile:
    name: str
    skills: list[str]                   # es. ["produzione", "ricette", "rete distributiva"]
    availability: str                   # es. "full-time", "part-time 20h/settimana"


@dataclass
class BusinessIdeaProfile:
    project_name: str
    idea_description: str               # descrizione libera dell'idea imprenditoriale
    need_addressed: str                 # il bisogno concreto che si vuole soddisfare
    product_type: ProductType
    sector_hint: str                    # es. "food & beverage artigianale"
    target_region: str                  # area geografica di partenza
    founders: list[FounderProfile]
    available_capital_eur: float        # quota propria disponibile (regola 25-30%)
    desired_timeline_months: int
    notes: str = ""
    raw_intake_notes: dict[str, str] = field(default_factory=dict)
    # chiavi: "vision" | "market" | "team" | "setup" | "financial" | "funding"
    # valori: sintesi fedele delle risposte grezze di quella sezione dell'intake,
    # passata come contesto extra ai singoli agenti oltre ai campi fissi sopra.


@dataclass
class IntakeReport:
    """Prodotto da IntakeAgent.parse_brief(). È il cancello di verifica prima
    di lanciare la pipeline a 6 agenti — non entra nel revision loop
    dell'Orchestrator."""
    profile: "BusinessIdeaProfile"
    needs_clarification: list[str]      # domande lasciate vuote o troppo vaghe
    summary_markdown: str               # riassunto leggibile per l'utente
    confidence: float


@dataclass
class ChartSpec:
    """Specifica strutturata di un grafico prodotta dal FinancialAgent.
    Il rendering (i pixel) è delegato a services/charts.py — nessun LLM
    genera immagini direttamente, solo questa struttura dati."""
    chart_type: str                     # "bar" | "line" | "pie" | "waterfall" | "table"
    title: str
    labels: list[str]
    series: dict[str, list[float]]      # nome_serie -> valori
    filename: str                       # es. "break_even_analysis"


@dataclass
class AgentOutput:
    agent_name: str
    status: str                         # "success" | "error"
    data: dict
    confidence: float
    reasoning: str
    revision_count: int = 0


@dataclass
class OrchestratorResult:
    plan_id: str
    profile: BusinessIdeaProfile
    agent_outputs: dict[str, AgentOutput]
    revision_log: list[dict]
    charts_generated: list[str]         # path dei PNG effettivamente renderizzati
    business_plan_markdown: str
    business_plan_docx_path: str
    total_iterations: int
    status: RevisionStatus
```

---

## SYSTEM PROMPTS — app/core/prompts.py

```python
INTAKE_AGENT_PROMPT = """
Sei un assistente che trasforma le risposte grezze di un aspirante imprenditore
(raccolte in un file Markdown, sezione per sezione) in un profilo strutturato
per un sistema di consulenza multi-agente.

Il file Markdown in ingresso è organizzato in 6 sezioni, con questi header
esatti (potrebbero avere spazi o numerazione leggermente diversi, gestiscili
con tolleranza):
"Vision", "Market", "Team", "Setup", "Financial", "Funding"

Il tuo compito:

1. ESTRAI i campi strutturati:
   - project_name: se non è dichiarato esplicitamente, deducilo dalla
     descrizione dell'idea; se non è deducibile con sicurezza, usa una stringa
     provvisoria e aggiungilo a needs_clarification.
   - idea_description, need_addressed, product_type (physical/service/mixed),
     sector_hint, target_region
   - founders: elenco con name, skills (lista), availability — da come sono
     descritti nella sezione Team
   - available_capital_eur: numero, dalla sezione Funding
   - desired_timeline_months: numero, dalla sezione Setup o Financial
   - notes: qualsiasi informazione rilevante che non rientra negli altri campi

2. Per ciascuna delle 6 sezioni, produci in raw_section_notes una sintesi
   fedele (3-6 frasi) di quello che l'utente ha scritto — NON il testo
   verbatim completo, ma nemmeno un'interpretazione che aggiunge informazioni
   non presenti.

3. NEEDS_CLARIFICATION: elenca ogni domanda che risulta non risposta, risposta
   con "non so"/vuoto, o troppo vaga per essere usata (es. "vedremo" per il
   capitale disponibile). Sii specifico: indica la sezione e la domanda, non
   solo "manca qualcosa".

4. SUMMARY: un riassunto in italiano, colloquiale, di massimo 150 parole, che
   ripete all'utente cosa hai capito della sua idea — utile per fargli
   confermare prima di lanciare la pipeline completa.

Regole:
- Non inventare mai numeri o fatti non presenti nel testo. Se un campo
  numerico non è ricavabile, mettilo a 0 e segnalalo in needs_clarification.
- Se l'utente ha risposto usando esempi (es. quelli suggeriti nel template
  di intake) invece di risposte proprie, trattali come needs_clarification,
  non come dati reali del suo progetto.
- Output solo JSON valido. Nessun markdown, nessun preambolo.

Schema di output:
{
  "project_name": str,
  "idea_description": str,
  "need_addressed": str,
  "product_type": "physical" | "service" | "mixed",
  "sector_hint": str,
  "target_region": str,
  "founders": [{"name": str, "skills": [str], "availability": str}],
  "available_capital_eur": float,
  "desired_timeline_months": int,
  "notes": str,
  "raw_section_notes": {
    "vision": str, "market": str, "team": str,
    "setup": str, "financial": str, "funding": str
  },
  "needs_clarification": [str],
  "summary_markdown": str,
  "confidence": float
}
"""

VISION_AGENT_PROMPT = """
Sei un consulente esperto in ideazione imprenditoriale e proposta di valore.

Data la descrizione di un'idea di business, il bisogno che vuole soddisfare e il
contesto del fondatore, produci:

1. NEED_VALIDATION: il bisogno descritto è chiaro e specifico? Se è vago, segnalalo
   in NEEDS_CLARIFICATION invece di inventare dettagli.
2. VALUE_PROPOSITION: proposta di valore in una frase (per chi, cosa, perché meglio)
3. DIFFERENTIATION: cosa rende l'idea diversa/migliore rispetto a soluzioni esistenti
4. BUSINESS_MODEL_CANVAS_LITE: 4 blocchi essenziali (segmenti clienti, value
   proposition, canali principali, flussi di ricavo) — versione sintetica, non i 9
   blocchi completi
5. RISK_FLAGS: se la proposta sembra un'idea "senza bisogno reale" dietro
   (soluzione in cerca di un problema), segnalalo esplicitamente

Regole:
- Non usare linguaggio da consulente generico ("sinergie", "leva strategica").
- Se l'idea è ancora troppo grezza per essere valutata, chiedi chiarimenti invece
  di riempire i vuoti con supposizioni.
- Output solo JSON valido. Nessun markdown, nessun preambolo.

Schema di output:
{
  "need_validation": {"is_clear": bool, "comment": str},
  "value_proposition": str,
  "differentiation": str,
  "business_model_canvas_lite": {
    "customer_segments": [str],
    "value_proposition": str,
    "channels": [str],
    "revenue_streams": [str]
  },
  "risk_flags": [str],
  "needs_clarification": [str],
  "confidence": float
}
"""

MARKET_AGENT_PROMPT = """
Sei un analista di mercato senior. Sai distinguere dati verificati da stime, e citi
sempre le fonti quando disponibili (via web search).

Dato il profilo dell'idea di business, produci:

1. MARKET_SIZING: stima di TAM/SAM/SOM — parti SEMPRE dal mercato locale/regionale
   raggiungibile nei primi 12 mesi (SOM), non dal mercato globale
2. TRENDS: 2-3 trend recenti rilevanti per il settore (a favore o contro)
3. COMPETITORS: 3-5 competitor diretti o indiretti, con punti di forza/debolezza
4. SWOT: analisi SWOT del progetto rispetto al mercato
5. ENTRY_BARRIERS: barriere all'ingresso specifiche del settore

Regole:
- Se hai accesso a web search, usalo per dati di mercato reali e recenti; altrimenti
  segnala chiaramente quali numeri sono stime e su quali basi.
- Non gonfiare il TAM per sembrare più attraente: preferisci stime prudenti.
- Output solo JSON valido. Nessun markdown, nessun preambolo.

Schema di output:
{
  "market_sizing": {"tam_eur": str, "sam_eur": str, "som_eur": str, "rationale": str},
  "trends": [{"trend": str, "direction": str, "impact": str}],
  "competitors": [{"name": str, "strengths": str, "weaknesses": str}],
  "swot": {"strengths": [str], "weaknesses": [str], "opportunities": [str], "threats": [str]},
  "entry_barriers": [str],
  "sources_used": [str],
  "confidence": float
}
"""

TEAM_AGENT_PROMPT = """
Sei uno specialista di organizzazione di team per startup e piccole imprese.

Dato l'elenco dei fondatori (competenze e disponibilità) e l'idea di business,
produci:

1. SKILLS_COVERAGE: quali competenze necessarie per l'idea sono già coperte dal team
2. SKILLS_GAP: quali competenze critiche mancano
3. GAP_STRATEGY: per ogni gap, se conviene assumere, esternalizzare, o cercare un socio
4. WORKLOAD_FEASIBILITY: la disponibilità dichiarata (full-time/part-time) è
   sufficiente per l'ambizione del progetto? Segnala se c'è disallineamento
5. GOVERNANCE_FLAG: se non è chiaro come si dividono le quote o le decisioni tra i
   soci, segnalalo come rischio (non inventare una ripartizione)

Regole:
- Aziende piccole/startup non hanno capacità di PMO strutturata: non assumere
  risorse enterprise.
- Non presumere competenze non dichiarate.
- Output solo JSON valido. Nessun markdown, nessun preambolo.

Schema di output:
{
  "skills_coverage": [{"skill_needed": str, "covered_by": str}],
  "skills_gap": [{"skill": str, "criticality": str}],
  "gap_strategy": [{"skill": str, "recommendation": str, "rationale": str}],
  "workload_feasibility": {"feasible": bool, "comment": str},
  "governance_flag": str,
  "confidence": float
}
"""

SETUP_AGENT_PROMPT = """
Sei un esperto di adempimenti legali e operativi per l'avvio di micro/piccole
imprese in Italia.

Dato il tipo di prodotto/servizio e il settore, produci:

1. LEGAL_FORM: forma giuridica consigliata (SRL, SRLS, impresa sociale,
   cooperativa...) con motivazione
2. AUTHORIZATIONS: autorizzazioni/permessi specifici necessari (es. sanitarie,
   HACCP, SCIA, ambientali) in base al settore dichiarato
3. REQUIRED_STEPS: sequenza di adempimenti (partita IVA, iscrizione Registro
   Imprese, Camera di Commercio, INPS/INAIL, dichiarazione al Comune)
4. TIMELINE_ESTIMATE: stima realistica dei tempi burocratici prima di poter
   iniziare a vendere
5. LOCATION_REQUIREMENTS: se il settore richiede requisiti specifici per il
   luogo (es. laboratorio certificato per alimentare)

Regole:
- Non inventare normative specifiche di regioni/comuni che non conosci con
  certezza — segnala di verificare con il Comune/Camera di Commercio locale.
- Sii specifico sul settore dichiarato, non generico.
- Output solo JSON valido. Nessun markdown, nessun preambolo.

Schema di output:
{
  "legal_form": {"recommended": str, "rationale": str},
  "authorizations": [{"name": str, "why_needed": str}],
  "required_steps": [{"step": str, "order": int}],
  "timeline_estimate_months": str,
  "location_requirements": [str],
  "verify_locally": [str],
  "confidence": float
}
"""

FINANCIAL_AGENT_PROMPT = """
Sei un consulente esperto in modellazione finanziaria per micro/piccole imprese.

Dato il piano (idea, mercato, team, setup legale), produci:

1. COST_BREAKDOWN: costi fissi vs variabili, diretti vs indiretti (non dimenticare
   costi indiretti come commercialista, pulizie, utenze — è un errore comune)
2. PRICING: prezzo di vendita proposto e margine per unità
3. BREAK_EVEN: volume di vendita necessario per coprire i costi fissi
4. SCENARIOS: proiezioni a 3 anni in scenario base/ottimistico/pessimistico
5. INITIAL_CAPITAL: capitale iniziale necessario, voce per voce
6. PAYBACK_PERIOD: stima prudente del tempo di recupero dell'investimento
7. ASSUMPTIONS: lista esplicita di tutte le assunzioni usate (non nasconderle
   nei numeri arrotondati)
8. CHARTS_NEEDED: specifica quali grafici aiuterebbero a comunicare questi numeri.
   Per ciascuno fornisci chart_type, title, labels e series con i valori numerici
   già calcolati sopra. Il rendering effettivo verrà fatto da codice esterno,
   tu fornisci solo la struttura dati.

Regole:
- Usa stime conservative. Proiezioni di ROI troppo ottimistiche distruggono la
  credibilità del business plan (è l'errore più comune negli aspiranti imprenditori).
- Non sovrastimare i ricavi rispetto al SOM fornito da MarketAgent nel contesto.
- Output solo JSON valido. Nessun markdown, nessun preambolo.

Schema di output:
{
  "cost_breakdown": {
    "fixed_costs_eur_month": [{"item": str, "amount": float}],
    "variable_costs_per_unit_eur": [{"item": str, "amount": float}],
    "indirect_costs_eur_month": [{"item": str, "amount": float}]
  },
  "pricing": {"unit_price_eur": float, "unit_margin_eur": float},
  "break_even": {"units_per_month": float, "rationale": str},
  "scenarios": [
    {"scenario": str, "year1_revenue_eur": float, "year2_revenue_eur": float, "year3_revenue_eur": float}
  ],
  "initial_capital": [{"item": str, "amount_eur": float}],
  "payback_period_months": str,
  "assumptions": [str],
  "charts_needed": [
    {
      "chart_type": "bar|line|pie|waterfall|table",
      "title": str,
      "labels": [str],
      "series": {"nome_serie": [float]},
      "filename": str
    }
  ],
  "confidence": float
}
"""

FUNDING_AGENT_PROMPT = """
Sei un consulente specializzato in finanziamenti per startup e PMI italiane
(Invitalia, bandi regionali/europei, incubatori, prestiti bancari).

Dato il capitale iniziale necessario (da FinancialAgent) e il capitale proprio
disponibile, produci:

1. FUNDING_GAP: differenza tra fabbisogno totale e capitale proprio disponibile
2. OWN_CAPITAL_CHECK: verifica se il capitale proprio copre almeno il 25-30% del
   fabbisogno (regola empirica citata da imprenditori reali) — se no, segnalalo
3. FUNDING_SOURCES: opzioni pertinenti (Invitalia, bandi, incubatori, prestiti,
   fondazioni) — usa web search per verificare bandi attivi al momento, se
   disponibile, altrimenti indica categorie generiche da verificare
4. RECOMMENDED_MIX: combinazione consigliata di fonti, con priorità e motivazione
5. CONTINGENCY: piano se il finanziamento arriva solo parzialmente

Regole:
- Non inventare nomi specifici di bandi se non li hai verificati via ricerca web:
  in assenza di dati recenti, descrivi la categoria e invita a verificare.
- Preferisci fondo perduto/agevolato prima di equity, se non specificato altrimenti.
- Output solo JSON valido. Nessun markdown, nessun preambolo.

Schema di output:
{
  "funding_gap_eur": float,
  "own_capital_check": {"meets_25_30_rule": bool, "comment": str},
  "funding_sources": [{"type": str, "description": str, "verified_current": bool}],
  "recommended_mix": [{"source": str, "priority": int, "rationale": str}],
  "contingency_plan": str,
  "confidence": float
}
"""

ORCHESTRATOR_PROMPT = """
Sei il senior partner di un team di consulenza. Hai ricevuto gli output di sei
agenti specialistici che hanno analizzato un'idea di business.

I tuoi compiti, in ordine:

STEP 1 — CONSISTENCY CHECK
Verifica la coerenza interna tra tutti gli output, in particolare questi 5 controlli
(derivati da errori reali osservati in imprenditori alle prime armi):

1. RICAVI VS MERCATO: i ricavi previsti da FinancialAgent superano il SOM stimato
   da MarketAgent? Se sì, è un'incoerenza da correggere.
2. COSTI GESTIONALI COMPLETI: FinancialAgent ha incluso i costi indiretti
   (commercialista, pulizie, utenze) o li ha dimenticati?
3. AFFERMAZIONI NON DIMOSTRABILI: ci sono claim ottimistici in qualsiasi agente
   senza un dato o un'assunzione esplicita a supporto?
4. COMPETENZE VS AMBIZIONE: il piano (Financial/Funding) richiede competenze che
   TeamAgent non ha mappato come coperte o gap-strategy?
5. FABBISOGNO VS COPERTURA: il capitale proprio rispetta la regola del 25-30% del
   fabbisogno totale (own_capital_check di FundingAgent)? Se no, e non è già
   segnalato, va evidenziato.

STEP 2 — CONTRADDIZIONI DIRETTE
Identifica altre contraddizioni dirette tra agenti (es. SetupAgent richiede
autorizzazione sanitaria ma FinancialAgent non ha budget per quel costo).

STEP 3 — DECISIONE DI REVISIONE
Per ogni incoerenza trovata:
- Emetti REVISION_NEEDED per l'agente/gli agenti responsabili
- Fornisci una CORRECTION_CONTEXT che spiega esattamente cosa correggere e perché
- Emetti APPROVED solo quando tutti gli output sono internamente coerenti

STEP 4 — BUSINESS PLAN FINALE (solo se APPROVED)
Sintetizza tutti gli output in un business plan Markdown unificato con queste
sezioni:
1. Executive Summary (max 200 parole)
2. L'Idea e la Proposta di Valore
3. Analisi di Mercato e Concorrenza
4. Il Team
5. Inquadramento Legale e Operativo
6. Piano Economico-Finanziario (con riferimenti ai grafici da includere)
7. Piano di Copertura Finanziaria
8. Prossimi Passi (azioni immediate nei prossimi 30 giorni)

Nella sezione 6, indica esplicitamente quali file immagine (dai charts_needed di
FinancialAgent) vanno incorporati e dove.

Output solo JSON valido. Nessun wrapper markdown attorno al JSON.

Schema di output:
{
  "status": "APPROVED" | "REVISION_NEEDED",
  "revisions_needed": [
    {"agent": str, "issue": str, "correction_context": str}
  ],
  "business_plan_markdown": str,
  "confidence_overall": float,
  "iteration": int
}
"""
```

---

## BANCA DOMANDE DI INTAKE — app/core/intake_questions.py

```python
"""
Domande approfondite per la CLI di intake, raggruppate per sezione.
Ogni voce ha una domanda e un hint breve (non una risposta completa: deve
restare un aiuto a orientarsi, non un esempio da copiare). Riusato sia dallo
script CLI (per porre le domande) sia dal generatore del template md.
"""

INTAKE_QUESTIONS: dict[str, list[dict[str, str]]] = {
    "Vision": [
        {"question": "Qual è il bisogno concreto e come l'hai scoperto?",
         "hint": "Es. un'osservazione diretta, una mancanza che vivi tu stesso"},
        {"question": "Cosa esiste già per questo bisogno, e quali sono i suoi limiti?",
         "hint": "Alternative attuali, anche imperfette"},
        {"question": "Proposta di valore in una frase (per chi, cosa, perché meglio)?",
         "hint": "Una frase sola, senza tecnicismi"},
        {"question": "Cosa ti rende unico rispetto a chi fa già qualcosa di simile?",
         "hint": ""},
        {"question": "Se dovessi tagliare 2 idee collaterali per concentrarti sul core, quali terresti?",
         "hint": "Aiuta a capire le priorità reali"},
    ],
    "Market": [
        {"question": "Chi è il cliente ideale, descritto come persona reale?",
         "hint": "Età, comportamento, dove lo trovi"},
        {"question": "Dove si trova il primo mercato, e quanto è grande realisticamente?",
         "hint": "Non il mercato globale — il primo passo concreto"},
        {"question": "Chi sono 3-5 concorrenti diretti o indiretti, e cosa fanno bene/male?",
         "hint": ""},
        {"question": "Quali barriere all'ingresso esistono?",
         "hint": "Autorizzazioni, fiducia del mercato, capitale iniziale..."},
        {"question": "Che trend stai cavalcando o contro cui vai?",
         "hint": ""},
    ],
    "Team": [
        {"question": "Chi sono i soci e cosa porta ciascuno?",
         "hint": "Competenze tecniche, gestionali, operative"},
        {"question": "Quali competenze critiche mancano oggi?",
         "hint": ""},
        {"question": "Per ogni competenza mancante: assumi, esternalizzi, o cerchi un socio?",
         "hint": ""},
        {"question": "Quanto tempo può dedicare ciascun socio?",
         "hint": "Full-time, part-time, ore/settimana"},
        {"question": "Come gestite in anticipo un possibile disaccordo tra soci?",
         "hint": "Quote, decisioni, patti"},
    ],
    "Setup": [
        {"question": "Prodotto fisico, servizio, o misto?", "hint": ""},
        {"question": "Servono autorizzazioni specifiche?",
         "hint": "Sanitarie, HACCP, ambientali..."},
        {"question": "Che forma giuridica hai in mente, e perché?",
         "hint": "SRL, SRLS, impresa sociale, cooperativa..."},
        {"question": "Dove si svolgerà l'attività? È già disponibile?", "hint": ""},
        {"question": "Hai stimato la tempistica burocratica prima di poter vendere?", "hint": ""},
    ],
    "Financial": [
        {"question": "Costi fissi mensili una volta avviati?",
         "hint": "Affitto, utenze, eventuali stipendi"},
        {"question": "Costi variabili per unità di prodotto/servizio?", "hint": ""},
        {"question": "Prezzo di vendita, e a chi?", "hint": ""},
        {"question": "Break-even stimato?",
         "hint": "Quante unità/mese per coprire i costi fissi"},
        {"question": "Capitale iniziale necessario, voce per voce?", "hint": ""},
        {"question": "Tempo di recupero dell'investimento (stima prudente)?", "hint": ""},
    ],
    "Funding": [
        {"question": "Quanto puoi mettere di tuo (idealmente il 25-30% del fabbisogno)?", "hint": ""},
        {"question": "Prestito, equity, o fondo perduto?", "hint": ""},
        {"question": "Sei disposto ad adattare il progetto per accedere a un bando?", "hint": ""},
        {"question": "Hai già contattato Invitalia, incubatori, banche?", "hint": ""},
        {"question": "Hai un piano B se il finanziamento arriva solo in parte?", "hint": ""},
    ],
}
```

---

## AGENT BASE CLASS — app/agents/base.py

```python
from abc import ABC, abstractmethod
from app.core.types import AgentOutput, BusinessIdeaProfile


class BaseAgent(ABC):
    def __init__(self, llm_service, name: str):
        self.llm = llm_service
        self.name = name

    @abstractmethod
    async def process(
        self,
        profile: BusinessIdeaProfile,
        context: dict | None = None,
        correction_context: str | None = None
    ) -> AgentOutput:
        pass

    def _build_user_message(
        self,
        profile: BusinessIdeaProfile,
        context: dict | None,
        correction: str | None
    ) -> str:
        founders_str = "; ".join(
            f"{f.name} ({', '.join(f.skills)}, {f.availability})"
            for f in profile.founders
        )
        msg = f"""
PROFILO IDEA DI BUSINESS:
- Nome progetto: {profile.project_name}
- Descrizione idea: {profile.idea_description}
- Bisogno da soddisfare: {profile.need_addressed}
- Tipo prodotto/servizio: {profile.product_type.value}
- Settore: {profile.sector_hint}
- Area geografica target: {profile.target_region}
- Fondatori: {founders_str}
- Capitale proprio disponibile: {profile.available_capital_eur} EUR
- Timeline desiderata: {profile.desired_timeline_months} mesi
- Note: {profile.notes}
"""
        if profile.raw_intake_notes:
            section_key = self.name.lower().replace("agent", "")
            note = profile.raw_intake_notes.get(section_key, "")
            if note:
                msg += f"\nNOTE GREZZE DELL'UTENTE PER QUESTA AREA (dall'intake):\n{note}\n"

        if context:
            msg += f"\nOUTPUT DEGLI AGENTI A MONTE (per riferimento):\n{context}\n"

        if correction:
            msg += f"\nCORREZIONE RICHIESTA DAL SUPERVISORE:\n{correction}\n"
            msg += "Rivedi il tuo output precedente correggendo quanto sopra.\n"

        return msg
```

---

## INTAKE AGENT — app/agents/intake_agent.py

```python
"""
IntakeAgent non eredita da BaseAgent: la sua forma è diversa (produce il
BusinessIdeaProfile invece di consumarlo, e non partecipa al revision loop
dell'Orchestrator). Ha due responsabilità: generare il template delle domande
e, dato un md compilato, estrarne un profilo strutturato + un report.
"""
import json
from app.core.intake_questions import INTAKE_QUESTIONS
from app.core.prompts import INTAKE_AGENT_PROMPT
from app.core.types import BusinessIdeaProfile, FounderProfile, IntakeReport, ProductType


class IntakeAgent:
    def __init__(self, llm_service):
        self.llm = llm_service
        self.name = "IntakeAgent"

    def generate_template_markdown(self) -> str:
        """Genera il template .md con tutte le domande, raggruppate per
        sezione. Usato sia dalla CLI (per stampare le domande) sia per
        produrre un file scaricabile via API."""
        lines = ["# Business Plan — Modulo di Intake",
                 "> Compila ogni sezione. Gli hint tra parentesi sono solo "
                 "orientativi: non copiarli come risposta.\n"]
        for section, questions in INTAKE_QUESTIONS.items():
            lines.append(f"## {section}")
            for q in questions:
                lines.append(f"**{q['question']}**")
                if q["hint"]:
                    lines.append(f"*(hint: {q['hint']})*")
                lines.append("> Risposta: \n")
            lines.append("")
        return "\n".join(lines)

    async def parse_brief(self, raw_markdown: str) -> IntakeReport:
        """Estrae un BusinessIdeaProfile strutturato da un file .md compilato
        dall'utente, e produce l'IntakeReport (cancello di verifica prima
        della pipeline a 6 agenti)."""
        raw = await self.llm.generate(
            system_prompt=INTAKE_AGENT_PROMPT,
            user_message=raw_markdown,
            temperature=0.1,
            max_tokens=3000
        )
        data = json.loads(raw)  # se fallisce, propaga l'errore: qui non c'è
                                 # un correction_context a cui appoggiarsi,
                                 # meglio far fallire esplicitamente e far
                                 # ricompilare l'intake che indovinare

        profile = BusinessIdeaProfile(
            project_name=data["project_name"],
            idea_description=data["idea_description"],
            need_addressed=data["need_addressed"],
            product_type=ProductType(data["product_type"]),
            sector_hint=data["sector_hint"],
            target_region=data["target_region"],
            founders=[FounderProfile(**f) for f in data["founders"]],
            available_capital_eur=data["available_capital_eur"],
            desired_timeline_months=data["desired_timeline_months"],
            notes=data.get("notes", ""),
            raw_intake_notes=data.get("raw_section_notes", {})
        )

        return IntakeReport(
            profile=profile,
            needs_clarification=data.get("needs_clarification", []),
            summary_markdown=data.get("summary_markdown", ""),
            confidence=data.get("confidence", 0.5)
        )
```

---

## CLI DI INTAKE — scripts/intake_cli.py

```python
"""
CLI interattiva: pone le domande di INTAKE_QUESTIONS una per una, raccoglie
le risposte, scrive l'md in data/intake/, chiama IntakeAgent.parse_brief() e
mostra il report. Stesso stile Typer + Rich già usato in
strategic-consulting-crew.

Uso:
    python -m scripts.intake_cli
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.prompt import Prompt
from rich.markdown import Markdown

from app.core.intake_questions import INTAKE_QUESTIONS
from app.services.llm import LLMService
from app.agents.intake_agent import IntakeAgent

app = typer.Typer()
console = Console()


@app.command()
def run():
    console.print("[bold cyan]Business Plan AI — Intake guidato[/]\n")

    answers_md = ["# Business Plan — Intake compilato\n"]
    for section, questions in INTAKE_QUESTIONS.items():
        console.print(f"\n[bold yellow]— {section} —[/]")
        answers_md.append(f"## {section}")
        for q in questions:
            if q["hint"]:
                console.print(f"[dim]({q['hint']})[/]")
            answer = Prompt.ask(q["question"])
            answers_md.append(f"**{q['question']}**")
            answers_md.append(f"> Risposta: {answer}\n")

    raw_markdown = "\n".join(answers_md)

    Path("data/intake").mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = Path("data/intake") / f"intake_{timestamp}.md"
    out_path.write_text(raw_markdown, encoding="utf-8")
    console.print(f"\n[green]Salvato:[/] {out_path}")

    console.print("\n[bold cyan]Estrazione ed elaborazione del report...[/]")
    llm = LLMService()
    intake_agent = IntakeAgent(llm)
    report = asyncio.run(intake_agent.parse_brief(raw_markdown))

    console.print(Markdown(report.summary_markdown))

    if report.needs_clarification:
        console.print("\n[bold red]Punti da chiarire prima di procedere:[/]")
        for item in report.needs_clarification:
            console.print(f"  - {item}")
        console.print(
            "\n[yellow]Consiglio: rispondi a questi punti prima di lanciare "
            "la pipeline completa (più lenta e più costosa in token).[/]"
        )
    else:
        console.print("\n[green]Nessun punto critico segnalato.[/]")

    console.print(f"\n[dim]Profilo estratto per: {report.profile.project_name}[/]")
    console.print("[dim]Usa questo profilo con Orchestrator.run(profile) "
                   "oppure passa data/intake/*.md a POST /api/v1/intake/parse.[/]")


if __name__ == "__main__":
    app()
```

---

## FINANCIAL AGENT (esempio completo, incluso l'output dei grafici) — app/agents/financial_agent.py

```python
import json
from app.agents.base import BaseAgent
from app.core.types import AgentOutput, BusinessIdeaProfile
from app.core.prompts import FINANCIAL_AGENT_PROMPT


class FinancialAgent(BaseAgent):
    def __init__(self, llm_service):
        super().__init__(llm_service, "FinancialAgent")

    async def process(
        self,
        profile: BusinessIdeaProfile,
        context: dict | None = None,
        correction_context: str | None = None
    ) -> AgentOutput:
        user_message = self._build_user_message(profile, context, correction_context)
        raw = await self.llm.generate(
            system_prompt=FINANCIAL_AGENT_PROMPT,
            user_message=user_message,
            temperature=0.2,
            max_tokens=3000
        )
        try:
            data = json.loads(raw)
            # NOTA: data["charts_needed"] contiene solo le SPECIFICHE dei grafici
            # (dati + tipo + titolo). Il rendering vero avviene in
            # services/charts.py, chiamato dall'Orchestrator dopo APPROVED —
            # questo agente non disegna nulla, produce solo la struttura dati.
            return AgentOutput(
                agent_name=self.name,
                status="success",
                data=data,
                confidence=data.get("confidence", 0.7),
                reasoning="Modello economico-finanziario completato.",
                revision_count=1 if correction_context else 0
            )
        except json.JSONDecodeError:
            return AgentOutput(
                agent_name=self.name,
                status="error",
                data={"raw": raw},
                confidence=0.0,
                reasoning="Parsing JSON fallito."
            )
```

> Ripeti lo stesso pattern per VisionAgent, MarketAgent, TeamAgent, SetupAgent,
> FundingAgent. Ognuno usa la propria costante di prompt da `prompts.py` e lo
> stesso `BaseAgent._build_user_message()`. MarketAgent e FundingAgent, in più,
> ricevono in iniezione anche `web_search_service` per dati real-time (vedi
> `services/web_search.py`).

---

## ORCHESTRATOR — app/agents/orchestrator.py

```python
import json
import uuid
from app.agents.vision_agent import VisionAgent
from app.agents.market_agent import MarketAgent
from app.agents.team_agent import TeamAgent
from app.agents.setup_agent import SetupAgent
from app.agents.financial_agent import FinancialAgent
from app.agents.funding_agent import FundingAgent
from app.core.types import (
    AgentOutput, BusinessIdeaProfile, OrchestratorResult, RevisionStatus
)
from app.core.prompts import ORCHESTRATOR_PROMPT
from app.services.charts import render_chart_specs
from app.services.report_builder import markdown_to_docx


MAX_REVISION_CYCLES = 3


class Orchestrator:
    def __init__(self, llm_service, web_search_service=None):
        self.llm = llm_service
        self.vision_agent = VisionAgent(llm_service)
        self.market_agent = MarketAgent(llm_service, web_search_service)
        self.team_agent = TeamAgent(llm_service)
        self.setup_agent = SetupAgent(llm_service)
        self.financial_agent = FinancialAgent(llm_service)
        self.funding_agent = FundingAgent(llm_service, web_search_service)

    async def run(self, profile: BusinessIdeaProfile) -> OrchestratorResult:
        plan_id = str(uuid.uuid4())[:8]
        revision_log = []

        # --- FASE 1: agenti paralleli (nessuna dipendenza tra loro) ---
        vision_out = await self.vision_agent.process(profile)
        market_out = await self.market_agent.process(profile)
        team_out = await self.team_agent.process(profile)
        setup_out = await self.setup_agent.process(profile)

        # --- FASE 2: FinancialAgent dipende dagli output di fase 1 ---
        upstream_context = {
            "vision": vision_out.data,
            "market": market_out.data,
            "team": team_out.data,
            "setup": setup_out.data
        }
        financial_out = await self.financial_agent.process(profile, context=upstream_context)

        # --- FASE 3: FundingAgent dipende da Financial ---
        funding_context = {**upstream_context, "financial": financial_out.data}
        funding_out = await self.funding_agent.process(profile, context=funding_context)

        agent_outputs = {
            "vision": vision_out,
            "market": market_out,
            "team": team_out,
            "setup": setup_out,
            "financial": financial_out,
            "funding": funding_out
        }

        # --- FASE 4: validation loop dell'Orchestratore ---
        for iteration in range(1, MAX_REVISION_CYCLES + 1):
            orchestrator_raw = await self.llm.generate(
                system_prompt=ORCHESTRATOR_PROMPT,
                user_message=self._build_orchestrator_message(profile, agent_outputs, iteration),
                temperature=0.1,
                max_tokens=5000
            )

            try:
                orch_data = json.loads(orchestrator_raw)
            except json.JSONDecodeError:
                break

            if orch_data.get("status") == "APPROVED":
                # Rendering deterministico dei grafici — SOLO qui, dopo APPROVED
                chart_specs = financial_out.data.get("charts_needed", [])
                charts_generated = render_chart_specs(chart_specs)

                markdown = orch_data.get("business_plan_markdown", "")
                docx_path = markdown_to_docx(
                    markdown, chart_paths=charts_generated,
                    output_filename=f"business_plan_{plan_id}.docx"
                )

                return OrchestratorResult(
                    plan_id=plan_id,
                    profile=profile,
                    agent_outputs=agent_outputs,
                    revision_log=revision_log,
                    charts_generated=charts_generated,
                    business_plan_markdown=markdown,
                    business_plan_docx_path=docx_path,
                    total_iterations=iteration,
                    status=RevisionStatus.APPROVED
                )

            # REVISION_NEEDED: rilancia gli agenti indicati con correction_context
            revisions = orch_data.get("revisions_needed", [])
            revision_log.append({"iteration": iteration, "revisions": revisions})

            for rev in revisions:
                agent_name = rev["agent"].lower().replace("agent", "").strip()
                correction = rev["correction_context"]

                if agent_name == "vision":
                    agent_outputs["vision"] = await self.vision_agent.process(
                        profile, correction_context=correction)
                elif agent_name == "market":
                    agent_outputs["market"] = await self.market_agent.process(
                        profile, correction_context=correction)
                elif agent_name == "team":
                    agent_outputs["team"] = await self.team_agent.process(
                        profile, correction_context=correction)
                elif agent_name == "setup":
                    agent_outputs["setup"] = await self.setup_agent.process(
                        profile, correction_context=correction)
                elif agent_name == "financial":
                    agent_outputs["financial"] = await self.financial_agent.process(
                        profile,
                        context={k: v.data for k, v in agent_outputs.items()
                                 if k in ("vision", "market", "team", "setup")},
                        correction_context=correction)
                elif agent_name == "funding":
                    agent_outputs["funding"] = await self.funding_agent.process(
                        profile,
                        context={k: v.data for k, v in agent_outputs.items() if k != "funding"},
                        correction_context=correction)

        # Max iterazioni raggiunte
        return OrchestratorResult(
            plan_id=plan_id,
            profile=profile,
            agent_outputs=agent_outputs,
            revision_log=revision_log,
            charts_generated=[],
            business_plan_markdown="Numero massimo di cicli di revisione raggiunto. Revisione manuale richiesta.",
            business_plan_docx_path="",
            total_iterations=MAX_REVISION_CYCLES,
            status=RevisionStatus.REVISION_NEEDED
        )

    def _build_orchestrator_message(
        self, profile: BusinessIdeaProfile, outputs: dict[str, AgentOutput], iteration: int
    ) -> str:
        return f"""
PROGETTO: {profile.project_name} | Settore: {profile.sector_hint}
ITERAZIONE: {iteration}

OUTPUT DEGLI AGENTI:

[VISION_AGENT]
{json.dumps(outputs['vision'].data, indent=2, ensure_ascii=False)}

[MARKET_AGENT]
{json.dumps(outputs['market'].data, indent=2, ensure_ascii=False)}

[TEAM_AGENT]
{json.dumps(outputs['team'].data, indent=2, ensure_ascii=False)}

[SETUP_AGENT]
{json.dumps(outputs['setup'].data, indent=2, ensure_ascii=False)}

[FINANCIAL_AGENT]
{json.dumps(outputs['financial'].data, indent=2, ensure_ascii=False)}

[FUNDING_AGENT]
{json.dumps(outputs['funding'].data, indent=2, ensure_ascii=False)}

Esegui tutti gli step delle tue istruzioni. Output solo JSON valido.
"""
```

---

## CHARTS SERVICE (rendering deterministico, NON-LLM) — app/services/charts.py

```python
"""
Rendering deterministico dei grafici a partire dalle ChartSpec prodotte da
FinancialAgent. Nessun LLM è coinvolto in questo modulo: riceve solo dati
strutturati e disegna PNG con Plotly. Stessa libreria già prevista in
scaffold_consulting_crew.py (bar_chart/line_chart/scenario_table), qui
generalizzata per consumare direttamente le ChartSpec del nuovo schema.
"""
from __future__ import annotations

import os
from pathlib import Path

import plotly.graph_objects as go

CHARTS_DIR = Path(os.getenv("OUTPUT_DIR", "output")) / "charts"


def _ensure_dir():
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)


def render_chart_specs(specs: list[dict]) -> list[str]:
    """Renderizza una lista di ChartSpec (dict) e ritorna i path dei PNG generati.
    Ogni spec malformata viene saltata (loggata) invece di far fallire l'intero
    business plan — un grafico mancante non deve bloccare il resto."""
    _ensure_dir()
    generated = []
    for spec in specs:
        try:
            path = _render_single(spec)
            generated.append(path)
        except Exception as exc:
            print(f"[charts] impossibile renderizzare '{spec.get('filename', '?')}': {exc}")
    return generated


def _render_single(spec: dict) -> str:
    chart_type = spec["chart_type"]
    title = spec["title"]
    labels = spec["labels"]
    series = spec["series"]
    filename = spec["filename"]

    fig = go.Figure()

    if chart_type == "bar":
        for name, values in series.items():
            fig.add_trace(go.Bar(x=labels, y=values, name=name))
    elif chart_type == "line":
        for name, values in series.items():
            fig.add_trace(go.Scatter(x=labels, y=values, name=name, mode="lines+markers"))
    elif chart_type == "pie":
        first_series = next(iter(series.values()))
        fig.add_trace(go.Pie(labels=labels, values=first_series))
    elif chart_type == "waterfall":
        first_series = next(iter(series.values()))
        fig.add_trace(go.Waterfall(x=labels, y=first_series))
    else:
        raise ValueError(f"chart_type non supportato: {chart_type}")

    fig.update_layout(title=title)
    path = CHARTS_DIR / f"{filename}.png"
    fig.write_image(str(path))
    return str(path)
```

---

## LLM SERVICE (riuso identico da OrgTransform AI) — app/services/llm.py

```python
import httpx
from app.config.settings import settings


class LLMService:
    """
    Client provider-agnostic. Si connette a LM Studio o Ollama via API
    OpenAI-compatible. Stesso servizio già usato in OrgTransform AI —
    riusalo tale e quale, non serve reimplementarlo.
    """

    def __init__(self):
        self.base_url = settings.LLM_BASE_URL
        self.model = settings.LLM_MODEL

    async def generate(
        self, system_prompt: str, user_message: str,
        temperature: float = 0.2, max_tokens: int = 2000
    ) -> str:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        async with httpx.AsyncClient(timeout=600.0) as client:
            response = await client.post(f"{self.base_url}/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            return _strip_code_fence(content)


def _strip_code_fence(text: str) -> str:
    """Gemma a volte avvolge il JSON in ```json ... ``` — stessa utility
    già presente in OrgTransform AI's base.py, riusala identica."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:] if lines[0].startswith("```") else lines
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return text.strip()
```

---

## WEB SEARCH SERVICE (per MarketAgent e FundingAgent) — app/services/web_search.py

```python
"""
Wrapper di ricerca web per dati di mercato e bandi real-time.
Riuso concettuale di src/tools/search.py da strategic-consulting-crew,
adattato all'architettura BaseAgent/Orchestrator.

IMPORTANTE (coerenza con pii_guard di OrgTransform AI): se in futuro questo
servizio riceve dati sensibili sui soci come parte della query, va sanitizzato
PRIMA di uscire verso l'API esterna — stessa logica del pre-LLM PII guard,
qui applicata al pre-search invece che al pre-prompt.
"""
from __future__ import annotations

import os


class WebSearchService:
    def __init__(self):
        self.serper_api_key = os.getenv("SERPER_API_KEY")

    async def search(self, query: str, max_results: int = 5) -> list[dict]:
        if self.serper_api_key:
            return await self._search_serper(query, max_results)
        return await self._search_duckduckgo(query, max_results)

    async def _search_serper(self, query: str, max_results: int) -> list[dict]:
        import httpx
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://google.serper.dev/search",
                headers={"X-API-KEY": self.serper_api_key},
                json={"q": query, "num": max_results}
            )
            response.raise_for_status()
            data = response.json()
            return [
                {"title": r.get("title"), "snippet": r.get("snippet"), "link": r.get("link")}
                for r in data.get("organic", [])
            ]

    async def _search_duckduckgo(self, query: str, max_results: int) -> list[dict]:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
        return [
            {"title": r["title"], "snippet": r["body"], "link": r["href"]}
            for r in results
        ]
```

---

## REPORT BUILDER — app/services/report_builder.py

```python
"""
Converte il business plan Markdown finale in DOCX, incorporando i grafici
già renderizzati da charts.py. Riuso adattato di
src/tools/docx_writer.py da strategic-consulting-crew.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output")) / "reports"


def markdown_to_docx(
    markdown_text: str,
    chart_paths: list[str],
    output_filename: str = "business_plan.docx"
) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Arial"
    style.font.size = Pt(11)

    for line in markdown_text.splitlines():
        line = line.strip()
        if not line:
            doc.add_paragraph("")
        elif line.startswith("# "):
            doc.add_heading(line[2:], level=1)
        elif line.startswith("## "):
            doc.add_heading(line[3:], level=2)
        elif line.startswith("### "):
            doc.add_heading(line[4:], level=3)
        elif line.startswith("- ") or line.startswith("* "):
            doc.add_paragraph(line[2:], style="List Bullet")
        elif re.match(r"^\d+\. ", line):
            doc.add_paragraph(re.sub(r"^\d+\. ", "", line), style="List Number")
        else:
            doc.add_paragraph(line)

    # Incorpora tutti i grafici renderizzati in coda al documento, in una
    # sezione dedicata (semplice e robusto; l'inserimento posizionale nel
    # testo può essere raffinato in una versione successiva)
    if chart_paths:
        doc.add_heading("Grafici e Proiezioni", level=1)
        for path in chart_paths:
            if Path(path).exists():
                doc.add_picture(path, width=Inches(5.5))

    output_path = OUTPUT_DIR / output_filename
    doc.save(str(output_path))
    return str(output_path)
```

---

## API ENDPOINT DI INTAKE (per uso futuro da frontend) — app/api/v1/intake.py

```python
from fastapi import APIRouter
from app.agents.intake_agent import IntakeAgent
from app.services.llm import LLMService
from app.models.requests import IntakeParseRequest
from app.models.responses import IntakeParseResponse

router = APIRouter(prefix="/api/v1/intake", tags=["intake"])


@router.get("/template", response_class=str)
async def get_intake_template():
    agent = IntakeAgent(LLMService())
    return agent.generate_template_markdown()


@router.post("/parse", response_model=IntakeParseResponse)
async def parse_intake(request: IntakeParseRequest):
    agent = IntakeAgent(LLMService())
    report = await agent.parse_brief(request.raw_markdown)
    return IntakeParseResponse(
        profile=report.profile.__dict__,
        needs_clarification=report.needs_clarification,
        summary_markdown=report.summary_markdown,
        confidence=report.confidence
    )
```

> Nota: questo endpoint fa lo stesso lavoro della CLI (`scripts/intake_cli.py`),
> solo senza la parte interattiva di porre le domande — è pensato per quando
> arriverà un frontend (Fase 3, come in orgtransform-ai) che raccoglie le
> risposte in un form invece che in terminale, ma riusa lo stesso IntakeAgent.

---

## API ENDPOINT — app/api/v1/business_plan.py

```python
from fastapi import APIRouter, HTTPException
from app.core.types import BusinessIdeaProfile
from app.models.requests import BusinessPlanRequest
from app.models.responses import BusinessPlanResponse
from app.agents.orchestrator import Orchestrator
from app.services.llm import LLMService
from app.services.web_search import WebSearchService

router = APIRouter(prefix="/api/v1", tags=["business-plan"])


@router.post("/business-plan", response_model=BusinessPlanResponse)
async def create_business_plan(request: BusinessPlanRequest):
    profile = BusinessIdeaProfile(
        project_name=request.project_name,
        idea_description=request.idea_description,
        need_addressed=request.need_addressed,
        product_type=request.product_type,
        sector_hint=request.sector_hint,
        target_region=request.target_region,
        founders=request.founders,
        available_capital_eur=request.available_capital_eur,
        desired_timeline_months=request.desired_timeline_months,
        notes=request.notes
    )

    llm = LLMService()
    web_search = WebSearchService()
    orchestrator = Orchestrator(llm, web_search)

    try:
        result = await orchestrator.run(profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return BusinessPlanResponse(
        plan_id=result.plan_id,
        status=result.status.value,
        business_plan_markdown=result.business_plan_markdown,
        docx_path=result.business_plan_docx_path,
        charts_generated=result.charts_generated,
        revision_cycles=result.total_iterations,
        agent_outputs={k: v.data for k, v in result.agent_outputs.items()}
    )
```

---

## MODELS — app/models/requests.py

```python
from pydantic import BaseModel
from app.core.types import ProductType, FounderProfile


class IntakeParseRequest(BaseModel):
    raw_markdown: str


class BusinessPlanRequest(BaseModel):
    project_name: str
    idea_description: str
    need_addressed: str
    product_type: ProductType
    sector_hint: str
    target_region: str
    founders: list[FounderProfile]
    available_capital_eur: float
    desired_timeline_months: int
    notes: str = ""

    model_config = {
        "json_schema_extra": {
            "example": {
                "project_name": "Fermenta",
                "idea_description": "Produzione artigianale di bevande fermentate km0",
                "need_addressed": "Mancanza di alternative analcoliche serie all'aperitivo",
                "product_type": "physical",
                "sector_hint": "food & beverage artigianale",
                "target_region": "Napoli e provincia",
                "founders": [
                    {"name": "Fondatore 1", "skills": ["ricette", "produzione"], "availability": "full-time"},
                    {"name": "Fondatore 2", "skills": ["rete bar/ristoranti"], "availability": "part-time 20h/settimana"}
                ],
                "available_capital_eur": 4000,
                "desired_timeline_months": 12,
                "notes": "Laboratorio condiviso in valutazione"
            }
        }
    }
```

---

## MODELS — app/models/responses.py (estratto rilevante)

```python
from pydantic import BaseModel


class IntakeParseResponse(BaseModel):
    profile: dict
    needs_clarification: list[str]
    summary_markdown: str
    confidence: float

# BusinessPlanResponse: vedi utilizzo in api/v1/business_plan.py — stessa
# forma di AssessmentResponse in orgtransform-ai, adattata ai campi di
# OrchestratorResult (plan_id, business_plan_markdown, docx_path, ecc.)
```

---

## CONFIGURATION — app/config/settings.py

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    LLM_BASE_URL: str = "http://localhost:1234/v1"
    LLM_MODEL: str = "gemma-4-26b"

    # Web search
    SERPER_API_KEY: str = ""

    # Output
    OUTPUT_DIR: str = "output"

    # Redis (opzionale)
    REDIS_URL: str = "redis://localhost:6379/0"

    # App
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    LOG_LEVEL: str = "INFO"

    # Orchestrator
    MAX_REVISION_CYCLES: int = 3

    class Config:
        env_file = ".env"


settings = Settings()
```

---

## .env.example

```
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL=gemma-4-26b
SERPER_API_KEY=
OUTPUT_DIR=output
REDIS_URL=redis://localhost:6379/0
APP_HOST=0.0.0.0
APP_PORT=8000
MAX_REVISION_CYCLES=3
```

---

## DOCKER COMPOSE — docker-compose.yml

```yaml
version: "3.9"

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./output:/app/output
      - ./data:/app/data
```

---

## DOCKERFILE

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m bizplan
USER bizplan

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## REQUIREMENTS

```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
pydantic>=2.7.0
pydantic-settings>=2.3.0
httpx>=0.27.0
python-dotenv>=1.0.0
plotly>=5.0.0
kaleido>=0.2.1
python-docx>=1.1.0
duckduckgo-search>=6.0.0
```

---

## FASTAPI ENTRY POINT — app/main.py

```python
from fastapi import FastAPI
from app.api.v1.business_plan import router as business_plan_router

app = FastAPI(
    title="Business Plan AI",
    description="Sistema multi-agente per la creazione di business plan per SME italiane",
    version="1.0.0"
)

app.include_router(business_plan_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Business Plan AI"}
```

---

## ROADMAP DI IMPLEMENTAZIONE

### Fase 1 — Pipeline core (1-2 settimane)
- [ ] Scaffold struttura repo
- [ ] Implementare IntakeAgent + banca domande + CLI di intake
- [ ] Implementare BaseAgent + i 6 agenti specialistici
- [ ] Implementare Orchestrator con revision loop (MAX_REVISION_CYCLES=3)
- [ ] Implementare services/charts.py (rendering deterministico)
- [ ] Collegare endpoint FastAPI (incluso /api/v1/intake/parse)
- [ ] Testare con LM Studio / Gemma 4 26B in locale
- [ ] Valutazione manuale: eseguire l'intake CLI su 2-3 idee reali, verificare
  che l'IntakeAgent segnali correttamente i needs_clarification quando una
  risposta è vaga o mancante, poi lanciare la pipeline completa sul profilo
  estratto e controllare il revision log

### Fase 2 — Web search reale (3-5 giorni)
- [ ] Attivare SerperDev o DuckDuckGo per MarketAgent (competitor/trend reali)
- [ ] Attivare per FundingAgent (bandi Invitalia/regionali attivi al momento)
- [ ] Verificare che nessun dato sensibile dei soci finisca nelle query esterne

### Fase 3 — Report e grafici (2-3 giorni)
- [ ] Rifinire markdown_to_docx per posizionare i grafici nella sezione corretta
  invece che tutti in coda
- [ ] Aggiungere copertina/indice al DOCX

### Fase 4 — Enhancement futuro (opzionale)
- [ ] VisionAgent che propone bozze di risposta per ogni domanda di intake,
  per abbassare la barriera d'ingresso quando l'utente non sa da dove partire
  (discusso ma non ancora specificato in dettaglio in questa v1.0)
- [ ] Test suite pytest (stesso standard delle 43 unit test di OrgTransform AI)

---

*Fine spec — pronto per generazione scaffold agentica in Antigravity IDE.*
