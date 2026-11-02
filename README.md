# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

1. **The route (`app.py::submit`)** receives JSON and checks it: `text` and
   `creator_id` present, and the text neither too short nor too long. Bad
   input is logged as a rejection and gets a 4xx. Good input is given a
   `content_id`.
2. **Signal one (`detector.model_signal`)** runs gpt2 locally and measures
   how predictable the text is, which adds `model_score`.
3. **Signal two (`stylometry.style_signal`)** measures the text's shape
   (sentence-length spread, vocabulary variety, punctuation), which adds
   `style_score`.
4. **The combining rule (`scoring.combine_signals`)** turns the two into one
   score, which is returned as `confidence`.
5. **The label mapping (`scoring.score_to_label`)** turns that score into a
   `guess` and the sentence a reader sees.
6. **The audit log (`audit.log_decision`)** records all nine fields with
   status `decided`.
7. **The response** returns the label, both signal scores and the
   `content_id` a writer needs to appeal. `POST /appeal` with that id moves
   the item to `under_review`.

The full plan is in [PLAN.md](PLAN.md): the false-positive trace and both
endpoint contracts field by field.


---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** how predictable the text is to gpt2 (its perplexity),
mapped to 0–1. Low perplexity gives a high score, meaning more likely AI.

**Why that might differ between human and AI writing:** a model writes by
picking a likely next word, so its output is easy for a model to predict.
People make odder word choices and change direction more.

**What it can't see:** authorship. Plain human writing in short sentences
with common words (a second-language writer, a younger writer, anyone writing
simply) scores as AI. AI text full of rare words scores as human. It also
only reads roughly the first 300 words (400 tokens), so whatever comes after
that is invisible to it.

### Signal two — the style signal

**What it measures:** the shape of the text without reading it. It combines
sentence-length spread (std / mean), type-token ratio, and the density of
"expressive" punctuation (semicolons, dashes, brackets, colons, ? and !).
Each is scaled to 0–1, with higher meaning more likely AI.

**Why that might differ between human and AI writing:** generated prose
tends toward even, mid-length sentences, a narrower vocabulary and safe
punctuation. Human writing is lumpier.

**What it can't see:** meaning. Typos, split sentences, added dashes or a
pasted quotation all move it without changing what the text says. Type-token
ratio also falls as text gets longer, and lists, poems and dialogue break the
sentence splitter. Like signal one, it reads plain, even writing as AI. The
two signals share that blind spot, so when the writer is plain-spoken they
agree, and agree wrongly.

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** a weighted average of the two signals, except when they
**split**. A split means one says AI (≥ 0.5), the other says human (< 0.5),
and they are at least 0.30 apart. Two methods pointing opposite ways is
uncertainty, so on a split the average is clamped inside the unsure band. No
single signal can produce a confident label on its own, and that includes
"ai".

I chose clamping over leaning toward the more human signal on purpose.
Rare-word AI text reads as human to signal one, so leaning human would give
that text a confident "human" label, which is an easy evasion.

**The numbers** (all in `config.py`):

| Setting | Value | Why |
|---|---|---|
| `WEIGHT_MODEL_SIGNAL` | 0.5 | Each signal has a blind spot the other lacks, and the calibration gave no reason to trust one more |
| `WEIGHT_STYLE_SIGNAL` | 0.5 | Same |
| `DISAGREEMENT_GAP` | 0.30 | Wide enough that small wobbles near 0.5 don't count as a split |
| `SPLIT_MARGIN` | 0.01 | A split lands strictly inside the band, never on a threshold |
| Split clamp | 0.36 – 0.64 | `HUMAN_THRESHOLD + margin` to `AI_THRESHOLD − margin`, so it follows the thresholds when Milestone 5 moves them |

Inside signal two (`stylometry.py`), each raw measure is scaled linearly
between an AI anchor (scores 1.0) and a human anchor (scores 0.0), then
weighted:

| Measure | AI anchor | Human anchor | Weight |
|---|---|---|---|
| Sentence-length spread (stdev / mean) | 0.10 | 0.70 | 0.4 |
| Type-token ratio (moving average, 50-word window) | 0.70 | 0.90 | 0.2 |
| Expressive punctuation per 100 words | 0.0 | 4.0 | 0.4 |

TTR gets the smallest weight because it hardly moved across the calibration
inputs (0.80–0.92) and didn't separate AI from human. A text with only one
sentence scores 0.5 on spread ("no evidence").

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**Calibration run.** Each input was written to sit in a known category, and
both signals were printed separately:

