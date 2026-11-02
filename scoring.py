"""
Turning two numbers into one, and one number into something a person can read.
← YOU BUILD THIS IN MILESTONES 4 AND 5

Two functions live here, and both are stubs.

`combine_signals` is where your false-positive decision from Milestone 1
actually gets made. Everything above it — the labels, the appeal path — is
downstream of a number this function produced.

`score_to_label` is where you stop writing for a machine and start writing for
a person. A score of 0.62 means nothing to a writer.

⚠️ Your README's **Signals and Scoring** section has to name the file and
function holding your combining rule. The grader checks your code against what
you claim, so that line should read `scoring.py::combine_signals`.
"""

import config


def combine_signals(model_score: float, style_score: float) -> float:
    """
    Combine two 0–1 signals into one 0–1 score. ← TODO (Milestone 4)

    Both inputs point the same way: higher means more likely AI. Your output
    should too.

    Args:
        model_score: from `detector.model_signal` — how predictable the text is.
        style_score: from `stylometry.style_signal` — the shape of the text.

    Returns:
        A float from 0.0 (confidently human) to 1.0 (confidently AI).

    ⚠️ **Write the rule down before you code it, and put the numbers in your
    README.** A weighted average is the obvious choice and it is not the only
    one. Things worth thinking about:

      - **What happens when they disagree?** One signal at 0.9 and the other at
        0.1 averages to 0.5 — "unsure". Is that what you want? It might be
        exactly right: two methods disagreeing IS uncertainty. Or you might
        decide one signal is more trustworthy when they split.

      - **Which way do you want to be wrong?** Weighting toward the signal that
        reads more human means fewer false accusations and more AI text
        getting through. There's no weighting that avoids the trade.

      - Milestone 4 asks you to find a case where your two signals split and
        write it down. That case is what this rule exists to handle.

    The weights in config.py are placeholders. Change them, or ignore them and
    write a different rule.

    My rule:

      1. Weighted average, 0.5 / 0.5 (config.WEIGHT_*).
      2. If the signals **split** — one at or above 0.5, the other below, and
         at least config.DISAGREEMENT_GAP apart — the average is clamped
         inside the unsure band. Two methods pointing opposite ways is
         uncertainty, so neither confident label is allowed. In particular,
         one signal alone can never produce "ai".

    Clamping rather than leaning toward the more-human signal is deliberate:
    rare-word AI text reads as human to signal one, so leaning human on a
    split would hand that text a confident "human" label.

    What this can't do: when both signals are wrong *together* — plain human
    writing, which both read as AI — there's no split to catch. That case is
    left to the thresholds (Milestone 5).
    """
    combined = (
        config.WEIGHT_MODEL_SIGNAL * model_score
        + config.WEIGHT_STYLE_SIGNAL * style_score
    )

    if signals_split(model_score, style_score):
        low = config.HUMAN_THRESHOLD + config.SPLIT_MARGIN
        high = config.AI_THRESHOLD - config.SPLIT_MARGIN
        combined = min(max(combined, low), high)

    return round(min(max(combined, 0.0), 1.0), 4)


def signals_split(model_score: float, style_score: float) -> bool:
    """True when the two signals point opposite ways by at least the gap."""
    opposite_sides = (model_score >= 0.5) != (style_score >= 0.5)
    return opposite_sides and abs(model_score - style_score) >= config.DISAGREEMENT_GAP


def score_to_label(score: float) -> tuple[str, str]:
    """
    Turn a score into a guess and the text a reader actually sees.
    ← TODO (Milestone 5)

    Returns:
        (guess, label_text) — where `guess` is a short machine-readable string
        like "ai" / "human" / "unsure", and `label_text` is the full sentence
        shown to a person.

    ⚠️ Write the label text for someone who has never heard the word
    "threshold".

        ✗ "human, 0.81 confidence"
        ✓ "We think this was probably written by a person."

    All three labels have to be **reachable**. If no score can produce one of
    them, your ranges have a gap — and Milestone 5 asks you to submit text that
    produces each one, which is how you'd find out.

    The hardest one to write is "unsure". It has to admit uncertainty without
    sounding like an accusation, because the person reading it may well have
    written every word themselves. Your breakout asks your group what they'd
    think if they got it on their own work. That question is the whole
    milestone.

    The thresholds themselves count as confident (>= / <=), which is why
    combine_signals clamps a split SPLIT_MARGIN inside them.

    Every label ends the same way: it's an estimate, and a person will look
    again if you ask. None of them says "this is AI" — the strongest one says
    what the system thinks and how to challenge it.
    """
    if score >= config.AI_THRESHOLD:
        return "ai", LABEL_AI
    if score <= config.HUMAN_THRESHOLD:
        return "human", LABEL_HUMAN
    return "unsure", LABEL_UNSURE


LABEL_HUMAN = (
    "We think this was probably written by a person. "
    "This is an automated estimate, not a final decision. If anything about "
    "it looks wrong, you can ask for a person to review it."
)

LABEL_UNSURE = (
    "We couldn't tell whether this was written by a person or with help from "
    "an AI tool. This is not an accusation: plenty of people's own writing "
    "lands here, and nothing has been decided against you. If you'd like a "
    "person to take a look, you can ask for a review."
)

LABEL_AI = (
    "Our system thinks this may have been written with help from an AI tool. "
    "This is an automated estimate and it can be wrong, especially with plain "
    "or simple writing. If you wrote this yourself, you can ask for a review "
    "and a person will look at it."
)


def label_ranges() -> list[tuple[str, str]]:
    """
    The score range each label covers. Your README needs these beside the
    label text — given to you so the numbers can't drift apart from config.py.
    """
    return [
        ("high-confidence human", f"0.00 – {config.HUMAN_THRESHOLD:.2f}"),
        ("unsure", f"{config.HUMAN_THRESHOLD:.2f} – {config.AI_THRESHOLD:.2f}"),
        ("high-confidence AI", f"{config.AI_THRESHOLD:.2f} – 1.00"),
    ]
