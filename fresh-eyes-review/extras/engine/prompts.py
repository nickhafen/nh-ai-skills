"""Build the prompts for each stage. All wording comes from the reference files where possible."""

import json
import re

from .references import read_reference

DOCUMENT_MARKER = "[[DOCUMENT]]"

# Which background sensitivities each access tier may see. Unlabeled background is
# treated as privileged (tier A only), per the spec.
TIER_ACCESS = {
    "A": {"privileged", "client_known", "public", "unlabeled"},
    "B": {"client_known", "public"},
    "C": {"public"},
    "none": {"privileged", "client_known", "public", "unlabeled"},
}

REVIEW_SYSTEM = """You simulate one reader of a legal document for fresh-eyes-review, a tool that shows a drafter how the document's real readers are likely to react before it goes out.

Follow the persona review format below exactly. Return JSON that matches the provided schema.

Rules for quotes:
- Every "quote" must be copied verbatim from the document. To join two parts of one passage, use "...".
- For something missing, quote the passage where it should have appeared, or the closest related passage.
- Use the section ids listed with the document for the attention map, one entry per section.

{review_format}"""

BASELINE_TASK = """Review this document for a senior lawyer on the author's side. Use the same output format. There is no persona file: leave "look_for" empty and describe how a careful senior lawyer would read it."""


def document_block(document, sections, cache=True):
    listing = "\n".join(f"{s['id']}: {s['label']}" for s in sections)
    block = {"type": "text",
             "text": f"<document>\n{document}\n</document>\n\n<sections>\n{listing}\n</sections>"}
    if cache:
        block["cache_control"] = {"type": "ephemeral"}
    return block


def background_text(items):
    if not items:
        return "None. You have only the document and the public record."
    return "\n".join(f"- [{b['id']}] {b['text']}" for b in items)


def review_system():
    return REVIEW_SYSTEM.format(review_format=read_reference("persona-review-format.md"))


def persona_task(persona, background_items=None, goal=None, restricted_items=None):
    """The per-persona instruction.

    background_items=None omits the background block (single-context runs give the
    background once, up front). restricted_items is used only in condition B.
    """
    parts = [f"<reader>\n{persona['adapted_text']}\n</reader>"]
    if background_items is not None:
        parts.append(f"<background>\n{background_text(background_items)}\n</background>")
    if goal:
        parts.append(f"<author_goal>\n{goal}\n</author_goal>")
    if restricted_items:
        listed = "\n".join(f"- [{b['id']}] {b['text']}" for b in restricted_items)
        parts.append("<not_known_to_this_reader>\nThis reader does not know the following. Do not use it, "
                     f"and don't let it shape this reader's reactions:\n{listed}\n</not_known_to_this_reader>")
    parts.append(f"Review the document as this reader ({persona['name']}).")
    return "\n\n".join(parts)


def single_context_intro(background_items):
    return ("You will review this document as several different readers, one at a time. Each reader is "
            "described in its own message.\n\n"
            f"<author_background>\n{background_text(background_items)}\n</author_background>")


# ---------- AI-reader check ----------

def ai_reader_batteries():
    """Parse ai-reader-prompts.md into {battery: [(number, prompt), ...]}."""
    text = read_reference("ai-reader-prompts.md")
    batteries = {}
    for match in re.finditer(r"^## (\w+) battery\n(.*?)(?=^## )", text, re.S | re.M):
        rows = re.findall(r"^\| (\d+) \| (.+?) \|$", match.group(2), re.M)
        batteries[match.group(1).lower()] = [(int(n), p.strip()) for n, p in rows]
    return batteries


def ai_reader_message(document, prompt):
    # No system prompt, persona, or framing: the document pasted, then the question.
    return f"{document}\n\n{prompt}"


def survival_system(analysis):
    text = read_reference("ai-reader-prompts.md")
    section = re.search(r"^## Survival check\n(.*?)(?=^## |\Z)", text, re.S | re.M).group(1).strip()
    return ("You check whether a legal document's key points survive when a recipient asks a general AI "
            "assistant about it. Return JSON matching the schema.\n\n"
            f"{section}\n\n<author_goal>\n{analysis['goal']['text']}\n</author_goal>\n"
            f"<ask>\n{analysis.get('ask') or 'Not stated'}\n</ask>\n"
            f"<deadline>\n{analysis.get('deadline') or 'None stated'}\n</deadline>")


def survival_user(document, answers):
    listing = "\n\n".join(f'<answer prompt_id="{a["prompt_id"]}" prompt="{a["prompt"]}">\n{a["answer"]}\n</answer>'
                          for a in answers)
    return f"<document>\n{document}\n</document>\n\n<ai_answers>\n{listing}\n</ai_answers>"


# ---------- Synthesis ----------

SYNTHESIS_SYSTEM = """You are the synthesis pass for fresh-eyes-review. Follow the rubric below and return JSON matching the schema.

Division of labor in this environment: you screen, merge, and classify findings and write the tradeoffs, what's working, AI-reader highlights, and next steps. Scripts then score and rank your issues, pick the priority actions, and compute run quality. So:
- Return every issue that survives screening, in any order. Don't rank them.
- Reference persona findings by their refs (e.g. "opposing-counsel/2"). Use persona ids for "reader".
- Turn each attention gap you are given into an issue with category "attention_gap" if the section holds something that matters; otherwise skip it.
- Survival-check "no" and "partly" results become issues with category "survival_failure".
- issue_index in revision prompts is the 0-based position of the issue in your "issues" array. Write one revision prompt per issue that is likely to be a priority (high severity, or raised by several readers).
- Revision prompts must work when pasted into an AI assistant with the document: quote the passage, name the reader and the problem, and ask for two or three options, not a finished rewrite.

{rubric}"""


def synthesis_system():
    return SYNTHESIS_SYSTEM.format(rubric=read_reference("synthesis-rubric.md"))


def synthesis_user(results, attention_gaps, review_gaps):
    personas = [{"id": p["id"], "name": p["name"], "tier": p["tier"], "role": p["role"],
                 "background_ids": p["background_ids"]} for p in results["personas"]]
    reviews = []
    for review in results["persona_reviews"]:
        out = dict(review["output"])
        out["findings"] = [dict(f, ref=f"{review['persona_id']}/{i}")
                           for i, f in enumerate(review["output"]["findings"], start=1)]
        reviews.append({"persona_id": review["persona_id"], "review": out})
    ai = results.get("ai_reader")
    payload = {
        "analysis": results["analysis"],
        "assumptions": results["assumptions"],
        "background": results["inputs"]["background"],
        "personas": personas,
        "persona_reviews": reviews,
        "attention_gaps": attention_gaps,
        "review_gaps": review_gaps,
        "ai_reader": None if ai is None else {
            "recipient": ai["recipient"],
            "answers": ai["answers"],
            "survival_check": ai["survival_check"],
        },
    }
    return (f"<document>\n{results['document']['text']}\n</document>\n\n"
            f"<run>\n{json.dumps(payload, indent=1, ensure_ascii=False)}\n</run>")
