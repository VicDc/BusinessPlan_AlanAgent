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
