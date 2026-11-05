#!/usr/bin/env python3
"""
Run your five criteria three times each.  <- UNIT 8, MILESTONE 3

    python app.py                              # in one terminal
    python run_eval.py --label before          # in another
    python run_eval.py --label after

The attack set tests what staff thought to test. This tests what *you* thought
to test, and the two rarely overlap much. Both count.

Fill in `scenarios.py` first — that's where you say what each criterion needs
run against it. A criterion about false positives needs your own writing. One
about label coverage needs inputs across the score range.

!! Three trials, and **your first signal runs a model, so identical input can
score differently twice.** That's exactly why repeats matter here.

This does the sending and the recording. Whether a trial passed depends on the
criterion you wrote, so each scenario in scenarios.py carries its own `check`,
and the Run and Verdict columns are filled from that. A scenario without one
comes back blank.

Beyond /submit, an "appeals" scenario submits, then appeals the content_id that
came back, and reads the audit log around each appeal. A scenario with
"check_log" records the log entries each request left.
"""

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import config

# Windows consoles often run a codepage that can't print every character in
# this file's help text. Without this, `--help` ends in a UnicodeEncodeError
# traceback instead of the help — which is a miserable first thing to hit.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(errors="replace")
    except (AttributeError, ValueError):  # not a normal text stream
        pass


DEFAULT_URL = f"http://{config.HOST}:{config.PORT}"


def bodies_for(scenario):
    """
    The request bodies one scenario sends.

    A "texts" scenario gets a creator_id made up for it. A "bodies" scenario is
    sent exactly as written, which is how a bad-input criterion says things a
    string can't — no `text` field, a null, something enormous.
    """
    if scenario.get("bodies"):
        return list(scenario["bodies"])
    return [
        {"text": text, "creator_id": f"eval_{scenario['name'][:12]}_{i}"}
        for i, text in enumerate(scenario["texts"], 1)
    ]


def read_json(response):
    """The body as a dict, or {"non_json": True} when it isn't JSON (a crash page)."""
    try:
        payload = response.json() if response.content else {}
    except ValueError:
        return {"non_json": True}
    return payload if isinstance(payload, dict) else {"non_json": True}


def log_count(requests, args):
    """How many lines the audit log has right now."""
    return requests.get(f"{args.url}/health", timeout=10).json()["log_entries"]


def new_log_entries(requests, args, before):
    """Every audit log entry written since the log had `before` lines."""
    entries = requests.get(f"{args.url}/log", timeout=10).json()["entries"]
    return entries[before:]


def send_submit(requests, args, scenario, i, body):
    """Send one body to /submit and record what came back."""
    preview = describe(body)
    try:
        before = log_count(requests, args) if scenario.get("check_log") else None
        response = requests.post(f"{args.url}/submit", json=body, timeout=args.timeout)
        payload = read_json(response)
        result = {
            "status": response.status_code,
            "guess": payload.get("guess"),
            "confidence": payload.get("confidence"),
            "model_score": payload.get("model_score"),
            "style_score": payload.get("style_score"),
            "label": payload.get("label"),
            "sent": preview,
        }
        for key in ("error", "message", "non_json"):
            if key in payload:
                result[key] = payload[key]
        if scenario.get("expect"):
            result["expect"] = scenario["expect"][i - 1]
        if before is not None:
            result["log_entries"] = [
                {k: e.get(k) for k in ("status", "event", "reason", "creator_id", "content_id")}
                for e in new_log_entries(requests, args, before)
            ]
        return result
    except Exception as exc:  # noqa: BLE001
        return {"status": None, "error": f"{type(exc).__name__}: {exc}", "sent": preview}


def send_appeal(requests, args, content_id, reasoning):
    """Appeal one content_id and count the appeal entries it left in the log."""
    before = log_count(requests, args)
    response = requests.post(f"{args.url}/appeal", timeout=args.timeout,
                             json={"content_id": content_id, "reasoning": reasoning})
    logged = [e for e in new_log_entries(requests, args, before)
              if e.get("event") == "appeal" and e.get("content_id") == content_id]
    return {
        "content_id": content_id,
        "status": response.status_code,
        "response": read_json(response),
        "appeal_entries_logged": len(logged),
        "logged_reasoning_matches": bool(logged) and all(
            e.get("reasoning") == reasoning for e in logged),
    }


