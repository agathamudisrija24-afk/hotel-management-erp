# Migrations

`0001_initial` establishes the complete SQLAlchemy metadata schema. Run `alembic upgrade head` before starting a production API process. Generate later reviewed migrations with `alembic revision --autogenerate -m descriptive_name`.

PostgreSQL deployments should also add a reviewed `EXCLUDE USING gist` constraint over each physical room and its active booking daterange. The service already locks candidate rooms and rechecks availability; the exclusion constraint is the final cross-process protection for high-volume deployments.
