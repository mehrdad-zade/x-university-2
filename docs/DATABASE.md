# X University Database Documentation

## PostgreSQL

### Main Database (xu2)
Primary database for the application.

#### Key Tables (to be implemented):
- users
- courses
- lessons
- enrollments
- progress
- payments

### Migrations
Managed through Alembic:
```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Run migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

## Neo4j (Optional)

### Learning Path Graph
Used to represent course prerequisites and learning paths.

#### Node Types:
- Course
- Topic
- Skill
- Learning Objective

#### Relationships:
- PREREQUISITE_OF
- LEADS_TO
- REQUIRES
- TEACHES

### Configuration
- Bolt port: 7687
- HTTP port: 7474
- Browser interface: http://localhost:7474
- Default credentials in dev: neo4j/devpass

### Usage
Neo4j is optional and can be disabled by setting `ENABLE_NEO4J=false` in `.env`
