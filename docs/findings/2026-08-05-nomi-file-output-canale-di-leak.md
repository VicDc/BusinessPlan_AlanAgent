---
id: F-2026-08-05-01
title: I nomi dei file di output sono un canale di leak quanto il contenuto
area: privacy-gdpr
date: 2026-08-05
severity: media
status: aperto
evidence: docs/evidence/2026-08-05-fase2/reports/business_plan_b5dfcf2e_aurora_sfusa_validation.xlsx
---

## Osservazione

Il bundle di evidenze della fase 2 contiene:

```
reports/business_plan_b5dfcf2e_aurora_sfusa_validation.xlsx
```

Il nome del progetto (`aurora_sfusa`) e finito nel **nome del file**, non solo nel suo
contenuto. In questo caso e un nome fittizio, quindi il file e stato lasciato invariato.
Il pattern pero e reale.

## Perche conta

L'anonimizzazione eseguita il 2026-08-05 ha ripulito il contenuto di tutti gli artefatti del
bundle (4 .md, intake .md, .docx). Il contenuto dell'xlsx e risultato gia pulito allo scan
con openpyxl: zero occorrenze di nomi personali nelle celle.

Un bundle con contenuto integralmente anonimizzato continua comunque a esporre il cliente
attraverso:

- il listing della directory;
- il manifest dello zip, se il bundle viene consegnato compresso;
- il nome dell'allegato in una email;
- i log del filesystem, i backup e gli URL se il file viene servito via HTTP.

Nessuno di questi canali viene coperto da una sostituzione testuale sul contenuto. Un revisore
che verifica l'anonimizzazione leggendo i file dichiara "pulito" un bundle che non lo e.

## Origine

La pipeline costruisce i nomi di output concatenando il run ID con il nome progetto fornito
dall'utente. Il run ID (`b5dfcf2e`) da solo e gia sufficiente a identificare la run in modo
univoco: la parte leggibile e ridondante ai fini della tracciabilita.

## Mitigazione proposta

Derivare i nomi dei file di output dal solo run ID, mantenendo il nome progetto leggibile
**dentro** il documento, dove una passata di anonimizzazione lo raggiunge:

```
reports/business_plan_b5dfcf2e_validation.xlsx
```

Da verificare prima di applicare: quali punti del codice costruiscono i nomi di output, e se
qualche consumatore a valle (test, README, script di pulizia) assume il nome corrente.

## Estensione da controllare

Lo stesso canale vale per i nomi di directory (`docs/evidence/<data>-<fase>/` oggi non contiene
dati cliente, ma nulla lo impedisce) e per i nomi dei fogli in un workbook — qui
`Verifica Finanziaria`, neutro.
