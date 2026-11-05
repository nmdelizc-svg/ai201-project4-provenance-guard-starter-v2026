"""
What your test runs. ← UNIT 8, MILESTONE 3

One scenario per criterion in criteria.md. `run_eval.py` runs every one of
them three times and fills in the Run columns of the run log from `check`.

A scenario carries **one** of these:

    "texts"    a list of strings. Each is sent to /submit as
               {"text": ..., "creator_id": ...} with a creator_id made up for
               you. Optional "expect" (same length) tags each text with the
               label it's aimed at, and is copied onto that text's result.

    "bodies"   a list of whole request bodies, sent to /submit exactly as
               written. Used when the malformed request IS the point.

    "appeals"  {"texts": [...], "fake_ids": [...], "reasoning": "..."}.
               Each text is submitted, then appealed with the content_id that
               came back. Each fake id is appealed without a submission. The
               audit log is read before and after every appeal.

And optionally:

    "target"     the target, as written in the run log's Target column
    "check_log"  read the audit log before and after each request and record
                 the new entries (bodies/texts scenarios)
    "check"      check(results) -> (passed: bool, cell: str). One trial's
                 results in, a pass/fail and the text for that Run cell out.
"""

# ── Criterion 1: my own writing ──────────────────────────────────────────────
# ⚠️ Ten pieces I wrote myself, not AI text. At least 4 deliberately plain: short
# sentences, everyday words, few commas. Triple quotes mean apostrophes and
# double quotes inside need no escaping.

MY_WRITING = [
    # 1 (plain) — my day
    """I got up early today. I made some eggs for breakfast. Then I took a shower. I left home at eight. The bus was almost full. I got to class on time. We had a math test today. It was not very hard. After class I went to the store. I bought some bread and juice. I went home and played games.""",
    # 2 (plain) — favourite food
    """My favorite food is chicken with rice. My mom makes it every Sunday. She uses garlic and onions. She also adds some peppers. First she cooks the chicken in a pan. Then she adds the vegetables. She lets everything cook for a while. The rice cooks in another pot. When everything is ready she serves it hot. I always ask for more.""",
    # 3 (plain) — best friend
    """My best friend lives near my house. We have known each other for years. We met when we were kids. We used to play outside every day. Now we both go to college. We do not see each other much. But we still talk almost every day. Sometimes we go out for food. He always makes me laugh.""",
    # 4 (plain) — an opinion
    """I think people spend too much time online. Most people check their phones all day. Even when they are with friends. I see this almost everywhere. People should spend more time outside. They could go for walks or play sports. They could also talk more with family. Phones are useful for many things. But I think we need more breaks.""",
    # 5 — a memory
    """One of my favorite memories is going to the beach with my family when I was younger. We used to leave really early because my dad hated traffic. My mom would pack sandwiches and cold drinks, and my brother always complained about having to wake up. We spent almost the whole day swimming and playing in the sand. I remember getting home completely exhausted, with salty hair and sunburned shoulders. At the time it felt like a normal weekend, but now I wish we could do that more often.""",
    # 6 — working while studying
    """Honestly, I think working while studying is harder than people make it sound. Everyone says it teaches you responsibility, and sure, that's true, but it also takes away a lot of your free time. Sometimes I get home from work and still have assignments to finish. By the time I'm done, I don't even feel like watching a movie or talking to anyone. I know plenty of people manage both, but I wish schools understood that students have responsibilities outside the classroom too.""",
    # 7 — a message to a friend
    """hey, are you free tomorrow afternoon? I was thinking we could go to the mall or maybe get something to eat. I haven't seen you in forever and I really need to get out of the house lol. Also I heard there's a new movie coming out this week, so we could check that out if you're interested. Let me know what time works for you because I have to help my mom in the morning.""",
    # 8 — a movie review
    """I watched The Truman Show last weekend because someone recommended it to me. I honestly wasn't expecting much, but I ended up really enjoying it. The idea is interesting, and I liked how the story slowly reveals what's actually happening. Jim Carrey was surprisingly good in a more serious role. Some parts felt a little slow, especially near the beginning, but the ending made up for it. It's one of those movies that makes you think about your own life afterward. I'd definitely recommend watching it at least once.""",
    # 9 — a stressful semester
    """This semester has been pretty stressful so far. I have classes almost every day, and some professors seem to think we don't have anything else to do. Last week I had two assignments due on the same day, plus a presentation that I barely had time to prepare for. I stayed up until almost three in the morning trying to finish everything. The worst part is that I actually enjoy most of my classes. I just wish the deadlines were spread out a little better.""",
    # 10 — saving for a laptop
    """I've been trying to save money lately because I really want to buy a laptop. My current one takes forever to start, and sometimes it freezes when I have too many tabs open. I started bringing lunch from home instead of buying food every day, which has helped more than I expected. I also stopped ordering things online just because they were on sale. It's not easy, especially when I see something I like, but I think having a goal makes it easier. Hopefully I'll have enough money by the end of the year.""",
]


