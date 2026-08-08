#!/usr/bin/env python3
"""Score local models against the rules: what they obey, how much they keep, how fast.

Every check here is mechanical. Whether an image is good stays with the author; what this
measures is whether a model can hold the rules and follow them, which is what decides
whether it is worth pointing at the deliverable at all.
"""

import argparse
import collections
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

import ask

# A style line may open with a proper adjective; anything else upper case is the rule ignored.
PROPER = {"japanese", "chinese", "french", "italian", "dutch", "german", "flemish", "spanish",
          "persian", "byzantine", "victorian", "edwardian", "georgian", "baroque", "renaissance",
          "gothic", "romanesque", "soviet", "russian", "greek", "roman", "egyptian", "nordic",
          "celtic", "bauhaus", "mughal", "ukiyo", "art", "pre", "neo", "post", "american",
          "british", "swiss", "danish", "norwegian", "mexican", "indian", "korean", "tibetan"}

# "portrait" alone is a legitimate subject, so only the orientation senses count.
FRAME = re.compile(r"\b(?:\d+:\d+|widescreen|panoramic|banner|letterbox|"
                   r"(?:portrait|landscape|square|wide|tall|vertical|horizontal)[- ]"
                   r"(?:frame|format|orientation|aspect)|aspect ratio)\b", re.I)

PHOTO = re.compile(r"\b(?:photograph\w*|photo|photorealistic|cinematic|film still|dslr|"
                   r"\d+mm lens|bokeh|depth of field)\b", re.I)

# Weights cover phrases as often as single words, so this cannot stop at \w+.
SYNTAX = re.compile(r"\([^()]{1,60}:\s*\d|\bBREAK\b|^\s*[-*]\s|^\s*\{", re.M)

# A fix or an edit that denies the fault instead of repairing it.
ABSENCE = re.compile(r"\b(?:no|without|not|never|free of|devoid of|lacking)\s+"
                     r"(?:any\s+)?(?:blur\w*|depth|bokeh|shadow\w*|photograph\w*|texture)", re.I)

WORD = re.compile(r"[a-z]{4,}")
# Function words, plus the reaction and filler the rules ban. Counting those made a revision
# score worse for dropping words it was never allowed to write.
STOP = {"with", "that", "this", "from", "into", "over", "under", "their", "there", "which",
        "where", "while", "above", "below", "along", "across", "onto", "upon", "than", "then",
        "also", "just", "very", "much", "some", "each", "both", "same", "other", "frame",
        "scene",
        "toward", "against", "between", "behind", "beside", "around", "through",
        "emphasizing", "indicating", "suggesting", "capturing", "conveying", "evoking",
        "creating", "adding", "lending", "giving", "rendered", "rendering", "depicting",
        "isolation", "silence", "solitude", "atmosphere", "mood", "sense", "feeling",
        "quality", "essence", "serene", "tranquil", "peaceful", "dramatic", "striking",
        "beautiful", "beautifully", "gently", "softly", "sharply", "confidently"}


def fences(reply):
    """Fenced blocks, which the rules now forbid. Kept to detect them, not to require them."""
    return [b.strip() for b in re.findall(r"```(?:\w*\n)?(.*?)```", reply, re.S) if b.strip()]


def split(block):
    """A block's style and scene line, or (None, None) if it is not shaped like a prompt.

    Fence markers are dropped first. Models still emit them despite the rule, and letting them
    land in the scene would cost it its full stop as well — one fault counted twice, which is
    what prompt_body exists to avoid."""
    lines = [l for l in block.splitlines() if l.strip() and l.strip().strip("`") != ""]
    if len(lines) < 2 or not lines[0].startswith("Style:"):
        return None, None
    return lines[0], " ".join(lines[1:])


def spoken(reply):
    """The answer with a leaked reasoning trace removed. Every call asks for no thinking and
    most models comply; ornith:9b emits the trace inline regardless, opening with "The user is
    asking me to" and closing on a bare </think>. That is the runtime leaking, not the model
    breaking a rule, and scoring it as a preamble measures the wrong thing."""
    cut = reply.rfind("</think>")
    return (reply[cut + len("</think>"):] if cut != -1 else reply).strip()


def prompt_body(reply):
    """The prompt in a reply, and whether it came wrapped in markup. Markup is one fault, not
    twelve: the wording and the prohibitions are all still there to judge."""
    fenced = fences(reply)
    for block in fenced:
        if split(block)[0] is not None:
            return block, len(fenced) == 1
    loose = re.search(r"^Style:.*", reply.strip(), re.M | re.S)
    return (loose.group(0).strip(), False) if loose else (None, False)


