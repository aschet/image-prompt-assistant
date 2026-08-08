#!/usr/bin/env python3
"""Time what a ruleset costs to follow: deliberation, output length and seconds per answer.

`score.py` asks whether a model keeps the rules. This asks what keeping them costs, which is a
separate question with a separate answer — a wording can hold every rule and still be unusable
because a single expansion takes a minute.

Two or more system prompts run over the same prompts at the same seed, so the ruleset is the
only thing that differs. Thinking is on by default: `score.py` runs with it off, so a sweep is
structurally blind to deliberation, and deliberation is where the time goes.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import score  # noqa: E402  the Output Format and Wording checks, so speed is never read alone

HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
ROOT = os.path.dirname(HERE)
DELIVERABLE = os.path.join(ROOT, "image-prompt-assistant.md")


def api(path, body, timeout=1800):
    request = urllib.request.Request(HOST + path, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.URLError as error:
        sys.exit(f"cannot reach Ollama at {HOST}: {error.reason}")


def prompts(path):
    """Blank-line separated. A # line annotates what the case stresses and is not sent; a
    `#! medium` line says the request names a medium, which decides whether choosing photography
    counts against the reply."""
    blocks = []
    for block in open(path, encoding="utf-8").read().split("\n\n"):
        lines = block.splitlines()
        given = any(l.lstrip().startswith("#!") and "medium" in l for l in lines)
        kept = "\n".join(l for l in lines if not l.lstrip().startswith("#"))
        if kept.strip():
            blocks.append((kept.strip(), given))
    return blocks


def style_words(reply):
    """Words in the style line, minus the label. None where no style line came back at all,
    which on a thinking model usually means the answer was lost rather than shortened."""
    for line in reply.splitlines():
        line = line.strip().strip("`").strip()
        if line.startswith("Style:"):
            return len(line[len("Style:"):].split())
    return None


def ask(model, system, text, ctx, seed, think, medium_given):
    started = time.time()
    data = api("/api/chat", {
        "model": model, "stream": False, "think": think,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": text}],
        "options": {"num_ctx": ctx, "seed": seed},
    })
    message = data.get("message", {})
    answer = message.get("content", "")
    # spoken() first: a runtime that leaks its trace inline would otherwise score as commentary.
    checks = score.prompt_checks(score.spoken(answer), medium_given)
    return {
        "seconds": time.time() - started,
        "think_chars": len((message.get("thinking") or "").strip()),
        "eval": data.get("eval_count", 0),
        "prompt_eval": data.get("prompt_eval_count", 0),
        "style_words": style_words(answer),
        "kept": sum(checks.values()),
        "asked": len(checks),
        "failed": [k for k, v in checks.items() if not v],
        # An empty answer is the failure that matters and does not look like one in a mean.
        "lost": not answer.strip(),
        "answer": answer,
    }


def selftest():
    """Check this file's own helpers before it is trusted to measure anything.

    score.py checks the rules; nothing checked the harness, and a harness that miscounts is
    worse than no harness because its numbers look like measurements."""
    import tempfile
    bad = 0

    def expect(name, got, want):
        nonlocal bad
        if got != want:
            print(f"  {name}: expected {want!r}, got {got!r}")
            bad += 1
        else:
            print(f"  {name}: ok")

    expect("style words", style_words("```\nStyle: a b c.\nScene: x.\n```"), 3)
    expect("style words, fenced label", style_words("`Style: a b.`"), 2)
    expect("style words, none", style_words("no prompt here"), None)

    handle, path = tempfile.mkstemp(suffix=".txt")
    os.close(handle)
    open(path, "w", encoding="utf-8").write(
        "# a comment that is never sent\n#! medium\nfirst case\n\n"
        "# another\nsecond case\n\n\n")
    cases = prompts(path)
    os.unlink(path)
    expect("cases parsed", len(cases), 2)
    expect("comments dropped", cases[0][0], "first case")
    expect("medium flag set", cases[0][1], True)
    expect("medium flag unset", cases[1][1], False)

    # The checks come from score.py, so a rule change cannot leave this file measuring the old
    # shape without the shared selftest noticing.
    good = "```\nStyle: an oil painting, brooding.\nScene: A fox crosses snow.\n```"
    expect("shared checks all pass on a good reply",
           sorted(k for k, v in score.prompt_checks(good, True).items() if not v), [])
    expect("shared checks catch a bad reply",
           score.prompt_checks("Style: a.\nScene: b.", True)["fenced block"], False)
    print("harness selftest passed" if not bad else f"harness selftest failed ({bad})")
    return bad


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Give --systems two files to compare a change against what it replaced; give it
one to time the deliverable as it stands. OLLAMA_HOST moves the server.

Seeds are pooled, and the default is three of them because one is not a measurement: the same
rules and prompts have scored 82% of checks at one seed and 97% at two others. No particular seed
is worse than another, so pool several rather than avoiding any.

The 8k default is what the front end the deliverable is written for provides, and raising it
measures something a user will not have. Read `lost` before reading the times: a run that
returns no answer at all still contributes a duration, and at 8k with thinking on that is a
real outcome rather than an anomaly.

tests/reference/expansion.txt is Krea 2's own expansion prompt, kept as a speed floor so a
number of seconds means something on a machine that is not this one. Read the seconds and the
deliberation only: it answers in one paragraph, so every check on the two-line format fails by
design and its Kept column is noise.

It expands and does nothing else, so it floors that path alone. Revision carries a whole prior
exchange, reverse engineering carries an image through the encoder, and neither is bounded by
anything measured against it.""")
    parser.add_argument("prompts", nargs="?", default=os.path.join(os.path.dirname(__file__),
                                                                   "expansion.txt"),
                        help="blank-line separated prompts (default: tests/expansion.txt)")
    parser.add_argument("--systems", default=DELIVERABLE,
                        help="comma-separated system-prompt files (default: the deliverable)")
    parser.add_argument("--models", help="comma-separated Ollama models")
    parser.add_argument("--ctx", type=int, default=8192, help="context window (default: 8192)")
    parser.add_argument("--seeds", default="1,2,3",
                        help="comma-separated seeds, pooled (default: 1,2,3). One seed is not a "
                             "measurement: single seeds have differed by 15 points on the same "
                             "rules")
    parser.add_argument("--no-think", action="store_true",
                        help="the configuration score.py measures; thinking is on by default")
    parser.add_argument("--selftest", action="store_true",
                        help="check this harness against known inputs and exit")
    parser.add_argument("--out", help="write every reply here as JSON")
    args = parser.parse_args()
    if args.selftest:
        sys.exit(1 if selftest() else 0)
    if not args.models:
        parser.error("--models is required unless --selftest is given")

    cases = prompts(args.prompts)
    systems = [(os.path.basename(p), open(p, encoding="utf-8").read())
               for p in args.systems.split(",")]
    seeds = [int(s) for s in args.seeds.split(",") if s.strip()]
    rows, saved = [], []
    for model in args.models.split(","):
        for label, system in systems:
            got = []
            for seed in seeds:
                for index, (text, given) in enumerate(cases, 1):
                    try:
                        result = ask(model, system, text, args.ctx, seed, not args.no_think,
                                     given)
                    except Exception as error:  # one bad case should not lose the run
                        print(f"  {model} {label} s{seed} #{index}: {error}", flush=True)
                        continue
                    got.append(result)
                    saved.append({"model": model, "system": label, "seed": seed,
                                  "case": index, **result})
                    print(f"  {model:<20} {label:<22} s{seed} #{index:<3} "
                          f"{result['seconds']:6.1f}s  think {result['think_chars']:6d}c  "
                          f"out {result['eval']:5d}t  style {str(result['style_words']):>4}  "
                          f"kept {result['kept']}/{result['asked']}"
                          f"{'  ANSWER LOST' if result['lost'] else ''}", flush=True)
            if got:
                rows.append((model, label, got))

    print(f"\n{'Model':<20} {'Ruleset':<24} {'Sys Tok':>8} {'Think':>8} {'Out Tok':>8} "
          f"{'Sec':>7} {'Style':>6} {'Kept':>9} {'Lost':>5}")
    for model, label, got in rows:
        n = len(got)
        styled = [g["style_words"] for g in got if g["style_words"]]
        kept, asked = sum(g["kept"] for g in got), sum(g["asked"] for g in got)
        print(f"{model:<20} {label:<24} {got[0]['prompt_eval']:8d} "
              f"{sum(g['think_chars'] for g in got) // n:8d} "
              f"{sum(g['eval'] for g in got) // n:8d} "
              f"{sum(g['seconds'] for g in got) / n:7.1f} "
              f"{(sum(styled) / len(styled) if styled else 0):6.1f} "
              f"{kept:4d}/{asked:<4d} {sum(g['lost'] for g in got):5d}")
    # Speed bought by breaking the format is not speed, so name what broke.
    for model, label, got in rows:
        broke = sorted({k for g in got for k in g["failed"]})
        if broke:
            print(f"\n{model} {label} failed: {', '.join(broke)}")
    if args.out:
        json.dump(saved, open(args.out, "w", encoding="utf-8"), indent=1)
        print(f"\nwrote {args.out}")


if __name__ == "__main__":
    main()
