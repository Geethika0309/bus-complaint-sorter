# Bus Complaint Sorter

A beginner-friendly, console-based Python project that classifies college bus complaints with an LLM, checks the model's response, prioritizes safety risks, and creates three reports.

## What it does

1. Reads `complaints.csv` and `routes.csv`.
2. Sends each complaint to Google Gemini using the system prompt in `system_prompt.txt`.
3. Requires JSON with `category`, `urgent`, `route`, and `summary`.
4. Validates each reply. If it is invalid, it retries once. If the second reply is invalid or the API is unavailable, the complaint is marked `needs_manual_review` rather than stopping the whole run.
5. Keeps a route only if it exists in `routes.csv` **and** its number appears in the original complaint. The program never trusts a guessed route.
6. Writes `results.csv`, `urgent.csv`, and `summary.txt`.

Safety complaints are flagged for the transport officer. The tool does not contact drivers, decide fault, or take action by itself.

## Requirements

- Python 3.10 or newer
- A Google Gemini API key (for live AI classification)
- Internet connection for live AI calls

## Setup on Windows

1. Extract the ZIP file.
2. Open the extracted `bus_complaint_sorter` folder.
3. Open Command Prompt in this folder.
4. Create a virtual environment (recommended):

   ```powershell
   py -m venv .venv
   .venv\Scripts\activate
   ```

5. Install packages:

   ```powershell
   py -m pip install -r requirements.txt
   ```

6. Copy `.env.example` to `.env` and paste your key after `GEMINI_API_KEY=`. Do not share `.env` or upload it to GitHub.
7. Run:

   ```powershell
   py main.py
   ```

The reports are created in the project folder. If no API key is set or the API fails, the program still completes and marks affected complaints for manual review. This is intentional so one API failure does not stop the batch.

## Run tests without an API key

```powershell
py -m unittest discover -s tests -v
```

Tests use mocked model responses and do not spend API credits.

## Files in this project

- `main.py` — main program and report generation
- `complaints.csv` — 24 sample student complaints, including safety and vague cases
- `routes.csv` — 12 routes and their areas
- `system_prompt.txt` — prompt using Authority, Exemplar, Constraint, Rubric, and Metadata
- `specification.md` — one-page project specification
- `tests/eval_harness.py` — five evaluation examples
- `tests/test_main.py` — automated validation and route-check tests
- `docs/red_team_results.md` — three adversarial test cases and observations
- `docs/judgment_framework.md` — human-checkpoint and accountability table
- `docs/cost_latency_note.md` — call-count, latency, and cost estimate
- `docs/ai_decision_journal.md` — AI use and verification journal
- `docs/reflection.md` — approximately 400-word reflection
- `.env.example` — safe environment-variable template
- `.gitignore` — excludes secrets and generated/local folders

## Output files

- `results.csv`: one row per complaint, including the original ID and model classification
- `urgent.csv`: safety complaints for the transport officer
- `summary.txt`: category counts, route counts (highest first), and safety list

`needs_manual_review` is a deliberate fallback category for technical/format failures. It is not one of the six normal complaint categories.

## GitHub upload checklist

Before uploading:
- Keep `.env` private. Only `.env.example` belongs in GitHub.
- Do not upload `.venv/`, `__pycache__/`, or API keys.
- Upload the extracted project folder contents, then commit with a clear message such as `Add Bus Complaint Sorter project`.
- Follow the supplied GitHub website upload manual.

## Important limitation

LLM output can be wrong. Review the generated reports, especially urgent complaints and `needs_manual_review`, before using them. The transport officer remains responsible for decisions.