def prompt_blocks(reply):
    """Every prompt in a reply, splitting on the Style: label when no fences were given."""
    good = [b for b in fences(reply) if split(b)[0] is not None]
    if good:
        return good
    parts = re.split(r"(?m)^(?=Style:)", reply.strip())
    return [p.strip() for p in parts if p.strip().startswith("Style:")]


def content(text):
    return {w for w in WORD.findall(text.lower()) if w not in STOP}


def kept(before, after):
    """Share of the earlier scene's content words still present. A revision that rewrites the
    scene instead of editing it scores low here even when its output is otherwise perfect."""
    old = content(before)
    return len(old & content(after)) / len(old) if old else 1.0


class Case:
    def __init__(self, name, turns, check, image=None, lit=True, hued=True):
        self.name, self.turns, self.check, self.image = name, turns, check, image
        self.lit = lit    # whether the source has a light direction to read at all
        self.hued = hued  # whether it has a palette to name; ink on cream has none


def prompt_checks(reply, medium_given=False):
    """Output Format and Wording, on a reply that must carry one prompt. Every key is always
    present: a reply with no prompt fails all of them rather than shrinking its denominator."""
    keys = ["no markup", "two lines", "no blank line", "Style: prefix", "Scene: prefix",
            "lower case", "full stops", "no commentary", "no 'digital'", "no frame named",
            "no prompt syntax", "no negative prompt"]
    if not medium_given:
        keys.append("photography not chosen")
    out = dict.fromkeys(keys, False)
    block, fenced = prompt_body(reply)
    if block is None:
        return out
    # Markup around the block is the fault now, not its absence: the labels delimit it, and a
    # fence a model only sometimes emits is worse than none for lifting the prompt out.
    out["no markup"] = not fenced
    style, scene = split(block)
    out["two lines"] = style is not None
    if style is None:
        return out
    body = style[len("Style:"):].strip()
    first = re.sub(r"[^a-z]", "", body.split(" ")[0].lower()) if body else ""
    # The scene sits directly under the style line so the block copies in one go.
    raw = block.splitlines()
    out["no blank line"] = len(raw) > 1 and raw[1].strip() != ""
    out["Style: prefix"] = style.startswith("Style: ")
    # Both lines are labelled. Models added "Scene:" unprompted often enough that requiring it
    # scored better than forbidding it, over three seeds and five models.
    out["Scene: prefix"] = scene.startswith("Scene: ")
    out["lower case"] = bool(body) and (body[0].islower() or first in PROPER)
    out["full stops"] = style.rstrip().endswith(".") and scene.rstrip().endswith(".")
    # Nothing but the prompt; any markup around it is scored above.
    stripped = reply.strip()
    # Prose around the block is a separate fault from wrapping it in markup, so a fenced reply
    # with nothing else in it fails "no markup" alone.
    out["no commentary"] = (stripped.startswith("```") and stripped.endswith("```")
                            if fenced else stripped == block)
    out["no 'digital'"] = not re.search(r"\bdigital\b", reply, re.I)
    out["no frame named"] = not FRAME.search(block)
    out["no prompt syntax"] = not SYNTAX.search(block)
    out["no negative prompt"] = not re.search(r"negative prompt", reply, re.I)
    if not medium_given:
        out["photography not chosen"] = not PHOTO.search(style)
    return out


def check_expand(reply, prior):
    return prompt_checks(reply)


def check_titles(reply, prior):
    # Titles arrive bolded often enough that emphasis must come off before judging their case.
    bullets = [re.sub(r"[*_`]", "", b).strip()
               for b in re.findall(r"^\s*[-*]\s+(.+)$", reply, re.M)]
    return {"routes to titles": not fences(reply),
            "five titles": len(bullets) == 5,
            "title case": bool(bullets) and all(
                sum(w[:1].isupper() for w in b.split()) >= max(1, len(b.split()) - 2)
                for b in bullets)}


def check_alternatives(reply, prior):
    # The name stands alone now, so the colon that used to introduce a description is optional.
    bullets = re.findall(r"^\s*[-*]\s+\*\*(.+?)\*\*\s*:?\s*$", reply, re.M)
    # Delimiter-agnostic, so the rule may mark the style line or not without the score moving.
    # Anchoring on the label and running to the next bullet also catches a span the model never
    # closed, which is how a style line turns into a whole prompt.
    lines = [m.group(1).strip().strip("`").strip()
             for m in re.finditer(r"(Style:.*?)(?=\n\s*[-*]\s+\*\*|\n\s*\n|\Z)", reply, re.S)]
    return {"five styles": len(bullets) == 5,
            "bold name": len(bullets) == 5,
            "style line each": len(lines) == 5,
            "no scene detail": all(len(l.split()) < 40 for l in lines) if lines else False}


