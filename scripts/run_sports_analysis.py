import argparse
import os
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from agent.ai.factory import create_providers
from agent.ai.schemas import EventResearchInput
from agent.analyzer.model_analyzer import ModelAnalyzer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run sports research analysis")
    parser.add_argument("--event-id", required=True)
    parser.add_argument("--sport", required=True, choices=["football", "basketball", "tennis", "table_tennis"])
    parser.add_argument("--competition", required=True)
    parser.add_argument("--start-time", required=True, help="ISO-8601 event start time")
    parser.add_argument("--participants", nargs=2, required=True)
    return parser.parse_args()


def main() -> int:
    load_dotenv()
    args = parse_args()
    event = EventResearchInput(
        event_id=args.event_id,
        sport=args.sport,
        competition=args.competition,
        start_time=args.start_time,
        participants=args.participants,
    )
    result = ModelAnalyzer(create_providers()).analyze(event)

    output_dir = Path(os.getenv("OUTPUT_DIR", "reports"))
    output_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = output_dir / f"{args.event_id}-{stamp}.json"
    output.write_text(__import__("json").dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
