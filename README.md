# Image Prompt Assistant

A system prompt for an assistant that writes image prompts for modern natural-language
text-to-image models — Krea 2, Flux 2, Z-Image and similar. It produces prompt text only; it
does not generate images.

## What It Does

- Expands an existing prompt, or develops an idea into one
- Reverse-engineers a prompt from one or more images
- Revises a prompt, rewrites it as an optimization pass, adapts it to another aspect ratio, or
  varies the scene while holding the style
- Fixes a prompt from a render that came out wrong, diagnosing the cause from what you describe
- Suggests styles — alternatives for a prompt, or examples within a category — each with a
  ready-to-paste style line
- Explains a style in detail, or gives an example prompt in it
- Proposes titles

## Output Format

Every prompt comes back as two lines, in a fenced block with no commentary around it:

```
Style: a gouache illustration with matte chalky coverage, flat layered shapes, a cool restrained palette, still and wintry in mood.
A red fox stands in profile mid-stride on unbroken snow in the lower third of the frame, one forepaw lifted, its tail held low and level behind it. Its coat runs rust-orange along the back and shoulders, fading to cream at the throat, with black stockings on all four legs. Shallow prints trail back from its hind paws to the left edge. Directly behind, the ground rises in three pale drifts, each fainter than the last, and a stand of thin dark trunks crosses the middle distance. The slope continues to a low ridgeline near the top edge, where a narrow band of overcast sky closes the frame. Soft even light falls without shadow, thin mist gathering between the trunks, and a single crow sits high on a bare branch at the right.
```

The `Style:` line carries the medium, how it is worked, the palette and the mood, in about twenty
words, naming a movement or artist only where that changes what the image looks like. The scene
line carries everything else — what is depicted, its attributes, placement, framing, atmosphere
and the light in the scene.

The split is the whole point. A style line must apply unchanged to any other scene, so it can be
swapped without disturbing what the image shows.

## Defaults

Prompts are composed for a 3:4 portrait frame. The aspect ratio is
never named in the prompt itself — it is a generation setting, and stating it would only spend
words the sampler ignores. Change the default frame in the Wording section if you work in
another shape.

Where you leave the style open, it picks a painting, illustration or print medium. Photography
is never its own choice — ask for it and you get it.

## Use

Paste `image-prompt-assistant.md` into an assistant's system prompt or custom instructions. It
is written to stand alone and depends on no other file.

Set the model's context window to at least 8k, and turn extended thinking off. The rules are
held just as well without it and a prompt comes back in about three seconds instead of fifty,
measured on the same file and the same machine. Left on at 8k, a model can also spend the whole
window deliberating and return an empty reply rather than a short one.

The rules were developed with Claude Opus 5, and Claude Sonnet 5 is the primary target. The
prompts were tested mainly against Krea 2, so anything claimed here about what a sampler does
was seen there first.

For a local model, use at least 8B and test the one you mean to use — parameter count does not
predict whether a model holds the rules, and below 8B the failure changes kind rather than
degree: a 4.7B swung 16 points across three seeds and in one run returned nothing usable for a
request it had just answered perfectly. What size does predict is speed. On a 12 GB card a
mixture of experts runs at 41–62 tok/s whatever its total, while dense weights above 20B spill
to the processor and fall to 6. Reading an image needs a model with vision.

## Local Models

`tests/score.py` runs every request type against a local Ollama model and checks the reply
mechanically: the output format, the prohibitions, whether each request reaches the right
section, and how much of a prompt survives a revision. `tests/strain.py` times what following
the rules costs, which is a separate question — a model can keep every rule and still take a
minute per prompt. It times the expansion path against Krea 2's own expansion prompt, so a
figure in seconds still means something on another machine. Whether a judgment is right, or a render any good, stays with you.

Measured on a Ryzen 7 7700 with an RTX 4070 (12 GB) and 64 GB of RAM, at an 8k context and a
fixed seed. Read the bands, not the ranking: nothing sets a sampling temperature, so a score is
one draw — three seeds moved two models by 9 and 16 points out of 88. Speed will not carry to
another machine; Rules Kept will.