def check_details(reply, prior):
    return {"description label": "**Description:**" in reply,
            "origin label": "**Origin:**" in reply,
            "suits label": "**Suits:**" in reply,
            "artists label": "**Artists:**" in reply,
            "example prompt": len(prompt_blocks(reply)) == 1}


def check_variations(reply, prior):
    """The wrong number of blocks is one fault. Whether the style line held and the scenes
    differ is still answerable across however many arrived, and is asked separately."""
    good = [b for b in (split(b) for b in prompt_blocks(reply)) if b[0] is not None]
    return {"three blocks": len(good) == 3,
            "style line identical": len(good) > 1 and len({s for s, _ in good}) == 1,
            "scenes differ": len(good) > 1 and len({c for _, c in good}) == len(good)}


def revision_checks(reply, prior, extra):
    """Format checks plus the two that say whether the edit stayed an edit."""
    out = prompt_checks(reply, medium_given=True)
    out.update(dict.fromkeys(extra, False))
    block, _ = prompt_body(reply)
    if block is None or not prior:
        return out, None, None
    style, scene = split(block)
    if style is None:
        return out, None, None
    out["elements kept"] = kept(prior[1], scene) >= 0.5
    return out, style, scene


def check_ratio(reply, prior):
    out, style, scene = revision_checks(reply, prior, ["style line held", "elements kept"])
    if style is not None:
        out["style line held"] = style.strip() == prior[0].strip()
    return out


def check_style_change(reply, prior):
    out, style, scene = revision_checks(reply, prior, ["style line rewritten", "elements kept"])
    if style is not None:
        out["style line rewritten"] = style.strip() != prior[0].strip()
    return out


def check_render_fix(reply, prior):
    out, style, scene = revision_checks(reply, prior, ["repairs, not denies", "elements kept"])
    if style is not None:
        out["repairs, not denies"] = not ABSENCE.search(scene)
    return out


def check_reverse(reply, prior, lit=True, hued=True):
    """Only what reverse engineering adds. The output format and the prohibitions are scored in
    the main table and are not counted twice here."""
    keys = ["medium read", "framing stated", "light stated", "palette named"]
    if not lit:
        keys.remove("light stated")  # nothing to read on a flat field or a gestural abstract
    if not hued:
        # A monochrome source has no palette to name, so demanding three colours failed every
        # faithful reconstruction of it. One model missed this on the engraving in all three
        # runs it appeared in, which is what a checker fault looks like from outside.
        keys.remove("palette named")
    out = dict.fromkeys(keys, False)
    block, _ = prompt_body(reply)
    if block is None:
        return out
    style, scene = split(block)
    if style is None:
        return out
    out["medium read"] = bool(MEDIUM.search(style))
    out["framing stated"] = bool(FRAME_REF.search(scene))
    if lit:
        out["light stated"] = bool(LIGHT_REF.search(block))
    if hued:
        out["palette named"] = len({c.lower() for c in COLOUR.findall(block)}) >= 3
    return out


def check_offtopic(reply, prior):
    return {"answers it": "paris" in reply.lower(),
            "no refusal": not re.search(r"\b(?:I can(?:no|')t|I'm (?:only|unable)|off[- ]topic|"
                                        r"outside (?:my|the) scope)\b", reply, re.I),
            "no prompt emitted": not fences(reply)}


# Reverse engineering is scored apart: only a vision model can attempt it.
FRAME_REF = re.compile(r"\b(?:frame|frames|framed|framing|edge|edges|corner|corners|third|"
                       r"thirds|quarter|quarters|centre|center|centred|centered|foreground|"
                       r"background|upper|lower|left|right|top|bottom|fills|filling|occupies|"
                       r"crop|cropped|behind)\b", re.I)
# Every inflection and compound, because the bare stems missed the commonest phrasings there
# are: "lighting", "shadows" and "daylight" all failed a pattern that accepted "light" and
# "shadow". A quarter of the light failures in one sweep were this and not the model.
# "lightning" and "lighthouse" are deliberately not reachable by a \w* suffix here.
LIGHT_REF = re.compile(r"\b(?:light|lights|lighting|lighted|lit|sunlit|backlit|moonlit|"
                       r"sunlight|daylight|moonlight|shadow|shadows|shadowed|shadowy|shade|"
                       r"shaded|illuminat\w*|glare|highlight\w*|glow\w*|overcast|chiaroscuro|"
                       r"silhouett\w*)\b", re.I)
