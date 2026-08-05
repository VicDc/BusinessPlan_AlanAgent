# 2026-08-05 — Anonimizzazione del bundle di evidenze fase 2

## Contesto

Il bundle `docs/evidence/2026-08-05-fase2/` contiene gli artefatti prodotti dalla run di fase 2:
4 report markdown (3 iterazioni + parziale), un .docx derivato, un .xlsx di validazione
finanziaria, due grafici .png, `llm_calls.jsonl`, l'intake compilato e i due audit
(`audit-fase1.md`, `audit-fase2.md`).

L'intake contiene i nomi reali dei due soci, che si propagano nei report generati. Prima di
poter condividere il bundle vanno rimossi. Gli audit sono evidenza grezza di cio che e stato
osservato durante l'audit e non vengono toccati da questa passata: l'anonimizzazione e un
evento successivo e separato, registrato qui.

Conteggi di riferimento forniti prima dell'intervento: ~29 nei 4 report .md, 8 nel .docx
(2 paragrafi + 6 celle), 2 nell'intake, 0 in `llm_calls.jsonl`.

## Cosa ho fatto

1. Identificati i due nomi dei soci presenti nell'intake, piu le occorrenze del solo nome
   proprio e del solo cognome. Nessun altro PII presente: scansione per email, telefoni,
   codice fiscale, partita IVA e IBAN su tutti i markdown, zero riscontri.
2. Misurate le occorrenze di partenza per capire cosa contassero i numeri di riferimento
   (vedi sotto).
3. Copia di backup dell'intero bundle nella scratchpad di sessione prima di scrivere.
4. Ogni nome e stato mappato su un placeholder posizionale (`Socio A`, `Socio B`): nome
   completo, solo nome proprio e solo cognome collassano tutti sullo stesso placeholder.
   Sostituzione case-sensitive e ordinata dalla stringa piu lunga alla piu corta, per non
   lasciare cognomi orfani.
5. Markdown (4 report + intake): sostituzione testuale.
6. .docx: riscritto con python-docx. Sostituzione a livello di run per preservare la
   formattazione; collasso sul primo run solo dove un nome attraversa piu run.
7. Verifica finale a zero occorrenze su tutti i file toccati.

Mappatura scelta: `Socio A` / `Socio B`, neutra e stabile fra i due formati, cosi che il .docx
e il .md da cui deriva restino confrontabili.

## Cosa e successo

| target | posizioni | token nome | dopo |
|---|---|---|---|
| 4 report .md | 30 | 35 | 0 |
| `intake_20260805_122503.md` | 2 | 3 | 0 |
| `business_plan_b5dfcf2e_partial.docx` | 8 (2 paragrafi + 6 celle) | 15 | 0 |
| `llm_calls.jsonl` | 0 | 0 | non modificato, gia pulito |
| `charts/*.png` | 0 | 0 | ispezionati visivamente |
| `*_validation.xlsx` (celle) | 0 | 0 | scansionato con openpyxl |

Il .docx e un artefatto derivato dal markdown ma archiviato separatamente: modificare il .md
non lo aggiorna. Vale la pena ripeterlo perche e esattamente il modo in cui questa passata
poteva risultare "completa" e non esserlo.

I file di evidenza restano identici byte per byte a quanto prodotto dalla run, a meno della
sola sostituzione dei nomi.

## Sorprese

**I numeri di riferimento contano posizioni, non token.** Il .docx era dato a 8 = 2 paragrafi +
6 celle: sono 8 *posizioni*, che contengono 15 token di nome (una cella contenente nome e
cognome ne contiene 2). Applicando la stessa lettura, l'intake torna esatto (2 righe, 3 token) e i report
danno 30 posizioni contro ~29 attese — dentro la tolleranza della tilde. Contando i token si
sarebbe letto 35 contro 29 e sembrato uno scarto grave che non esiste. Un conteggio di
riferimento senza unita dichiarata e ambiguo: qui era recuperabile perche la scomposizione del
.docx fissava l'unita.

**Le occorrenze non sono tutte nomi completi.** 13 delle 35 occorrenze nei report sono soli nomi
propri in mezzo alla prosa corrente. Una sostituzione limitata al nome completo le avrebbe
lasciate in chiaro e sarebbe comunque passata a un controllo che cercava il nome completo.

**Il .docx era pulito ovunque tranne che nel corpo.** Le proprieta del documento non contengono
PII (`author = python-docx`, generato dal codice, non da un utente). Fra tutte le parti XML del
pacchetto, solo `word/document.xml` conteneva nomi: nessun header, footer o commento.

**L'xlsx era gia pulito nel contenuto ma non nel nome.** Zero nomi personali nelle celle, e il
nome progetto e nel nome del file. Vedi sotto.

## Findings prodotti

- [I nomi dei file di output sono un canale di leak quanto il contenuto](../findings/2026-08-05-nomi-file-output-canale-di-leak.md)
  (area `privacy-gdpr`). `business_plan_b5dfcf2e_aurora_sfusa_validation.xlsx` porta il nome
  progetto nel nome del file. Qui e fittizio, quindi il file e stato lasciato invariato, ma il
  contenuto anonimizzato non copre directory listing, manifest zip e nomi di allegati.
- [Una passata di anonimizzazione che registra la propria mappatura nello stesso repository non
  ha anonimizzato nulla](../findings/2026-08-05-perimetro-di-verifica-anonimizzazione.md)
  (area `privacy-gdpr`). La prima stesura di questa nota conteneva la mappatura in chiaro: il
  bundle superava ogni controllo di contenuto ed era comunque reversibile da un file a due
  directory di distanza. Il perimetro di verifica escludeva il documento che descriveva
  l'operazione.

## Aperto

- Il finding sui nomi di output non e stato applicato: nessuna modifica al codice che costruisce
  i nomi dei file. Va prima verificato chi a valle dipende dai nomi attuali.
- L'anonimizzazione e stata eseguita con uno script una tantum nella scratchpad, non con codice
  del repo. Se il bundle viene rigenerato, i nomi tornano: la fase di export non ha una passata
  di anonimizzazione propria.
- Nessun registro delle sostituzioni e conservato in alcun punto del repository, per scelta:
  la re-identificazione a partire dal bundle non e possibile, e chi deve riconciliare i report
  con l'intake originale deve disporre dell'intake originale.
- Scansione estesa a tutto il repository, non al solo bundle: gli unici riscontri residui erano
  in questa stessa nota, ora riscritta. Vedi il finding sul perimetro di verifica.
- `audit-fase1.md` e `audit-fase2.md` non contengono nomi personali e non sono stati modificati.
