# Working on This Repo

`image-prompt-assistant.md` is the deliverable: a system prompt pasted into an assistant's
instructions. It must stand alone — no rule may reference another file, and nothing outside it is
available at runtime. `README.md` states the same behavior for a reader, and a change to the rules
is not finished until the README matches it.

The prompt format and the request types it serves are given. Rules may be reworded, merged,
reordered or dropped; the two-line block and the features are not.

## Changing a Rule

- Length is not what a rule costs. Reading the rules is one batched pass; deliberating over them
  is not, and a ruleset cut to a quarter of its size deliberated longer than the full one. What a
  rule costs is how much it leaves to settle: the cheapest change measured added three lines
  naming what to settle before writing, and halved deliberation without dropping a rule.
- Put a requirement where the model acts on it, and know that emphasis inside a rule is zero-sum.
  Every gain measured so far came from moving a requirement rather than adding or removing one —
  but leading the variations rule with the count it kept getting wrong fixed the count and broke
  the style line that had been right until then. A second requirement goes inline in the same
  sentence, never in front of the first.
- An option offered is read as the thing to produce. Letting a critique close with a revised
  prompt "where a working prompt is in play" made a model answer with the prompt and no critique
  at all. Require a second output or drop it, never make it conditional.
- A rule's section is its scope, for a rule the section leaves out. Folding a rule about style
  names into Wording, which governs full prompts alone, stopped it reaching the bare style lines
  under Alternatives; three faults have come from moving a rule between sections rather than from
  any word in it. Restating a convention the model has already read is a different thing and does
  nothing — revisions drop the fence a third of the time, and naming it in the revision rule moved
  nothing over five seeds.
- Prefer generative instructions to checks. Naming five registers assigns variety; asking for
  variety makes the model audit a finished list. A fixed count removes a decision; "at most six"
  adds one.
- State the prohibition alongside the criterion. Rules that say only what to do get violated;
  rules that say only what to avoid produce generate-and-filter loops.
- Instructions about the model's own process bind weakly where they ask for less of something.
  A scaffold that terminates is different and does bind: naming what to settle, and how many
  things, gives deliberation a finish line it otherwise never reaches.
- A rule the sampler cannot see can still be load-bearing. Capitalization after the label and the
  closing full stop change no render and fail often, so both were dropped; adherence to unrelated
  rules then fell in all three seeds, 97% to 94%. Output discipline behaves like a property of the
  section rather than of the rules in it, so measure before removing one.
- Cut what a capable model already works out, never an output convention. Attribute binding and
  medium-matched vocabulary were each stated once and dropped; the fence is inferred by some
  models and not others, and that tracks nothing about the rest.
- A change is only safe where something can see it. A flat score is not evidence: either no check
  covers what moved, or nothing capable enough ran. One wording left two small models flat and
  made the strongest answer in coordinates.
- An example earns its place when it fixes a degree or an output convention, and goes when it
  only illustrates a term. It may show a requirement and never carry it alone: where a rule can
  be read as illustration, it will be.
- One model failing alone belongs in its score, and a fix nothing else needs is a workaround
  wearing a rule's clothes. Most of them failing the same check is the rule's fault, and usually
  means a prohibition with no criterion or a criterion buried behind one.
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

- Time a wording as well as scoring it: a ruleset can keep every rule and still be unusable, the
  same file answering in five seconds with thinking off and fifty-six with it on. `score.py` asks
  for no thinking and cannot see any of that, so every conclusion about deliberation comes from
  `strain.py`. A trace many times the length of its answer means a rule the model filters against
  instead of generating from.
- A ruleset can deliberate past the context window. At 8k with thinking on, runs came back with
  no answer at all — not truncated, empty — and an empty answer fails every check at once, so on
  a small model every quality number is downstream of whether the reply survived. Raising the
  context fixes the loss and costs time rather than saving it, because the wall was the only
  thing ending the deliberation.
- A degree fails differently in each mode, so check the one being recommended. Style lines ran
  to about twenty-five words with thinking on and to forty without it, from the same rule.
- Size does not predict whether a model can hold the rules. Across twenty-two measured, a 9B
  kept 95% and a 33B kept 82%, and the lowest score of all belonged to an 8B.
- Below about 8B the failure changes kind, not degree. A 4.7B swung 16 points across three seeds,
  returned nothing usable for a request it had just answered perfectly, and answered one request
  type in another's format. Test small models to find an ambiguous wording, never to decide
  whether one works.
- The noise floor is high and was measured, not guessed: nothing sets a temperature, so a run
  inherits the model's own, and three seeds with nothing else changed moved two models by 9 and
  16 points out of 88. A sweep's aggregate is steady enough to read; one model's score is not,
  and one model across two sweeps says nothing. Compare two wordings across seeds, and never
  change a check while a comparison is running.
- Where a repeat does not reproduce, the machine cannot measure anything: say so and wait.
- Warming hides what a user meets first. One model declined a composition judgment as subjective
  on three cold loads out of three and never once in twenty-two warm samples. Test the cold path
  whenever a rule governs how a reply opens.
- A capability belongs in a column of its own, never averaged into a score.
- Render to settle rules that claim what the sampler does — that an unnamed color cannot appear,
  that extent must precede relation. Hold every setting fixed and read three seeds; a single
  sample confirms whatever you hoped for. Whether an image is good stays with the author.
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
