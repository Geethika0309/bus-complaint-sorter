# Cost and Latency Note

## Approximate call count
The sample input contains 24 complaints. The program makes one API call per complaint in the normal case: **24 calls**. The validator retries an invalid/API-failed item once, so the theoretical maximum for this sample is **48 calls** if every first attempt triggers a retry. If an API key is missing, calls fail locally and the program falls back to manual review.

## Latency
Actual latency depends on model availability, network conditions, prompt size, and service load. For planning only, assume about 1–5 seconds per successful call. Sequential processing of 24 complaints could therefore take roughly 24–120 seconds, plus any retry delays. Measure real runs and replace this assumption with observed timings.

## Cost estimate
Pricing can change by model and date. This project does not hard-code a price because the current Gemini model's input/output token rates must be checked on the provider's official pricing page when the project is run. Estimate cost as:

`(input_tokens / 1,000,000 × current_input_price_per_million) + (output_tokens / 1,000,000 × current_output_price_per_million)`

Multiply by the actual number of calls. A compact complaint and prompt will use tokens on every request; the system prompt is repeated for each complaint. Record the selected model, actual calls, token usage if available, and the price page/date in the final submission.

## Responsible-use note
Do not claim a precise daily cost until actual token counts and current pricing are checked. Keep a human checkpoint for all safety items and manual-review fallbacks.
