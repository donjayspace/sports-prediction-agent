from datetime import datetime, timezone

def main() -> None:
    print(f"analyze-events started at {datetime.now(timezone.utc).isoformat()}")

if __name__ == "__main__":
    main()