# ── Criteria 2 and 3: text whose origin isn't in doubt ───────────────────────
# AI: generated by an AI assistant (Claude) in the default "explain a topic"
# register, unedited.
# Human: published before 1900, so no model was involved. Openings of
# well-known books — gpt2 has probably seen some of them, which can only push
# signal one toward "ai", so if anything this makes the human side harder.

CLEAR_AI = [
    "Climate change is one of the most pressing challenges facing the world today. Rising global temperatures are causing more frequent extreme weather events, including droughts, floods, and heatwaves. Additionally, these changes have significant impacts on ecosystems, agriculture, and human health. It is important for governments, businesses, and individuals to work together to reduce greenhouse gas emissions and build a more sustainable future.",
    "Effective time management is an essential skill for students and professionals alike. By setting clear goals and prioritizing tasks, individuals can improve their productivity and reduce stress. Furthermore, creating a consistent schedule helps ensure that important deadlines are met. Overall, developing strong time management habits can lead to greater success in both academic and professional settings.",
    "Social media has transformed the way people communicate and share information. Platforms such as Facebook, Instagram, and Twitter allow users to connect with friends and family around the world. However, social media also presents several challenges, including the spread of misinformation and concerns about privacy. It is important for users to think critically about the content they encounter online.",
    "Regular physical activity offers numerous benefits for both physical and mental health. Exercise can help strengthen the heart, improve muscle tone, and maintain a healthy weight. In addition, physical activity has been shown to reduce symptoms of anxiety and depression. Experts recommend that adults engage in at least 150 minutes of moderate exercise each week.",
    "Reading is a valuable activity that offers many benefits for people of all ages. It helps improve vocabulary, strengthen critical thinking skills, and expand knowledge about a wide range of topics. Moreover, reading can be a relaxing way to reduce stress and escape from daily pressures. Encouraging a love of reading from an early age can have a lasting positive impact.",
]

CLEAR_HUMAN = [
    # Mark Twain, Adventures of Huckleberry Finn (1884)
    "You don't know about me without you have read a book by the name of The Adventures of Tom Sawyer; but that ain't no matter. That book was made by Mr. Mark Twain, and he told the truth, mainly. There was things which he stretched, but mainly he told the truth. That is nothing. I never seen anybody but lied one time or another, without it was Aunt Polly, or the widow, or maybe Mary.",
    # Herman Melville, Moby-Dick (1851)
    "Call me Ishmael. Some years ago—never mind how long precisely—having little or no money in my purse, and nothing particular to interest me on shore, I thought I would sail about a little and see the watery part of the world. It is a way I have of driving off the spleen and regulating the circulation.",
    # Frederick Douglass, Narrative of the Life of Frederick Douglass (1845)
    "I was born in Tuckahoe, near Hillsborough, and about twelve miles from Easton, in Talbot county, Maryland. I have no accurate knowledge of my age, never having seen any authentic record containing it. By far the larger part of the slaves know as little of their ages as horses know of theirs, and it is the wish of most masters within my knowledge to keep their slaves thus ignorant.",
    # Henry David Thoreau, Walden (1854)
    "I went to the woods because I wished to live deliberately, to front only the essential facts of life, and see if I could not learn what it had to teach, and not, when I came to die, discover that I had not lived. I did not wish to live what was not life, living is so dear; nor did I wish to practise resignation, unless it was quite necessary.",
    # Charles Dickens, Great Expectations (1861)
    "My father's family name being Pirrip, and my Christian name Philip, my infant tongue could make of both names nothing longer or more explicit than Pip. So, I called myself Pip, and came to be called Pip. I give Pirrip as my father's family name, on the authority of his tombstone and my sister,—Mrs. Joe Gargery, who married the blacksmith.",
]


