from datetime import datetime, timezone

def main() -> None:
    print(f"evaluate-results started at {datetime.now(timezone.utc).isoformat()}")

if __name__ == "__main__":
    main()
