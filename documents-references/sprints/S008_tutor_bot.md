# Sprint 8 — Personal teacher chatbot

## Goals
Per-student tutor. Stores chats. Assigns homework. Auto-grades simple answers.

## Data (Postgres)
- chat_sessions(id, user_id, course_id nullable, title, created_at, updated_at)
- chat_messages(id, session_id fk, role enum['system','assistant','user'], content jsonb, created_at)
- homeworks(id, lesson_id fk, assigned_by_bot bool, due_at, created_at)
- homework_submissions(id, homework_id fk, user_id fk, answers jsonb, score, feedback, created_at, graded_at)

## API
- POST /chat/sessions
- GET /chat/sessions
- POST /chat/{session_id}/messages -> streams assistant reply; persists
- POST /chat/{session_id}/assign-homework
- POST /homeworks/{id}/submit

## Bot
- System prompt restricted to syllabus and user progress.
- Tools:
  - get_user_progress(user_id)
  - get_lesson_context(lesson_id)
  - grade_submission(answers)

## Acceptance
- Chats persist. Bot assigns homework and grades basic submissions.
