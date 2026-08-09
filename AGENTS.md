# Working on This Repo

`image-prompt-assistant.md` is the deliverable: a system prompt pasted into an assistant's
instructions. It must stand alone — no rule may reference another file, and nothing outside it is
available at runtime. `README.md` states the same behavior for a reader, and a change to the rules
is not finished until the README matches it.

The prompt format and the request types it serves are given. Rules may be reworded, merged,
reordered or dropped; the two-line block and the features are not.

What each feature is for, which the rules cannot say and a reply cannot show:

- **Expansion** — turn a sketch of an idea into a prompt that renders.
- **Reverse engineering** — recover a prompt from an image worth having again.
- **Revision** — change one thing about a prompt without disturbing the rest.
- **Alternatives** — five ways to render the same image, to choose a style by.
- **Details** — what a style is, for someone who has chosen it and wants to use it well.
- **Titles** — name the finished work.

A feature failing its checks is worth repairing only if it still serves one of these.

The paths those features are reached by, which is where they have gone wrong. Drafted from one
session with the author and worth correcting when it is wrong: every mistake here came from
knowing what a feature produced and not how anyone arrived at it.

- **Style first.** "What styles suit a winter forest?" — five alternatives. "A winter forest in
  that gouache style" — the subject is stated again rather than carried, and this is an ordinary
  request to develop an idea. Then edits. A whole prompt pasted with the question is answered
  from, not adopted: it arrives in whatever form the user keeps it in, and the working prompt is
  always one built here and always in the two-line format.
- **Prompt first.** An idea or a rough prompt is expanded, then changed one thing at a time: add
  something to the background, move what carries the frame, swap the medium, tighten the whole.
- **Image first.** An image the author liked is reverse-engineered, and the prompt that comes
  back is then edited like any other.
- **A render that went wrong.** The fault is described rather than the fix, and the cause is
  repaired in the prompt.
- **Learning a style.** A detail list, read rather than pasted. An example prompt in it is a
  separate request, made only if wanted.
- **Naming it.** Titles come last, and only where there is something to name: the prompt just
  built, or one pasted with the request — "a fitting title for: …", which is answered without
  the pasted text becoming the working prompt. Titles asked for with neither is a question, not
  an invented scene.

What no path wants: several prompts in one reply. Every request produces one, and a reply that
carries more than one prompt cannot be lifted out in a single action.

These paths are guidance, not checks. Nothing tests them: the scoring script sends each request
on its own, so what a journey asserts about the turn before it — that a subject is restated
rather than carried, that an example prompt is a request of its own — is written here and
measured nowhere. Testing one means driving several turns through a model and scoring the last,
which is new machinery rather than another check. Held open deliberately, not overlooked.

## Changing a Rule

- Length is not what a rule costs. Reading the rules is one batched pass; deliberating over them
  is not, and a ruleset cut to a quarter of its size deliberated longer than the full one. What a
  rule costs is how much it leaves to settle, which is why an instruction about the model's own
  process binds when it terminates and not when it asks for less: naming what to settle before
  writing, and how many things, halved deliberation without dropping a rule.
- Put a requirement where the model acts on it, and know that emphasis inside a rule is zero-sum.
  Every gain measured so far came from moving a requirement rather than adding or removing one —
  but leading the variations rule with the count it kept getting wrong fixed the count and broke
  the style line that had been right until then. A second requirement goes inline in the same
  sentence, never in front of the first.
- A rule set against what the training data is full of fails at a rate, and that rate is what
  holding the position costs rather than a fault to reword away. Half the models offer a
  "digital" style when alternatives are asked for, and a fifth reach for photography where the
  medium is theirs to choose — both rules are clear, both are obeyed inside a prompt, and both
  lose to the prior somewhere else. Measure the rate, keep the rule, and leave the wording alone.
- Naming a category makes it likelier, and a prohibition names it. Asking a detail list for the
  terms that decide an output, "never the equipment or the settings behind them", returned more
  equipment and settings than any wording that had left them unmentioned — aperture and ISO for
  photography, linseed oil and canvas for paint. Say what to produce; describing what to avoid
  puts it in front of the model.
- An option offered is read as the thing to produce. Letting a critique close with a revised
  prompt "where a working prompt is in play" made a model answer with the prompt and no critique
  at all. Require a second output or drop it, never make it conditional.
- A rule's section is its scope, for a rule the section leaves out: folding a style-name rule into
  Wording, which governs full prompts alone, stopped it reaching the bare style lines under
  Alternatives, and three faults have come from moving a rule between sections rather than from
  any word in it. Restating a convention the model has already read is different and does nothing
  — naming the fence in the revision rule moved nothing over five seeds.
