#!/usr/bin/env python3
"""Write MODELS.md from a saved sweep, so the tables are never transcribed by hand.

The whole file is written every time and nothing in it is edited: splicing into a page that also
holds prose published a stale table once already, since the sweep process holds the checker as it
was when it started and a checker fixed afterwards leaves the numbers wrong until rebuilt. The
README keeps the observations and links here; this file is output.
"""

import argparse
import contextlib
import io
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import score  # noqa: E402

# The page around the tables, written fresh each time. It says what the numbers are and what
# they cannot carry; what a reader should conclude from them stays in the README.
HEADER = """# Scored Models

Measured on a Ryzen 7 7700 with an RTX 4070 (12 GB) and 64 GB of RAM, at an 8k context and a
fixed seed. Read the bands, not the ranking: nothing sets a sampling temperature, so a score is
one draw — three seeds moved two models by 9 and 16 points out of 88. Speed will not carry to
another machine; Rules Kept will.

Written by `tests/table.py` from a saved sweep, whole file at a time — anything edited here is
overwritten. [README.md](README.md) says what the scores mean and how to run your own.
"""


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
        epilog="""The file is replaced outright, so this is safe to run as often as the numbers
change. A model dropped with --drop stays out of the page but stays in the transcript, which is
the evidence and is never edited.""")
    parser.add_argument("transcript", help="a run saved by score.py --transcript")
    parser.add_argument("--into", default=os.path.join(os.path.dirname(ROOT), "MODELS.md"),
                        help="file to write (default: MODELS.md)")
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

    with open(args.into, "w", encoding="utf-8") as handle:
        handle.write(f"{HEADER}\n{built}\n")
    print(f"wrote {built.count(chr(10) + '| `')} rows to {args.into}")


if __name__ == "__main__":
    main()
