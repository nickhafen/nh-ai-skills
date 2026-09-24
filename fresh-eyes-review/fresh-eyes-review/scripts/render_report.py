"""Render a results.json as a self-contained HTML report.

Usage:
    python render_report.py results.json [--out report.html]
    python render_report.py --viewer [--out viewer.html]   # no embedded results: open/paste a file

The report is assets/report-template.html with the results embedded inline, so it
opens by double-click with no server and no network access.
"""

import argparse
import json
import sys
from pathlib import Path

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "report-template.html"
PLACEHOLDER = "/*RESULTS_JSON*/null"


def render_html(results):
    template = TEMPLATE.read_text(encoding="utf-8")
    if PLACEHOLDER not in template:
        raise RuntimeError("report-template.html is missing the results placeholder")
    payload = "null" if results is None else json.dumps(results, ensure_ascii=False)
    # Keep the JSON from closing the <script> tag or breaking JavaScript parsing.
    payload = payload.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return template.replace(PLACEHOLDER, payload)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("results", nargs="?")
    parser.add_argument("--out")
    parser.add_argument("--viewer", action="store_true", help="write the empty viewer instead of a report")
    args = parser.parse_args(argv)
    if args.viewer:
        html, default = render_html(None), "viewer.html"
    elif args.results:
        html = render_html(json.loads(Path(args.results).read_text(encoding="utf-8")))
        default = str(Path(args.results).with_name("report.html"))
    else:
        parser.error("give a results.json path, or --viewer")
    out = Path(args.out or default)
    out.write_text(html, encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
