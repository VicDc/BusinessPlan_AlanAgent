---
id: F-2026-08-05-02
title: Una passata di anonimizzazione che registra la propria mappatura nello stesso repository non ha anonimizzato nulla
area: privacy-gdpr
date: 2026-08-05
severity: alta
status: aperto
evidence: docs/research-log/2026-08-05-anonimizzazione-evidence.md
---

## Osservazione

L'anonimizzazione del bundle `docs/evidence/2026-08-05-fase2/` ha superato ogni controllo a
livello di contenuto: 0 occorrenze nei 4 report .md, 0 nel .docx, 0 nelle celle dell'.xlsx,
0 in `llm_calls.jsonl`, 0 nell'intake. Tutti gli artefatti puliti, verificati uno per uno.

La nota di research-log che descriveva l'operazione conteneva pero la mappatura in chiaro:
nome originale accanto al placeholder che lo aveva sostituito, piu alcune citazioni verbatim
della prosa originale dei report. Sei righe, in un file a due directory di distanza dal bundle.

Il bundle era quindi **integralmente reversibile**. Chiunque avesse ricevuto il repository
avrebbe potuto ricostruire ogni nome con una singola sostituzione inversa.

## Perche conta

Il fallimento non e nell'esecuzione, e nel **perimetro**. La sostituzione era corretta,
esaustiva, verificata a zero. La verifica e stata disegnata attorno agli artefatti da
condividere ed escludeva il documento che descriveva l'operazione.

Un registro delle sostituzioni conservato nello stesso repository degli artefatti anonimizzati
annulla l'anonimizzazione: il dato pseudonimizzato e le informazioni aggiuntive per la
re-identificazione tornano nella disponibilita dello stesso soggetto e viaggiano insieme, in un
unico clone o in un unico zip.

E un fallimento particolarmente insidioso perche produce evidenza positiva: il report di
verifica mostra zero occorrenze su tutti i target ed e vero. La riga sbagliata sta nel documento
che dichiara il successo.

Lo stesso vale per ogni altro sottoprodotto dell'operazione, non solo per la nota:
- messaggi e descrizioni di commit;
- storia git (`git log -S` sui nomi originali continua a trovarli nei commit precedenti);
- issue, PR, appunti;
- script una tantum che contengono le stringhe di sostituzione hardcoded;
- copie di backup pre-modifica, se finiscono dentro l'albero del repository.

## Mitigazione

**La verifica va fatta repo-wide, non bundle-wide.** Il controllo di uscita non e "gli artefatti
sono puliti" ma "la stringa non compare in nessun punto del repository", inclusi i documenti
di processo scritti durante l'operazione stessa.

Regole operative:

1. Nessun registro delle sostituzioni nel repository. Se serve conservarlo, sta fuori, sotto
   controllo di accesso separato.
2. Le note di processo descrivono la metodologia in modo strutturale (mappatura posizionale,
   ordinamento, case-sensitivity) senza mai citare i valori originali.
3. Niente citazioni verbatim della prosa originale negli esempi: si riporta il conteggio e la
   forma dell'occorrenza, non il testo.
4. Lo script di anonimizzazione tiene i target fuori dal codice versionato.
5. Il backup pre-modifica sta fuori dall'albero del repository.
6. Controllo finale case-insensitive e repo-wide sui nomi originali, eseguito **dopo** aver
   scritto la documentazione dell'operazione, non prima. La documentazione e essa stessa un
   artefatto da verificare.

**Base normativa.** L'art. 4(5) GDPR definisce la pseudonimizzazione come il trattamento
per cui i dati non possono essere attribuiti a un interessato specifico senza informazioni
aggiuntive, a condizione che queste siano **conservate separatamente** e soggette a misure
tecniche e organizzative. Un registro delle sostituzioni nello stesso repository viola
entrambe le condizioni: i dati restano personali a tutti gli effetti, e il trattamento non
beneficia di alcuna delle attenuazioni previste per i dati pseudonimizzati (artt. 25, 32,
e la valutazione di compatibilità dell'art. 6(4)(e)).

## Nota sui falsi positivi

Il controllo repo-wide case-insensitive genera falsi positivi su cognomi che sono sottostringhe
di parole comuni (in questo bundle un cognome italiano compariva dentro una parola ordinaria in
quattro file). Vanno esaminati, non silenziati con un filtro a priori: e la stessa insensibilita
al contesto che fa trovare le occorrenze vere.
