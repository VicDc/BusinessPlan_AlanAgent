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
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

from app.core.intake_questions import INTAKE_QUESTIONS
from app.services.llm import LLMService
from app.agents.intake_agent import IntakeAgent
from app.services.web_search import WebSearchService
from app.agents.orchestrator import Orchestrator

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
    _process_and_report(raw_markdown, source_label=str(out_path))


def _process_and_report(raw_markdown: str, source_label: str):
    console.print("\n[bold cyan]Estrazione ed elaborazione del report...[/]")
    llm = LLMService()
    
    stem = Path(source_label).stem
    llm.run_id = stem if stem.startswith("intake_") else f"intake_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
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
    console.print(f"[dim]Usa questo profilo con Orchestrator.run(profile) "
                   f"oppure passa {source_label} a POST /api/v1/intake/parse.[/]")

    if Confirm.ask("\nVuoi lanciare subito la pipeline completa con questo profilo?"):
        console.print("\n[bold cyan]Avvio della pipeline multi-agente...[/]")
        web_search = WebSearchService()
        orchestrator = Orchestrator(llm, web_search)
        result = asyncio.run(orchestrator.run(report.profile))

        console.print(f"\n[bold]ID del piano:[/] {result.plan_id}")
        console.print(f"[bold green]Pipeline completata con stato:[/] {result.status.value}")
        console.print(f"[bold]Percorso DOCX:[/] {result.business_plan_docx_path}")
        console.print(f"[bold]Percorso MD:[/] {result.business_plan_md_path}")
        console.print(f"[bold]Grafici generati:[/] {result.charts_generated}")
        console.print(f"[bold]Cicli di revisione totali:[/] {result.total_iterations}")


@app.command()
def parse(file: Path = typer.Argument(..., help="Path al file .md di intake già compilato")):
    """Rilancia solo estrazione+report su un intake già scritto su disco,
    senza rifare le domande."""
    if not file.exists():
        console.print(f"[red]File non trovato: {file}[/]")
        raise typer.Exit(1)
    raw_markdown = file.read_text(encoding="utf-8")
    _process_and_report(raw_markdown, source_label=str(file))


if __name__ == "__main__":
    app()