def run_appeals(requests, args, scenario):
    """
    One trial of an appeal scenario: submit each text, appeal the content_id
    that came back, then appeal each made-up id. /submit alone can't test this,
    because an appeal needs a real content_id first.
    """
    spec = scenario["appeals"]
    results = []
    for i, text in enumerate(spec["texts"], 1):
        try:
            submitted = requests.post(f"{args.url}/submit", timeout=args.timeout,
                                      json={"text": text, "creator_id": f"eval_appeal_{i}"})
            sub = read_json(submitted)
            result = send_appeal(requests, args, sub.get("content_id"), spec["reasoning"])
            result.update(kind="real", submit_status=submitted.status_code,
                          original_guess=sub.get("guess"))
        except Exception as exc:  # noqa: BLE001
            result = {"kind": "real", "status": None, "error": f"{type(exc).__name__}: {exc}"}
        results.append(result)
    for fake_id in spec.get("fake_ids", []):
        try:
            result = send_appeal(requests, args, fake_id, spec["reasoning"])
            result["kind"] = "fake"
        except Exception as exc:  # noqa: BLE001
            result = {"kind": "fake", "status": None, "error": f"{type(exc).__name__}: {exc}"}
        results.append(result)
    return results


def describe(body):
    """A short, readable note of what was sent — for the report."""
    if set(body) == {"text", "creator_id"} and isinstance(body.get("text"), str):
        text = body["text"]
        return text[:70] if text else "(empty text)"
    return json.dumps(body)[:120]


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--trials", type=int, default=3)
    parser.add_argument("--label", default="")
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--timeout", type=float, default=90.0)
    args = parser.parse_args()

    try:
        import requests
    except ImportError:
        print("The `requests` package isn't installed.\n"
              "Run: pip install -r requirements.txt", file=sys.stderr)
        sys.exit(1)

    try:
        import scenarios
    except ImportError:
        print("No scenarios.py found. Milestone 3 starts by filling it in.",
              file=sys.stderr)
        sys.exit(1)

    problems = scenarios.validate()
    if problems:
        print("scenarios.py has problems:\n", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        sys.exit(1)

    try:
        requests.get(f"{args.url}/health", timeout=5)
    except Exception:  # noqa: BLE001
        print(f"Nothing answering at {args.url}. Start it:  python app.py",
              file=sys.stderr)
        sys.exit(1)

    if args.trials < 3:
        print(f"!! {args.trials} trial(s). The submission asks for three.\n")

    rows = []
    for scenario in scenarios.SCENARIOS:
        print(f"\n{scenario['name']}  (criterion {scenario.get('criterion') or '—'})")

        trials, checks = [], []
        for trial in range(1, args.trials + 1):
            if scenario.get("appeals"):
                results = run_appeals(requests, args, scenario)
            else:
                results = [send_submit(requests, args, scenario, i, body)
                           for i, body in enumerate(bodies_for(scenario), 1)]

            trials.append(results)
            check = scenario.get("check")
            checks.append(check(results) if check else None)
            if checks[-1]:
                passed, cell = checks[-1]
                print(f"  trial {trial}: {cell}  {'pass' if passed else 'FAIL'}")
            else:
                guesses = [r.get("guess") or str(r.get("status")) for r in results]
                print(f"  trial {trial}: {', '.join(guesses)}")

        rows.append({"scenario": scenario, "trials": trials, "checks": checks})

    write_report(rows, args)


def write_report(rows, args):
    config.RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    label = f"_{args.label}" if args.label else ""
    path = config.RESULTS_DIR / f"run_{stamp}{label}.md"

    n = args.trials
    headers = " | ".join(f"Run {i}" for i in range(1, n + 1))
    divider = "|".join(["---"] * n)

    lines = [
        f"# Run log{f' — {args.label}' if args.label else ''}",
        "",
        "- Produced by: `run_eval.py::main`",
        "- Service: `app.py::submit` · scoring: `scoring.py::combine_signals`",
        f"- {n} trials per criterion · {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Run cells and verdicts come from each scenario's `check` in",
        "`scenarios.py`. MET means the target held in every trial. Check them",
        "against the output underneath.",
        "",
        f"| Criterion | Target | {headers} | Verdict |",
        f"|---|---|{divider}|---|",
    ]

    for row in rows:
        scenario = row["scenario"]
        number = scenario.get("criterion")
        name = f"{number}. {scenario['name']}" if number else scenario["name"]
        checks = row["checks"]
        if all(checks):
            cells = [cell for _, cell in checks]
            verdict = "MET" if all(passed for passed, _ in checks) else "MISSED"
        else:
            cells, verdict = [" "] * n, ""
        lines.append(f"| {name} | {scenario.get('target', '')} | {' | '.join(cells)} | {verdict} |")

    lines += ["", "---", "", "## What actually came back", "",
              "Real output. Paste the relevant parts into your README — the rubric",
              "asks for the actual JSON, not a description of it.", ""]

    for row in rows:
        scenario = row["scenario"]
        lines += [f"### {scenario['name']}", ""]
        for trial_number, results in enumerate(row["trials"], 1):
            lines += [f"**Trial {trial_number}**", "", "```json",
                      json.dumps(results, indent=2), "```", ""]

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nWrote {path.relative_to(config.ROOT)}")
    print("Commit it. It's the evidence the test actually happened.")


if __name__ == "__main__":
    main()
