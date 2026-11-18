import unittest
from pathlib import Path
from unittest.mock import MagicMock

from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from jarvis.server.app import create_app
from jarvis.server.origins import is_allowed_host, is_allowed_origin


class IsAllowedOriginTests(unittest.TestCase):
    def test_loopback_origins_on_any_port_are_allowed(self):
        for origin in (
            "http://127.0.0.1:7341",
            "http://localhost:7341",
            "http://localhost:5173",
            "http://127.0.0.1:9000",
            "http://[::1]:7341",
            "https://localhost",
        ):
            with self.subTest(origin=origin):
                self.assertTrue(is_allowed_origin(origin))

    def test_requests_without_origin_are_allowed(self):
        self.assertTrue(is_allowed_origin(None))

    def test_foreign_and_lookalike_origins_are_rejected(self):
        for origin in (
            "https://evil.example",
            "http://localhost.evil.example",
            "http://127.0.0.1.evil.example:7341",
            "http://evil.example/http://localhost:7341",
            "null",
            "",
        ):
            with self.subTest(origin=origin):
                self.assertFalse(is_allowed_origin(origin))


class IsAllowedHostTests(unittest.TestCase):
    def test_loopback_hosts_are_allowed(self):
        for host in ("127.0.0.1:7341", "localhost:5173", "LOCALHOST", "[::1]:7341", "127.0.0.1"):
            with self.subTest(host=host):
                self.assertTrue(is_allowed_host(host))

    def test_other_hosts_are_rejected(self):
        for host in (None, "", "evil.example", "evil.example:7341", "localhost.evil.example", "192.168.1.10:7341"):
            with self.subTest(host=host):
                self.assertFalse(is_allowed_host(host))


class OriginGuardIntegrationTests(unittest.TestCase):
    def setUp(self):
        app = create_app(
            cfg=MagicMock(),
            orchestrator=MagicMock(),
            registry=MagicMock(),
            memory=MagicMock(),
            agents=MagicMock(),
            web_dist=Path("does-not-exist"),
        )
        self.app = app
        self.client = TestClient(app, base_url="http://127.0.0.1:7341")

    def test_http_request_from_foreign_origin_is_rejected(self):
        r = self.client.post("/api/does-not-matter", headers={"Origin": "https://evil.example"})
        self.assertEqual(r.status_code, 403)

    def test_http_request_from_loopback_origin_passes_the_guard(self):
        r = self.client.get("/", headers={"Origin": "http://127.0.0.1:7341"})
        self.assertNotEqual(r.status_code, 403)

    def test_dns_rebinding_request_is_rejected(self):
        # After DNS rebinding the page is same-origin with the API: no Origin header, foreign Host.
        rebinding = TestClient(self.app, base_url="http://evil.example:7341")
        self.assertEqual(rebinding.get("/api/persona").status_code, 403)

    def test_websocket_with_foreign_host_is_closed(self):
        rebinding = TestClient(self.app, base_url="http://evil.example:7341")
        with self.assertRaises(WebSocketDisconnect) as ctx:
            with rebinding.websocket_connect("/ws") as ws:
                ws.receive_text()
        self.assertEqual(ctx.exception.code, 1008)

    def test_cors_allows_loopback_on_custom_port(self):
        r = self.client.options(
            "/api/tts",
            headers={"Origin": "http://localhost:9000", "Access-Control-Request-Method": "POST"},
        )
        self.assertEqual(r.headers.get("access-control-allow-origin"), "http://localhost:9000")

    def test_websocket_from_foreign_origin_is_closed_with_policy_violation(self):
        with self.assertRaises(WebSocketDisconnect) as ctx:
            with self.client.websocket_connect("/ws", headers={"Origin": "https://evil.example"}) as ws:
                ws.receive_text()
        self.assertEqual(ctx.exception.code, 1008)


if __name__ == "__main__":
    unittest.main()
