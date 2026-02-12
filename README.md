# Data Ingestion Pipeline with Docker

This document contains all the commands and configurations needed to set up a PostgreSQL database, a management interface (pgAdmin), and run a Python data ingestion script using Docker.

---

## 1. Project Structure

Ensure your project directory is organized as follows:

```text
/my-docker-project
├── ingest_data.py       # The Python script
├── Dockerfile          # Docker image definition for the script
├── docker-compose.yaml # Orchestration for DB and Admin
└── README.md           # This file
```

---

## 2. Docker Network Setup

Create a custom network so containers can communicate by name.

```bash
docker network create pg-network
```

---

## 3. Infrastructure (Database & Admin)

### Option A: Manual Setup (Docker Run)

#### Step 1: Run PostgreSQL Database

```bash
docker run -it \
  --rm \
  --name pgdatabase \
  --network=pg-network \
  -e POSTGRES_USER=root \
  -e POSTGRES_PASSWORD=root \
  -e POSTGRES_DB=ny_taxi \
  -p 5432:5432 \
  -v $(pwd)/ny_taxi_postgres_data:/var/lib/postgresql/data \
  postgres:13
```

#### Step 2: Run pgAdmin (Management UI)

- **URL:** http://localhost:8085  
- **Login:** admin@admin.com / root  
- **Host to Register:** `pgdatabase` (Internal Docker Name)

```bash
docker run -it \
  --rm \
  --name pgadmin \
  --network=pg-network \
  -e PGADMIN_DEFAULT_EMAIL="admin@admin.com" \
  -e PGADMIN_DEFAULT_PASSWORD="root" \
  -p 8085:80 \
  dpage/pgadmin4
```

---

### Option B: Automated Setup (Docker Compose) ✅ Recommended

This option saves time and manages the network automatically.

Create a `docker-compose.yaml` file:

```yaml
services:
  pgdatabase:
    image: postgres:13
    environment:
      - POSTGRES_USER=root
      - POSTGRES_PASSWORD=root
      - POSTGRES_DB=ny_taxi
    volumes:
      - "./ny_taxi_postgres_data:/var/lib/postgresql/data"
    ports:
      - "5432:5432"
    networks:
      - pg-network

  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@admin.com
      - PGADMIN_DEFAULT_PASSWORD=root
    ports:
      - "8085:80"
    networks:
      - pg-network

networks:
  pg-network:
    driver: bridge
```

Run it with:

```bash
docker-compose up -d
```

---

## 4. Data Ingestion (The Script)

### Step 1: Dockerize the Python Script

Create a `Dockerfile` in the same directory:

```dockerfile
FROM python:3.9

# Install dependencies
RUN pip install pandas sqlalchemy psycopg2-binary click tqdm

WORKDIR /app
COPY ingest_data.py ingest_data.py

ENTRYPOINT ["python", "ingest_data.py"]
```

---

### Step 2: Build the Image

```bash
docker build -t taxi_ingest:v001 .
```

---

### Step 3: Run the Ingestion Container

This container connects to the `pgdatabase` host on the `pg-network`.

```bash
docker run -it \
  --rm \
  --network=pg-network \
  taxi_ingest:v001 \
  --user=root \
  --password=root \
  --host=pgdatabase \
  --port=5432 \
  --db=ny_taxi \
  --table_name=yellow_taxi_data \
  --url="https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/yellow_tripdata_2021-01.csv"
```

---

✅ **You are now ready to ingest NYC taxi data into PostgreSQL using Docker!**