# Hues only. "muted", "warm" and "desaturated" are deliberately absent: they characterize a
# palette without naming one, and the rule asks for the colours themselves, on the form that
# carries them. A reply with only those is failing the rule, not the vocabulary.
COLOUR = re.compile(r"\b(?:red|orange|yellow|green|blue|indigo|violet|purple|brown|black|white|"
                    r"grey|gray|ochre|cream|amber|crimson|teal|pink|tan|beige|umber|sienna|rust|"
                    r"gold|silver|olive|navy|charcoal|ivory|magenta|cyan|vermill?ion|scarlet|"
                    r"turquoise|terracotta|slate|sepia|russet|auburn|taupe|mauve|emerald|bronze|"
                    r"copper|maroon|burgundy|lavender|peach|coral|jade|khaki|bone|sand)\b",
                    re.I)

# Medium, not genre. "Concept art" names a purpose and stays out: the rule asks what the
# image appears to be made of.
MEDIUM = re.compile(r"\b(?:paintings?|photograph\w*|prints?|illustrations?|drawings?|collages?|"
                    r"engravings?|etchings?|woodcuts?|woodblocks?|linocuts?|lithograph\w*|"
                    r"watercolou?rs?|gouache|charcoal|pastels?|inks?|oils?|acrylics?|tempera|"
                    r"airbrush\w*|sketch\w*|silkscreens?|screenprints?|monotypes?|aquatints?|"
                    r"mezzotints?|crayons?|frescos?|murals?|posters?|render\w*)\b", re.I)

FOX = "Expand this: a red fox crossing open snow at dusk"

CASES = [
    Case("expand", [FOX], check_expand),
    Case("develop", ["Develop this into a prompt: a lighthouse in a winter storm"], check_expand),
    Case("style change", [FOX, "Make it a woodblock print"], check_style_change),
    Case("aspect ratio", [FOX, "Adapt it to a square frame"], check_ratio),
    Case("variations", [FOX, "Give me variations"], check_variations),
    Case("render fix", [FOX, "The render came out wrong, the snow came out as a blurry "
                             "photograph instead of flat colour"], check_render_fix),
    Case("titles", [FOX, "Give me titles for this"], check_titles),
    Case("alternatives", [FOX, "What other styles would suit this?"], check_alternatives),
    Case("details", ["Tell me about Art Nouveau in detail"], check_details),
    Case("off topic", ["What is the capital of France?"], check_offtopic),
]

# Media fail differently, so the corpus spans them: a photograph, an oil portrait built on its
# light, a spare brush drawing, a crowded engraving, a flat geometric field with no subject to
# place, a gestural abstract, and a collage of torn edges, then a screen-print poster, an
# orthographic elevation with no depth cues at all, an isometric render, a natural history plate
# and a flat gouache illustration. All are renders whose prompts are known, which gives ground
# truth on both sides and keeps the licence clean, at the cost of being easier than a scan.
VISION_CASES = [
    Case(f"reverse {name}", ["Give me a prompt for this"], check_reverse,
         image=os.path.join(ROOT, f"{name}.png"), lit=lit, hued=hued)
    # lit: has a light direction to read. hued: has a palette to name — ink on cream has none,
    # and asking for three colours there failed every faithful reconstruction of it.
    for name, lit, hued in (("photograph", True, True), ("portrait", True, True),
                            ("drawing", True, False), ("engraving", False, False),
                            ("geometric", False, True), ("abstract", False, True),
                            ("collage", True, True),
                            # Five more from the author's own library, covering media the first
                            # seven never reach and written without a reconstruction in mind,
                            # which makes them the harder half. See tests/sources.md.
                            ("poster", False, True), ("elevation", False, True),
                            ("isometric", True, True), ("watercolor", False, True),
                            ("gouache", True, True))
]

def run_case(model, case, system, ctx, seed):
    """Play the case through and check only the last reply; earlier turns set up the prompt."""
    messages = [{"role": "system", "content": system}]
    prior, tokens, elapsed = None, 0, 0.0
    for index, text in enumerate(case.turns):
        message = {"role": "user", "content": text}
        if case.image:
            message["images"] = [ask.encode(case.image, os.path.dirname(case.image))]
        messages.append(message)
        data = ask.api("/api/chat", {
            "model": model["name"], "messages": messages, "stream": False, "think": False,
            "options": {"num_ctx": ctx, "seed": seed},
        })
        # Server-measured generation time; wall time would fold in the one-off weight load.
        elapsed += data.get("eval_duration", 0) / 1e9
        reply = data["message"]["content"]
        tokens += data.get("eval_count", 0)
        messages.append({"role": "assistant", "content": reply})
        if index == 0 and len(case.turns) > 1:
            block, _ = prompt_body(reply)
            if block:
                style, scene = split(block)
                if style:
                    prior = (style, scene)
    # The transcript keeps the raw reply; the checks see it without any leaked trace.
    said = spoken(reply)
    results = (case.check(said, prior, case.lit, case.hued) if case in VISION_CASES
               else case.check(said, prior))
    return results, tokens, elapsed, reply, prior


