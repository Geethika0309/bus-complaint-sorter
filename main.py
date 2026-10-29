"""Bus Complaint Sorter: classify complaints, validate responses, and write reports."""
import csv
import json
import os
import re
import time
from collections import Counter
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent
CATEGORIES = {"delay", "crowding", "driver", "vehicle", "route_request", "other"}
RESULT_FIELDS = ["id", "category", "urgent", "route", "summary"]
URGENT_FIELDS = ["id", "date", "route", "area", "complaint", "summary"]


def load_complaints(path=BASE_DIR / "complaints.csv"):
    """Read complaint rows from CSV. Return an empty list if the file cannot be read."""
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))
        return [row for row in rows if row.get("id") and row.get("complaint") is not None]
    except (OSError, csv.Error) as error:
        print(f"Could not load complaints: {error}")
        return []


def load_routes(path=BASE_DIR / "routes.csv"):
    """Read route numbers and their areas from CSV."""
    routes = {}
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                try:
                    number = int(row["route"])
                    routes[number] = row["area"].strip()
                except (KeyError, ValueError, TypeError):
                    continue
    except (OSError, csv.Error) as error:
        print(f"Could not load routes: {error}")
    return routes


def extract_json(text):
    """Parse a JSON object, also tolerating a model response wrapped in code fences."""
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start == -1 or end < start:
        raise ValueError("No JSON object found")
    value = json.loads(cleaned[start:end + 1])
    if not isinstance(value, dict):
        raise ValueError("Response is not a JSON object")
    return value


def is_valid(result):
    """Check the shape and basic rules of one model response."""
    if not isinstance(result, dict):
        return False
    if set(result.keys()) != {"category", "urgent", "route", "summary"}:
        return False
    if result["category"] not in CATEGORIES:
        return False
    if not isinstance(result["urgent"], bool):
        return False
    route = result["route"]
    if route is not None and (isinstance(route, bool) or not isinstance(route, int)):
        return False
    summary = result["summary"]
    if not isinstance(summary, str) or not summary.strip():
        return False
    if len(summary.split()) > 12:
        return False
    return True


def check_route(result, complaint, routes):
    """Remove a route unless it is known and explicitly written in the complaint."""
    route = result.get("route")
    if route is None:
        return None
    if route not in routes:
        return None
    # Accept explicit forms such as "route 4", "bus 4", or "route number 4".
    number_is_written = re.search(
        rf"\b(?:route(?:\s+number)?|bus)\s*#?\s*{route}\b",
        complaint,
        flags=re.IGNORECASE,
    )
    return route if number_is_written else None


def call_gemini(complaint, system_prompt):
    """Make one Gemini API call. Raises an exception if setup/API fails."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured")
    from google import genai
    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    response = client.models.generate_content(
        model=model,
        contents=f"{system_prompt}\n\nComplaint to classify:\n{complaint}",
        config={"response_mime_type": "application/json", "temperature": 0},
    )
    if not getattr(response, "text", None):
        raise ValueError("The model returned an empty response")
    return extract_json(response.text)


def classify(complaint, routes, system_prompt, model_function=None, retries=1):
    """Classify one complaint; retry once on invalid output/API errors, then safely fall back."""
    model_function = model_function or call_gemini
    last_error = "Unknown classification error"
    for attempt in range(retries + 1):
        try:
            result = model_function(complaint, system_prompt)
            if isinstance(result, str):
                result = extract_json(result)
            if not is_valid(result):
                raise ValueError("Model response did not pass validation")
            result = dict(result)
            result["route"] = check_route(result, complaint, routes)
            result["summary"] = result["summary"].strip()
            return result
        except Exception as error:
            last_error = str(error)
            if attempt < retries:
                time.sleep(0.1)
    # Fallback does not guess the category, urgency, route, or summary.
    return {
        "category": "needs_manual_review",
        "urgent": False,
        "route": None,
        "summary": f"Manual review required ({last_error[:70]})",
    }


def write_reports(complaints, routes, classified_rows, output_dir=BASE_DIR):
    """Write results.csv, urgent.csv, and summary.txt."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    complaint_by_id = {row["id"]: row for row in complaints}

    with open(output_dir / "results.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(classified_rows)

    urgent_rows = []
    for result in classified_rows:
        if result["urgent"] is True:
            original = complaint_by_id.get(result["id"], {})
            route = result["route"]
            urgent_rows.append({
                "id": result["id"],
                "date": original.get("date", ""),
                "route": route if route is not None else "",
                "area": routes.get(route, "") if route is not None else "",
                "complaint": original.get("complaint", ""),
                "summary": result["summary"],
            })
    with open(output_dir / "urgent.csv", "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=URGENT_FIELDS)
        writer.writeheader()
        writer.writerows(urgent_rows)

    category_counts = Counter(row["category"] for row in classified_rows)
    route_counts = Counter(row["route"] for row in classified_rows if row["route"] is not None)
    lines = ["BUS COMPLAINT SORTER — SUMMARY", "=" * 32, "",
             "CATEGORY COUNTS"]
    for category, count in sorted(category_counts.items()):
        lines.append(f"{category}: {count}")
    lines.extend(["", "ROUTE COUNTS (most complaints first)"])
    if route_counts:
        for route, count in sorted(route_counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"Route {route} ({routes.get(route, 'Unknown area')}): {count}")
    else:
        lines.append("No validated route numbers were found.")
    lines.extend(["", f"SAFETY LIST ({len(urgent_rows)} items)"])
    if urgent_rows:
        for item in urgent_rows:
            lines.append(
                f"- {item['id']} | Route {item['route'] or 'unknown'} | "
                f"{item['summary']} | Original: {item['complaint']}"
            )
    else:
        lines.append("No items were marked urgent.")
    lines.extend(["", "Human checkpoint: the transport officer must review safety items and manual-review cases.",
                  "This tool is advisory only; it does not contact drivers or decide fault."])
    (output_dir / "summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    complaints = load_complaints()
    routes = load_routes()
    prompt_path = BASE_DIR / "system_prompt.txt"
    try:
        system_prompt = prompt_path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"Could not read system prompt: {error}")
        system_prompt = "Return JSON with category, urgent, route, and summary."
    if not complaints:
        print("No complaints were loaded. Check complaints.csv.")
        # Still create empty output reports so the program finishes predictably.
        write_reports([], routes, [])
        return
    print(f"Loaded {len(complaints)} complaints and {len(routes)} routes.")
    results = []
    for index, complaint_row in enumerate(complaints, start=1):
        print(f"[{index}/{len(complaints)}] Classifying {complaint_row['id']}...")
        result = classify(complaint_row["complaint"], routes, system_prompt)
        results.append({"id": complaint_row["id"], **result})
    write_reports(complaints, routes, results)
    manual_count = sum(row["category"] == "needs_manual_review" for row in results)
    urgent_count = sum(row["urgent"] is True for row in results)
    print("Finished. Created results.csv, urgent.csv, and summary.txt.")
    print(f"Urgent items: {urgent_count}; manual-review items: {manual_count}.")
    if manual_count:
        print("Some items need manual review. This can happen if the API key is missing or the API fails.")


if __name__ == "__main__":
    main()
