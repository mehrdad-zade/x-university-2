# Sprint 7 — Progress tracking

## Goals
Track per-user progress and submissions.

## Data
- user_courses(user_id, course_id, started_at, completed_at)
- user_lessons(user_id, lesson_id, status enum['locked','in_progress','done'], started_at, completed_at, score nullable)
- user_materials(user_id, material_id, status enum['not_started','in_progress','submitted','graded'], score, answers jsonb, graded_at)

## API
- POST /enroll/{course_id}
- POST /lessons/{id}/start
- POST /materials/{id}/submit {answers}
- GET /me/progress

## Rules
- If matching course exists use it. Else call AI generation then enroll.

## Acceptance
- Progress reflects accurately on dashboard.
