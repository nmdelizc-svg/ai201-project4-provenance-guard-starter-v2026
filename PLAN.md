# Provenance Guard — Milestone 1 plan

Written before any of the service is built. This is the map the seven pieces
have to agree on: the path, the two signals, the person a false positive lands
on, and the two endpoint contracts.

---

## 1. The path a piece of text takes

From arriving at the service to the label a reader sees.

1. **The route — `app.py::submit`.** The request arrives as JSON. The route
   checks that it has a non-empty `text` and `creator_id` and that the text
   is neither too short nor too long to score. If something is wrong it stops
   here, logs a rejection, and answers with a 4xx error. If everything is
   fine it gives the submission a `content_id` (a UUID). That id lets the log
   entry, the response and any later appeal refer to the same piece of text.
   *(In unit 8 the rate limiter sits in front of this step.)*
2. **Signal one — `detector.model_signal(text)`.** gpt2 runs on this machine
   and measures how predictable the text is. *Adds `model_score`*, 0–1,
   where higher means more likely AI.
3. **Signal two — `stylometry.style_signal(text)`.** This measures the text's
   shape: how much sentence length varies, how varied the vocabulary is, and
   how much and what kind of punctuation it uses. *Adds `style_score`*, 0–1,
   where higher means more likely AI.
4. **The combining rule — `scoring.combine_signals(model, style)`.** Turns
   the two scores into one. *Adds the combined score*, 0–1, where higher
   means more likely AI. The response returns it as `confidence` and the log
   stores it as `combined_score`.
5. **The label mapping — `scoring.score_to_label(score)`.** Compares the
   combined score with the two thresholds in `config.py`. *Adds `guess`*
   (`"human"` / `"unsure"` / `"ai"`) *and `label`*, the plain-English
   sentence a person reads.
6. **The audit log — `audit.log_decision(...)`.** Writes one line holding
   all nine fields, with `status: "decided"`. *Adds a lasting record*,
   which is the only trace of the decision once the response has been sent,
   and what `/appeal` looks the item up by.
7. **The response.** The JSON goes back to the caller. The reader sees the
   `label` and keeps the `content_id`, which they need if they want to
   appeal.

**A branch off the end: `POST /appeal`.** A writer who disagrees sends the
`content_id` and their reasoning. The route checks that the id exists in the
log and appends an appeal entry with `audit.log_appeal`. The item moves to
`under_review`. Nothing is re-scored automatically and the original decision
stays in the log.

---

## 2. The two signals

### Signal one — the model signal (`detector.py`, given)