# ── Criterion 3: three aimed at each label ───────────────────────────────────

AIMED_AI = [
    # The README's Sample Run "ai" input
    "Artificial intelligence has become an increasingly important part of modern society. It is used in a wide variety of applications, including healthcare, finance, and education. Additionally, AI systems can help organizations improve efficiency and make better decisions. However, it is important to consider the ethical implications of these technologies.",
    # Generated by an AI assistant, unedited
    "Renewable energy sources, such as solar and wind power, play a crucial role in reducing reliance on fossil fuels. These technologies generate electricity without producing harmful emissions. Furthermore, advances in battery storage are making renewable energy more reliable and affordable. As a result, many countries are investing heavily in clean energy infrastructure to meet their climate goals.",
    "Teamwork is an important part of success in the workplace. When team members communicate effectively and share responsibilities, they can achieve their goals more efficiently. Additionally, collaboration encourages creativity and allows individuals to learn from one another. Organizations that foster a positive team culture often experience higher employee satisfaction and productivity.",
]

AIMED_UNSURE = [
    # The README's Sample Run "unsure" input
    "My grandmother kept her buttons in a Danish cookie tin, the blue one, and when I was six I swallowed a brass one shaped like an anchor. Nobody panicked. She just handed me a slice of white bread, told me to chew slow, and went back to her crossword.",
    # AI-generated, then roughened: contractions, a dash, an aside, a hedge
    "Remote work has changed a lot about how people do their jobs. It's flexible, sure — you skip the commute and set your own hours. But it can also be isolating, and plenty of people find it hard to switch off at the end of the day. Companies are still figuring out the right balance, and honestly, I don't think anyone has it nailed yet.",
    "Starting a vegetable garden doesn't have to be complicated. Pick a sunny spot, build up the soil with some compost, and start with easy crops like lettuce, beans or tomatoes. You'll make mistakes (everyone does), but that's part of learning. Most beginners find that a small plot is plenty for the first year.",
]

AIMED_HUMAN = [
    # Jane Austen, Pride and Prejudice (1813)
    "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want of a wife. However little known the feelings or views of such a man may be on his first entering a neighbourhood, this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful property of some one or other of their daughters.",
    # Mark Twain, The Adventures of Tom Sawyer (1876)
    '"Tom!" No answer. "Tom!" No answer. "What\'s gone with that boy, I wonder? You TOM!" No answer. The old lady pulled her spectacles down and looked over them about the room; then she put them up and looked out under them.',
    # Mary Shelley, Frankenstein (1818)
    "You will rejoice to hear that no disaster has accompanied the commencement of an enterprise which you have regarded with such evil forebodings. I arrived here yesterday, and my first task is to assure my dear sister of my welfare and increasing confidence in the success of my undertaking.",
]


# ── The checks: one trial's results in, (passed, Run cell) out ───────────────

def check_own_writing(results):
    """Criterion 1: at most 1 of 10 labelled high-confidence AI."""
    flagged = sum(r.get("guess") == "ai" for r in results)
    errors = sum(r.get("status") != 200 for r in results)
    cell = f"{flagged}/{len(results)}" + (f" ({errors} errored)" if errors else "")
    return flagged <= 1 and errors == 0, cell


def check_spread(results):
    """Criterion 2: mean AI confidence at least 0.30 above mean human."""
    def mean(kind):
        scores = [r.get("confidence") for r in results if r.get("expect") == kind]
        if not scores or any(s is None for s in scores):
            return None
        return sum(scores) / len(scores)

    ai, human = mean("ai"), mean("human")
    if ai is None or human is None:
        return False, "errored"
    gap = ai - human
    return gap >= 0.30, f"{gap:.3f}"


def check_labels(results):
    """Criterion 3: at least 2 of the 3 aimed at each label get it."""
    counts = {}
    for label in ("human", "unsure", "ai"):
        aimed = [r for r in results if r.get("expect") == label]
        counts[label] = (sum(r.get("guess") == label for r in aimed), len(aimed))
    passed = all(hit >= 2 for hit, _ in counts.values())
    cell = ", ".join(f"{k} {hit}/{n}" for k, (hit, n) in counts.items())
    return passed, cell


