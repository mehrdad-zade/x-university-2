# Sprint 6 — AI content generation

## Goals
Generate course material via OpenAI and store in DB. Idempotent by (subject, level, age range).

## Data
- ai_jobs(id, type, payload jsonb, status enum['queued','running','done','failed'], created_at, updated_at, error_text)
- ai_generations(id, job_id fk, course_id fk nullable, lesson_id fk nullable, model, prompt, completion, tokens_input, tokens_output, created_at)

## Contract
Model must return strict JSON:
{
  "course": {
    "title": "string",
    "description": "string",
    "lessons": [
      {
        "title": "string",
        "summary": "string",
        "est_minutes": 20,
        "materials": [
          {"type": "text", "content": {"md": "string"}},
          {"type": "quiz", "content": {"questions":[{"q":"string","choices":["A","B"],"answer_index":0}]}}
        ]
      }
    ]
  }
}

## API
- POST /ai/generate-course {subject, age_min, age_max, level} (admin)
- POST /ai/generate-next-for-user (user) -> returns existing or new course id

## Acceptance
- JSON validated, persisted in one transaction. Deterministic prompts.
