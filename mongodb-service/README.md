# pocketLLM MongoDB Service

Dedicated microservice that owns persistence for users, chat sessions, and message history using MongoDB. It allows the FastAPI backend (or any other internal client) to interact with Mongo through a clean HTTP API or via direct repository imports during service composition.

## Features

- FastAPI service exposing `/users` and `/sessions` endpoints.
- Motor-based async Mongo client with lifecycle management.
- Repository layer that abstracts BSON/ObjectId semantics.
- Pydantic schemas for request validation and API responses.
- Ready-to-run Dockerfile and `.env.example`.

## Project Layout

```
mongodb-service/
├── app/
│   ├── config.py          # Service settings / env variables
│   ├── db.py              # Mongo connection + health checks
│   ├── main.py            # FastAPI app + routers
│   ├── repositories/      # CRUD helpers that talk to Mongo
│   ├── routers/           # HTTP endpoints for users/sessions
│   ├── schemas/           # Pydantic models shared across layers
│   └── utils/             # BSON/ObjectId helpers
├── Dockerfile
├── README.md
├── requirements.txt
└── .env.example
```

## Quickstart

```bash
cd mongodb-service
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8100
```

By default the `.env` points to the Docker hostname `mongo` (the compose-managed Mongo container). If you run Mongo directly on your host, update `MONGODB_URI` to `mongodb://localhost:27017` before starting the service.

## Docker

```
docker build -t pocketllm-mongodb .
docker run --rm -p 8100:8100 --env-file .env pocketllm-mongodb
```

The root `docker-compose.yml` already includes both the `mongo` database container and this service so everything comes up with `docker compose up --build`.

## Integrating with the Backend

- **Option 1 – HTTP**: call the service from `backend/app/routers` using the `/api/v1/users` and `/api/v1/sessions` endpoints exposed here. This keeps DB logic contained in this folder.
- **Option 2 – Shared package**: import the repositories directly by adding this folder to the backend's Python path (e.g., via Poetry workspace or editable install). The repositories are framework-agnostic.
- **Auth**: This service assumes upstream auth has already run (it does not issue tokens). Pass the authenticated `user_id` when creating sessions.
- **Environment**: point the backend to the internal Docker hostname `mongodb-service:8100` (HTTP) or `mongo:27017` (direct Mongo connectivity) depending on the integration style.

### API surface

| Method | Path | Description |
| --- | --- | --- |
| `POST` | `/api/v1/users` | Create a new user (expects pre-hashed password). |
| `GET` | `/api/v1/users` | Paginated list of users. |
| `GET` | `/api/v1/users/{id}` | Fetch single user. |
| `POST` | `/api/v1/sessions` | Create chat session for a user. |
| `GET` | `/api/v1/sessions/{id}` | Fetch chat session (messages included). |
| `GET` | `/api/v1/sessions/users/{user_id}` | List sessions for a user. |
| `POST` | `/api/v1/sessions/{id}/messages` | Append a new chat message. |
| `DELETE` | `/api/v1/sessions/{id}` | Soft delete (full removal) of a session. |

## Next Steps

- Expand repositories with richer queries (filters, pagination, soft-delete).
- Add domain events so backend can subscribe to data changes.
- Wire backend routes to call this service (REST) or import the repositories directly when both services share a deployment.
- Add unit tests using `mongomock_motor` or a temp Mongo container.


