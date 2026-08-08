# Working on This Repo

`image-prompt-assistant.md` is the deliverable: a system prompt pasted into an assistant's
instructions. It must stand alone — no rule may reference another file, and nothing outside it is
available at runtime. `README.md` states the same behavior for a reader, and a change to the rules
is not finished until the README matches it.

The prompt format and the request types it serves are given. Rules may be reworded, merged,
reordered or dropped; the two-line block and the features are not.

## Changing a Rule

- Every rule is read before every answer, but length is not what costs the time. Reading the
  rules is one batched pass; deliberating over them is not, and that is where a reply's seconds
  go. A ruleset cut to a quarter of its size deliberated longer than the full one on both models
  it was measured against.
- What a rule costs is set by how much it leaves to settle, not by how long it is. The cheapest
  change measured so far added three lines: naming what to settle before writing, and saying the
  rules shape the writing rather than forming a checklist, halved deliberation without removing
  a single rule.
- Put a requirement where the model acts on it, and know that emphasis inside a rule is zero-sum.
  Every gain measured so far came from moving a requirement rather than adding or removing one —
  but leading the variations rule with the count it kept getting wrong fixed the count and broke
  the style line that had been right until then. A second requirement goes inline in the same
  sentence, never in front of the first.
- An option offered is read as the thing to produce. Letting a critique close with a revised
  prompt "where a working prompt is in play" made a model answer with the prompt and no critique
  at all. Require a second output or drop it, never make it conditional.
- A rule's section is its scope. Wording sits under a note saying it governs full prompts and no
  other reply, so folding a rule about style names into it stopped that rule reaching the bare
  style lines under Alternatives. Three faults have come from moving a rule between sections
  rather than from any word in it.
- That holds for a rule the section leaves out, not for one already stated. Revisions drop the
  fence about a third of the time; naming the fence inside the revision rule, where the model
  acts on it, moved nothing at all over five seeds. Restating an output convention the model has
  already read is not the same lever as putting a missing requirement where it is needed.
- Prefer generative instructions to checks. Naming five registers assigns variety; asking for
  variety makes the model audit a finished list. A fixed count removes a decision; "at most six"
  adds one.
- State the prohibition alongside the criterion. Rules that say only what to do get violated;
  rules that say only what to avoid produce generate-and-filter loops.
- Instructions about the model's own process bind weakly where they ask for less of something.
  A scaffold that terminates is different and does bind: naming what to settle, and how many
  things, gives deliberation a finish line it otherwise never reaches.
- A rule the sampler cannot see can still be load-bearing. Capitalization after the label and the
  closing full stop change no render, fail on 6% and 18% of replies, and were dropped for exactly
  that reason; adherence to rules they have nothing to do with — naming the frame, the word
  "digital", commentary around the block — then got worse in all three seeds, 97% to 94%. Output
  discipline behaves like a property of the section rather than of the rules in it, so measure
  before removing one, however plainly it earns nothing on its own.
- Cut what a capable model already works out, never an output convention. Attribute binding and
  medium-matched vocabulary were each stated once and dropped; the fence is inferred by some
  models and not others, and that tracks nothing about the rest.
- A change is only safe where something can see it. A flat score is not evidence: either no check
  covers what moved, or nothing ran that was capable enough to break on it. Asking an observation
  to open "as a fraction of that frame" was read literally by the strongest model here, which
  answered in coordinates, while the two small ones it had been checked against left the
  aggregate flat.
- An example earns its place when it fixes a degree or an output convention, and goes when it
  only illustrates a term. It may show a requirement and never carry it alone: where a rule can
  be read as illustration, it will be.
- One model failing alone belongs in its score, and a fix nothing else needs is a workaround
  wearing a rule's clothes. Most of them failing the same check is the rule's fault — models
  sharing no lineage or size do not break one together by coincidence, and it usually means a
  prohibition with no criterion, or a criterion buried behind one.
- A rule that adds or reshapes a request type or an output convention changes what
  `tests/score.py` checks, in the same commit. A check left behind keeps passing while the rule
  it no longer matches goes untested.

## Internal Testing

Reading needs nothing installed, so it is always the first pass and never the one that gets
skipped. Doing the work yourself is the second, and comes before any local model.

- Confirm every request type resolves to exactly one section and every section is reachable from
  a request type. Scan for terminology drift, and for rules referencing rules that have gone.
