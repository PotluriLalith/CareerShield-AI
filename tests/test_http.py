import json
import os
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import HTTPError
from unittest.mock import patch

from app import Handler


class CareerShieldHTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_health_endpoint_and_security_headers(self):
        with urlopen(f"http://127.0.0.1:{self.port}/health", timeout=3) as response:
            payload = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertEqual(payload["status"], "ok")
            self.assertIn("Content-Security-Policy", response.headers)
            self.assertEqual(response.headers["X-Frame-Options"], "DENY")

    def test_ready_endpoint_reports_configuration_without_secret(self):
        with patch.dict(os.environ, {"TAVILY_API_KEY": "do-not-return-this"}):
            with urlopen(f"http://127.0.0.1:{self.port}/ready", timeout=3) as response:
                body = response.read().decode()
                payload = json.loads(body)
                self.assertEqual(response.status, 200)
                self.assertEqual(payload["status"], "ready")
                self.assertEqual(payload["live_search"], "configured")
                self.assertNotIn("do-not-return-this", body)

    def test_browser_ui_uses_text_nodes_for_report_data(self):
        with urlopen(f"http://127.0.0.1:{self.port}/", timeout=3) as response:
            page = response.read().decode("utf-8")
            self.assertEqual(response.status, 200)
            self.assertIn("textContent", page)
            self.assertNotIn("innerHTML", page)
            self.assertIn("Prompt injection", page)

    def test_json_api_returns_versioned_report(self):
        body = json.dumps({
            "company_name": "Example Co",
            "recruiter_email": "hiring@gmail.com",
            "job_url": "https://example.com/careers",
            "job_text": "Pay a registration fee to secure your offer immediately."
        }).encode()
        request = Request(f"http://127.0.0.1:{self.port}/api/v1/analyze", data=body, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(request, timeout=3) as response:
            payload = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertEqual(payload["agent_name"], "CareerShield AI")
            self.assertEqual(payload["schema_version"], "2.0")
            self.assertTrue(payload["report_id"].startswith("csr_"))
            self.assertIn("generated_at", payload)
            self.assertIn("payment_request", {s["code"] for s in payload["signals"]})

    def test_legacy_form_endpoint_remains_compatible(self):
        body = urlencode({
            "company_name": "Example Co",
            "recruiter_email": "recruiter@gmail.com",
            "job_url": "https://example.com/careers",
            "job_text": "Pay a registration fee to secure the job immediately."
        }).encode()
        request = Request(f"http://127.0.0.1:{self.port}/analyze", data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
        with urlopen(request, timeout=3) as response:
            payload = json.loads(response.read())
            self.assertEqual(response.status, 200)
            self.assertEqual(payload["agent_name"], "CareerShield AI")
            self.assertIn("payment_request", {s["code"] for s in payload["signals"]})

    def test_json_api_rejects_wrong_field_types(self):
        body = json.dumps({"company_name": ["unexpected", "list"]}).encode()
        request = Request(f"http://127.0.0.1:{self.port}/api/v1/analyze", data=body, headers={"Content-Type": "application/json"}, method="POST")
        with self.assertRaises(HTTPError) as caught:
            urlopen(request, timeout=3)
        self.assertEqual(caught.exception.code, 400)
        self.assertIn("must be a string", caught.exception.read().decode())

    def test_json_api_rejects_oversized_field(self):
        body = json.dumps({"job_text": "x" * 20_001}).encode()
        request = Request(f"http://127.0.0.1:{self.port}/api/v1/analyze", data=body, headers={"Content-Type": "application/json"}, method="POST")
        with self.assertRaises(HTTPError) as caught:
            urlopen(request, timeout=3)
        self.assertEqual(caught.exception.code, 413)

    def test_json_api_rejects_malformed_json_and_unsupported_content_type(self):
        request = Request(f"http://127.0.0.1:{self.port}/api/v1/analyze", data=b"{broken", headers={"Content-Type": "application/json"}, method="POST")
        with self.assertRaises(HTTPError) as caught:
            urlopen(request, timeout=3)
        self.assertEqual(caught.exception.code, 400)
        request = Request(f"http://127.0.0.1:{self.port}/api/v1/analyze", data=b"x", headers={"Content-Type": "text/plain"}, method="POST")
        with self.assertRaises(HTTPError) as caught:
            urlopen(request, timeout=3)
        self.assertEqual(caught.exception.code, 415)

    def test_internal_error_does_not_echo_user_input_or_traceback(self):
        body = json.dumps({"job_text": "private message content"}).encode()
        request = Request(f"http://127.0.0.1:{self.port}/api/v1/analyze", data=body, headers={"Content-Type": "application/json"}, method="POST")
        with patch("app.investigate_offer", side_effect=RuntimeError("private message content traceback")):
            with self.assertRaises(HTTPError) as caught:
                urlopen(request, timeout=3)
        self.assertEqual(caught.exception.code, 500)
        response = caught.exception.read().decode()
        self.assertIn("internal analysis error", response)
        self.assertNotIn("private message content", response)


if __name__ == "__main__":
    unittest.main(verbosity=2)
