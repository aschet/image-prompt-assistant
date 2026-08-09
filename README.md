# Image Prompt Assistant

A system prompt for an assistant that writes image prompts for modern natural-language
text-to-image models — Krea 2, Flux 2, Z-Image and similar. It produces prompt text only; it
does not generate images.

## What It Does

- Expands an existing prompt, or develops an idea into one
- Reverse-engineers a prompt from one or more images
- Revises a prompt: a style change, a targeted edit, an optimization pass, or an adaptation to
  another aspect ratio
- Fixes a prompt from a render that came out wrong, diagnosing the cause from what you describe
- Suggests styles — alternatives for a prompt, or examples within a category — each with a
  ready-to-paste style line
- Explains a style in detail, or gives an example prompt in it
- Proposes titles

Every prompt comes back as two labelled lines, with no commentary and no markup around them:

```
Style: a gouache illustration with matte chalky coverage, flat layered shapes, a cool restrained palette, still and wintry in mood.
Scene: A red fox stands in profile mid-stride on unbroken snow in the lower third of the frame, one forepaw lifted, its coat rust-orange along the back and cream at the throat. Behind it the ground rises in three pale drifts and thin dark trunks cross the middle distance, closing on a narrow band of overcast sky. Soft even light falls without shadow.
```

The style line carries the medium, how it is worked, the palette and the mood; the scene line
carries everything else. The split is the point: a style line must apply unchanged to any other
scene, so it can be swapped without disturbing what the image shows.

## Use

Paste `image-prompt-assistant.md` into an assistant's system prompt or custom instructions. It
is written to stand alone and depends on no other file.

Give the model at least 8k of context, and turn extended thinking off where the front end offers
it: the rules hold without it, a prompt comes back in about three seconds instead of fifty, and a
model left deliberating in a small context can spend the whole of it and return nothing.

Prompts are composed for a 3:4 portrait frame — change the default in the Wording section if you
work in another shape. Where you leave the style open, it picks a painting, illustration or print
medium; photography is never its own choice, so ask for it and you get it.

The rules were developed with Claude Opus 5, and Claude Sonnet 5 is the primary target.

## Limitations

- It writes prompts. Whether one renders well, and whether the result is any good, stays with
  you.
- The prompts were tested mainly against Krea 2, so anything claimed here about what a sampler
  does was seen there first.
- Reading an image needs a model with vision and needs it to be good at it — one model here
  keeps 98% of the rules and recovers barely half of what a picture shows.

## Local Models

Test the model you mean to use, but three things hold generally. Below about 4B a model falls
apart rather than degrading: a 2.3B keeps a third of the checks and a 0.87B answered a request
for a style's details with a prompt instead. Stated size predicts less than it looks — most large
models are mixtures of experts running a fraction of their weights at a time, so a 5B dense model
can hold the rules better than a 30B that activates four experts of sixty-four, and here it does.
What size predicts reliably is speed: on a 12 GB card a mixture runs at 41–62 tok/s whatever its
total, while dense weights above 20B spill to the processor and fall to 6.

[MODELS.md](MODELS.md) carries the scores for every model tested here, written
straight from a saved sweep so nothing in it is transcribed by hand.

## Scoring Your Own Model

Python 3 and a running Ollama server, nothing else to install:

```
python3 tests/score.py --models all --verify --free --unload
```

`--verify` skips a model whose repeated reply differs, which means something else is using the
machine; `--free` unloads a running ComfyUI, which otherwise takes the memory the model needs.
Name a model instead of `all` to score one, and see `--help` for the rest; a failing check names
the rule it came from. `tests/strain.py` answers the separate question of what following the
rules costs in time, which a score does not tell you.

## License

© 2026 Thomas Ascher. Licensed under [CC BY 4.0](LICENSE) — use, adapt and redistribute it,
including commercially, provided you give credit.

`tests/reference/expansion.txt` is not covered by that: it is Krea 2's own prompt-expansion
system prompt, copied unmodified from [krea-ai/krea-2](https://github.com/krea-ai/krea-2) and
licensed under Apache 2.0, with its licence beside it.
