"""Read-only GitHub PR metadata triage via Jev. No review comments or merges."""
import json
import os
import re
from urllib import request

from jev_client import ask_jev


def fetch_pr(repository, number, github_token, *, opener=None):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Invalid GITHUB_REPOSITORY")
    if type(number) is not int or number <= 0:
        raise ValueError("PR_NUMBER must be a positive integer")
    if not github_token:
        raise ValueError("GITHUB_TOKEN is required")
    url = f"https://api.github.com/repos/{repository}/pulls/{number}"
    req = request.Request(url, method="GET", headers={
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    })
    with (opener or request.urlopen)(req, timeout=25) as response:
        data = json.loads(response.read().decode("utf-8"))
    return {"title": data["title"], "body": data.get("body") or ""}


def triage_pull_request(title, body):
    """Only supplied title and description are sent to the chosen model provider."""
    response = ask_jev({"title": title[:500], "description": body[:10000]}, {
        "area": {
            "type": "choice",
            "instructions": "Based on PR title and description, which part is most directly changed?",
            "criteria": {
                "backend": "Backend, Python, HTTP services, or data processing",
                "frontend": "Web, frontend, mobile interface, accessibility or UI",
                "ci": "Build system, tests, GitHub Actions or developer tooling",
                "docs": "Documentation only",
                "mixed": "Multiple areas or insufficient information",
            },
        },
        "priority": {
            "type": "score",
            "instructions": "How urgently should a human reviewer inspect this proposed change, based only on its description?",
            "criteria": [
                "Routine change with no stated high-impact behavior",
                "Moderate change that needs normal review",
                "Potentially high-impact change that warrants focused review",
            ],
        },
        "security_change": {
            "type": "noul",
            "instructions": "Does the PR description explicitly mention changes to authentication, authorization, permissions, or secrets?",
        },
    })
    answers = response["answers"]
    area = answers["area"]["choice"]
    if area not in ("backend", "frontend", "ci", "docs", "mixed"):
        raise ValueError("Invalid Jev area classification")
    score = float(answers["priority"]["score"])
    probability = float(answers["security_change"]["noul"])
    if not (0 <= score <= 2 and 0 <= probability <= 1):
        raise ValueError("Invalid Jev scores")
    return {
        "model": response.get("model"),
        "area": area,
        "area_confidence": answers["area"].get("confidence"),
        "review_priority_score_0_to_2": score,
        "priority_confidence": answers["priority"].get("confidence"),
        "security_change_probability": probability,
        "informational_only": True,
        "evidence": "PR title and description only; code diff and tests NOT reviewed",
    }


def main():
    repository = os.environ["GITHUB_REPOSITORY"]
    number = int(os.environ["PR_NUMBER"])
    token = os.environ["GITHUB_TOKEN"]
    pr = fetch_pr(repository, number, token)
    assessment = triage_pull_request(pr["title"], pr["body"])
    output = json.dumps(assessment, indent=2)
    print(output)
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_file:
        with open(summary_file, "a", encoding="utf-8") as handle:
            handle.write(f"## Jev PR #{number} metadata assessment\n\n")
            handle.write("Read-only. No diff was analyzed. No PR changes were made.\n\n")
            handle.write("```json\n" + output + "\n```\n")


if __name__ == "__main__":
    main()
