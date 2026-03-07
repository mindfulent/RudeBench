"""CLI entry point for RudeBench."""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="rudebench",
        description="RudeBench: Multi-dimensional behavioral benchmark for LLMs under hostile prompting",
    )
    subparsers = parser.add_subparsers(dest="command")

    # validate
    validate_parser = subparsers.add_parser("validate", help="Validate prompt dataset")
    validate_parser.add_argument("--data", default="data/prompts.jsonl", help="Path to prompts JSONL file")

    # generate
    gen_parser = subparsers.add_parser("generate", help="Generate completions from all models")
    gen_parser.add_argument("--config", default="config", help="Config directory")
    gen_parser.add_argument("--models", default=None, help="Comma-separated model IDs to run")
    gen_parser.add_argument("--dry-run", action="store_true", help="Print jobs without calling APIs")

    # judge
    judge_parser = subparsers.add_parser("judge", help="Run LLM judge scoring")
    judge_parser.add_argument("--config", default="config", help="Config directory")
    judge_parser.add_argument("--models", default=None, help="Comma-separated model IDs to judge")
    judge_parser.add_argument("--judge", choices=["primary", "secondary"], default="primary", help="Which judge to use")

    # results
    results_parser = subparsers.add_parser("results", help="Show results and leaderboard")
    results_parser.add_argument("--config", default="config", help="Config directory")
    results_parser.add_argument("--format", choices=["table", "csv", "json"], default="table", help="Output format")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "validate":
        print("validate: not yet implemented (Phase 1)")
    elif args.command == "generate":
        print("generate: not yet implemented (Phase 2)")
    elif args.command == "judge":
        print("judge: not yet implemented (Phase 3)")
    elif args.command == "results":
        print("results: not yet implemented (Phase 4)")


if __name__ == "__main__":
    main()
