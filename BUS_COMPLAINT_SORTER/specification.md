# Project Specification: Bus Complaint Sorter

## Purpose
Build a console-based Python tool that sorts student complaints about college buses so that safety risks are brought to the transport officer's attention first. The tool supports human review; it does not contact drivers, determine fault, or make decisions.

## Inputs
- `complaints.csv`: complaint ID, date, and original complaint text. It contains at least 20 student-style complaints, every required category, at least four safety cases, two vague cases, and one Tamil/Tanglish example.
- `routes.csv`: the 12 recognised bus routes and the areas they serve.

## Processing
For every complaint, Python sends the complaint to an LLM with `system_prompt.txt`. The LLM must return JSON with exactly `category`, `urgent`, `route`, and `summary`. Python validates the category, boolean urgent flag, route type, and summary length. An invalid response is retried once; after a second failure, the complaint is marked `needs_manual_review`. API errors are caught so the batch can continue. The route is retained only when it is listed in `routes.csv` and the same number appears in the original complaint; otherwise it becomes `null`.

## Categories and urgency
Allowed categories: `delay`, `crowding`, `driver`, `vehicle`, `route_request`, `other`. `urgent` is true only for a safety risk such as rash driving, phone use while driving, near misses, faulty brakes/doors/tyres, smoke, or students on the footboard. A rude driver is not automatically urgent.

## Outputs
- `results.csv`: one classification row per complaint (`id`, `category`, `urgent`, `route`, `summary`).
- `urgent.csv`: safety list with ID, date, route, area, original complaint, and summary.
- `summary.txt`: category totals, route totals in descending complaint order with area names, and the safety list.

## Human checkpoint and limitations
The transport officer reviews urgent items and all `needs_manual_review` rows. The system is advisory only; the human officer remains accountable for decisions. LLM classifications can be incorrect and must be checked.

## Security
The API key is stored in `.env`, loaded through environment variables, and excluded from Git using `.gitignore`. Only `.env.example` is included in the repository.