def check_appeals(results):
    """Criterion 4: 5/5 real appeals land and log once; 3/3 fakes 404 and log none."""
    real = [r for r in results if r["kind"] == "real"]
    fake = [r for r in results if r["kind"] == "fake"]
    real_ok = sum(
        r.get("status") == 200
        and r.get("response", {}).get("status") == "under_review"
        and r.get("appeal_entries_logged") == 1
        and r.get("logged_reasoning_matches") is True
        for r in real
    )
    fake_ok = sum(
        r.get("status") == 404
        and r.get("response", {}).get("error") == "unknown_content_id"
        and r.get("appeal_entries_logged") == 0
        for r in fake
    )
    passed = real_ok == len(real) and fake_ok == len(fake)
    return passed, f"{real_ok}/{len(real)} + {fake_ok}/{len(fake)}"


def check_bad_input(results):
    """Criterion 5: each gets a 4xx with error+message and one rejected log entry."""
    def ok(r):
        status = r.get("status") or 0
        rejected = [e for e in r.get("log_entries", []) if e.get("status") == "rejected"]
        return (
            400 <= status < 500
            and status != 429               # a 429 never reached the route
            and bool(r.get("error")) and bool(r.get("message"))
            and len(rejected) == 1
        )

    good = sum(ok(r) for r in results)
    crashes = sum((r.get("status") or 500) >= 500 for r in results)
    cell = f"{good}/{len(results)}" + (f" ({crashes} × 5xx)" if crashes else "")
    return good == len(results), cell


# ── The scenarios ────────────────────────────────────────────────────────────

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        "target": "≤ 1 of 10 labelled ai",
        "texts": MY_WRITING,
        "check": check_own_writing,
    },
    {
        "name": "score spread",
        "criterion": 2,
        "target": "AI mean − human mean ≥ 0.30",
        "texts": CLEAR_AI + CLEAR_HUMAN,
        "expect": ["ai"] * len(CLEAR_AI) + ["human"] * len(CLEAR_HUMAN),
        "check": check_spread,
    },
    {
        "name": "label coverage",
        "criterion": 3,
        "target": "≥ 2 of 3 per label",
        "texts": AIMED_HUMAN + AIMED_UNSURE + AIMED_AI,
        "expect": ["human"] * 3 + ["unsure"] * 3 + ["ai"] * 3,
        "check": check_labels,
    },
    {
        "name": "appeal path",
        "criterion": 4,
        "target": "5 of 5 real + 3 of 3 fake",
        "appeals": {
            # Two of each confident kind plus one borderline: an appeal must
            # work whatever the original label was.
            "texts": CLEAR_AI[:2] + CLEAR_HUMAN[:2] + AIMED_UNSURE[:1],
            "fake_ids": [
                "not-a-real-id",
                "00000000-0000-0000-0000-000000000000",
                "3f2b8c1e-9a4d-4e57-b0a1-6c2d9e8f7a10",  # the PLAN.md example id
            ],
            "reasoning": "I wrote this myself. Please have a person look at it.",
        },
        "check": check_appeals,
    },
    {
        "name": "bad input",
        "criterion": 5,
        "target": "6 of 6 get 4xx + logged",
        "check_log": True,
        "bodies": [
            {"text": "", "creator_id": "eval_bad_empty"},
            {"text": "   \n\t  ", "creator_id": "eval_bad_whitespace"},
            {"creator_id": "eval_bad_missing"},              # no text field at all
            {"text": None, "creator_id": "eval_bad_null"},
            {"text": "word " * 50000, "creator_id": "eval_bad_huge"},  # 250,000 chars
            {"text": CLEAR_AI[0]},                           # no creator_id
        ],
        "check": check_bad_input,
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        kinds = [k for k in ("texts", "bodies", "appeals") if scenario.get(k)]
        if len(kinds) > 1:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has {' and '.join(kinds)} "
                f"— pick one"
            )
            continue

        if scenario.get("appeals"):
            spec = scenario["appeals"]
            if not spec.get("texts") or not spec.get("reasoning"):
                problems.append(f"scenario {i}: appeals needs texts and reasoning")
            continue

        bodies = scenario.get("bodies")
        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        texts = scenario.get("texts")
        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        expect = scenario.get("expect")
        if expect is not None and len(expect) != len(texts):
            problems.append(f"scenario {i}: expect has {len(expect)} tags for {len(texts)} texts")

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