| Input | Model | Style | Combined | Notes |
|---|---|---|---|---|
| Clearly AI | 0.895 | 0.835 | **0.865** | Both agree: AI |
| Clearly human | 0.411 | 0.087 | **0.249** | Both agree: human. 0.62 below clearly AI (criterion 2 asks for 0.30) |
| Formal human (committee minutes) | 0.542 | 0.461 | **0.502** | Both sit near the middle, so it's unsure |
| Lightly-edited AI | 0.709 | 0.582 | **0.646** | Contractions and a dash pulled style down. It sits just under 0.65 |
| Plain human (second-language writer) | 0.836 | 0.810 | **0.823** | ⚠️ **Both wrong, together** |
| Rare-word AI | 0.143 | 0.709 | **0.426** | **The split** (below) |

The plain-human row is the false positive from PLAN.md §3, now measured. It
scores almost as high as clearly-AI text, because short even sentences with
no expressive punctuation look like AI to *both* signals. The signals agree,
so the split rule can't catch it. That job falls to the thresholds in
Milestone 5: with the AI threshold at 0.65 this writer would be accused.

**A case where my two signals split, and what my rule does with it:**
the rare-word AI paragraph ("Cartographic epistemologies invariably
foreground the palimpsestic nature of territorial inscription…"). Signal one
gives 0.143, because gpt2 can't predict words like "palimpsestic", so it
looks human. Signal two gives 0.709: even sentence lengths and no
punctuation beyond commas and full stops. They're on opposite sides of 0.5
and 0.566 apart, so it's a split. Here the average (0.426) already falls
inside the 0.36–0.64 band, so the clamp leaves it alone and it reads
"unsure", which is the honest answer. The clamp matters when a split
averages outside the band. Model 0.95 with style 0.45 averages 0.70, which a
plain average would label "ai" on one signal's word. My rule holds it at
0.64.


---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human |  |  |
| unsure |  |  |
| high-confidence AI |  |  |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

*Milestone 4: both signals and the combined score (`confidence`) are real.
`guess` and `label` are placeholders until Milestone 5.*

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "Artificial intelligence has become an increasingly important part of modern society. It is used in a wide variety of applications, including healthcare, finance, and education. Additionally, AI systems can help organizations improve efficiency and make better decisions. However, it is important to consider the ethical implications of these technologies.", "creator_id": "nancy"}'
```

```json
{
  "confidence": 0.8706,
  "content_id": "5fc28325-5f5d-4f41-aa43-fb182a0ffbe1",
  "creator_id": "nancy",
  "guess": "unsure",
  "label": "placeholder",
  "model_score": 0.9207,
  "status": "decided",
  "style_score": 0.8206
}
```

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "My grandmother kept her buttons in a Danish cookie tin, the blue one, and when I was six I swallowed a brass one shaped like an anchor. Nobody panicked. She just handed me a slice of white bread, told me to chew slow, and went back to her crossword.", "creator_id": "nancy"}'
```

```json
{
  "confidence": 0.3931,
  "content_id": "d652551d-e0e3-4615-bb31-4ef482306d85",
  "creator_id": "nancy",
  "guess": "unsure",
  "label": "placeholder",
  "model_score": 0.3229,
  "status": "decided",
  "style_score": 0.4633
}
```

A request with no `text` is refused and logged rather than crashing:

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"creator_id": "nancy"}'
```

```json
{"error": "missing_text", "message": "text is required and must be a string."}
```
*(HTTP 400)*

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "...", "reasoning": "..."}'
```

```json

```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 3,
  "entries": [
    {
      "combined_score": 0.8706,
      "content_id": "5fc28325-5f5d-4f41-aa43-fb182a0ffbe1",
      "creator_id": "nancy",
      "guess": "unsure",
      "label": "placeholder",
      "model_score": 0.9207,
      "status": "decided",
      "style_score": 0.8206,
      "timestamp": "2026-11-02T17:06:37+00:00"
    },
    {
      "combined_score": 0.3931,
      "content_id": "d652551d-e0e3-4615-bb31-4ef482306d85",
      "creator_id": "nancy",
      "guess": "unsure",
      "label": "placeholder",
      "model_score": 0.3229,
      "status": "decided",
      "style_score": 0.4633,
      "timestamp": "2026-11-02T17:06:37+00:00"
    },
    {
      "creator_id": "nancy",
      "event": "rejected",
      "reason": "missing_text",
      "status": "rejected",
      "timestamp": "2026-11-02T17:06:46+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- *What I asked for:*
- *What came back:*
- *What I changed:*

**Moment 2**

- *What I asked for:*
- *What came back:*
- *What I changed:*

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