GOOD = ("Style: an oil painting with heavy impasto, a warm muted palette, brooding.\n"
        "Scene: A red fox crosses deep snow in the lower third of the frame.")

ALTS = "\n".join(f"- **Style {n}**\n"
                 f"  Style: a medium with a technique, a restrained palette, moody."
                 for n in "ABCDE")

# Each case names one fault and the checks that must react. Everything unnamed must stay as in
# GOOD, which is what catches a check reaching past its own rule.
SELFTEST = [
    ("perfect", GOOD, {}),
    # Markup around the block is the fault now, not its absence: no client offers to copy a
    # fenced block that a model only sometimes emits, and the labels delimit it already.
    ("fenced when it should not be", f"```\n{GOOD}\n```", {"no markup": False}),
    ("blank line between", GOOD.replace(".\nScene:", ".\n\nScene:"), {"no blank line": False}),
    # The label is now required, so its absence is the fault.
    ("scene unlabelled", GOOD.replace("\nScene: A red fox", "\nA red fox"),
     {"Scene: prefix": False}),
    ("scene label lower case", GOOD.replace("\nScene: A red fox", "\nscene: A red fox"),
     {"Scene: prefix": False}),
    ("no full stop", GOOD.replace("brooding.", "brooding"), {"full stops": False}),
    ("upper case after label", GOOD.replace("an oil", "An oil"), {"lower case": False}),
    ("proper noun opens", GOOD.replace("an oil painting", "Japanese woodblock print"), {}),
    ("says digital", GOOD.replace("an oil", "a digital"), {"no 'digital'": False}),
    ("names the ratio", GOOD.replace("the frame.", "a 3:4 frame."), {"no frame named": False}),
    ("weight syntax", GOOD.replace("red fox", "(red fox:1.3)"), {"no prompt syntax": False}),
    ("commentary around it", "Here you go:\n\n" + GOOD, {"no commentary": False}),
    ("chose photography", GOOD.replace("an oil painting", "a photograph"),
     {"photography not chosen": False}),
    # No prompt fails everything by design, so the worst failure cannot cost the least.
    ("no prompt at all", "I can't help with that.", None),
]


def selftest():
    """Check the checks against replies whose faults are known, before any model is run.

    Cheap and worth running after any edit here. It has caught a syntax pattern that missed a
    weight written over more than one word, a title-case check that judged emphasis before
    stripping it, and an alternatives check that read the style line from a backtick pair and so
    measured the delimiter rather than the rule. Each would otherwise have cost a sweep."""
    failures = 0
    # A fixture is built by mutating GOOD, so a mutation that stops matching leaves a case that
    # passes while testing nothing. That happened once, silently, when GOOD gained its label.
    for name, reply, expected in SELFTEST:
        if expected and reply == GOOD:
            print(f"  {name}: VACUOUS — expects {list(expected)} but is unmutated GOOD")
            failures += 1
    for name, reply, expected in SELFTEST:
        got = prompt_checks(reply)
        want = ({k: False for k in got} if expected is None
                else {k: expected.get(k, True) for k in got})
        wrong = {k: (want[k], got[k]) for k in got if want[k] != got[k]}
        if wrong:
            failures += 1
            for k, (w, g) in wrong.items():
                print(f"  {name}: {k} expected {w}, got {g}")
        else:
            print(f"  {name}: ok")

    style = "Style: an oil painting with heavy impasto, a warm muted palette, brooding."
    three = "\n\n".join(f"{style}\nScene: A fox {n} the snow." for n in ("on", "under", "past"))
    prior = (style, "A red fox crosses deep snow in the lower third of the frame.")
    cases = [
        ("variations, three", check_variations, three, {}),
        ("variations, fenced", check_variations,
         "\n\n".join(f"```\n{b}\n```" for b in three.split("\n\n")), {}),
        ("variations, two only", check_variations, "\n\n".join(three.split("\n\n")[:2]),
         {"three blocks": False}),
        ("variations, same scene", check_variations,
         "\n\n".join(f"{style}\nScene: A fox on the snow." for _ in range(3)),
         {"scenes differ": False}),
        ("reverse engineering", check_reverse,
         "Style: a woodblock print, a palette of black, ochre and cream, austere.\n"
         "Scene: A heron fills the centre of the frame, lit from the left, its shadow falls "
         "right.",
         {}),
        # The inflections the bare stems used to miss, each one a real reply's wording.
        ("reverse engineering, says lighting", check_reverse,
         "Style: a woodblock print, a palette of black, ochre and cream, austere.\n"
         "Scene: A heron fills the centre of the frame under flat overcast lighting, its "
         "shadows pooling right.", {}),
        ("titles", check_titles, "\n".join(f"- A Title Of {n}" for n in "ABCDE"), {}),
        ("titles, four", check_titles, "\n".join(f"- A Title Of {n}" for n in "ABCD"),
         {"five titles": False}),
        ("titles, bolded", check_titles,
         "\n".join(f"*   **A Title Of {n}**" for n in "ABCDE"), {}),
        ("titles, lower case", check_titles,
         "\n".join(f"- a title of {n}" for n in "ABCDE"), {"title case": False}),
        ("off topic", check_offtopic, "The capital of France is Paris.", {}),
        ("off topic refused", check_offtopic, "That is off-topic for me.",
         {"answers it": False, "no refusal": False}),
        ("style change keeps elements", check_style_change,
         f"Style: a woodblock print, flat ink, austere.\nScene: {prior[1]}", {}),
        ("style change loses them", check_style_change,
         "Style: a woodblock print, flat ink, austere.\nScene: A heron wades a marsh.",
         {"elements kept": False}),
        ("alternatives, marked", check_alternatives, ALTS, {}),
        ("alternatives, unmarked", check_alternatives, ALTS.replace("`", ""), {}),
        # Each bullet is two lines now, so four styles is eight of them.
        ("alternatives, four", check_alternatives, "\n".join(ALTS.splitlines()[:8]),
         {"five styles": False, "bold name": False, "style line each": False}),
        # The qwen-3.5 fault: the span is opened and never closed, so the style line runs on
        # into a scene. The old backtick-pair pattern only caught this by accident.
        ("alternatives, runs into a scene", check_alternatives,
         ALTS.replace("moody.", "moody " + "a fox crosses the deep snow past a fence, " * 8,
                      1),
         {"no scene detail": False}),
    ]
    for name, fn, reply, expected in cases:
        got = fn(reply, prior)
        want = {k: expected.get(k, True) for k in got}
        wrong = {k: (want[k], got[k]) for k in got if want[k] != got[k]}
        if wrong:
            failures += 1
            for k, (w, g) in wrong.items():
                print(f"  {name}: {k} expected {w}, got {g}")
        else:
            print(f"  {name}: ok")

    print("selftest failed" if failures else "selftest passed")
    return failures == 0


