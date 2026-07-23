"""
Converte il business plan Markdown finale in DOCX, incorporando i grafici
già renderizzati da charts.py. Riuso adattato di
src/tools/docx_writer.py da strategic-consulting-crew.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from docx import Document
from docx.shared import Inches, Pt

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output")) / "reports"


def build_draft_markdown(profile, agent_outputs: dict, iteration: int, issues: list[str]) -> str:
    """Business plan PARZIALE con l'ultimo output di ciascun agente e i
    problemi segnalati in questa iterazione."""
    lines = [
        f"# Bozza — Iterazione {iteration}\n",
        "⚠️ Non ancora approvata dall'Orchestrator.\n",
    ]
    for agent_key, ao in agent_outputs.items():
        lines.append(f"\n## {agent_key.capitalize()}\n")
        lines.append(f"```json\n{json.dumps(ao.data, indent=2, ensure_ascii=False)}\n```")
    if issues:
        lines.append("\n## Problemi segnalati in questa iterazione\n")
        for issue in issues:
            if issue:
                lines.append(f"- {issue}")
    return "\n".join(lines)


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


def save_markdown_report(
    markdown_text: str,
    chart_paths: list[str],
    output_filename: str = "business_plan.md"
) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / output_filename

    content = markdown_text
    if chart_paths:
        content += "\n\n# Grafici e Proiezioni\n"
        for path in chart_paths:
            p = Path(path)
            content += f"\n![{p.stem}](file:///{p.as_posix()})\n"

    output_path.write_text(content, encoding="utf-8")
    return str(output_path)
