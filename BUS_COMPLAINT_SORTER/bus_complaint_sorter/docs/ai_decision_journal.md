# AI Decision Journal

Use this journal to record AI assistance and your own verification. The entries below describe the project design; add your own dates and observations before submission.

| Decision | AI/tool contribution | Human verification required |
|---|---|---|
| Project structure | Suggested separate input CSVs, prompt, Python program, tests, and documentation. | Confirm the files match the course specification. |
| Prompt design | Drafted the Authority, Exemplar, Constraint, Rubric, and Metadata sections with two examples. | Check each category and urgent rule against the assignment spec. |
| Route safety | Added a Python-side check requiring a recognised route that is explicitly written in the complaint. | Test route 99, no route, and route mentions in multiple formats. |
| Failure handling | Added one retry and `needs_manual_review` fallback so a failed model call does not stop the batch. | Simulate invalid replies and API errors. |
| Reporting | Added CSV and text reports with counts calculated in Python. | Compare report counts with source rows. |
| Security | Uses environment variables and ignores `.env`. | Ensure the real key is never committed to GitHub. |

## Before submission
Fill in the date, model used, actual API results, test score, unexpected failures, changes made, and what you personally learned. Do not claim a test passed unless you ran it.
