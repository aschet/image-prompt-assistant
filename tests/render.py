#!/usr/bin/env python3
"""Render prompts through a ComfyUI workflow, to test rules that claim what the sampler does."""

import argparse
import html
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

HOST = os.environ.get("COMFYUI_HOST", "http://127.0.0.1:8188").rstrip("/")
CLIENT = str(uuid.uuid4())


def api(path, body=None, timeout=600, raw=False):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(HOST + path, data=data,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return response.read() if raw else json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:2000]
        sys.exit(f"ComfyUI rejected the request ({error.code}):\n{detail}")
    except urllib.error.URLError as error:
        sys.exit(f"cannot reach ComfyUI at {HOST}: {error.reason}")


def preflight():
    """Fail before doing any work if ComfyUI is not up; it often is not."""
    try:
        with urllib.request.urlopen(HOST + "/system_stats", timeout=5) as response:
            stats = json.load(response)
    except Exception as error:
        sys.exit(f"ComfyUI is not reachable at {HOST} ({error}).\n"
                 f"Start it, or point COMFYUI_HOST elsewhere. Rendering is optional — "
                 f"tests/ask.py does not need it.")
    return stats.get("system", {}).get("comfyui_version", "?")


def ollama_resident(free=False):
    """Models Ollama is holding, optionally freed. One box will not fit a 30B alongside a
    diffusion model."""
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
    try:
        with urllib.request.urlopen(host + "/api/ps", timeout=5) as response:
            loaded = json.load(response).get("models", [])
    except Exception:
        return
    for model in loaded:
        gb = model.get("size", 0) / 1e9
        if not free:
            print(f"note: Ollama holds {model['name']} ({gb:.1f} GB); --free unloads it",
                  flush=True)
            continue
        body = json.dumps({"model": model["name"], "keep_alive": 0}).encode()
        request = urllib.request.Request(host + "/api/generate", data=body,
                                         headers={"Content-Type": "application/json"})
        try:
            urllib.request.urlopen(request, timeout=60).read()
            print(f"freed {model['name']} ({gb:.1f} GB)", flush=True)
        except Exception as error:
            print(f"could not free {model['name']}: {error}", flush=True)


def find(workflow, classes, what, override=None):
    if override:
        if override not in workflow:
            sys.exit(f"no node {override} in the workflow")
        return override
    found = [k for k, v in workflow.items() if v.get("class_type") in classes]
    if len(found) != 1:
        sys.exit(f"expected exactly one {what} node, found {found or 'none'}; "
                 f"name one explicitly")
    return found[0]


def read_prompts(source):
    """Blank-line separated blocks. Code fences are stripped, so ask.py output pastes in."""
    text = open(source, encoding="utf-8").read() if os.path.isfile(source) else source
    blocks = []
    for block in text.split("\n\n"):
        lines = [l for l in block.strip().splitlines() if l.strip() != "```"]
        if lines:
            blocks.append("\n".join(lines).strip())
    return blocks


def render(workflow, text_node, seed_node, prompt, seed, prefix):
    workflow[text_node]["inputs"]["text"] = prompt
    workflow[seed_node]["inputs"]["seed"] = seed
    for node in workflow.values():
        if node.get("class_type") == "SaveImage":
            node["inputs"]["filename_prefix"] = prefix
    queued = api("/prompt", {"prompt": workflow, "client_id": CLIENT})
    if "prompt_id" not in queued:
        sys.exit(f"unexpected reply from /prompt: {queued}")
    pid = queued["prompt_id"]
    while True:
        history = api(f"/history/{pid}")
        if pid in history:
            status = history[pid].get("status", {})
            if status.get("status_str") == "error":
                return []
            images = []
            for out in history[pid].get("outputs", {}).values():
                images.extend(out.get("images", []))
            if images:
                return images
        time.sleep(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompts", help="file of blank-line separated prompts, or a prompt")
    parser.add_argument("--workflow", default="tests/krea2-api.json", help="API-format export")
    parser.add_argument("--out", default="renders", help="output directory (default: renders)")
    parser.add_argument("--seeds", type=int, default=3, help="renders per prompt (default: 3)")
    parser.add_argument("--seed", type=int, default=1, help="first seed; the rest follow it")
    parser.add_argument("--text-node", help="node id of the prompt encoder, if ambiguous")
    parser.add_argument("--seed-node", help="node id of the sampler, if ambiguous")
    parser.add_argument("--free", action="store_true",
                        help="unload any resident Ollama model before rendering")
    args = parser.parse_args()

    print(f"ComfyUI {preflight()} at {HOST}", flush=True)
    ollama_resident(free=args.free)
    workflow = json.load(open(args.workflow, encoding="utf-8"))
    text_node = find(workflow, {"CLIPTextEncode"}, "prompt encoder", args.text_node)
    seed_node = find(workflow, {"KSampler", "KSamplerAdvanced", "SamplerCustom",
                                "SamplerCustomAdvanced"}, "sampler", args.seed_node)
    prompts = read_prompts(args.prompts)
    if not prompts:
        sys.exit("no prompts found")
    os.makedirs(args.out, exist_ok=True)

    rows = []
    for index, prompt in enumerate(prompts, 1):
        print(f"\n[{index}/{len(prompts)}] {prompt.splitlines()[0][:70]}", flush=True)
        shots = []
        for offset in range(args.seeds):
            seed = args.seed + offset
            started = time.time()
            images = render(workflow, text_node, seed_node, prompt, seed, f"rule-test/{index:03d}")
            if not images:
                print(f"  seed {seed}: failed", flush=True)
                continue
            for image in images:
                query = urllib.parse.urlencode({"filename": image["filename"],
                                                "subfolder": image.get("subfolder", ""),
                                                "type": image.get("type", "output")})
                blob = api("/view?" + query, raw=True)
                name = f"{index:03d}-seed{seed}.png"
                with open(os.path.join(args.out, name), "wb") as handle:
                    handle.write(blob)
                shots.append(name)
            print(f"  seed {seed}: {time.time() - started:.0f}s", flush=True)
        rows.append((prompt, shots))

    index_path = os.path.join(args.out, "index.html")
    with open(index_path, "w", encoding="utf-8") as page:
        page.write("<meta charset='utf-8'><style>body{font:14px/1.5 system-ui;margin:2rem;"
                   "max-width:70rem}pre{white-space:pre-wrap;background:#f4f4f4;padding:.75rem;"
                   "border-radius:6px}img{max-width:22rem;vertical-align:top;margin:.25rem}"
                   "@media(prefers-color-scheme:dark){body{background:#111;color:#eee}"
                   "pre{background:#222}}</style>\n")
        for prompt, shots in rows:
            page.write(f"<pre>{html.escape(prompt)}</pre>\n")
            for shot in shots:
                page.write(f"<img src='{html.escape(shot)}' loading='lazy'>")
            page.write("\n<hr>\n")
    print(f"\nwrote {index_path}")


if __name__ == "__main__":
    main()
