# Alembic

## Generic single-database configuration with an async dbapi

### Usage

> **Note**:
>
> You need to bash into the server container to run from **vaultexe directory**:
>
> ```./scripts/bash-into-server.sh```

#### Create a new migration script

```bash
./scripts/alembic-generate.sh "table_name"
```

### Run migrations

```bash
alembic upgrade head # upgrade to the latest revision
or
alembic upgrade +1 # upgrade one revision after
or
alembic upgrade revesion_id # upgrade to a specific revision
```

#### Downgrade to a previous migration

```bash
alembic downgrade base # downgrade to base revision
or
alembic downgrade -1 # downgrade one revision before
or
alembic downgrade revesion_id # downgrade to a specific revision
```
