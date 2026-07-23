import json
import os
from pathlib import Path
import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()

LOG_FILE = Path("logs/llm_calls.jsonl")


def main():
    if not LOG_FILE.exists():
        console.print("[yellow]Nessun log trovato. Esegui prima almeno un run per generare logs/llm_calls.jsonl.[/]")
        return

    # Leggi il file riga per riga per evitare problemi di inferenza tipi
    llm_calls = []
    agent_results = []
    orchestrator_iterations = []

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    rec_type = data.get("type")
                    if rec_type == "llm_call":
                        llm_calls.append(data)
                    elif rec_type == "agent_result":
                        agent_results.append(data)
                    elif rec_type == "orchestrator_iteration":
                        orchestrator_iterations.append(data)
                except Exception:
                    continue
    except Exception as e:
        console.print(f"[red]Errore nella lettura del file di log: {e}[/]")
        return

    df_calls = pd.DataFrame(llm_calls)
    df_results = pd.DataFrame(agent_results)
    df_iterations = pd.DataFrame(orchestrator_iterations)

    console.print("[bold cyan]=== ANALISI LOG CHIAMATE LLM ===[/]\n")

    # 1. Metriche per agente (Token & Latenza - richiede df_calls e df_results)
    if not df_calls.empty and not df_results.empty:
        df_merged = pd.merge(df_calls, df_results, on="call_id", suffixes=("_call", "_res"))

        agent_stats = []
        
        # Raggruppa per agent_name_res
        grouped = df_merged.groupby("agent_name_res")
        for name, group in grouped:
            total_calls = len(group)
            avg_prompt = group["prompt_tokens"].mean()
            avg_completion = group["completion_tokens"].mean()
            avg_total = group["total_tokens"].mean()
            avg_latency = group["latency_seconds"].mean()
            p95_latency = group["latency_seconds"].quantile(0.95)

            agent_stats.append({
                "name": name,
                "calls": total_calls,
                "avg_prompt": avg_prompt,
                "avg_completion": avg_completion,
                "avg_total": avg_total,
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
            })

        # Aggiungiamo l'Orchestrator dalle sole chiamate
        orch_calls = df_calls[df_calls["agent_name"] == "Orchestrator"]
        if not orch_calls.empty:
            total_calls = len(orch_calls)
            avg_prompt = orch_calls["prompt_tokens"].mean()
            avg_completion = orch_calls["completion_tokens"].mean()
            avg_total = orch_calls["total_tokens"].mean()
            avg_latency = orch_calls["latency_seconds"].mean()
            p95_latency = orch_calls["latency_seconds"].quantile(0.95)

            agent_stats.append({
                "name": "Orchestrator",
                "calls": total_calls,
                "avg_prompt": avg_prompt,
                "avg_completion": avg_completion,
                "avg_total": avg_total,
                "avg_latency": avg_latency,
                "p95_latency": p95_latency,
            })

        # Stampiamo la tabella delle metriche degli agenti
        table = Table(title="Latenza e Consumo Token per Agente", show_header=True, header_style="bold magenta")
        table.add_column("Agente", style="cyan")
        table.add_column("Chiamate", justify="right")
        table.add_column("Lat. Media (s)", justify="right")
        table.add_column("Lat. p95 (s)", justify="right")
        table.add_column("Prompt Tok. (med)", justify="right")
        table.add_column("Compl. Tok. (med)", justify="right")
        table.add_column("Total Tok. (med)", justify="right")

        for stat in agent_stats:
            table.add_row(
                stat["name"],
                str(stat["calls"]),
                f"{stat['avg_latency']:.2f}" if pd.notnull(stat['avg_latency']) else "N/D",
                f"{stat['p95_latency']:.2f}" if pd.notnull(stat['p95_latency']) else "N/D",
                f"{stat['avg_prompt']:.1f}" if pd.notnull(stat['avg_prompt']) else "N/D",
                f"{stat['avg_completion']:.1f}" if pd.notnull(stat['avg_completion']) else "N/D",
                f"{stat['avg_total']:.1f}" if pd.notnull(stat['avg_total']) else "N/D"
            )
        console.print(table)
        console.print()
    else:
        console.print("[yellow]Nessun dato di chiamata LLM reale trovato nei log per calcolare latenze e token.[/]\n")

    # 2. JSON validity rate & Confidence (richiede solo df_results)
    if not df_results.empty:
        table_validity = Table(title="Validità JSON & Confidence Dichiarata", show_header=True, header_style="bold green")
        table_validity.add_column("Agente", style="cyan")
        table_validity.add_column("Chiamate", justify="right")
        table_validity.add_column("JSON Validity Rate", justify="right")
        table_validity.add_column("Conf. Media", justify="right")
        table_validity.add_column("Conf. Min/Max", justify="right")

        grouped_results = df_results.groupby("agent_name")
        for name, group in grouped_results:
            total_calls = len(group)
            valid_calls = group["json_valid"].sum()
            json_validity_rate = (valid_calls / total_calls) * 100 if total_calls > 0 else 0.0

            valid_conf = group["confidence"].dropna()
            avg_conf = valid_conf.mean() if not valid_conf.empty else None
            min_conf = valid_conf.min() if not valid_conf.empty else None
            max_conf = valid_conf.max() if not valid_conf.empty else None

            val_str = f"{json_validity_rate:.1f}%"
            conf_str = f"{avg_conf:.2f}" if avg_conf is not None else "N/A"
            min_max_str = f"{min_conf:.2f} / {max_conf:.2f}" if min_conf is not None else "N/A"

            table_validity.add_row(name, str(total_calls), val_str, conf_str, min_max_str)

        console.print(table_validity)
        console.print()
    else:
        console.print("[yellow]Nessun risultato di agente (agent_result) trovato nei log.[/]\n")

    # 3. Analisi di convergenza dei run (richiede solo df_iterations)
    if not df_iterations.empty:
        table_runs = Table(title="Stato Convergenza dei Run dell'Orchestratore", show_header=True, header_style="bold blue")
        table_runs.add_column("Run ID", style="cyan")
        table_runs.add_column("Iterazioni Totali", justify="right")
        table_runs.add_column("Stato Finale", justify="center")
        table_runs.add_column("Agenti Flagged (Ultima iterazione)", style="yellow")

        grouped_runs = df_iterations.groupby("run_id")
        for run_id, group in grouped_runs:
            group_sorted = group.sort_values("iteration")
            total_runs = len(group_sorted)
            last_row = group_sorted.iloc[-1]
            final_status = last_row["final_status"]
            flagged = last_row.get("agents_flagged", [])

            status_style = "green" if final_status == "APPROVED" else "red"
            status_display = f"[{status_style}]{final_status}[/]"

            if final_status != "APPROVED" and total_runs >= 3:
                status_display += " (NON CONVERGE)"

            table_runs.add_row(
                run_id,
                str(total_runs),
                status_display,
                ", ".join(flagged) if flagged else "-"
            )
        console.print(table_runs)
        console.print()
    else:
        console.print("[yellow]Nessuna iterazione dell'Orchestratore trovata nei log.[/]\n")


if __name__ == "__main__":
    main()
