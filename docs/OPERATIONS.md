# Reference operations runbook

## Supported deployment boundary

This beta package is a single-instance reference deployment using SQLite. It is suitable for demonstrations and controlled technical evaluation. It is not a multi-tenant or horizontally scaled production service. Put TLS, request limits, and network policy at a trusted ingress before exposing it outside a controlled environment.

## Configuration

- `DECISION360_API_KEYS`: required JSON object mapping secret tokens to actor names and roles. Supported roles are `viewer`, `operator`, `approver`, `auditor`, and `admin`.
- `DECISION360_DB`: SQLite path; defaults to `var/decision360.db` locally and `/app/var/decision360.db` in the container.
- `HOST` and `PORT`: bind address and port. Local defaults are `127.0.0.1:8000`.

The service deliberately returns `503` for protected endpoints when authentication is not configured. Never commit real tokens or place them in command history.

## Start and health

```bash
python -m pip install -e ".[dev]"
python -m decision360.api
curl http://127.0.0.1:8000/healthz
```

Container start:

```bash
docker compose up --build -d
docker compose ps
```

Healthy output contains `status: ok` and `audit_integrity: true`. Treat a false integrity result as an incident; stop writes and preserve the database and logs.

## Backup and restore

Use the online SQLite backup operation, not a filesystem copy of a live database:

```bash
decision360-maintenance backup var/decision360.db backups/decision360-YYYYMMDD.db
decision360-maintenance verify backups/decision360-YYYYMMDD.db
```

Restore into a new path, verify it, stop the service, update `DECISION360_DB`, and start the service. Retain the prior database unchanged until evaluation IDs, schema version, audit event count, and integrity have been checked.

## Incident response

1. Stop external traffic and preserve the database, container logs, configuration metadata, and deployment revision.
2. Rotate all API keys if disclosure is possible.
3. Run `decision360-maintenance verify` against a forensic copy.
4. Compare the last trusted audit hash and identify the first divergent event.
5. Restore only from a verified backup; do not rewrite audit rows.
6. Add a sanitized regression test and document scope before reopening traffic.

## Rollback

Deploy the prior immutable image while retaining the current database. Schema version 1 is the only current schema. A future schema change must include a tested forward migration and an explicit data rollback plan before release.
