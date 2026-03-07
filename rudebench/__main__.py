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
    validate_parser.add_argument("--report", action="store_true", help="Print word count deviation report")

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
        from scripts.validate_prompts import validate_prompts, print_report

        if hasattr(args, "report") and args.report:
            print_report(args.data)
            print()

        errors = validate_prompts(args.data)
        total_errors = sum(len(e) for e in errors.values())
        passed = sum(1 for e in errors.values() if not e)

        for check, errs in sorted(errors.items()):
            status = "PASS" if not errs else "FAIL"
            print(f"[{status}] {check}")
            for err in errs[:10]:
                print(f"       {err}")
            if len(errs) > 10:
                print(f"       ... and {len(errs) - 10} more errors")

        print(f"\n{passed}/10 checks passed, {total_errors} total errors")
        sys.exit(0 if total_errors == 0 else 1)
    elif args.command == "generate":
        import asyncio
        from rudebench.gen_completions import main as gen_main
        asyncio.run(gen_main(
            config_dir=args.config,
            models_filter=args.models,
            dry_run=args.dry_run,
        ))
    elif args.command == "judge":
        print("judge: not yet implemented (Phase 3)")
    elif args.command == "results":
        print("results: not yet implemented (Phase 4)")


if __name__ == "__main__":
    main()
