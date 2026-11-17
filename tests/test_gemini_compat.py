import unittest
from types import SimpleNamespace

from jarvis.core.brain import ToolCall, _add_penalties

GEMINI = "https://generativelanguage.googleapis.com/v1beta/openai"


def model(endpoint, frequency_penalty=0.3, presence_penalty=0.2):
    return SimpleNamespace(
        endpoint=endpoint, frequency_penalty=frequency_penalty, presence_penalty=presence_penalty
    )


class PenaltyTests(unittest.TestCase):
    def test_penalties_are_omitted_for_gemini(self):
        payload = {}
        _add_penalties(payload, model(GEMINI))
        self.assertNotIn("frequency_penalty", payload)
        self.assertNotIn("presence_penalty", payload)

    def test_penalties_are_kept_for_other_providers(self):
        payload = {}
        _add_penalties(payload, model("http://localhost:11434/v1"))
        self.assertEqual(payload, {"frequency_penalty": 0.3, "presence_penalty": 0.2})

    def test_zero_penalties_are_not_sent(self):
        payload = {}
        _add_penalties(payload, model("http://localhost:11434/v1", 0, 0))
        self.assertEqual(payload, {})

    def test_missing_endpoint_does_not_crash(self):
        payload = {}
        _add_penalties(payload, model(None))
        self.assertIn("frequency_penalty", payload)


class ToolCallExtraTests(unittest.TestCase):
    def test_extra_defaults_to_none_for_existing_callers(self):
        self.assertIsNone(ToolCall("web_search", {"q": "x"}).extra)

    def test_extra_keeps_thought_signature(self):
        extra = {"google": {"thought_signature": "abc"}}
        self.assertEqual(ToolCall("web_search", {}, extra=extra).extra, extra)


if __name__ == "__main__":
    unittest.main()
