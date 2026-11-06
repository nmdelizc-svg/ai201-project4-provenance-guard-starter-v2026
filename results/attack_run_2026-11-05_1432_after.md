# Attack run — after

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-05 14:32
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `9c111869-59f9-4dc4-b592-280e4a14c01e` | unsure | 0.462 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `f296fc1a-6baa-479c-90cd-0e2287c8fe31` | unsure | 0.360 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `55dcd9ec-3a0b-43e4-8699-c70278fe0c97` | unsure | 0.524 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `735be6f5-1c63-4965-993c-9ec43e379723` | unsure | 0.681 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `3be8f6f8-d6e3-4451-8a9e-bf7b78220afe` | human | 0.328 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `feb091f2-53f8-479d-a5aa-e3e3e6dd6c61` | unsure | 0.512 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `f7f46632-4c84-4219-96f2-49e4823153ca` | unsure | 0.420 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `5ce68eac-125a-47a6-b0ee-ebf6e469241b` | unsure | 0.462 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c7647aa4-330e-4988-ae77-43b67a04ebbc` | unsure | 0.630 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `1047ae9c-a2df-4d9f-9cc5-411545d9eb28` | ai | 0.892 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `4ff9bc97-6aaa-4baa-88a0-10c3fdfe78ad` | unsure | 0.636 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `ab17e7bd-fe08-40f7-b6e2-ffb7bd2bc9f8` | unsure | 0.788 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `7abbf006-968e-4c04-a937-ee68fa827b99` | unsure | 0.767 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `7387ce62-df88-4025-a108-2c57755fc9aa` | unsure | 0.767 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `f9a9f126-7bb0-4d61-8c5a-fedcf9ce5c26` | ai | 0.841 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `c769ec9b-ea76-4220-8f35-7dd65d1588f5` | unsure | 0.773 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `a2e459ee-bcd6-4355-a68f-347a50792fcb` | unsure | 0.741 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `0da6d68b-6d3f-439e-b7ed-a2a200af48d8` | unsure | 0.450 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `48026093-e00c-45c2-bf10-6d00a0e9cc14` | unsure | 0.444 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `e3e88672-3ea8-4323-8c2b-26a96447529d` | human | 0.207 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `e9e0d9f9-cd49-46da-bd0e-4aaab1aa26cf` | unsure | 0.416 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `263a23da-29b2-4a79-99d8-fa77f2982627` | unsure | 0.375 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `f7638683-bcb6-45b1-9207-2a51ce2de925` | unsure | 0.396 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `90e822d8-b399-42d0-94fc-c980c90babbb` | unsure | 0.608 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 422 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `7f767604-3497-4ab4-995b-1ef8728b0cf5` | human | 0.100 |  |
| MF04 | malformed | text is only punctuation | 200 | `c49c952d-a396-45a5-b12b-945f11464355` | unsure | 0.506 |  |
| MF05 | malformed | text is a very long single word | 200 | `6867c919-8adf-46e4-83cf-f07c6bbae171` | unsure | 0.799 |  |
| MF06 | malformed | text is emoji only | 200 | `8ec566df-af55-45f4-b926-d2ef90d281d9` | ai | 0.898 |  |
| MF07 | malformed | text is right-to-left script | 200 | `d728561e-3b4d-4df1-86a9-978b6516a84d` | ai | 0.853 |  |
| MF08 | malformed | text is 60,000 characters | 200 | `e86c39a7-8ffb-43cc-af0d-6eacba18a03b` | ai | 0.843 |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — |  |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 429 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 429 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `b578ca86-df30-405c-89cd-e1a72ea4499f` | unsure | 0.360 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `6c5cc04d-0142-4482-abbf-950ed04c43cd` | unsure | 0.360 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `8733264b-4264-4acd-9e80-7c0730230b91` | unsure | 0.360 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `289a6726-30b4-4ace-a5ff-362f7e7948aa` | unsure | 0.360 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `2655dd95-b634-44b5-a14c-05e122ad77e0` | unsure | 0.360 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "9c111869-59f9-4dc4-b592-280e4a14c01e",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.4615,
  "model_score": 0.1635,
  "style_score": 0.7595,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "f296fc1a-6baa-479c-90cd-0e2287c8fe31",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.36,
  "model_score": 0.5943,
  "style_score": 0.076,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "55dcd9ec-3a0b-43e4-8699-c70278fe0c97",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.5243,
  "model_score": 0.6662,
  "style_score": 0.3824,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "735be6f5-1c63-4965-993c-9ec43e379723",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.681,
  "model_score": 0.6114,
  "style_score": 0.7506,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "3be8f6f8-d6e3-4451-8a9e-bf7b78220afe",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.3281,
  "model_score": 0.3212,
  "style_score": 0.3351,
  "label": "We think this was probably written by a person. This is an automated estimate, not a final decision. If anything about it looks wrong, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "feb091f2-53f8-479d-a5aa-e3e3e6dd6c61",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.512,
  "model_score": 0.5727,
  "style_score": 0.4512,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "f7f46632-4c84-4219-96f2-49e4823153ca",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.4204,
  "model_score": 0.5862,
  "style_score": 0.2546,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "5ce68eac-125a-47a6-b0ee-ebf6e469241b",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.4617,
  "model_score": 0.2452,
  "style_score": 0.6781,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "c7647aa4-330e-4988-ae77-43b67a04ebbc",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.6296,
  "model_score": 0.7042,
  "style_score": 0.555,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "1047ae9c-a2df-4d9f-9cc5-411545d9eb28",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.8917,
  "model_score": 0.9792,
  "style_score": 0.8041,
  "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "4ff9bc97-6aaa-4baa-88a0-10c3fdfe78ad",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.6364,
  "model_score": 0.6175,
  "style_score": 0.6554,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "ab17e7bd-fe08-40f7-b6e2-ffb7bd2bc9f8",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.7877,
  "model_score": 0.7387,
  "style_score": 0.8368,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "7abbf006-968e-4c04-a937-ee68fa827b99",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.7668,
  "model_score": 0.8051,
  "style_score": 0.7285,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "7387ce62-df88-4025-a108-2c57755fc9aa",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.7671,
  "model_score": 0.8329,
  "style_score": 0.7012,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "f9a9f126-7bb0-4d61-8c5a-fedcf9ce5c26",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.8413,
  "model_score": 0.8005,
  "style_score": 0.8821,
  "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "c769ec9b-ea76-4220-8f35-7dd65d1588f5",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.773,
  "model_score": 0.8814,
  "style_score": 0.6646,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "a2e459ee-bcd6-4355-a68f-347a50792fcb",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.7408,
  "model_score": 0.8816,
  "style_score": 0.6,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "0da6d68b-6d3f-439e-b7ed-a2a200af48d8",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.4501,
  "model_score": 0.3223,
  "style_score": 0.578,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "48026093-e00c-45c2-bf10-6d00a0e9cc14",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.4437,
  "model_score": 0.4625,
  "style_score": 0.4249,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "e3e88672-3ea8-4323-8c2b-26a96447529d",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.2072,
  "model_score": 0.2044,
  "style_score": 0.2099,
  "label": "We think this was probably written by a person. This is an automated estimate, not a final decision. If anything about it looks wrong, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "e9e0d9f9-cd49-46da-bd0e-4aaab1aa26cf",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.4162,
  "model_score": 0.5943,
  "style_score": 0.238,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "263a23da-29b2-4a79-99d8-fa77f2982627",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.3749,
  "model_score": 0.4998,
  "style_score": 0.25,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "f7638683-bcb6-45b1-9207-2a51ce2de925",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.3962,
  "model_score": 0.6401,
  "style_score": 0.1524,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "90e822d8-b399-42d0-94fc-c980c90babbb",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.6078,
  "model_score": 0.5583,
  "style_score": 0.6572,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 422,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "7f767604-3497-4ab4-995b-1ef8728b0cf5",
  "creator_id": "attacker_MF03",
  "guess": "human",
  "confidence": 0.1,
  "model_score": 0.0,
  "style_score": 0.2,
  "label": "We think this was probably written by a person. This is an automated estimate, not a final decision. If anything about it looks wrong, you can ask for a person to review it.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "c49c952d-a396-45a5-b12b-945f11464355",
  "creator_id": "attacker_MF04",
  "guess": "unsure",
  "confidence": 0.5056,
  "model_score": 0.0112,
  "style_score": 1.0,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "6867c919-8adf-46e4-83cf-f07c6bbae171",
  "creator_id": "attacker_MF05",
  "guess": "unsure",
  "confidence": 0.7988,
  "model_score": 0.9976,
  "style_score": 0.6,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "8ec566df-af55-45f4-b926-d2ef90d281d9",
  "creator_id": "attacker_MF06",
  "guess": "ai",
  "confidence": 0.8984,
  "model_score": 0.9969,
  "style_score": 0.8,
  "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "d728561e-3b4d-4df1-86a9-978b6516a84d",
  "creator_id": "attacker_MF07",
  "guess": "ai",
  "confidence": 0.8532,
  "model_score": 0.9064,
  "style_score": 0.8,
  "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 200,
  "content_id": "e86c39a7-8ffb-43cc-af0d-6eacba18a03b",
  "creator_id": "attacker_MF08",
  "guess": "ai",
  "confidence": 0.8425,
  "model_score": 0.9876,
  "style_score": 0.6974,
  "label": "Our system thinks this may have been written with help from an AI tool. This is an automated estimate and it can be wrong, especially with plain or simple writing. If you wrote this yourself, you can ask for a review and a person will look at it.",
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 429,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "b578ca86-df30-405c-89cd-e1a72ea4499f",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.36,
  "model_score": 0.0287,
  "style_score": 0.6,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "6c5cc04d-0142-4482-abbf-950ed04c43cd",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.36,
  "model_score": 0.0287,
  "style_score": 0.6,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "8733264b-4264-4acd-9e80-7c0730230b91",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.36,
  "model_score": 0.0287,
  "style_score": 0.6,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "289a6726-30b4-4ace-a5ff-362f7e7948aa",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.36,
  "model_score": 0.0287,
  "style_score": 0.6,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "2655dd95-b634-44b5-a14c-05e122ad77e0",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.36,
  "model_score": 0.0287,
  "style_score": 0.6,
  "label": "We couldn't tell whether this was written by a person or with help from an AI tool. This is not an accusation: plenty of people's own writing lands here, and nothing has been decided against you. If you'd like a person to take a look, you can ask for a review.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
