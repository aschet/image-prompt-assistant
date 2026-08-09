#!/usr/bin/env python3
"""Write the score tables into README.md, so they are never transcribed by hand.

Hand-splicing published a stale table once already: the sweep process holds the checker as it
was when it started, so a checker fixed afterwards leaves the numbers wrong until they are
rebuilt. This rebuilds them from the saved transcript, which is why every sweep should keep one.
"""

import argparse
import contextlib
import io
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import score  # noqa: E402

START = "<!-- tables:start -->"
END = "<!-- tables:end -->"
# Where the tables go when the markers are not there yet.
ANCHOR = "\nSpeed is throughput on that machine"


def tables(transcript, drop):
    """The three tables as score.py writes them, with any dropped models removed."""
    handle, path = tempfile.mkstemp(suffix=".md")
    os.close(handle)
    quiet = io.StringIO()
    try:
        # rescore prints the tables and every failure list; only the file is wanted here.
        with contextlib.redirect_stdout(quiet):
            score.rescore(transcript, path)
        text = open(path, encoding="utf-8").read().strip()
    finally:
        os.unlink(path)
    if drop:
        text = "\n".join(l for l in text.splitlines()
                         if not any(f"`{d}`" in l and l.startswith("|") for d in drop))
    return text


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Markers are inserted on the first run and reused after it, so this is safe to
run as often as the numbers change. A model dropped with --drop stays out of the README but
stays in the transcript, which is the evidence and is never edited.""")
    parser.add_argument("transcript", help="a run saved by score.py --transcript")
    parser.add_argument("--into", default=os.path.join(os.path.dirname(ROOT), "README.md"),
                        help="file to write the tables into (default: README.md)")
    parser.add_argument("--drop", default="", help="comma-separated models to leave out")
    parser.add_argument("--print", action="store_true", help="print them instead of writing")
    args = parser.parse_args()

    # score.py empties the transcript before its first model, so an empty one means the sweep
    # died before finishing a single model. Rebuilding from it would publish nothing measured.
    saved = json.load(open(args.transcript, encoding="utf-8"))
    if not saved:
        sys.exit(f"{args.transcript} is empty: the sweep that should have written it did not "
                 f"finish a model. Rerun it rather than rebuilding from this.")
    built = tables(args.transcript, [d for d in args.drop.split(",") if d])
    if args.print:
        print(built)
        return

    page = open(args.into, encoding="utf-8").read()
    block = f"{START}\n\n{built}\n\n{END}"
    if START in page and END in page:
        page = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: block, page,
                      flags=re.S)
        where = "replaced"
    elif ANCHOR in page:
        at = page.index(ANCHOR)
        page = page[:at] + "\n" + block + "\n" + page[at:]
        where = "inserted"
    else:
        sys.exit(f"no markers and no anchor in {args.into}; add {START} and {END} by hand")
    open(args.into, "w", encoding="utf-8").write(page)
    print(f"{where} {built.count(chr(10) + '| `')} rows in {args.into}")


if __name__ == "__main__":
    main()
