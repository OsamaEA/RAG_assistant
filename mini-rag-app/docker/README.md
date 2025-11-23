# Docker Setup for MiniRAG App

## Services
- **FastAPI Application**: Main applicaiton running on UVICORN.
- **NGINX**: Web server for serving FASTAPI Application.
-**POSTGRES (PGVECTOR)**: Vector-enabled database for stroing embeddings.
-**QDRANT**: Vector Database for Similarity Search.
-**PROMETHEUS**: Metrics Collection.
-**GRAFANA**: Visualization Dashboard for Metrics.
-**Node-Exporter**: System Metrics Collection.

### Start the Services:
```bash
cd docker
docker compose up --build -d
```

#### Start Databases first:
```bash
docker compose up -d pgvector qdrant postgres-exporter
# Wait fpr database to be healthy
sleep 30
# start the applications services

docker compose up fastapi nginx pgvector qdrant prometheus grafana node-exporter --build -d
```

#### To delete all containers
```bash
sudo docker compose down #down
sudo docker container prune -f #containesr
sudo docker network prune -f #network
sudo docker compose down -v  #all contianers and volumes
```

### Accessing Services:
- FastAPI App: http://localhost:8000
- FastAPI Documentation: http://localhost:8000/docs
- Nginx (Serving FastAPI): http://localhost
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000
- Qdrant UI: http:/localhost:6333/dashboard
- Qdrant Metrics: http://localhost:6333/metrics


### Investigating Logs of the container:
```bash
 docker compose logs -f fastapi
 sudo docker compose exec fastapi bash #get into the container
 ```
