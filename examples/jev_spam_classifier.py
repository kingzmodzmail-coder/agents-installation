"""Real Jev spam classification demo; never deletes or hides comments."""
import json
from jev_client import ask_jev


def classify_spam(comment):
    if not isinstance(comment, str) or not comment.strip():
        raise ValueError("comment must contain text")
    response = ask_jev(comment, {"spam": {
        "type": "noul",
        "instructions": "Is this comment primarily unsolicited advertising, deceptive promotion, or repetitive spam?",
        "criteria": {
            "true": "Unsolicited advertising, repetitive promotion or deceptive solicitation",
            "false": "A legitimate on-topic comment, including ordinary disagreement",
        },
    }})
    answer = response["answers"]["spam"]
    if answer.get("type") != "noul" or type(answer.get("noul")) not in (float, int):
        raise ValueError("Malformed Jev noul answer")
    probability = float(answer["noul"])
    if not 0 <= probability <= 1:
        raise ValueError("Spam probability out of range")
    decision = "spam" if probability >= 0.8 else "not_spam" if probability <= 0.2 else "review"
    return {"decision": decision, "spam_probability": probability, "model": response.get("model")}


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python -m examples.jev_spam_classifier "comment text"')
    print(json.dumps(classify_spam(" ".join(sys.argv[1:])), indent=2))
