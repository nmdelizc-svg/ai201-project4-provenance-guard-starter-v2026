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

**Where it lives:** `scoring.py::combine_signals`. It calls
`scoring.py::signals_split` to decide whether the two signals split, and
reads every number from `config.py`.

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
| high-confidence human (`guess: "human"`) | 0.00 – 0.35 | We think this was probably written by a person. This is an automated estimate, not a final decision. If anything about it looks wrong, you can ask for a person to review it. |
| unsure (`guess: "unsure"`) | above 0.35 and below 0.65 | We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review. |
| high-confidence AI (`guess: "ai"`) | 0.65 – 1.00 | Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it. |

The thresholds count as confident: exactly 0.35 is "human" and exactly 0.65
is "ai". The bands touch, so every score from 0 to 1 gets a label. The text
lives in `scoring.py` (`LABEL_HUMAN`, `LABEL_UNSURE`, `LABEL_AI`), and
`scoring.py::score_to_label` picks one.

All three are reachable. In the Sample Run below, three submissions scored
0.8706, 0.3931 and 0.2264 and got "ai", "unsure" and "human".

Every label ends the same way: it's an estimate, and a person will look again
if you ask. None of them says "this is AI". The strongest one says what the
system *thinks*, warns that plain writing is where it goes wrong (the false
positive from PLAN.md §3), and tells the writer what to do.

**Why I worded the "unsure" one this way:**
The person reading it may well have written every word, so it says what
happened ("we couldn't tell") and not what the writer might have done. It
names both possibilities with equal weight, so neither sounds like the real
answer. Then it says outright that it isn't an accusation and that nothing
has been decided against them, because "unsure" on your own essay reads as
suspicion unless someone tells you otherwise. "Plenty of people's own writing
lands here" is there so the writer doesn't feel singled out. The review offer
comes last and is framed as an option, not a defence they have to mount.



---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

Three submissions, one aimed at each label.

High-confidence AI:

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "Artificial intelligence has become an increasingly important part of modern society. It is used in a wide variety of applications, including healthcare, finance, and education. Additionally, AI systems can help organizations improve efficiency and make better decisions. However, it is important to consider the ethical implications of these technologies.", "creator_id": "nancy"}'
```

```json
{
  "confidence": 0.8706,
  "content_id": "01f550bf-c880-40fb-935d-a59dbe0b15d8",
  "creator_id": "nancy",
  "guess": "ai",
  "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
  "model_score": 0.9207,
  "status": "decided",
  "style_score": 0.8206
}
```

Unsure:

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "My grandmother kept her buttons in a Danish cookie tin, the blue one, and when I was six I swallowed a brass one shaped like an anchor. Nobody panicked. She just handed me a slice of white bread, told me to chew slow, and went back to her crossword.", "creator_id": "nancy"}'
```

```json
{
  "confidence": 0.3931,
  "content_id": "8a18d7f2-d652-4f47-92cc-41c45c3c5a27",
  "creator_id": "nancy",
  "guess": "unsure",
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "model_score": 0.3229,
  "status": "decided",
  "style_score": 0.4633
}
```

High-confidence human:

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "Okay, so the bus was late again (third time this week!) and I'\''m standing there in the rain, soaked, thinking: why do I even bother? Then this guy, maybe seventy, wearing a full tuxedo, honestly, a tuxedo at 7am, starts humming Sinatra; loudly. Nobody looked up. I laughed so hard I missed the bus anyway. Worth it? Absolutely.", "creator_id": "nancy"}'
```

```json
{
  "confidence": 0.2264,
  "content_id": "eee798e3-52da-47c8-a257-a19393650c97",
  "creator_id": "nancy",
  "guess": "human",
  "label": "We think this was probably written by a person. This is an automated estimate, not a final decision. If anything about it looks wrong, you can ask for a person to review it.",
  "model_score": 0.4306,
  "status": "decided",
  "style_score": 0.0222
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

Against the "ai" submission above, using its real `content_id`:

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "01f550bf-c880-40fb-935d-a59dbe0b15d8", "reasoning": "I wrote this myself for a class assignment. I write in a plain, formal style on purpose."}'
```

```json
{
  "appealed_at": "2026-11-02T18:17:51+00:00",
  "content_id": "01f550bf-c880-40fb-935d-a59dbe0b15d8",
  "message": "We've received your appeal. A person will review this piece, and the original result is on hold until they do.",
  "status": "under_review"
}
```

An id that was never submitted is refused, and the refusal is logged:

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "not-a-real-id", "reasoning": "test"}'
```

