# Sprint 2 — Course model and initial catalog

## Goals
Subjects math and reading. Ages 4–20. Course > Lesson > Material.

## Data (Postgres)
- subjects(id, key unique, name)
- courses(id, subject_id fk, title, age_min, age_max, level, description, created_by, created_at)
- lessons(id, course_id fk, index int, title, summary, est_minutes)
- materials(id, lesson_id fk, type enum['text','quiz','assignment'], content jsonb, created_at)

## API
- GET /subjects
- GET /courses?subject=&age_min=&age_max=&level=&q=
- GET /courses/{id}
- GET /courses/{id}/lessons
- Admin: POST /courses, POST /lessons, POST /materials

## Frontend
- Catalog list with filters. Course detail page listing lessons and materials.

## Acceptance
- Seed 2 starter courses per subject with 3–5 lessons. Filtering works.

//todo: design the db for scalability of courses and topics per age group