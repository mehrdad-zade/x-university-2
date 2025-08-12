# Sprint 3 — Learning-path graph (no buildings)

## Goals
Use a graph DB to model prerequisite relations between lessons and courses. No physical map. Optional feature flag ENABLE_NEO4J.

## Data (Neo4j)
- Nodes: Course {id, subject, level}; Lesson {id, index, course_id}
- Rels: (:Lesson)-[:PREREQ_OF]->(:Lesson); (:Course)-[:UNLOCKS]->(:Course)

## API
- GET /graph/path?fromLessonId=&toLessonId= -> sequence of lesson ids and estimated total est_minutes
- GET /graph/recommendations?userId= -> next N lessons based on completed history
- Feature flag: if disabled, backend returns 200 with empty recommendations and computes a simple next-lesson via SQL fallback.

## Acceptance
- Given a user progress set, API returns deterministic next-steps. Works with flag off.
