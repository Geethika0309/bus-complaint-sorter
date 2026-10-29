import tempfile
import unittest
from pathlib import Path
from main import check_route, classify, is_valid, write_reports


class BusComplaintSorterTests(unittest.TestCase):
    def setUp(self):
        self.routes = {1: "Tambaram", 4: "Medavakkam", 7: "Chromepet"}

    def test_valid_response(self):
        self.assertTrue(is_valid({
            "category": "delay", "urgent": False, "route": 4,
            "summary": "Bus arrived late"
        }))

    def test_invalid_category(self):
        self.assertFalse(is_valid({
            "category": "late", "urgent": False, "route": 4,
            "summary": "Bus arrived late"
        }))

    def test_route_must_be_in_complaint(self):
        self.assertIsNone(check_route(
            {"route": 7}, "The bus arrived late", self.routes
        ))

    def test_route_must_be_known(self):
        self.assertIsNone(check_route(
            {"route": 99}, "Bus 99 was late", self.routes
        ))

    def test_retry_then_fallback(self):
        calls = {"count": 0}
        def bad_model(complaint, prompt):
            calls["count"] += 1
            return {"wrong": "shape"}
        result = classify("Bus was late", self.routes, "", model_function=bad_model)
        self.assertEqual(calls["count"], 2)
        self.assertEqual(result["category"], "needs_manual_review")
        self.assertIsNone(result["route"])

    def test_route_accepted_if_written_and_known(self):
        self.assertEqual(check_route(
            {"route": 4}, "Route 4 was late", self.routes
        ), 4)

    def test_reports_are_created(self):
        complaints = [{"id": "C1", "date": "2026-10-01", "complaint": "Route 4 was late"}]
        results = [{"id": "C1", "category": "delay", "urgent": False,
                    "route": 4, "summary": "Route 4 was late"}]
        with tempfile.TemporaryDirectory() as directory:
            write_reports(complaints, self.routes, results, directory)
            self.assertTrue((Path(directory) / "results.csv").exists())
            self.assertTrue((Path(directory) / "urgent.csv").exists())
            self.assertTrue((Path(directory) / "summary.txt").exists())


if __name__ == "__main__":
    unittest.main()