```json
{
  "error": "unknown_content_id",
  "message": "We couldn't find a submission with that content_id."
}
```
*(HTTP 404)*

**What the log shows afterwards**

The original decision for `01f550bf…` is still there, unchanged, with status
`decided`. The appeal sits after it as its own entry with status
`under_review`. Its `creator_id` was copied from the decision, not taken from
the request.

```bash
$ curl "http://127.0.0.1:5000/log?limit=6"
```

```json
{
  "count": 6,
  "entries": [
    {
      "creator_id": "nancy",
      "event": "rejected",
      "reason": "missing_text",
      "status": "rejected",
      "timestamp": "2026-11-02T17:06:46+00:00"
    },
    {
      "combined_score": 0.8706,
      "content_id": "01f550bf-c880-40fb-935d-a59dbe0b15d8",
      "creator_id": "nancy",
      "guess": "ai",
      "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
      "model_score": 0.9207,
      "status": "decided",
      "style_score": 0.8206,
      "timestamp": "2026-11-02T18:17:40+00:00"
    },
    {
      "combined_score": 0.3931,
      "content_id": "8a18d7f2-d652-4f47-92cc-41c45c3c5a27",
      "creator_id": "nancy",
      "guess": "unsure",
      "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
      "model_score": 0.3229,
      "status": "decided",
      "style_score": 0.4633,
      "timestamp": "2026-11-02T18:17:40+00:00"
    },
    {
      "combined_score": 0.2264,
      "content_id": "eee798e3-52da-47c8-a257-a19393650c97",
      "creator_id": "nancy",
      "guess": "human",
      "label": "We think this was probably written by a person. This is an automated estimate, not a final decision. If anything about it looks wrong, you can ask for a person to review it.",
      "model_score": 0.4306,
      "status": "decided",
      "style_score": 0.0222,
      "timestamp": "2026-11-02T18:17:40+00:00"
    },
    {
      "content_id": "01f550bf-c880-40fb-935d-a59dbe0b15d8",
      "creator_id": "nancy",
      "event": "appeal",
      "reasoning": "I wrote this myself for a class assignment. I write in a plain, formal style on purpose.",
      "status": "under_review",
      "timestamp": "2026-11-02T18:17:51+00:00"
    },
    {
      "creator_id": "unknown",
      "event": "rejected",
      "reason": "unknown_content_id",
      "status": "rejected",
      "timestamp": "2026-11-02T18:17:51+00:00"
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

**My limits:** 5 per minute, 50 per day

**Why those numbers and not others:**
A real writer checks their own work a few times an hour: they paste a draft, maybe fix something and send it again. Five a minute leaves room for that kind of quick back-and-forth, and fifty a day is more than anyone needs to check their own writing. A script trying to map my thresholds needs hundreds of variations. At 5 a minute it can't send them in a burst, and at 50 a day a 1,000-variation run takes 20 days per creator_id. Ten a minute and 200 a day (the starter's defaults) would let that same script finish in five days.

**What a caller counts as:** Per `creator_id`, falling back to the caller's address when there isn't one. That way people who share a network (a household or a classroom) don't use up each other's limit. The weakness is that `creator_id` is whatever the caller sends, so a script can make up a new one for every request and never hit the limit. Per-address limiting would stop that script, but it would also lump a whole household together. A real deployment would need verified accounts, or both limits together.

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```
200 200 200 200 200 429 429 429 429 429 429 429 429 429 429
```

Each of the ten 429s left a `rejected` entry in `logs/audit.jsonl` with `reason: "rate_limited"` and `limit: "5 per 1 minute"`. Every log line, including appeals and rejections, has all nine fields (`timestamp, content_id, creator_id, guess, model_score, style_score, combined_score, label, status`). Fields that don't apply are written as `null`, never left out.

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

The whole attack set, run once with nothing changed: `python run_attacks.py
--set attack_set --label before` against `app.py::submit` with rate limiting
on (5/minute, 50/day). That's 56 attacks, 44 from `attacks.csv` and 12 from
`attacks_malformed_requests.csv`. Raw output is in
[results/attack_run_2026-11-04_2206.md](results/attack_run_2026-11-04_2206.md),
and the audit log for the run is in
[results/audit_extract.json](results/audit_extract.json). No attack caused a
5xx, a dropped connection or a crash.

**How I marked them.** An attack is BROKE if it got what its `targets`
column was going for:

- **Evasion, and injections carrying AI text:** HELD only if the AI text
  still came back `ai`. "Unsure" counts as BROKE, because the AI text got
  through without being flagged, which is what the attacker wanted.
- **False positive:** BROKE if the human writing came back `ai`. "Unsure"
  is HELD, because that label says outright it isn't an accusation.
- **Prompt injection aimed at the label or the log:** HELD if the label text
  and the log line came out intact.
- **Malformed:** HELD if the service refused it with a 4xx, or accepted it
  without making a confident claim. BROKE if it put a confident `ai` or
  `human` label on something that isn't writing in English.
- **Flood:** HELD if the limiter cut the shared creator off.

RQ10 and RQ11 came back 429. They have no usable `creator_id`, so they were
counted against my own address alongside RQ02 and RQ06–RQ09. That bucket was
already full, so neither request reached the route. I resent each one alone
afterwards to see what the route would have done. Both were a clean
`400 invalid_json` (`results/attack_run_2026-11-04_2208_recheck_RQ1*.md`).
The first-pass outcome recorded below is still the 429.

| ID | Family | Targeting | Status | Guess | Model | Style | Combined | Verdict | What happened |
|---|---|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | unsure | 0.164 | 0.759 | 0.462 | **BROKE** | typos dropped signal one to 0.16; split → unsure, AI text not flagged |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | unsure | 0.594 | 0.076 | 0.360 | **BROKE** | "Really." fragments dropped signal two to 0.08 → unsure |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | unsure | 0.666 | 0.382 | 0.524 | **BROKE** | quotation pulled signal two to 0.38 → unsure |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | ai | 0.611 | 0.751 | 0.681 | **HELD** | rare words barely moved signal one (0.61); still ai |
| EV05 | evasion | both signals: heavy human editing pass | 200 | human | 0.321 | 0.335 | 0.328 | **BROKE** | **labelled human**: both signals fooled by the edit |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | unsure | 0.573 | 0.451 | 0.512 | **BROKE** | one long + one short sentence → unsure |
| EV07 | evasion | signal two: padding with punctuation | 200 | unsure | 0.586 | 0.255 | 0.420 | **BROKE** | "; and, moreover," padding dropped signal two to 0.25 → unsure |
| EV08 | evasion | signal one: text below the token window | 200 | unsure | 0.245 | 0.678 | 0.462 | **BROKE** | 65 chars: signal one has too little to read → unsure |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | unsure | 0.704 | 0.555 | 0.630 | **BROKE** | human opening → 0.63, just under the 0.65 line |
| EV10 | evasion | signal two: repeated stanza structure | 200 | ai | 0.979 | 0.804 | 0.892 | **HELD** | repetition made it look *more* AI (0.89) |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | unsure | 0.618 | 0.655 | 0.636 | **HELD** | unsure, but 0.636 is 0.014 from an accusation |
| FP02 | false_positive | human writing in a formal register | 200 | ai | 0.739 | 0.837 | 0.788 | **BROKE** | formal human report labelled ai |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | ai | 0.805 | 0.729 | 0.767 | **BROKE** | non-native writer labelled ai; both signals agree |
| FP04 | false_positive | a student essay written to a rubric | 200 | ai | 0.833 | 0.701 | 0.767 | **BROKE** | rubric essay labelled ai |
| FP05 | false_positive | technical documentation written by a person | 200 | ai | 0.800 | 0.882 | 0.841 | **BROKE** | human documentation labelled ai (0.84, highest FP) |
| FP06 | false_positive | a person imitating a formal template | 200 | ai | 0.881 | 0.665 | 0.773 | **BROKE** | templated cover letter labelled ai |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | ai | 0.882 | 0.600 | 0.741 | **BROKE** | deliberate repetition labelled ai |
| FP08 | false_positive | very short genuine human submission | 200 | unsure | 0.322 | 0.578 | 0.450 | **HELD** | 36 chars → unsure, not accused |
| PI01 | prompt_injection | instruction to ignore the check | 200 | unsure | 0.463 | 0.425 | 0.444 | **BROKE** | instruction did nothing, but the added words dropped AI text to unsure |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | human | 0.204 | 0.210 | 0.207 | **BROKE** | asked for guess=human and **got human (0.21)**: the fake SYSTEM line changed both scores |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | unsure | 0.594 | 0.238 | 0.416 | **BROKE** | "note to the reviewing system" → unsure, AI text not flagged |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | unsure | 0.500 | 0.250 | 0.375 | **HELD** | label is fixed text from scoring.py; the script tag is never echoed |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | unsure | 0.640 | 0.152 | 0.396 | **HELD** | log line written with json.dumps, so the fake fields stayed inside the text |
| PI06 | prompt_injection | instruction plus real human text | 200 | unsure | 0.558 | 0.657 | 0.608 | **HELD** | human text stayed unsure; instruction had no effect |
| MF01 | malformed | text is only whitespace | 400 | — | — | — | — | **HELD** | 400 empty_text |
| MF02 | malformed | text is a single character | 422 | — | — | — | — | **HELD** | 422 text_too_short |
| MF03 | malformed | text is control characters | 200 | human | 0.000 | 0.200 | 0.100 | **BROKE** | control characters scored and labelled **human** (0.10) |
| MF04 | malformed | text is only punctuation | 200 | unsure | 0.011 | 1.000 | 0.506 | **HELD** | accepted, but landed unsure (0.51), so no claim made |
| MF05 | malformed | text is a very long single word | 200 | ai | 0.998 | 0.600 | 0.799 | **BROKE** | 4,000 × "a" labelled ai (0.80) |
| MF06 | malformed | text is emoji only | 200 | ai | 0.997 | 0.800 | 0.898 | **BROKE** | emoji only labelled ai (0.90) |
| MF07 | malformed | text is right-to-left script | 200 | ai | 0.906 | 0.800 | 0.853 | **BROKE** | Arabic text labelled ai (0.85); gpt2 can't read it |
| MF08 | malformed | text is 60,000 characters | 200 | ai | 0.988 | 0.697 | 0.843 | **BROKE** | no length cap: 57,640 chars accepted; repeated human text labelled ai (0.84) |
| RQ01 | malformed | no text field at all | 400 | — | — | — | — | **HELD** | 400 missing_text |
| RQ02 | malformed | no creator_id | 400 | — | — | — | — | **HELD** | 400 missing_creator_id |
| RQ03 | malformed | text is a number | 400 | — | — | — | — | **HELD** | 400 missing_text |
| RQ04 | malformed | text is a list | 400 | — | — | — | — | **HELD** | 400 missing_text |
| RQ05 | malformed | text is null | 400 | — | — | — | — | **HELD** | 400 missing_text |
| RQ06 | malformed | creator_id is an object | 400 | — | — | — | — | **HELD** | 400 missing_creator_id |
| RQ07 | malformed | body is a JSON array, not an object | 400 | — | — | — | — | **HELD** | 400 invalid_json |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | — | — | **HELD** | 400 invalid_json |
| RQ09 | malformed | body is empty | 400 | — | — | — | — | **HELD** | 400 invalid_json |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | — | — | — | — | **HELD** | 429 from the per-address bucket, never reached the route (resent alone: 400 invalid_json) |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | — | — | — | — | **HELD** | 429 from the per-address bucket, never reached the route (resent alone: 400 invalid_json) |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | — | — | **HELD** | 400 missing_text |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.029 | 0.600 | 0.360 | **HELD** | allowed (within 5/min) |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.029 | 0.600 | 0.360 | **HELD** | allowed (within 5/min) |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.029 | 0.600 | 0.360 | **HELD** | allowed (within 5/min) |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.029 | 0.600 | 0.360 | **HELD** | allowed (within 5/min) |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | unsure | 0.029 | 0.600 | 0.360 | **HELD** | allowed (within 5/min) |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | 429 rate_limited, logged |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | 429 rate_limited, logged |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | 429 rate_limited, logged |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | 429 rate_limited, logged |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | 429 rate_limited, logged |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | 429 rate_limited, logged |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | — | — | **HELD** | 429 rate_limited, logged |

| Family | Attacks | Held | Broke |
|---|---|---|---|
| `evasion` | 10 | 2 | 8 |
| `false_positive` | 8 | 2 | 6 |
| `prompt_injection` | 6 | 3 | 3 |
| `malformed` | 20 | 15 | 5 |
| `flood_same_creator` | 12 | 12 | 0 |
| **Total** | **56** | **34** | **22** |

**What the counts say.** 22 of 56 broke, and they break into three
patterns, not 22 separate problems:

1. **AI text slides into "unsure" (8 evasions, 3 injections).** Almost any
   edit pushes one signal under 0.5 while the other stays high. The split
   rule then clamps the result into the unsure band, by design. EV05 (a real
   editing pass) and PI02 (a fake SYSTEM header) went all the way to
   `human`.
2. **Plain human writing reads as AI (6 false positives).** Formal,
   templated, rubric-shaped and second-language writing all score high on
   *both* signals. Because the signals agree, the split rule never steps in.
3. **Non-English and junk input gets a confident label (5 malformed).** The
   route checks type, emptiness and minimum length, but nothing else. Emoji,
   Arabic, 4,000 repeated letters and a 57,640-character body were all
   scored and labelled `ai`. Control characters were labelled `human`.
   There's no maximum length, even though step 1 of *What This Does* says
   there is.

**Ten audit log entries from the run**

These are copied from `logs/audit.jsonl` exactly as written. The first eight
are the most telling failures. The last two are rate-limit rejections: one
from the flood family, and one from a malformed row that was rejected by
address before it reached the route. Rejections leave `content_id`, `guess`,
the scores and `label` as `null`, and add `reason` and `limit`.

```json
[
  {
    "timestamp": "2026-11-05T02:06:50+00:00",
    "content_id": "09a7842c-1bb5-4709-b144-98254a501d80",
    "creator_id": "attacker_FP03",
    "guess": "ai",
    "model_score": 0.8051,
    "style_score": 0.7285,
    "combined_score": 0.7668,
    "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T02:06:50+00:00",
    "content_id": "1664b887-96c6-44f9-83b4-819e048a535e",
    "creator_id": "attacker_FP05",
    "guess": "ai",
    "model_score": 0.8005,
    "style_score": 0.8821,
    "combined_score": 0.8413,
    "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T02:06:49+00:00",
    "content_id": "5fdbd321-5a20-42d2-9ace-d2f99f562e53",
    "creator_id": "attacker_EV05",
    "guess": "human",
    "model_score": 0.3212,
    "style_score": 0.3351,
    "combined_score": 0.3281,
    "label": "We think this was probably written by a person. This is an automated estimate, not a final decision. If anything about it looks wrong, you can ask for a person to review it.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T02:06:51+00:00",
    "content_id": "bd709758-c4ed-43e6-a5a7-f5064fcb7f0a",
    "creator_id": "attacker_PI02",
    "guess": "human",
    "model_score": 0.2044,
    "style_score": 0.2099,
    "combined_score": 0.2072,
    "label": "We think this was probably written by a person. This is an automated estimate, not a final decision. If anything about it looks wrong, you can ask for a person to review it.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T02:06:48+00:00",
    "content_id": "616d70a9-4833-4c7f-970a-a0a928985cee",
    "creator_id": "attacker_EV01",
    "guess": "unsure",
    "model_score": 0.1635,
    "style_score": 0.7595,
    "combined_score": 0.4615,
    "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T02:06:52+00:00",
    "content_id": "ad6cf3cf-2447-40f0-bbda-39aed42296cd",
    "creator_id": "attacker_MF07",
    "guess": "ai",
    "model_score": 0.9064,
    "style_score": 0.8,
    "combined_score": 0.8532,
    "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T02:06:51+00:00",
    "content_id": "acb76ced-4d37-4d98-9009-5ec213efa67f",
    "creator_id": "attacker_MF03",
    "guess": "human",
    "model_score": 0.0,
    "style_score": 0.2,
    "combined_score": 0.1,
    "label": "We think this was probably written by a person. This is an automated estimate, not a final decision. If anything about it looks wrong, you can ask for a person to review it.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T02:06:53+00:00",
    "content_id": "d9d302cc-5c29-46b2-88fa-500b5ccd9d0d",
    "creator_id": "attacker_MF08",
    "guess": "ai",
    "model_score": 0.9876,
    "style_score": 0.6974,
    "combined_score": 0.8425,
    "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
    "status": "decided"
  },
  {
    "timestamp": "2026-11-05T02:06:53+00:00",
    "content_id": null,
    "creator_id": "attacker_flood",
    "guess": null,
    "model_score": null,
    "style_score": null,
    "combined_score": null,
    "label": null,
    "status": "rejected",
    "event": "rejected",
    "reason": "rate_limited",
    "limit": "5 per 1 minute"
  },
  {
    "timestamp": "2026-11-05T02:06:53+00:00",
    "content_id": null,
    "creator_id": "unknown",
    "guess": null,
    "model_score": null,
    "style_score": null,
    "combined_score": null,
    "label": null,
    "status": "rejected",
    "event": "rejected",
    "reason": "rate_limited",
    "limit": "5 per 1 minute"
  }
]
```

**The single worst outcome**, the one I'd least want to explain to a writer
whose work got caught by it:

**FP03, the non-native English speaker writing carefully.** Their piece
about their first month in a new country was labelled `ai` at 0.767. Signal
one gave 0.805 and signal two gave 0.729.

It's the worst because the system did exactly what it was built to do, and
I had already predicted this. It's the false positive traced in PLAN.md §3,
and the calibration run measured it at 0.823. This writer did what they're
told to do when writing in a second language: short complete sentences,
common words, no risky punctuation. Both signals read that care as
machine-like. Since the two signals agree, the split rule (my one safeguard
against a single signal being wrong) never comes into play. The label does
say "it can be wrong, especially with plain or simple writing", but that
still leaves the person with the weakest command of English to argue their
case in English. I'd also find it hard to defend because the honest
explanation is "you wrote too clearly".

Runners-up: FP05 (human documentation, 0.841, the highest-scoring false
positive) and MF07 (a sentence in Arabic labelled `ai` at 0.853). For MF07
the model can't read the language at all, so a confident label there is
made up.

---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

All five criteria from [criteria.md](criteria.md), three trials each, with
nothing changed in between: `python run_eval.py --label before`, against the
same service and settings as *Attack Run — Before*. The inputs are in
[scenarios.py](scenarios.py), and the raw output for every input in every
trial is in
[results/run_2026-11-04_2258_before.md](results/run_2026-11-04_2258_before.md).

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing labelled high-confidence AI | ≤ 1 of 10 | 10/10 | 10/10 | 10/10 | **MISSED** |
| 2. Clearly-AI mean minus clearly-human mean | ≥ 0.30 | 0.379 | 0.379 | 0.379 | MET |
| 3. Inputs aimed at each label that get it | ≥ 2 of 3 for each label | human 0/3, unsure 2/3, ai 3/3 | human 0/3, unsure 2/3, ai 3/3 | human 0/3, unsure 2/3, ai 3/3 | **MISSED** |
| 4. Appeals: real ids → 200 `under_review` + one log entry; fake ids → 404 + no entry | 5 of 5 real, 3 of 3 fake | 5/5, 3/3 | 5/5, 3/3 | 5/5, 3/3 | MET |
| 5. Malformed bodies → 4xx with `error` + `message` and one `rejected` log entry | 6 of 6 | 5/6 | 5/6 | 5/6 | **MISSED** |

**What each criterion ran.**

1. Ten pieces I wrote myself. Pieces 1–4 are deliberately plain: short
   sentences, everyday words, almost no commas.
2. Five paragraphs generated by an AI assistant, unedited. Five openings of
   books published before 1900 (Twain, Melville, Douglass, Thoreau, Dickens).
3. Three inputs aimed at each label:
   - human: Austen, Twain, Shelley
   - unsure: the Sample Run "unsure" paragraph, plus two AI paragraphs
     roughened with contractions, a dash and an aside
   - ai: the Sample Run "ai" paragraph, plus two unedited AI paragraphs
4. Five submissions, each appealed with the `content_id` it got back, plus
   three made-up ids. `run_eval.py` only sent to `/submit`, so instead of
   testing this by hand with `curl` (as criteria.md planned) I extended it.
   `run_eval.py::run_appeals` submits, appeals, and reads `/log` before and
   after each appeal to count the `appeal` entries it left.
5. The six bodies from criteria.md: empty `text`, whitespace `text`, no
   `text`, `text: null`, 250,000 characters, and no `creator_id`.
   `run_eval.py::send_submit` reads `/log` around each one.

The Run cells come from each scenario's `check` function in `scenarios.py`.

**All three trials were identical**, down to the fourth decimal of every
score. That's expected. gpt2 runs in eval mode and only scores the text, so
nothing is sampled, and the style signal is plain arithmetic. Every verdict
above is therefore a property of the pipeline, not bad luck in one trial.

**Real output from trial 1**, pasted from
`results/run_2026-11-04_2258_before.md`. Each block was recorded by
`run_eval.py::main` (through `send_submit` or `run_appeals`) from the
response of `app.py::submit` or `app.py::appeal`. The scores come from
`scoring.py::combine_signals` and the labels from `scoring.py::score_to_label`.
Each block is a selection of that trial's inputs. The report has every one.

*Criterion 1. Two of my plain pieces and my most casual one (a text to a
friend). All three are labelled `ai`. The casual one is the lowest of all
ten, and still above the 0.65 line.*

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8679,
    "model_score": 0.8135,
    "style_score": 0.9223,
    "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
    "sent": "I got up early today. I made some eggs for breakfast. Then I took a sh"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.9395,
    "model_score": 0.912,
    "style_score": 0.9671,
    "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
    "sent": "My best friend lives near my house. We have known each other for years"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6932,
    "model_score": 0.8273,
    "style_score": 0.559,
    "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
    "sent": "hey, are you free tomorrow afternoon? I was thinking we could go to th"
  }
]
```

