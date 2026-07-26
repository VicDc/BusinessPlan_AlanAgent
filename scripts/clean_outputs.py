"""
Pulizia dei file generati localmente (report, grafici, log, intake compilati).
Serve solo per igiene della working copy — quelle cartelle sono già gitignorate,
quindi non c'è rischio di leak, ma possono contenere dati reali degli intake.

Uso:
    python -m scripts.clean_outputs            # chiede conferma
    python -m scripts.clean_outputs --yes      # senza conferma
"""
from __future__ import annotations

import shutil
from pathlib import Path

import typer
from rich.console import Console

app = typer.Typer()
console = Console()

# Cartelle il cui CONTENUTO viene cancellato (le cartelle restano).
TARGETS = ["output", "logs", "data/intake"]


@app.command()
def run(yes: bool = typer.Option(False, "--yes", "-y", help="Non chiedere conferma")):
    existing = [Path(t) for t in TARGETS if Path(t).exists()]
    if not existing:
        console.print("[green]Niente da pulire.[/]")
        return

    console.print("[yellow]Verranno svuotate:[/] " + ", ".join(str(p) for p in existing))
    if not yes and not typer.confirm("Procedere?"):
        console.print("[red]Annullato.[/]")
        raise typer.Exit(1)

    for base in existing:
        for child in base.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
        console.print(f"[green]Svuotata:[/] {base}")


if __name__ == "__main__":
    app()
