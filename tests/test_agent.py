import unittest
from careershield.agent import investigate_offer


class CareerShieldAgentTests(unittest.TestCase):
    def test_payment_and_urgency_raise_risk(self):
        result = investigate_offer({
            "company_name": "Example Technologies",
            "recruiter_email": "example.hiring@gmail.com",
            "job_url": "http://bit.ly/example-job",
            "job_text": "Guaranteed job selection without interview. Pay a registration fee immediately to secure the offer. Act now; limited slots.",
        })
        codes = {signal["code"] for signal in result["signals"]}
        self.assertIn("payment_request", codes)
        self.assertIn("urgency", codes)
        self.assertIn("instant_offer", codes)
        self.assertIn("shortened_url", codes)
        self.assertEqual(result["risk_level"], "High")
        self.assertGreaterEqual(result["score"], 50)

    def test_low_signal_example_does_not_claim_verified(self):
        result = investigate_offer({
            "company_name": "Northwind Example",
            "recruiter_email": "talent@northwind.example",
            "job_url": "https://careers.northwind.example/jobs/123",
            "job_text": "Software engineering intern role. Responsibilities include testing APIs and writing Python code. Requirements include basic programming skills.",
        })
        self.assertEqual(result["risk_level"], "Low")
        self.assertTrue(any("never fetched" in x for x in result["limitations"]))
        self.assertIn("official website", " ".join(result["recommendations"]))

    def test_explicit_no_fee_statement_is_not_flagged_as_payment_request(self):
        result = investigate_offer({
            "company_name": "Northwind Example",
            "recruiter_email": "talent@northwind.example",
            "job_url": "https://careers.northwind.example/jobs/123",
            "job_text": "We never charge any registration fee. Responsibilities include testing APIs and writing Python code. Requirements include basic programming skills.",
        })
        codes = {signal["code"] for signal in result["signals"]}
        self.assertNotIn("payment_request", codes)

    def test_request_for_otp_is_a_high_severity_signal(self):
        result = investigate_offer({
            "company_name": "Example Technologies",
            "job_url": "https://example.com/careers",
            "job_text": "Send your OTP and password to confirm your job offer.",
        })
        codes = {signal["code"] for signal in result["signals"]}
        self.assertIn("credential_request", codes)

    def test_missing_information_is_explicit(self):
        result = investigate_offer({"company_name": "", "recruiter_email": "", "job_url": "", "job_text": ""})
        self.assertEqual(result["risk_level"], "Needs more information")
        self.assertIsNone(result["score"])
        self.assertEqual(result["assessment_status"], "incomplete")

    def test_domain_mismatch_is_a_signal_not_proof(self):
        result = investigate_offer({
            "company_name": "Contoso",
            "recruiter_email": "recruiter@contoso-careers.example",
            "job_url": "https://contoso.example/jobs",
            "job_text": "Software engineer role. Responsibilities include coding and testing. Requirements include Python experience.",
        })
        signals = {s["code"]: s for s in result["signals"]}
        self.assertIn("domain_mismatch", signals)
        self.assertIn("not proof of fraud", signals["domain_mismatch"]["evidence"])

    def test_invalid_email_and_url_are_handled(self):
        result = investigate_offer({
            "company_name": "Example",
            "recruiter_email": "not-an-email",
            "job_url": "https://",
            "job_text": "A role with responsibilities and requirements is available.",
        })
        codes = {s["code"] for s in result["signals"]}
        self.assertIn("invalid_email", codes)
        self.assertIn("unparseable_url", codes)


if __name__ == "__main__":
    unittest.main(verbosity=2)
