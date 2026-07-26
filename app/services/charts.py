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
    path = CHARTS_DIR / f"{Path(filename).stem}.png"
    fig.write_image(str(path))
    return str(path)
