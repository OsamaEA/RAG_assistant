## Run Alembic Migration

### Configuration

```bash
cp alembic.ini.example alembic.ini
```

- update the `alembic.ini` with your database credentials (`sqlalchemy.url`)
- update target_metadata = YourParentclass.metadata

```bash
alembic revision --autogenerate -m "Initial Commit"
alembic upgrade head
```




### Failed to Load Alembic
```bash
docker exec -it pgvectordb bash
echo "host all all all scram-sha-256" >> /var/lib/postgresql/data/pg_hba.conf
sed -i "s/^#listen_addresses =.*/listen_addresses = '*'/" /var/lib/postgresql/data/postgresql.conf
exit
docker restart pgvectordb

psql -h pgvectordb -U postgres -d minirag
CREATE EXTENSION IF NOT EXISTS vector;
postgresql://postgres:123456@localhost:5432/minirag
```


### To avoid confusion on DBeaver if you have Postgres setup on local PC, run WSL on 5433 Port
```bash
psql -h localhost -p 5433 -U postgres -d minirag
alembic stamp head

```