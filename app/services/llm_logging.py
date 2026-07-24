import json
import time
import uuid
import sys
from datetime import datetime, timezone
from pathlib import Path

LOGS_DIR = Path("logs")
LOGS_FILE = LOGS_DIR / "llm_calls.jsonl"


class Timer:
    def __enter__(self):
        self.start = time.monotonic()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.monotonic() - self.start


def new_call_id() -> str:
    return uuid.uuid4().hex[:12]


def _ensure_log_file():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)


def _safe_write_log(data: dict):
    try:
        _ensure_log_file()
        with open(LOGS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
    except Exception as e:
        print(f"[llm_logging] Warning: Impossibile scrivere i log su disco: {e}", file=sys.stderr)


def log_llm_call(
    call_id: str,
    run_id: str | None,
    agent_name: str | None,
    iteration: int | None,
    model: str,
    temperature: float,
    max_tokens: int,
    latency_seconds: float,
    prompt_tokens: int | None,
    completion_tokens: int | None,
    total_tokens: int | None,
    error: str | None = None
):
    record = {
        "type": "llm_call",
        "call_id": call_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "agent_name": agent_name,
        "iteration": iteration,
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "latency_seconds": latency_seconds,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "error": error
    }
    _safe_write_log(record)


def log_agent_result(
    call_id: str,
    run_id: str | None,
    agent_name: str,
    iteration: int | None,
    json_valid: bool,
    status: str,
    confidence: float | None = None,
    is_revision: bool = False
):
    record = {
        "type": "agent_result",
        "call_id": call_id,
        "run_id": run_id,
        "agent_name": agent_name,
        "iteration": iteration,
        "json_valid": json_valid,
        "status": status,
        "confidence": confidence,
        "is_revision": is_revision
    }
    _safe_write_log(record)


def log_orchestrator_iteration(
    run_id: str,
    iteration: int,
    final_status: str,
    revisions_needed_count: int,
    agents_flagged: list[str],
    revisions_applied: int | None = None
):
    record = {
        "type": "orchestrator_iteration",
        "run_id": run_id,
        "iteration": iteration,
        "final_status": final_status,
        "revisions_needed_count": revisions_needed_count,
        "agents_flagged": agents_flagged,
        "revisions_applied": revisions_applied
    }
    _safe_write_log(record)


def log_failed_raw_response(call_id: str, raw_text: str):
    """Salva il testo grezzo di una risposta che ha fallito il parsing JSON,
    per diagnosi successiva."""
    dir_path = Path("logs/failed_responses")
    dir_path.mkdir(parents=True, exist_ok=True)
    (dir_path / f"{call_id}.txt").write_text(raw_text, encoding="utf-8")
