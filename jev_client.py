"""Minimal, dependency-free Jev Decisions API client. No simulated answers."""
import json
import os
from urllib import error, request


class JevError(RuntimeError):
    """A safe, non-secret error for an API or configuration failure."""


_TARGETS = {
    "typesafe": ("https://api.typesafe.ai/v1/systemone", "jev-1.14.0", "TYPESAFE_API_KEY"),
    "defapi": ("https://api.defapi.org/api/v1/decisions", "typesafe/jev-1.14.0", "DEFAPI_API_KEY"),
}


def ask_jev(state, questions, *, provider=None, api_key=None, opener=None):
    """Send structured questions; never silently fall back or fabricate an answer.

    Official TypeSafe is the default, because DefAPI currently lists 1.14.0
    as coming soon. Opt into DefAPI using JEV_PROVIDER=defapi.
    """
    provider = (provider or os.environ.get("JEV_PROVIDER") or "typesafe").lower()
    if provider not in _TARGETS:
        raise JevError("JEV_PROVIDER must be 'typesafe' or 'defapi'")
    url, model, key_variable = _TARGETS[provider]
    key = api_key if api_key is not None else os.environ.get(key_variable, "")
    if not key or key == "your_key_here":
        raise JevError(f"Set {key_variable} in your environment or GitHub Actions secrets")
    if not isinstance(state, (str, dict, list)) or not state:
        raise ValueError("state must be nonempty text, an object, or a list")
    if not isinstance(questions, dict) or not questions:
        raise ValueError("questions must be a nonempty mapping")
    body = json.dumps({"model": model, "state": state, "questions": questions}).encode("utf-8")
    if len(body) > 128 * 1024:
        raise ValueError("This metadata-only integration limits requests to 128 KiB")
    req = request.Request(url, data=body, method="POST", headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    try:
        with (opener or request.urlopen)(req, timeout=25) as resp:
            result = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise JevError(f"{provider} returned HTTP {exc.code}; check key, model availability and account access") from None
    except (error.URLError, TimeoutError) as exc:
        raise JevError(f"{provider} request failed due to network or timeout") from None
    except (UnicodeError, ValueError):
        raise JevError(f"{provider} returned invalid JSON") from None
    if not isinstance(result, dict) or not isinstance(result.get("answers"), dict):
        raise JevError(f"{provider} response missing answers")
    if set(questions) - set(result["answers"]):
        raise JevError(f"{provider} response missing one or more requested answers")
    return result
