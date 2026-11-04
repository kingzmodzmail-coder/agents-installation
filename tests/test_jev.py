import json
import os
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from jev_client import JevError, ask_jev
from examples.jev_spam_classifier import classify_spam
from scripts.jev_github_pr import triage_pull_request, fetch_pr


class FakeResponse:
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def read(self):
        return json.dumps(self.value).encode()


class JevTests(unittest.TestCase):
    def test_key_required(self):
        with patch.dict(os.environ, {"JEV_PROVIDER": "typesafe", "TYPESAFE_API_KEY": ""}):
            with self.assertRaisesRegex(JevError, "TYPESAFE_API_KEY"):
                ask_jev("hello", {"ok": {"type": "noul", "instructions": "Yes?"}})

    def test_typesafe_request_has_pinned_model(self):
        sent = {}

        def opener(req, timeout):
            sent.update({"url": req.full_url, "body": json.loads(req.data),
                         "auth": req.get_header("Authorization"), "timeout": timeout})
            return FakeResponse({"model": "jev-1.14.0", "answers": {"ok": {"type": "noul", "noul": 0.6}}})

        result = ask_jev("hello", {"ok": {"type": "noul", "instructions": "Yes?"}},
                         provider="typesafe", api_key="test-token", opener=opener)
        self.assertEqual(sent["url"], "https://api.typesafe.ai/v1/systemone")
        self.assertEqual(sent["body"]["model"], "jev-1.14.0")
        self.assertEqual(sent["auth"], "Bearer test-token")
        self.assertEqual(result["answers"]["ok"]["noul"], 0.6)

    def test_defapi_request_uses_correct_model(self):
        def opener(req, timeout):
            self.assertEqual(req.full_url, "https://api.defapi.org/api/v1/decisions")
            self.assertEqual(json.loads(req.data)["model"], "typesafe/jev-1.14.0")
            return FakeResponse({"answers": {"ok": {"type": "noul", "noul": 0.3}}})

        ask_jev("hello", {"ok": {"type": "noul", "instructions": "Yes?"}},
                provider="defapi", api_key="test-token", opener=opener)

    def test_does_not_log_secret_on_http_failure(self):
        def opener(req, timeout):
            raise HTTPError(req.full_url, 401, "Invalid key", {}, None)

        with self.assertRaises(JevError) as context:
            ask_jev("x", {"ok": {"type": "noul", "instructions": "Yes?"}},
                    provider="typesafe", api_key="VERY_PRIVATE", opener=opener)
        self.assertNotIn("VERY_PRIVATE", str(context.exception))
        self.assertIn("401", str(context.exception))

    def test_rejects_missing_answer(self):
        with self.assertRaisesRegex(JevError, "missing"):
            ask_jev("x", {"ok": {"type": "noul", "instructions": "Yes?"}},
                    provider="typesafe", api_key="x",
                    opener=lambda req, timeout: FakeResponse({"answers": {}}))

    @patch("examples.jev_spam_classifier.ask_jev")
    def test_spam_uncertain_requires_review(self, mock_ask):
        mock_ask.return_value = {"model": "jev-1.14.0", "answers": {"spam": {"type": "noul", "noul": 0.51}}}
        self.assertEqual(classify_spam("unclear text")["decision"], "review")

    @patch("scripts.jev_github_pr.ask_jev")
    def test_pr_review_never_makes_policy_decision(self, mock_ask):
        mock_ask.return_value = {"model": "jev-1.14.0", "answers": {
            "area": {"type": "choice", "choice": "backend", "confidence": 0.8},
            "priority": {"type": "score", "score": 1.2, "confidence": 0.7},
            "security_change": {"type": "noul", "noul": 0.63}}}
        result = triage_pull_request("Fix bug", "Only PR metadata")
        self.assertEqual(result["area"], "backend")
        self.assertTrue(result["informational_only"])
        self.assertEqual(result["security_change_probability"], 0.63)

    def test_github_fetch_read_only(self):
        def opener(req, timeout):
            self.assertEqual(req.get_method(), "GET")
            self.assertEqual(req.full_url, "https://api.github.com/repos/foo/bar/pulls/12")
            return FakeResponse({"title": "Fix", "body": "Description"})

        self.assertEqual(fetch_pr("foo/bar", 12, "token", opener=opener)["title"], "Fix")


if __name__ == "__main__":
    unittest.main()