Every model here above 20B is a mixture of experts. No larger dense model is included: on a
12 GB card their weights spill to the processor and they run at 6 to 8 tok/s against 41 and up
for everything listed, which is too slow to use. That is a property of the card, not of the
models — with more memory they would belong here.

<!-- tables:start -->

| Model | Size | Vision | Rules Kept | Speed | Verdict |
| --- | --- | --- | --- | --- | --- |
| `laguna-xs-2.1:latest` | 33.4B | No | 85/85 (100%) | 57 tok/s | Recommended |
| `ornith:9b` | 9.0B | No | 85/85 (100%) | 73 tok/s | Recommended |
| `gemma4:12b` | 11.9B | Yes | 84/85 (99%) | 49 tok/s | Recommended |
| `gemma4:26b` | 25.8B | Yes | 84/85 (99%) | 45 tok/s | Recommended |
| `qwen3.6:35b` | 36.0B | Yes | 84/85 (99%) | 47 tok/s | Recommended |
| `glm-4.7-flash:latest` | 29.9B | No | 82/85 (96%) | 42 tok/s | Recommended |
| `gpt-oss:20b` | 20.9B | No | 82/85 (96%) | 60 tok/s | Recommended |
| `qwen3.5:9b` | 9.7B | Yes | 79/85 (93%) | 76 tok/s | Recommended |
| `nemotron3:33b` | 33.0B | Yes | 77/85 (91%) | 40 tok/s | Recommended |
| `nemotron-3-nano:30b` | 31.6B | No | 76/85 (89%) | 46 tok/s | Usable |
| `gemma4:e4b` | 8.0B | Yes | 75/85 (88%) | 101 tok/s | Usable |
| `ministral-3:14b` | 13.9B | Yes | 74/85 (87%) | 49 tok/s | Usable |
| `north-mini-code-1.0:q4_K_M` | 30.5B | No | 72/85 (85%) | 46 tok/s | Usable |
| `ornith:35b` | 34.7B | No | 69/85 (81%) | 54 tok/s | Usable |
| `granite4.1:8b` | 8.8B | No | 22/85 (26%) | 71 tok/s | Unusable |

### Reverse Engineering

Over 12 source images, one per medium. Light is asked only
of sources with a direction to read, and a palette only of sources that have
one — ink on cream has neither.

| Model | Medium Read | Framing Stated | Light Stated | Palette Named | Kept |
| --- | --- | --- | --- | --- | --- |
| `gemma4:12b` | 12/12 | 12/12 | 4/6 | 9/10 | 37/40 (92%) |
| `gemma4:26b` | 12/12 | 12/12 | 6/6 | 10/10 | 40/40 (100%) |
| `qwen3.6:35b` | 11/12 | 12/12 | 5/6 | 9/10 | 37/40 (92%) |
| `qwen3.5:9b` | 12/12 | 12/12 | 6/6 | 9/10 | 39/40 (98%) |
| `nemotron3:33b` | 11/12 | 11/12 | 5/6 | 6/10 | 33/40 (82%) |
| `gemma4:e4b` | 11/12 | 8/12 | 4/6 | 8/10 | 31/40 (78%) |
| `ministral-3:14b` | 12/12 | 12/12 | 5/6 | 7/10 | 36/40 (90%) |

<!-- tables:end -->

The first table is text only, so every model answers the same cases. The two below it hold what
only a model with vision can attempt, kept apart so a capability is never averaged into a score.

### Scoring Your Own Model

Python 3 and a running Ollama server, nothing else to install:

```
python3 tests/score.py --models all --verify --free --unload
```

`--verify` skips a model whose repeated reply differs, which means something else is using the
machine; `--free` unloads a running ComfyUI, which otherwise takes the memory the model needs.
Name a model instead of `all` to score just that one, and see `--help` for the rest. A failing
check names the rule it came from.

## License

© 2026 Thomas Ascher. Licensed under [CC BY 4.0](LICENSE) — use, adapt and redistribute it,
including commercially, provided you give credit.

One file is not covered by that. `tests/reference/expansion.txt` is Krea 2's own prompt-expansion
system prompt, copied unmodified from [krea-ai/krea-2](https://github.com/krea-ai/krea-2) and
licensed under Apache 2.0; its licence sits beside it. It is kept only as a speed floor for
`tests/strain.py` and is no part of the deliverable.