- Where models keep producing what a rule forbids, try requiring it. The scene line was told to
  take no label, and five models kept writing "Scene:" anyway; labelling both lines beat
  forbidding one across three seeds and was perfect on two of them. A prohibition the models
  push back on is worth re-reading as a preference they do not share.
- Prefer generative instructions to checks. Naming five registers assigns variety; asking for
  variety makes the model audit a finished list. A fixed count removes a decision; "at most six"
  adds one.
- State the prohibition alongside the criterion. Rules that say only what to do get violated;
  rules that say only what to avoid produce generate-and-filter loops.
- A rule the sampler cannot see can still be load-bearing. Capitalization after the label and the
  closing full stop change no render and fail often, so both were dropped; adherence to unrelated
  rules then fell in all three seeds, 97% to 94%. Output discipline behaves like a property of the
  section rather than of the rules in it, so measure before removing one.
- Cut what a capable model already works out, and keep an output convention only where models
  can produce it. Attribute binding and medium-matched vocabulary were each stated once and
  dropped. The fence was kept for the opposite reason and should not have been: seven wordings
  failed to make it reliable, one model emitted it 5 times in 51 and another dropped it on a
  third of revisions, and removing it took both to every reply. A convention the models cannot
  hold is not a convention, it is a failure rate.
- A change is only safe where something can see it. A flat score is not evidence: either no check
  covers what moved, or nothing capable enough ran. One wording left two small models flat and
  made the strongest answer in coordinates.
- An example earns its place when it fixes a degree or an output convention, and goes when it
  only illustrates a term. It may show a requirement and never carry it alone: where a rule can
  be read as illustration, it will be.
- One model failing alone belongs in its score, and a fix nothing else needs is a workaround
  wearing a rule's clothes. Most of them failing the same check is the rule's fault, and usually
  means a prohibition with no criterion or a criterion buried behind one.
- Before measuring why a feature fails, establish that it is wanted. A drift in scene variations
  was found across five models, diagnosed, fixed and committed before the one person who uses
  this said he would never ask for several variants of one scene. The feature came out, and the
  hour spent repairing it bought nothing. Asking is cheaper than measuring.
- A rule that adds or reshapes a request type or an output convention changes what
  `tests/score.py` checks, in the same commit, and `--smoke` runs before that commit. It costs
  minutes on the two smallest models and covers every request type, which no other quick check
  does: dropping the code fence was measured on expansions and revisions, shipped, and only
  later found to have broken variations on every model that had held it. The check that would
  have caught it existed and was not run.

## Internal Testing

Reading needs nothing installed, so it is always the first pass and never the one that gets
skipped. Doing the work yourself is the second, and comes before any local model.

- Run `score.py --selftest` and `strain.py --selftest` first; neither needs a server and each has
  caught a fault that would have cost a sweep. They test the checks against replies whose faults
  are known, and the fixtures too: a fixture is a mutated good reply, so a mutation that stops
  matching leaves a case that passes while testing nothing.
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
  `strain.py`. A trace many times the length of its reply means a rule the model filters against
  instead of generating from.
- A ruleset can deliberate past the context window. At 8k with thinking on, runs came back with
  no reply at all — not truncated, empty — and an empty reply fails every check at once, so on
  a small model every quality number is downstream of whether the reply survived. Raising the
  context fixes the loss and costs time rather than saving it, because the wall was the only
  thing ending the deliberation.
- A degree fails differently in each mode, so check the one being recommended. Style lines ran
  to about twenty-five words with thinking on and to forty without it, from the same rule.
- Size does not predict whether a model can hold the rules: a 9B kept 95% where a 33B kept 82%,
  and the lowest score of all belonged to an 8B. Below about 8B the failure changes kind rather
  than degree — a 4.7B returned nothing usable for a request it had just answered perfectly, and
  answered one request type in another's format — so test small models to find an ambiguous
  wording, never to decide whether one works.
- One seed is not a measurement. Nothing sets a temperature, so a run inherits the model's own:
  three seeds with nothing else changed moved two models by 9 and 16 points out of 88, and one
  five-model comparison scored 82% of checks at its first seed and 97% at the other two. No seed
  is worse than another — a seed picks a trajectory, nothing more — so pool several rather than
  avoiding any. A sweep's aggregate is steady enough to read; one model's score is not, and one
  model across two sweeps says nothing. `strain.py` pools three seeds, and never change a check
  while a comparison is running.
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
