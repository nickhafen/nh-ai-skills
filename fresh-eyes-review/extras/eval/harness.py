"""Run fixtures through the pipeline under validation conditions A-E.

Examples:
    # Offline check of every code path (no API calls, meaningless reviews):
    python eval/harness.py --fixture eval/fixtures/smoke-demand-letter --client mock

    # Real run: 5 runs of conditions B and C
    python eval/harness.py --fixture eval/fixtures/smoke-demand-letter --conditions B C --runs 5

Output goes to eval/results/<fixture>/<batch>/<condition>-run<k>/results.json, with a
manifest.json per batch. Score a batch with eval/score.py.
"""

import argparse
import json
import sys
import traceback
from datetime import datetime
from pathlib import Path

EXTRAS_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(EXTRAS_DIR))

from engine import pipeline  # noqa: E402
from engine.model import AnthropicClient, ClaudeCodeClient, MockClient  # noqa: E402
from engine.references import content_hash, git_commit  # noqa: E402
from validate_results import validate  # noqa: E402  (skill script; engine puts it on the path)


def load_fixture(path):
    path = Path(path)
    config = json.loads((path / "fixture.json").read_text(encoding="utf-8"))
    config["document"] = (path / config["document_file"]).read_text(encoding="utf-8").strip()
    return config


def make_client(args, seed=0):
    if args.client == "mock":
        return MockClient(seed=seed)
    if args.client == "claude-code":
        return ClaudeCodeClient(model=args.model, effort=args.effort)
    return AnthropicClient(model=args.model, effort=args.effort, fallbacks=not args.no_fallbacks)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fixture", required=True, help="fixture folder (with fixture.json)")
    parser.add_argument("--conditions", nargs="+", default=list(pipeline.CONDITIONS), choices=list(pipeline.CONDITIONS))
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--client", choices=["anthropic", "claude-code", "mock"], default="anthropic",
                        help="anthropic = Claude API (needs credentials); claude-code = the Claude Code CLI "
                             "on your own plan; mock = offline")
    parser.add_argument("--model", default="claude-opus-5")
    parser.add_argument("--effort", default="high", choices=["low", "medium", "high", "xhigh", "max"])
    parser.add_argument("--no-fallbacks", action="store_true", help="don't send the server-side refusal fallback")
    parser.add_argument("--no-ai-reader", action="store_true", help="skip the AI-reader check")
    parser.add_argument("--no-synthesis", action="store_true", help="skip the synthesis pass")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--out", default=str(EXTRAS_DIR / "eval" / "results"))
    args = parser.parse_args(argv)

    config = load_fixture(args.fixture)
    if args.no_ai_reader:
        config["ai_reader"] = None
    batch = datetime.now().strftime("%Y%m%d-%H%M%S") + ("-mock" if args.client == "mock" else "")
    batch_dir = Path(args.out) / config["id"] / batch
    batch_dir.mkdir(parents=True, exist_ok=True)
    manifest = {
        "fixture": str(Path(args.fixture).resolve().relative_to(EXTRAS_DIR)).replace("\\", "/"),
        "batch": batch, "client": args.client, "model": args.model if args.client != "mock" else "mock",
        "effort": args.effort, "conditions": args.conditions, "runs": args.runs,
        "content_hash": content_hash(), "git_commit": git_commit(),
        "ai_reader_shared_across_conditions": True, "results": [],
    }

    failures = 0
    clients = []
    for k in range(1, args.runs + 1):
        client = make_client(args, seed=k)
        clients.append(client)
        ai_shared = None
        if config.get("ai_reader"):
            # The AI-reader check doesn't depend on the condition: run it once per run index
            # and share it, so conditions differ only in the persona reviews.
            analysis = pipeline.build_analysis(config, [])
            ai_shared = pipeline.run_ai_reader(config, analysis, client, args.workers)
        for condition in args.conditions:
            label = f"{condition}-run{k}"
            out_dir = batch_dir / label
            out_dir.mkdir(exist_ok=True)
            try:
                results = pipeline.run(config, condition, client, ai_reader=ai_shared or (None, []),
                                       run_synthesis=not args.no_synthesis, workers=args.workers)
            except Exception as exc:  # record the failure and keep going with other conditions
                failures += 1
                (out_dir / "error.txt").write_text(traceback.format_exc(), encoding="utf-8")
                print(f"FAIL  {label}: {exc}")
                manifest["results"].append({"label": label, "status": "error", "error": str(exc)})
                continue
            errors = validate(results)
            (out_dir / "results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
            usage = results["run"]["usage"]
            q = results["quality"]
            cost = usage["estimated_cost_usd"]
            status = "ok" if not errors else f"schema errors: {len(errors)}"
            print(f"{status:4}  {label}: {usage['calls']} calls, {usage['input_tokens'] + usage['output_tokens']} tokens"
                  f"{f', ~${cost:.2f}' if cost is not None else ''}, anchoring "
                  f"{q['anchoring']['rate'] if q['anchoring']['rate'] is not None else 'n/a'}")
            for error in errors[:5]:
                print(f"        - {error}")
            failures += bool(errors)
            manifest["results"].append({"label": label, "status": "ok" if not errors else "schema_error",
                                        "path": f"{label}/results.json"})

    reported = [c.reported_cost_usd for c in clients if hasattr(c, "reported_cost_usd")]
    if reported:
        manifest["claude_code_reported_cost_usd"] = round(sum(reported), 4)
        print(f"\nClaude Code reported an API-equivalent cost of ${sum(reported):.2f} for this batch "
              "(on a subscription this is drawn from plan usage, not billed).")
    (batch_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"\nBatch written to {batch_dir}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
