# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. My own writing is rarely called AI

Of 10 pieces I wrote myself, **at most 1 is labelled high-confidence AI in
each of the three trials**. At least 4 of the 10 are deliberately plain:
short sentences, everyday words, few commas.

**Why this target:** on a writing site a wrong accusation costs the writer
far more than a missed detection costs the site. Both of my signals read
plain writing as AI-like (see PLAN.md §2), so the plain pieces are the
inputs most likely to break this. If they're left out the test is too easy.
A target of 0 would ignore that signal one is noisy and perplexity isn't
authorship, but more than 1 in 10 would mean accusing one writer in every
handful.

---

## 2. Clearly-AI and clearly-human text score far apart

On 5 texts I'm confident are AI-generated and 5 I'm confident are
human-written, the **average `confidence` (combined score) of the AI set is
at least 0.30 higher than the average of the human set, in each of the three
trials**.

**Why this target:** the unsure band will sit between my two thresholds, and
it needs to be wide, around 0.30, to protect writers like the one in
criterion 1. If the clear cases aren't at least that far apart, the human
and AI labels can't both be right on clear cases without the unsure band
swallowing everything. A gap under 0.30 means the scoring isn't separating
anything, however I set the thresholds.

---

## 3. All three labels are reachable, and land where aimed

Of 9 inputs, 3 aimed at each label (3 clearly human, 3 borderline, 3
clearly AI), **at least 2 of the 3 aimed at each label get that label, in
each of the three trials**.

**Why this target:** a label no score can produce is a gap in my ranges, and
one that only appears by accident tells me nothing. Requiring 2 of 3 per
label proves each band is both reachable and hit on purpose. Requiring 3 of
3 on the borderline inputs would demand a precision that the "unsure" label
itself admits we don't have.

---

## 4. Every appeal changes status and is recorded

Of **5 appeals sent against real `content_id`s, 5 of 5 return `200` with
`status: "under_review"`, and each adds exactly one `appeal` entry to the
audit log** with the matching `content_id` and reasoning. Of **3 appeals
against made-up ids, 3 of 3 return `404` with `error: "unknown_content_id"`**
and add no appeal entry. (I'll test this by hand with `curl` and `/log`,
because `run_eval.py` only sends to `/submit`.)

**Why this target:** the appeal is the only thing standing between a wrong
accusation and nothing at all. An appeal that silently fails, or lands on
the wrong item, is worse than no appeal path, because the writer thinks
they've been heard. Nothing here depends on the model, so anything short of
every single one counts as a bug, not noise.

---

## 5. Bad input never crashes the service

Of 6 malformed `/submit` bodies (empty `text`, whitespace-only `text`, no
`text` field, `text: null`, a 250,000-character `text`, and no
`creator_id`), **6 of 6 get a 4xx response with `error` and `message`
fields, 0 of 6 get a 5xx, and each one writes one `rejected` entry to the
audit log, in each of the three trials**.

**Why this target:** a crash on malformed input is one of the most common
real failures, and unit 8's attack set will send exactly these. A 500 gives
the caller nothing to act on. An unlogged rejection is an attack that shows
up only as an absence. Like the appeal path, this is deterministic code, so
the only honest target is all of them.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
