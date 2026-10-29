# Judgment Framework

| Part | Cost of being wrong | Can it be verified without AI? | Who is accountable? | Human checkpoint |
|---|---|---|---|---|
| Category | A complaint may be routed to the wrong queue. | Partly: staff can read the original complaint and category rules. | Transport office for operational decisions; developer for software behaviour. | Review unclear and manual-review items. |
| Urgency | A missed safety risk could delay action; a false alarm uses staff time. | Staff can read the original complaint, but context may be needed. | Transport officer. | Review every item in `urgent.csv` promptly. |
| Route | Wrong route counts can mislead service planning. | Yes: compare the text with `routes.csv`. | Developer for validation logic; transport office for route follow-up. | Python only accepts a listed route explicitly mentioned in the complaint. |
| Summary | Important context may be omitted or wording may be misleading. | Yes: compare summary with original text. | Transport officer for interpretation. | Review summaries before sharing or acting. |
| Reports/counts | Missing or duplicate rows can distort the picture. | Yes: compare output row counts with input and inspect counts. | Developer for report code; transport office for use. | Check row counts and route/category totals after each run. |
| API failure/fallback | Some complaints remain unclassified. | Yes: look for `needs_manual_review` in results. | Developer for resilience; transport officer for follow-up. | Review all manual-review rows. |

## Accountability rule

The tool is advisory only. It never contacts drivers, assigns blame, or decides action. Safety complaints go to the transport officer, who is responsible for reviewing them and deciding what to do.
