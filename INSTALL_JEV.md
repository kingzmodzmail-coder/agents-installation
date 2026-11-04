# Jev 1.14.0 for GitHub and local agents

This integrates TypeSafe's **System One decisions model**, not a text-generating code assistant. It does not replace GitHub Copilot or Codex. Automated PR assessments are informational and read-only.

## Endpoints and current availability

- **Official TypeSafe** (default): `https://api.typesafe.ai/v1/systemone`, model `jev-1.14.0`, listed in the TypeSafe models documentation.
- **DefAPI** (optional): `https://api.defapi.org/api/v1/decisions`, model `typesafe/jev-1.14.0`. The DefAPI listing currently says **Coming Soon**, so live calls through DefAPI may not work.

## Local setup

1. Run `./setup.sh` (Python 3.10+ and Bash).
2. In the generated `.env`, replace `TYPESAFE_API_KEY` with your actual key from https://console.typesafe.ai. Never commit `.env`.
3. Export variables from the file: `set -a; source .env; set +a`.
4. Try `python -m examples.jev_spam_classifier "Buy this product now!"`.
5. Run offline tests: `python -m unittest discover -s tests -v`.

For the DefAPI mode, explicitly select `JEV_PROVIDER=defapi` and provide `DEFAPI_API_KEY`, but only after that model is available.

## GitHub Actions

1. Under **Settings → Secrets and variables → Actions**, add a repository secret named `TYPESAFE_API_KEY`. Never share the key in a PR description or issue.
2. When the workflow is available on the default branch, open **Actions → Jev API integration → Run workflow**, enter an existing PR number and start the workflow. During PR review, the tests also run without needing a key.
3. Manual triage fetches **only the PR title and description** and sends that metadata to TypeSafe. Its output is a GitHub Actions job summary and log. No diff is read, no labels/comments are added, no code executes from the PR, no merge or deploy occurs.
4. Do not use this result as a security audit or a release gate: the diff and runtime are not inspected.

**Privacy:** The title and description are shared with the selected external service when you run triage. Do not run manual triage against confidential PR descriptions without permission.

## Troubleshooting

- `Set TYPESAFE_API_KEY`: secret missing or local key not exported.
- HTTP 401: credentials missing, invalid, or not authorized.
- HTTP 400, model unavailable: check model access. DefAPI currently does not expose Jev 1.14.0 for calls.
- HTTP 429: rate-limited; retry later.
- Invalid responses fail closed; the integration never fabricates success.

References: https://docs.typesafe.ai/models ; https://docs.typesafe.ai/api/system-one ; https://defapi.org/model-group/typesafe/jev?model=jev-1.14.0
