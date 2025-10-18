# 🧙‍♂️ API Genie  
**A unified catalog and natural-language interface for exploring public APIs**

---

## 📖 Overview

API Genie is a full-stack project built with **FastAPI**, **PostgreSQL**, and a **React + Vite** frontend.  
It automatically ingests and structures thousands of entries from the [public-apis](https://github.com/public-apis/public-apis) repository into a searchable database.  
The goal is to make it easy to explore, query, and manage APIs through a clean UI and (future) AI-powered natural-language search.

---

## 🧩 Architecture

```

api-genie/
├─ docker-compose.yml         # orchestrates Postgres, backend, and frontend
├─ .env.example               # template for environment variables
├─ db/
│  └─ init/001_schema.sql     # database schema + schema creation
├─ backend/
│  ├─ app/
│  │  ├─ main.py              # FastAPI entrypoint + CORS
│  │  ├─ routers/catalog.py   # /catalog routes (ping, search, etc.)
│  │  ├─ models.py, deps.py   # models and helpers
│  │  └─ services/            # nl2sql, recommendations (future)
│  ├─ pyproject.toml          # backend dependencies
│  └─ README.md
├─ ingestion/
│  ├─ ingest_public_apis.py   # parser + loader for public-apis README
│  ├─ requirements.txt
│  └─ public_apis_README.md   # local copy of upstream README
└─ frontend/
├─ src/
│  ├─ main.tsx, App.tsx    # React/Vite entry + UI logic
│  └─ components/          # Chat, ResultsTable, etc.
├─ vite.config.ts
└─ package.json

````

---

## ⚙️ Setup & Run

### 1️⃣ Prerequisites
- Docker + Docker Compose  
- Node 18+ (for local frontend dev)  
- Python 3.11+ (for ingestion script)

---

### 2️⃣ Environment variables

Create `.env` in project root (or copy `.env.example`):

```bash
POSTGRES_USER=api_genie
POSTGRES_PASSWORD=api_genie_pw
POSTGRES_DB=api_genie
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
````

The frontend uses its own env file (`frontend/.env`):

```bash
VITE_API_BASE_URL=http://localhost:8000
```

---

### 3️⃣ Build and run all services

```bash
docker compose up -d --build
```

That will:

* Start PostgreSQL (with schema from `db/init/001_schema.sql`)
* Build and serve the FastAPI backend at [http://localhost:8000](http://localhost:8000)
* Build the Vite frontend at [http://localhost:5173](http://localhost:5173)

---

### 4️⃣ Ingest Public APIs

If you haven’t yet populated the database:

```bash
# Run from host (not inside docker)
cd ingestion
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Make sure your DB is running via Docker
POSTGRES_HOST=localhost POSTGRES_PORT=5432 POSTGRES_PASSWORD=api_genie_pw \
python ingest_public_apis.py --readme ingestion/public_apis_README.md
```

This loads ~1.4 K APIs from the public-apis README into PostgreSQL.

---

### 5️⃣ Verify everything works

**Backend health check:**

```bash
curl http://localhost:8000/health
```

**Sample search:**

```bash
curl 'http://localhost:8000/catalog/search?q=weather&https=true'
```

**Frontend:**
Open [http://localhost:5173](http://localhost:5173) in your browser
→ search “weather”, “blockchain”, etc.

---

## 🧠 Features

✅ FastAPI backend with modular routers
✅ PostgreSQL schema with category-based indexing
✅ CORS-enabled API for local React dev
✅ Ingestion parser that scrapes all 1.4 K+ entries from public-apis
✅ Dockerized services for easy setup
🚧 (Coming soon) Natural-language → SQL query service (NL2SQL)
🚧 (Coming soon) AI recommendations for similar APIs

---

## 🧪 Example Queries

```
GET /catalog/search?q=weather
GET /catalog/search?category=Blockchain&https=true
GET /catalog/search?auth=apiKey&cors=true
```

---

## 🧰 Tech Stack

| Layer            | Technology                         |
| ---------------- | ---------------------------------- |
| Frontend         | React 19 + Vite + TypeScript       |
| Backend          | FastAPI (Python 3.11)              |
| Database         | PostgreSQL 15                      |
| Ingestion        | Python (psycopg2, regex, requests) |
| Containerization | Docker & Docker Compose            |

---

## 🚀 Development

**Frontend (local dev mode)**

```bash
cd frontend
npm install
npm run dev
```

Vite will serve at [http://localhost:5173](http://localhost:5173).

**Backend (local dev mode)**

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧹 Common issues

| Error                                                           | Cause / Fix                                                                                                |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `psycopg2.OperationalError: connection refused`                 | Backend trying to connect to `localhost` inside container → set `POSTGRES_HOST=postgres` in docker-compose |
| `NetworkError` / `CORS` in browser                              | Add `CORSMiddleware` in FastAPI (already included)                                                         |
| `ON CONFLICT DO UPDATE command cannot affect row a second time` | Duplicate entries in ingestion → dedupe logic fixed                                                        |
| `No entries parsed`                                             | Ensure you downloaded full `public_apis_README.md` (≈ 1,900 lines)                                         |

---

## 🧑‍💻 Contributors

* **Sai Vignesh Naragoni** — Full-stack developer & system architect
* Open for pull requests and extensions (AI querying, category analytics, etc.)

---

## 🪪 License

This project is for educational purposes under the **MIT License**.
The ingested data comes from the [Public APIs repository](https://github.com/public-apis/public-apis).

---

## 🌟 Future Roadmap

* [ ] Natural-language → SQL (LLM-based) query interface
* [ ] Recommendation engine for similar APIs
* [ ] Pagination, sorting, and API detail pages
* [ ] Role-based admin dashboard
* [ ] Automated ingestion sync (GitHub Actions)

---
**Made with ❤️ using FastAPI, React, and PostgreSQL**