*Criterion 2. One AI paragraph and Thoreau, the highest-scoring human
text. The AI mean is 0.837 and the human mean 0.458, so the gap is 0.379.
Thoreau was labelled `ai` anyway.*

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8147,
    "model_score": 0.9568,
    "style_score": 0.6727,
    "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
    "sent": "Climate change is one of the most pressing challenges facing the world",
    "expect": "ai"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6523,
    "model_score": 0.6233,
    "style_score": 0.6814,
    "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
    "sent": "I went to the woods because I wished to live deliberately, to front on",
    "expect": "human"
  }
]
```

*Criterion 3. The three inputs that missed their label. Austen and Shelley
were aimed at `human`, and the roughened remote-work paragraph at `unsure`.
All three came back `ai`. The third human-aimed input (Tom Sawyer) landed
`unsure` at 0.375.*

```json
[
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.6864,
    "model_score": 0.6779,
    "style_score": 0.6948,
    "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
    "sent": "It is a truth universally acknowledged, that a single man in possessio",
    "expect": "human"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.7209,
    "model_score": 0.5581,
    "style_score": 0.8837,
    "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
    "sent": "You will rejoice to hear that no disaster has accompanied the commence",
    "expect": "human"
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.678,
    "model_score": 0.803,
    "style_score": 0.553,
    "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
    "sent": "Remote work has changed a lot about how people do their jobs. It's fle",
    "expect": "unsure"
  }
]
```

*Criterion 4. One real appeal and one made-up id. `logged_reasoning_matches`
is false on the fake because there's no entry to match.*

```json
[
  {
    "content_id": "9f1c7e28-3dc0-4371-883a-f71ba0757453",
    "status": 200,
    "response": {
      "appealed_at": "2026-11-05T02:58:43+00:00",
      "content_id": "9f1c7e28-3dc0-4371-883a-f71ba0757453",
      "message": "We've received your appeal. A person will review this piece, and the original result is on hold until they do.",
      "status": "under_review"
    },
    "appeal_entries_logged": 1,
    "logged_reasoning_matches": true,
    "kind": "real",
    "submit_status": 200,
    "original_guess": "ai"
  },
  {
    "content_id": "not-a-real-id",
    "status": 404,
    "response": {
      "error": "unknown_content_id",
      "message": "We couldn't find a submission with that content_id."
    },
    "appeal_entries_logged": 0,
    "logged_reasoning_matches": false,
    "kind": "fake"
  }
]
```

*Criterion 5. Two clean rejections, and the one that got through: 250,000
characters of `"word "`, scored, labelled `ai` and logged as `decided`.*

```json
[
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "(empty text)",
    "error": "empty_text",
    "message": "text can't be empty.",
    "log_entries": [
      {
        "status": "rejected",
        "event": "rejected",
        "reason": "empty_text",
        "creator_id": "eval_bad_empty",
        "content_id": null
      }
    ]
  },
  {
    "status": 200,
    "guess": "ai",
    "confidence": 0.8988,
    "model_score": 0.9975,
    "style_score": 0.8,
    "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
    "sent": "word word word word word word word word word word word word word word ",
    "log_entries": [
      {
        "status": "decided",
        "event": null,
        "reason": null,
        "creator_id": "eval_bad_huge",
        "content_id": "cea494a4-1ad8-4827-a55c-dade78a76009"
      }
    ]
  },
  {
    "status": 400,
    "guess": null,
    "confidence": null,
    "model_score": null,
    "style_score": null,
    "label": null,
    "sent": "{\"text\": \"Climate change is one of the most pressing challenges facing the world today. Rising global temperatures are c",
    "error": "missing_creator_id",
    "message": "creator_id is required.",
    "log_entries": [
      {
        "status": "rejected",
        "event": "rejected",
        "reason": "missing_creator_id",
        "creator_id": "unknown",
        "content_id": null
      }
    ]
  }
]
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
