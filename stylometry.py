"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics

# Window for the moving-average type-token ratio. See `type_token_ratio`.
TTR_WINDOW = 50

# ; : — – ( ) [ ] ? ! and a hyphen used as a dash (with a space either side).
EXPRESSIVE_PUNCTUATION = re.compile(r"[;:—–()\[\]?!]|(?<=\s)-{1,2}(?=\s)")


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies. ← TODO

    Returns:
        A float. Decide yourself what scale it's on and which direction means
        "more human" — then write that down, because your combining rule
        depends on knowing it.

    A hint on what you're reaching for: the standard deviation of sentence
    lengths, probably divided by the mean so a long text and a short one are
    comparable. `statistics.stdev` is imported for you.

    Watch the edge case: a one-sentence submission has no spread at all, and
    `stdev` raises on fewer than two values. Decide what that should return
    before the attack set decides for you.

    My decision: the coefficient of variation (stdev / mean) of words per
    sentence. Roughly 0.0–1.0 in practice; **higher means more human**. Fewer
    than two sentences returns 0.0, and `style_signal` treats that case as "no
    evidence" rather than "very even", so one long sentence isn't called AI.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    lengths = [n for n in lengths if n > 0]
    if len(lengths) < 2:
        return 0.0
    return statistics.stdev(lengths) / statistics.mean(lengths)


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words. ← TODO

    Returns:
        A float between 0 and 1. Higher means more varied vocabulary.

    Worth knowing before you rely on it: this measure falls as text gets
    longer, because common words repeat. Two texts of different lengths aren't
    directly comparable on it, and if your test inputs vary a lot in length,
    that alone can look like a signal.

    My decision: to blunt that length effect, texts longer than
    `TTR_WINDOW` words get a moving-average TTR — the plain ratio over every
    window of that many words, averaged. A 60-word paragraph and a 300-word
    essay are then measured on the same footing. Shorter texts get the plain
    ratio. No words at all returns 0.0.
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    if len(tokens) <= TTR_WINDOW:
        return len(set(tokens)) / len(tokens)
    ratios = [
        len(set(tokens[i:i + TTR_WINDOW])) / TTR_WINDOW
        for i in range(len(tokens) - TTR_WINDOW + 1)
    ]
    return statistics.mean(ratios)


def punctuation_density(text: str) -> float:
    """
    How much punctuation, relative to length. ← TODO

    Returns:
        A float. Whether you count all punctuation or only some kinds — commas,
        semicolons, dashes — is a real choice. Semicolons and em dashes are
        more interesting than full stops, because they vary more between
        writers.

    My decision: only "expressive" marks count — semicolons, colons, dashes
    (em, en, or a hyphen standing between spaces), brackets, question marks
    and exclamation marks — per 100 words. Commas and full stops are left out:
    every writer uses them. A hyphen inside a word ("well-known") is not a
    dash and isn't counted. **Higher means more human.** No words returns 0.0.
    """
    total = len(words(text))
    if total == 0:
        return 0.0
    marks = len(EXPRESSIVE_PUNCTUATION.findall(text))
    return 100 * marks / total


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.** ← TODO

    Combine your three measures into one number. Same direction as
    `detector.model_signal`, so that `scoring.combine_signals` can treat them
    the same way — if one of your signals runs backwards, everything above it
    is wrong in a way that's hard to see.

    Two things to decide and write down:

      1. Which direction each measure points. Low spread means more AI-ish, so
         it needs flipping. Work out which of your three need that.
      2. How to get each onto a comparable scale. A raw type-token ratio sits
         between 0 and 1; a raw punctuation count doesn't. Adding them
         unscaled means whichever has the bigger numbers wins by default.

    Test it on the four calibration inputs from Milestone 4 — clearly AI,
    clearly human, plain conventional human writing, lightly-edited AI — before
    you trust it. Plain and ordinary, not formal: formal prose reads as *human*
    to signal one, and it is plain writing that gets accused.

    My decisions:

      1. All three raw measures point toward *human* as they rise, so all
         three are flipped.
      2. Each is mapped linearly onto 0–1 between two anchors (see `ANCHORS`)
         and clipped: at or past the AI anchor scores 1.0, at or past the
         human anchor scores 0.0. The anchors come from the raw values of the
         calibration inputs, recorded in the README.
      3. Weighted average: spread 0.4, punctuation 0.4, type-token ratio 0.2.
         TTR gets less because on the calibration inputs it barely moved
         (0.80–0.86) and didn't separate AI from human at all.

    With fewer than two sentences there is no spread to measure, so that
    component scores 0.5 ("no evidence") instead of 1.0.
    """
    parts = {
        "spread": _scale(sentence_length_spread(text), *ANCHORS["spread"]),
        "ttr": _scale(type_token_ratio(text), *ANCHORS["ttr"]),
        "punctuation": _scale(punctuation_density(text), *ANCHORS["punctuation"]),
    }
    if len(sentences(text)) < 2:
        parts["spread"] = 0.5

    score = sum(STYLE_WEIGHTS[k] * v for k, v in parts.items())
    return round(min(max(score, 0.0), 1.0), 4)


# (AI anchor, human anchor) for each raw measure. A raw value at the AI anchor
# scores 1.0, at the human anchor 0.0, linear in between, clipped outside.
ANCHORS = {
    "spread": (0.10, 0.70),        # stdev / mean of words per sentence
    "ttr": (0.70, 0.90),           # moving-average type-token ratio
    "punctuation": (0.0, 4.0),     # expressive marks per 100 words
}

STYLE_WEIGHTS = {"spread": 0.4, "ttr": 0.2, "punctuation": 0.4}


def _scale(value: float, ai_anchor: float, human_anchor: float) -> float:
    """Map a raw measure onto 0–1 where 1.0 is the AI end. Clipped."""
    fraction = (value - ai_anchor) / (human_anchor - ai_anchor)
    return 1.0 - min(max(fraction, 0.0), 1.0)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