- Reading settles whether a rule is coherent, never whether a model obeys it. Where that is the
  open question, say so and offer the extended pass.
- Answer the request yourself, following the rules as written rather than as you meant them. This
  is what separates a rule asking for the wrong thing from a model too weak to follow the right
  one; in a model's reply the two are indistinguishable.
- Whatever you had to supply from your own judgement to make that answer work is a missing rule.
  Lighting, which way a figure faces and how a repeating arrangement is laid out were all found
  this way, each supplied by hand without noticing.

## Extended Testing

Optional and slower: running the rules needs Ollama, rendering them needs ComfyUI. It comes after
the internal pass and never instead of it — a model reached for first answers a question the
first pass has not yet asked. Where a server is not up, name what went unverified rather than
reporting the change as tested.

`tests/ask.py` puts the deliverable in front of a model, `tests/score.py` scores the reply,
`tests/strain.py` times what following it costs, `tests/render.py` renders what it produces.
Each `--help` carries its own flags and the order to climb the rungs in; what follows is only
what those cannot say.

- Time a wording as well as scoring it. A ruleset can keep every rule and still be unusable: the
  same file answered in five seconds with thinking off and fifty-six with it on, and nobody runs
  a local model that takes a minute to expand one prompt.
- `score.py` asks for no thinking, so a sweep cannot see any of this. Every conclusion about
  deliberation comes from `strain.py`, and the two are not interchangeable.
- A ruleset can deliberate past the context window. At 8k with thinking on, runs came back with
  no answer at all — not truncated, empty — and an empty answer fails every check at once, so on
  a small model every quality number is downstream of whether the reply survived. Raising the
  context fixes the loss and costs time rather than saving it, because the wall was the only
  thing ending the deliberation.
- A degree fails differently in each mode, so check the one being recommended. Style lines ran
  to about twenty-five words with thinking on and to forty without it, from the same rule.
- Size does not predict whether a model can hold the rules. Across twenty-two measured, a 9B
  kept 95% and a 33B kept 82%, and the lowest score of all belonged to an 8B.
- Below about 8B the failure changes kind, so do not read a small model's score as a weaker
  version of a large one's. A 4.7B swung 16 points across three seeds, returned nothing usable
  for a request it had just answered perfectly under another wording, copied a placeholder out
  of the format template as literal text, and answered one request type in another's format.
  Test against small models to find where a wording is ambiguous, never to decide whether it
  works.
- The noise floor is high, and it was measured rather than guessed: nothing sets a temperature,
  so a run inherits the model's own — often 1.0 — and rerunning two models across three seeds
  with nothing else changed moved one by 9 points out of 88 and the other by 16. A whole sweep's
  aggregate is steady enough to read, one model's score is not, and a single-model comparison
  across two sweeps says nothing at all. Compare two wordings at temperature 0, where the
  sampler is only a nuisance variable, and count a rate across seeds to ask what a model does in
  use.
- Where a repeat does not reproduce, the machine cannot measure anything: say so and wait.
- Warming hides what a user meets first. One model declined a composition judgment as subjective
  on three cold loads out of three and never once in twenty-two warm samples. Test the cold path
  whenever a rule governs how a reply opens.
- `--think` shows the wasted effort an answer hides. A trace many times the length of its answer
  usually means a rule the model filters against instead of generating from.
- A capability belongs in a column of its own, never averaged into a score.
- Render to settle rules that claim what the sampler does — that an unnamed color cannot appear,
  that extent must precede relation, that naming the frame is wasted. Hold every setting fixed
  and read at least three seeds; a single sample confirms whatever you hoped for. Whether an
  image is good stays with the author.
- Reverse engineering tests as a round trip: render a prompt, hand the render back, render what
  comes out, compare. Reconstruct it yourself first — a weak model dropping the crop and a rule
  never asking for it look identical in the output.
- Grow the half of the corpus that was not written for it; `tests/sources.md` says which is
  which. A source composed as a test states what a reconstruction should recover, and one taken
  from finished work does not.

## Conventions

- One rule per bullet. Merge only what is genuinely one idea.
- One term per concept, and never a term of art that could be read as literal output.
- No rationale unless the rule reads as arbitrary without it.
- American English.
- Headings are title case, including any a script writes, since those land in the README.
