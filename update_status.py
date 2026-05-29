import json
import sys
from datetime import datetime
from pathlib import Path

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent

STATUS_FILE = BASE_DIR / "status.json"
VALID = {"idle", "running", "done", "confirm", "error"}


def main():
    if len(sys.argv) < 2:
        print("Usage: python update_status.py <status>")
        print(f"Valid: {', '.join(sorted(VALID))}")
        sys.exit(1)

    status = sys.argv[1]
    if status not in VALID:
        print(f"Invalid status '{status}'. Valid: {', '.join(sorted(VALID))}")
        sys.exit(1)

    STATUS_FILE.write_text(
        json.dumps({"status": status, "timestamp": datetime.now().isoformat()}),
        encoding="utf-8",
    )
    print(f"Status -> {status}")


if __name__ == "__main__":
    main()
