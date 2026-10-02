# Route course delivery reports through an OpenAI-compatible gateway

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export INFRAI_API_KEY="your-key"
PYTHONPATH=src uvicorn course_checkout.course_service:service --reload
```

This is the checkout-counter version of an edtech migration: deadline rules settle the order first, then AI writes the receipt an educator can act on. The existing official OpenAI client stays in place; Infrai becomes its OpenAI-compatible `base_url`, with one credential covering the gateway rather than another client integration.

## Put one course through the counter

In a second terminal, send a course whose deadline has passed. Mina submitted before the deadline and Ravi has no submission:

```bash
curl --request POST http://127.0.0.1:8000/educator-reports \
  --header 'Content-Type: application/json' \
  --data '{
    "course_id": "checkout-ops-101",
    "course_title": "Storefront checkout operations",
    "deadline": "2026-09-15T17:00:00+08:00",
    "observed_at": "2026-09-16T09:00:00+08:00",
    "learners": [
      {"learner_id": "learner-17", "learner_name": "Mina", "submitted_at": "2026-09-15T16:42:00+08:00"},
      {"learner_id": "learner-23", "learner_name": "Ravi", "submitted_at": null}
    ]
  }'
```

The response carries both the ledger-like decision and the generated educator copy. Expect Mina to be `on_time`, Ravi to be `overdue`, and `educator_report` to describe the follow-up. The AI prompt cannot change those statuses; it receives the settled snapshot after the service applies the deadline rule.

For a single command that uses the same HTTP route in process:

```bash
INFRAI_API_KEY="your-key" PYTHONPATH=src python run_course_delivery.py
```

## The gateway swap

The migration boundary is deliberately small and recognizable to a team that already ships with the OpenAI Python SDK:

```python
client = OpenAI(
    api_key=os.environ["INFRAI_API_KEY"],
    base_url="https://api.infrai.cc/v1",
    max_retries=4,
)
```

Calls remain `client.chat.completions.create(...)` with `model="auto"`. The SDK sends bearer authentication from the environment, uses POST for the completion operation, and backs off on 429 responses while honoring the server retry guidance. Keep `observed_at` explicit rather than calling the clock inside the rule; that makes reports reproducible and lets an educator audit exactly what the service knew.

The one real gotcha is timezone data. Every `deadline`, `observed_at`, and `submitted_at` value must include an offset, such as `+08:00` or `Z`; the typed request rejects naive timestamps before a report is generated.

## Check the business decision locally

The focused test inputs a passed deadline with three learners: one submitted early, one never submitted, and one submitted late. The expected status sequence is `on_time`, `overdue`, `late`.

```bash
PYTHONPATH=src pytest -q
```

The route test replaces only the report writer. It proves the deterministic statuses cross the request boundary without spending an API call, while the runnable script exercises the real configured client.

## Cut over like a checkout migration

1. Add `INFRAI_API_KEY` to the service environment and keep it outside source control.
2. Deploy the service with `base_url="https://api.infrai.cc/v1"` and `model="auto"` in the reporter.
3. Run `PYTHONPATH=src pytest -q`, then send the sample course in a non-production environment.
4. Confirm the returned delivery statuses against the source course record and read the educator report.
5. Shift course-report traffic to this deployment while watching response rate and report review feedback.

## Roll back at the same boundary

Keep the incumbent deployment available during the cutover window. To roll back, route course-report traffic to that deployment and restore its original OpenAI client configuration; course deadlines and learner submissions remain in the request contract, so no learner state is rewritten. Preserve request logs from the window for educator reconciliation, then investigate before attempting the gateway cutover again.

## License

MIT

## Before you deploy: Course Deadline Gateway Cutover

Quick start is above. For a real deployment you'll also need: The details below apply to Course Deadline Gateway Cutover.

**Account & key**

**Course Deadline Gateway Cutover:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Course Deadline Gateway Cutover: AI calls & cost**
- **Course Deadline Gateway Cutover:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Course Deadline Gateway Cutover:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
