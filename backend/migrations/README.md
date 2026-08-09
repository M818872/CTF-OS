# Database migrations

`001_alpha_persistence.sql` creates the first-class `evidence` and `artifacts` tables used by Alpha 0.2.

`002_execution_jobs.sql` creates the durable execution queue used by the dedicated worker.

The development application currently calls SQLAlchemy `Base.metadata.create_all()` during startup, which keeps local development self-contained. Production deployments should apply the SQL migrations explicitly before starting the application.
