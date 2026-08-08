#!/usr/bin/env python3
"""Run image-prompt-assistant.md as a system prompt against local Ollama models."""

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request

HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYSTEM_PROMPT = os.path.join(ROOT, "image-prompt-assistant.md")


def api(path, body=None, timeout=900):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(HOST + path, data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.load(response)
    except urllib.error.URLError as error:
        sys.exit(f"cannot reach Ollama at {HOST}: {error.reason}")


def installed():
    """Installed models. Capabilities come from /api/show, which /api/tags under-reports."""
    models = []
    for entry in api("/api/tags")["models"]:
        name = entry["name"]
        shown = api("/api/show", {"model": name})
        caps = shown.get("capabilities", [])
        info = shown.get("model_info", {})
        # Dense or a mixture of experts. It is the better predictor of speed on a small card:
        # a mixture runs at its active size, dense weights above the card's memory do not.
        used = next((v for k, v in info.items() if k.endswith("expert_used_count")), 0)
        count = next((v for k, v in info.items() if k.endswith("expert_count")), 0)
        models.append({
            "name": name,
            "size": entry.get("details", {}).get("parameter_size", "?"),
            "caps": [c for c in caps if c != "completion"],
            "kind": f"MoE {used}/{count}" if count else "dense",
        })
    return sorted(models, key=lambda m: m["name"])


def select(spec, models):
    if spec == "all":
        return models
    if spec == "vision":
        return [m for m in models if "vision" in m["caps"]]
    known = {m["name"]: m for m in models}
    chosen = []
    for name in spec.split(","):
        name = name.strip()
        if name not in known:
            sys.exit(f"{name} is not installed; run --list to see what is")
        chosen.append(known[name])
    return chosen


def parse_script(path):
    """One user turn per line, a blank line starting a fresh conversation. A turn may begin
    with @<path> to attach an image, and # comments out a line."""
    conversations, turns = [], []
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("#"):
                continue
            if not line:
                if turns:
                    conversations.append(turns)
                    turns = []
                continue
            image = None
            if line.startswith("@"):
                reference, _, line = line.partition(" ")
                image = reference[1:]
            turns.append((line.strip(), image))
    if turns:
        conversations.append(turns)
    return conversations


def encode(path, base):
    """Read an image, looking beside the script that named it and then at the repo root."""
    for candidate in (path, os.path.join(base, path), os.path.join(ROOT, path)):
        if os.path.isfile(candidate):
            with open(candidate, "rb") as handle:
                return base64.b64encode(handle.read()).decode()
    sys.exit(f"no such image: {path}")


def unload(model):
    """Free the weights. ComfyUI needs the memory back before it can render."""
    api("/api/generate", {"model": model, "keep_alive": 0}, timeout=60)


def run(model, conversations, system, base, ctx, think, seed=None):
    print(f"\n########## {model['name']} ##########", flush=True)
    for turns in conversations:
        messages = [{"role": "system", "content": system}]
        for text, image in turns:
            print(f"\n>>> {text}", flush=True)
            if image and "vision" not in model["caps"]:
                print(f"[skipped: {model['name']} reports no vision capability]", flush=True)
                continue
            message = {"role": "user", "content": text}
            if image:
                message["images"] = [encode(image, base)]
            messages.append(message)
            started = time.time()
            options = {"num_ctx": ctx}
            if seed is not None:
                options["seed"] = seed
            reply = api("/api/chat", {
                "model": model["name"],
                "messages": messages,
                "stream": False,
                "think": think,
                "options": options,
            })["message"]
            print(f"[{time.time() - started:.0f}s]", flush=True)
            if think and reply.get("thinking"):
                print(f"--- thinking ---\n{reply['thinking'].strip()}\n--- answer ---",
                      flush=True)
            print(reply["content"], flush=True)
            messages.append({"role": "assistant", "content": reply["content"]})


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""OLLAMA_HOST moves the server. The 8k context default matches the front end the
deliverable is written for, so raising it measures something the user will not have.""")
    parser.add_argument("turn", nargs="*", help="a user turn; repeat for one conversation")
    parser.add_argument("--list", action="store_true", help="print installed models and exit")
    parser.add_argument("--models", default="all",
                        help="comma-separated names, or all, or vision (default: all)")
    parser.add_argument("--script", help="file of user turns; see parse_script")
    parser.add_argument("--image", help="image attached to the last turn given on the command line")
    parser.add_argument("--ctx", type=int, default=8192, help="context window (default: 8192)")
    parser.add_argument("--think", action="store_true", help="show the reasoning trace")
    parser.add_argument("--unload", action="store_true",
                        help="free each model when it finishes, leaving memory for ComfyUI")
    parser.add_argument("--seed", type=int,
                        help="fix sampling, so a rule change is the only thing that differs")
    args = parser.parse_args()

    models = installed()
    if args.list:
        width = max(len(m["name"]) for m in models)
        for model in models:
            print(f"{model['name']:<{width}}  {model['size']:>6}  {' '.join(model['caps'])}")
        return

    base = os.getcwd()
    if args.script:
        conversations = parse_script(args.script)
        base = os.path.dirname(os.path.abspath(args.script))
    elif args.turn:
        turns = [(text, None) for text in args.turn]
        if args.image:
            turns[-1] = (turns[-1][0], args.image)
        conversations = [turns]
    else:
        parser.error("give a turn or --script")

    with open(SYSTEM_PROMPT, encoding="utf-8") as handle:
        system = handle.read()
    for model in select(args.models, models):
        run(model, conversations, system, base, args.ctx, args.think, args.seed)
        if args.unload:
            unload(model["name"])


if __name__ == "__main__":
    main()