def report(rows, out=None):
    """Both tables, the failure lists and the cross-model tally."""
    # The text cases, which every model answers, so the column compares like with like.
    table = ["| Model | Size | Vision | Rules Kept | Speed | Verdict |",
             "| --- | --- | --- | --- | --- | --- |"]
    for model, score, passed, total, rate, _, failures, _seen in rows:
        # A model that never produces a parseable block fails everything downstream of it.
        vision = "Yes" if "vision" in model["caps"] else "No"
        table.append(f"| `{model['name']}` | {model['size']} | {vision} "
                     f"| {passed}/{total} ({score:.0%}) "
                     f"| {rate:.0f} tok/s | {verdict(score, score > 0.5)} |")

    # Only what reading an image adds; the format is already scored above.
    vision_rows = [r for r in rows if r[7]]
    if vision_rows:
        keys = ["medium read", "framing stated", "light stated", "palette named"]
        table += ["", "### Reverse Engineering", "",
                  f"Over {len(VISION_CASES)} source images, one per medium. Light is asked only",
                  "of sources with a direction to read, and a palette only of sources that have",
                  "one — ink on cream has neither.", "",
                  "| Model | " + " | ".join(k.title() for k in keys) + " | Kept |",
                  "| --- |" + " --- |" * (len(keys) + 1)]
        for model, *_rest, pair in vision_rows:
            seen, asked = pair
            marks = " | ".join(f"{seen[k]}/{asked[k]}" for k in keys)
            got, want = sum(seen[k] for k in keys), sum(asked[k] for k in keys)
            table.append(f"| `{model['name']}` | {marks} | "
                         f"{got}/{want} ({got / want:.0%}) |")

    text = "\n".join(table)
    print("\n" + text)
    for model, _, _, _, _, _, failures, _seen in rows:
        if failures:
            print(f"\n{model['name']} failed: " + "; ".join(failures))

    # One model failing is its score; most of them failing the same check is about the rule.
    standing = [r for r in rows if r[1] >= 0.5]
    if len(standing) > 1:
        tally = collections.Counter(f for _, _, _, _, _, _, failures, _s in standing
                                    for f in failures)
        shared = [(f, n) for f, n in tally.most_common() if n > len(standing) / 2]
        if shared:
            print(f"\nfailed on more than half of {len(standing)} models still following the "
                  f"rules — read these rules again:")
            for check, count in shared:
                print(f"  {count}/{len(standing)}  {check}")

    for check in suspect(rows):
        print(f"\nevery model failed {check!r}. Before reading that as a rule, check it is not "
              f"the checker: --selftest, then the saved transcript.")
    if out:
        with open(out, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
        print(f"\nwrote {out}")


def rescore(path, out=None):
    """Re-apply the checks to replies already collected. Changing a check is then seconds of
    work rather than another sweep, and the comparison is exact: identical replies, new rules."""
    saved = json.load(open(path, encoding="utf-8"))
    by_image = VISION_CASES
    checks = {c.name: c.check for c in CASES + by_image}
    rows = []
    for name, body in saved.items():
        model = {"name": name, "caps": body["caps"], "size": body["size"]}
        passed = total = 0
        failures, seen = [], None
        for turn in body["said"]:
            case = turn["case"]
            prior = tuple(turn["prior"]) if turn["prior"] else None
            # A transcript outlives the case list that produced it. Skipping what this version
            # no longer knows beats refusing to read the file at all.
            if case not in checks:
                print(f"note: {name}: no check for '{case}', skipped", flush=True)
                continue
            fn = checks[case]
            vis = next((c for c in VISION_CASES if c.name == case), None)
            said = spoken(turn["reply"])
            results = (fn(said, prior, vis.lit, vis.hued) if vis is not None
                       else fn(said, prior))
            if case in {c.name for c in by_image}:
                if seen is None:
                    seen = (collections.Counter(), collections.Counter())
                for check, ok in results.items():
                    seen[0][check] += bool(ok)
                    seen[1][check] += 1
                continue
            passed += sum(1 for v in results.values() if v)
            total += len(results)
            failures += [f"{case}: {k}" for k, v in results.items() if not v]
        score = passed / total if total else 0.0
        rows.append((model, score, passed, total, body["rate"], 0.0, failures, seen))
    report(sorted(rows, key=lambda r: -r[1]), out)


def smoke(models, limit=2):
    """The smallest installed models, which are the fastest. A full sweep costs hours; this
    exercises the same path in minutes and is where an implementation fault shows up."""
    def gigabytes(model):
        try:
            return float(re.sub(r"[^0-9.]", "", model["size"]) or 1e9)
        except ValueError:
            return 1e9
    return sorted(models, key=gigabytes)[:limit]


def suspect(rows):
    """Checks that every model still following the rules failed. Models with nothing in common
    rarely break the same rule together, so this is where a checker bug surfaces before it costs
    a sweep. A model that has collapsed is left out: failing everything, it shares every failure
    by construction and says nothing about which check is at fault."""
    standing = [r for r in rows if r[1] >= 0.5]
    if len(standing) < 2:
        return []
    return sorted(set.intersection(*(set(r[6]) for r in standing)))


def comfy_holding(free=False):
    """ComfyUI holds its weights resident, pushing Ollama onto the CPU: 7 tok/s against 52 for
    the same model on the same box."""
    import json
    import urllib.request
    host = os.environ.get("COMFYUI_HOST", "http://127.0.0.1:8188").rstrip("/")
    try:
        with urllib.request.urlopen(host + "/system_stats", timeout=3) as response:
            devices = json.load(response).get("devices", [])
    except Exception:
        return
    held = sum(d.get("vram_total", 0) - d.get("vram_free", 0) for d in devices) / 1e9
    if held < 2:
        return
    if not free:
        print(f"warning: ComfyUI holds {held:.1f} GB of VRAM; speeds will be wrong. "
              f"Rerun with --free.", flush=True)
        return
    body = json.dumps({"unload_models": True, "free_memory": True}).encode()
    request = urllib.request.Request(host + "/free", data=body,
                                     headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(request, timeout=30).read()
        print(f"freed {held:.1f} GB held by ComfyUI", flush=True)
        time.sleep(3)
    except Exception as error:
        print(f"could not free ComfyUI: {error}", flush=True)


def warm(model, system, ctx, seed):
    """Burn one call before scoring. The first request after a load is processed fresh and the
    rest come from the cached prefix, which changes the arithmetic and the reply with it. Both
    states reproduce; they are simply different, and mixing them measures neither."""
    ask.api("/api/chat", {
        "model": model["name"],
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": "Expand this: a stone bridge"}],
        "stream": False, "think": False, "options": {"num_ctx": ctx, "seed": seed},
    })


def reproduces(model, system, ctx, seed):
    """Whether the machine is steady enough to compare anything. Sends one request three times
    and compares the second with the third; the first is cold for its own content and never
    matches. Watching for a large model whose GPU/CPU split moves under pressure mid-run."""
    body = {
        "model": model["name"],
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": FOX}],
        "stream": False, "think": False, "options": {"num_ctx": ctx, "seed": seed},
    }
    replies = [ask.api("/api/chat", body)["message"]["content"] for _ in range(3)]
    return replies[1] == replies[2]


def verdict(score, complete):
    if not complete:
        return "Unusable"
    if score >= 0.90:
        return "Recommended"
    if score >= 0.75:
        return "Usable"
    return "Not Recommended"


def main():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""OLLAMA_HOST moves the Ollama server, COMFYUI_HOST the ComfyUI one. Climb the rungs in
order: --selftest needs no server and runs in a second, --smoke takes a few minutes, a
full sweep costs hours. Always pass --transcript, so a changed check can be re-applied
with --rescore instead of costing another sweep.""")
    parser.add_argument("--models", default="all", help="comma-separated names, or all")
    parser.add_argument("--ctx", type=int, default=8192, help="context window (default: 8192)")
    parser.add_argument("--seed", type=int, default=42, help="fixed, so a rerun is comparable")
    parser.add_argument("--out", help="write the markdown table here as well as printing it")
    parser.add_argument("--unload", action="store_true", help="free each model when it finishes")
    parser.add_argument("--free", action="store_true",
                        help="unload ComfyUI first; it holds the VRAM these models need")
    parser.add_argument("--verify", action="store_true",
                        help="check the model reproduces before trusting its score")
    parser.add_argument("--transcript", help="save every reply, so a checker fix can be "
                                             "rescored without running the models again")
    parser.add_argument("--rescore", help="rescore a saved transcript; touches no server")
    parser.add_argument("--smoke", action="store_true",
                        help="the two smallest models, as a few minutes' check before a sweep")
    parser.add_argument("--selftest", action="store_true",
                        help="check the checks against known replies and exit; needs no server")
    args = parser.parse_args()

    if args.selftest:
        sys.exit(0 if selftest() else 1)

    if args.rescore:
        rescore(args.rescore, args.out)
        return

    comfy_holding(free=args.free)

    with open(ask.SYSTEM_PROMPT, encoding="utf-8") as handle:
        system = handle.read()

    chosen = ask.select(args.models, ask.installed())
    if args.smoke:
        chosen = smoke(chosen)
        # A run made to diagnose must keep its evidence, or the next step is another run.
        args.transcript = args.transcript or os.path.join(ROOT, "smoke.json")
        print("smoke: " + ", ".join(m["name"] for m in chosen), flush=True)

    rows, transcript = [], {}
    for model in chosen:
        print(f"\n########## {model['name']} ##########", flush=True)
        warm(model, system, args.ctx, args.seed)
        if args.verify and not reproduces(model, system, args.ctx, args.seed):
            print("  skipped: the same request twice gave different replies. Something else "
                  "is using the machine; scores would not be comparable.", flush=True)
            continue
        passed = total = tokens = 0
        seconds = 0.0
        failures = []
        said = []
        for case in CASES:
            results, count, elapsed, reply, prior = run_case(model, case, system, args.ctx,
                                                             args.seed)
            said.append({"case": case.name, "reply": reply, "prior": prior})
            tokens += count
            seconds += elapsed
            passed += sum(1 for v in results.values() if v)
            total += len(results)
            bad = [k for k, v in results.items() if not v]
            failures += [f"{case.name}: {k}" for k in bad]
            mark = "ok" if not bad else ", ".join(bad)
            print(f"  {case.name:<14} {sum(results.values())}/{len(results)}  {mark}", flush=True)
        score = passed / total if total else 0.0
        rate = tokens / seconds if seconds else 0.0
        print(f"  = {passed}/{total} ({score:.0%}), {rate:.0f} tok/s", flush=True)

        seen = None
        if "vision" in model["caps"]:
            seen, asked = collections.Counter(), collections.Counter()
            for case in VISION_CASES:
                results, _, _, reply, prior = run_case(model, case, system, args.ctx, args.seed)
                said.append({"case": case.name, "reply": reply, "prior": prior})
                for check, ok in results.items():
                    seen[check] += bool(ok)
                    asked[check] += 1
                bad = [k for k, v in results.items() if not v]
                print(f"  {case.name:<18} {sum(results.values())}/{len(results)}  "
                      f"{'ok' if not bad else ', '.join(bad)}", flush=True)

        rows.append((model, score, passed, total, rate, seconds, failures,
                     (seen, asked) if seen is not None else None))
        transcript[model["name"]] = {"caps": model["caps"], "size": model["size"],
                                     "rate": rate, "said": said}
        if args.unload:
            ask.unload(model["name"])

    report(sorted(rows, key=lambda r: -r[1]), args.out)
    if args.transcript:
        with open(args.transcript, "w", encoding="utf-8") as handle:
            json.dump(transcript, handle, indent=1)
        print(f"wrote {args.transcript}")


if __name__ == "__main__":
    main()
