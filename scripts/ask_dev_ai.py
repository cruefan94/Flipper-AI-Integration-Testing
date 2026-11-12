"""Manual, read-only development assistant CLI. No autonomous writes."""
import argparse
import json
from pathlib import Path
from scripts.ai_dev_gateway import Gateway, GatewayError

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt")
    parser.add_argument("--provider")
    parser.add_argument("--config", default="config/ai_dev_gateway.example.json")
    args = parser.parse_args()
    try:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
        result = Gateway(config).ask(args.prompt, args.provider)
        print(result["answer"])
    except (GatewayError, OSError, ValueError, KeyError) as exc:
        parser.exit(2, f"AI gateway error: {exc}\n")

if __name__ == "__main__":
    main()