**What it measures:** how predictable the text is to a language model
(gpt2's perplexity), squashed to 0–1. Low perplexity gives a high score.

**Why it might differ between human and AI writing:** a language model writes
by choosing a likely next word over and over, so its output is text a model
finds easy to predict. People wander more: they pick odd words, change
direction abruptly, and choose specific details over typical ones.

**What it can't see:**
- **Authorship.** It measures predictability, and plenty of people write
  predictably. Plain writing in short sentences with common words scores like
  machine writing. That includes someone writing in a second language, a
  younger writer, and anyone keeping it simple on purpose.
- **The reverse case.** AI text that has been told to use rare words, or
  that someone has edited to add unusual vocabulary, scores as *human*
  because rare words are exactly what the model fails to predict.
- **Anything past roughly the first 300 words.** It truncates at
  `DETECTOR_MAX_TOKENS = 400`, so a submission that opens with human writing
  and ends with AI writing is judged on the opening alone.
- **Its own noise on short texts.** A few sentences give an unsteady reading,
  and a text under 3 tokens raises an error instead of returning a score.

### Signal two — the style signal (`stylometry.py`, mine to build)

**What it measures:** the shape of the text, without reading it. It combines
three measures:
- *sentence-length spread*: standard deviation over mean of the sentence
  lengths. Low spread points to AI.
- *type-token ratio*: unique words over total words. Low variety points to
  AI.
- *punctuation density and variety*: how often semicolons, dashes,
  parentheses, colons and question or exclamation marks appear per word.
  Plain commas and full stops only point to AI.

Each measure is scaled to 0–1 and flipped where needed so that higher means
more likely AI. The three are then averaged.

**Why it might differ between human and AI writing:** "most likely next word"
writing tends toward even, mid-length sentences, a narrower set of words, and
safe punctuation. Human writing is lumpier, with a three-word sentence next
to a forty-word one, a dash, an aside in brackets.

**What it can't see:**
- **Meaning.** It can't read, so anything that changes the shape without
  changing the substance moves it. Examples: adding typos (which raise
  vocabulary variety), splitting or merging sentences, sprinkling in dashes,
  pasting in a quotation. All of these are cheap to do on purpose.
- **Length effects.** Type-token ratio drops as text gets longer, so a long
  human essay can look less varied than a short AI paragraph.
- **Non-prose.** Lists, poems, dialogue, code and bullet points have
  "sentences" that the splitter doesn't understand.
- **Writers with a steady rhythm.** Technical writers, people following a
  template, and second-language writers who stick to one sentence pattern
  have even sentences and a narrow vocabulary, so they look like AI.

### The blind spot they share

Both signals score **plain, even, conventional writing** as AI-like. Signal
one does it because the words are predictable; signal two because the
sentences are even and the vocabulary is narrow. So for the writer most at
risk, the two signals **agree**, and agree wrongly. A rule that treats
disagreement as uncertainty can't protect this person, because there's no
disagreement to catch. That shapes the false positive below.

---

## 3. Tracing the false positive

**The writer:** a student writing in their second language. They wrote every
word of a 250-word reflection themselves, in short, careful sentences, using
vocabulary they're sure of. They hardly use any punctuation besides full
stops and commas.

**What happens to them in the service as currently configured** (placeholder
weights 0.5 / 0.5, thresholds 0.35 / 0.65). These scores are expected values
and haven't been measured yet. Milestone 4 checks them with a plain human
calibration paragraph.

| Step | What it produces for them |
|---|---|
| Route | Accepted, given a `content_id` |
| Signal one | Low perplexity, so `model_score` ≈ 0.75–0.85 |
| Signal two | Even sentences, repeated words, only commas and full stops, so `style_score` ≈ 0.65–0.75 |
| Combine (average) | ≈ 0.70–0.80. The signals agree, so nothing pulls it toward the middle |
| Label | Above 0.65, so `guess: "ai"`, the high-confidence AI label |
| Log | Recorded as `decided` |

**What the label says to them:** with the placeholder thresholds, a
confident statement that their own work was machine-written. For this writer
that's an accusation they may not have the words or the standing to argue
with.

**What they can do about it:** only `POST /appeal` with their `content_id`
and a reason. The item moves to `under_review` and a person has to look at
it. Nothing is re-scored. For that to work at all:
- the response **must** carry `content_id` (without it they can't appeal),
- the label text **must** tell them they can appeal and that the result is
  an estimate, and
- the appeal response **must** confirm in plain words that it was received
  and what happens next.

**What this decides for Milestones 4 and 5:**
1. **The high-confidence AI band has to be hard to reach.** Its threshold
   should sit well above where plain human writing lands on my calibration
   inputs, even if that lets lightly edited AI text through as "unsure". A
   missed AI text costs the site a little; this accusation costs the writer
   a lot.
2. **Averaging alone isn't enough**, because the two signals share this
   blind spot. I'll consider requiring *both* signals to be high and the
   combined score to clear the threshold before saying "ai".
3. **The unsure band carries the weight.** It should be wide, and its
   wording must not read as an accusation, since the person reading it may
   well have written every word.
4. **None of the labels should say "this is AI".** The strongest one says
   what the system *thinks* and how to challenge it.

---

## 4. The endpoint contracts

All bodies are JSON. All scores are floats from 0.0 to 1.0, rounded to 4
places, and **higher always means more likely AI**. Every error, on either
endpoint, has the same shape:

```json
{ "error": "<machine_code>", "message": "<one plain-English sentence>" }
```

### `POST /submit`

**Request**

| Field | Type | Required | Rules |
|---|---|---|---|
| `text` | string | yes | After trimming whitespace: at least **40 words** and at most **10,000 characters** |
| `creator_id` | string | yes | Non-empty after trimming, at most 100 characters |

Any other fields are ignored.

**Response: `200 OK`**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | UUID4 for this submission. Needed to appeal |
| `creator_id` | string | Echoed back as received (trimmed) |
| `guess` | string | Exactly one of `"human"`, `"unsure"`, `"ai"` |
| `confidence` | float 0–1 | The **combined score**, i.e. how likely the text is AI. It is the same number logged as `combined_score`. *Not* "how sure we are of the guess": 0.10 means confidently human |
| `label` | string | The full sentence shown to the reader. Ends by saying the result is an estimate and can be appealed |
| `model_score` | float 0–1 | Signal one, as returned by `detector.model_signal` |
| `style_score` | float 0–1 | Signal two, as returned by `stylometry.style_signal` |
| `status` | string | Always `"decided"` on a new submission |

```json
{
  "content_id": "3f2b8c1e-9a4d-4e57-b0a1-6c2d9e8f7a10",
  "creator_id": "writer_42",
  "guess": "unsure",
  "confidence": 0.5312,
  "label": "<the unsure label text, written in Milestone 5>",
  "model_score": 0.6120,
  "style_score": 0.4504,
  "status": "decided"
}
```

**Errors.** Every one is logged with `audit.log_rejection` and none of them
creates a `content_id`.

| Status | `error` | When |
|---|---|---|
| 400 | `invalid_json` | The body isn't JSON, or is JSON but not an object (a list, a string) |
| 400 | `missing_text` | `text` is absent or not a string |
| 400 | `empty_text` | `text` is only whitespace |
| 400 | `missing_creator_id` | `creator_id` is absent, not a string, empty, or over 100 characters |
| 413 | `text_too_long` | Over 10,000 characters |
| 422 | `text_too_short` | Under 40 words, too short to score honestly |
| 429 | `rate_limited` | Unit 8. Uses the existing handler's shape, which adds a `limit` field |
| 503 | `detector_unavailable` | The model couldn't load. The item isn't scored and nothing is guessed |

There are no 500s by design. Any input that reaches a signal has already
passed validation.

### `POST /appeal`

**Request**

| Field | Type | Required | Rules |
|---|---|---|---|
| `content_id` | string | yes | Must match a `content_id` already in the audit log |
| `reasoning` | string | yes | Non-empty after trimming, at most 2,000 characters |

`creator_id` is **not** taken from the request. It is copied from the
original decision entry so that the appeal is tied to the person who
submitted.

**Response: `200 OK`**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | Echoed back |
| `status` | string | Always `"under_review"` |
| `message` | string | Plain-English confirmation: the appeal was received, a person will review it, and the original result stands until then |
| `appealed_at` | string | ISO-8601 UTC timestamp, matching the log entry |

```json
{
  "content_id": "3f2b8c1e-9a4d-4e57-b0a1-6c2d9e8f7a10",
  "status": "under_review",
  "message": "We've received your appeal. A person will review this piece, and the original result is on hold until they do.",
  "appealed_at": "2026-11-02T18:04:11+00:00"
}
```

**Errors**

| Status | `error` | When |
|---|---|---|
| 400 | `invalid_json` | The body isn't a JSON object |
| 400 | `missing_content_id` | Absent, not a string, or empty |
| 400 | `missing_reasoning` | Absent, not a string, empty, or over 2,000 characters |
| 404 | `unknown_content_id` | No decision in the log has this id |

**A second appeal** on the same `content_id` is accepted. It is appended to
the log as another appeal entry and gets the same `200` response, because a
writer who adds more reasoning shouldn't be refused.

### The check: could someone else build against this?

Reading it back, the questions a stranger might ask, and where each is
answered:
- *Which way do the scores point?* Higher always means AI, stated at the
  top.
- *Is `confidence` "how sure" or "how AI"?* How AI, stated in the table.
- *What happens on bad input?* Every case has a status, a code and a shape.
- *Where does `/appeal` get `creator_id`?* From the log, not the request.
- *Can someone appeal twice?* Yes, and it's logged both times.

The label *wording* is still open. That's Milestone 5, and the contract only
fixes that `label` is a full sentence ending with the appeal note.
