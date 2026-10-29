"""Five expected-answer checks for the classifier.

Run with: py tests/eval_harness.py
This harness uses representative expected labels and does not call the live API.
It checks deterministic validator/route rules, not the model's semantic accuracy.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from main import check_route, is_valid

cases = [
    {"id": "E1", "complaint": "Route 4 bus came 25 minutes late",
     "expected": {"category": "delay", "urgent": False, "route": 4}},
    {"id": "E2", "complaint": "Bus 7 driver used a phone while driving",
     "expected": {"category": "driver", "urgent": True, "route": 7}},
    {"id": "E3", "complaint": "Bus 2 is crowded and students are on the footboard",
     "expected": {"category": "crowding", "urgent": True, "route": 2}},
    {"id": "E4", "complaint": "Please add a stop near the railway station",
     "expected": {"category": "route_request", "urgent": False, "route": None}},
    {"id": "E5", "complaint": "ok",
     "expected": {"category": "other", "urgent": False, "route": None}},
]
routes = {1: "Tambaram", 2: "Velachery", 4: "Medavakkam", 7: "Chromepet"}
# Fixed reference outputs are used so this file can be run without an API key.
reference_outputs = [
    {"category": "delay", "urgent": False, "route": 4, "summary": "Route 4 bus arrived late"},
    {"category": "driver", "urgent": True, "route": 7, "summary": "Driver used a phone while driving"},
    {"category": "crowding", "urgent": True, "route": 2, "summary": "Students are standing on the footboard"},
    {"category": "route_request", "urgent": False, "route": None, "summary": "Request for a new bus stop"},
    {"category": "other", "urgent": False, "route": None, "summary": "Complaint is too vague to classify"},
]
correct = 0
for case, output in zip(cases, reference_outputs):
    route = check_route(output, case["complaint"], routes)
    shape_ok = is_valid(output)
    matched = (shape_ok and output["category"] == case["expected"]["category"]
               and output["urgent"] == case["expected"]["urgent"]
               and route == case["expected"]["route"])
    correct += int(matched)
    print(f"{case['id']}: {'PASS' if matched else 'FAIL'}; expected={case['expected']}; got="
          f"category={output.get('category')}, urgent={output.get('urgent')}, route={route}")
print(f"Score: {correct}/{len(cases)}")
