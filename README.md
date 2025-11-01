# Mobileye — GitLab API Service (Home Assignment)

## Purpose
This project implements helpers to interact with a GitLab server:
- grant/update user roles on projects/groups (grant_user_role)
- retrieve merge requests and issues by year (get_items_by_year)

These functions are implemented in src/gitlab_calls/gitlab_calls.py (Requirement 1).

## Architecture
The project is split into two parts:
- Frontend: a FastAPI service that exposes HTTP endpoints implemented in src/app.py. The API provides routes for health checks, listing endpoints, granting roles and retrieving items.
- Backend: the gitlab_calls module contains the logic for calling the GitLab API (user lookup, project/group resolution, members PUT/POST, pagination, date filtering).

Requirement 2 (container runtime) is provided by the Dockerfile at the repository root; the Dockerfile builds an image that runs the FastAPI app.

## Configuration
Environment variables:
- GITLAB_URL (default: http://localhost:8080)
- GITLAB_TOKEN (default: empty)
- PORT (optional; used by Dockerfile/runtime)

Set them before running locally or in the container.

## Run locally
From repository root (important for imports and pytest):
Windows (PowerShell / cmd):
```powershell
cd /d j:\Develop\Mobileye_Home_Assignment
python -m uvicorn src.app:app --host 0.0.0.0 --port 8000
```
Health: http://localhost:8000/health

## Docker
Build:
``` 
docker build -t gitlab-api-service .
```
Run:
``` 
docker run -d -p 8000:8000 `
  -e GITLAB_URL="https://gitlab.example.com" `
  -e GITLAB_TOKEN="glpat_xxx" `
  gitlab-api-service
```

## TEST
Run tests from project root to avoid import errors:
```powershell
cd /d j:\Develop\Mobileye_Home_Assignment
python -m pytest -q
```
Notes:
- tests/app_test.py is integration-style and expects the FastAPI service available at BASE_URL (default http://localhost:8000).
- Unit tests for gitlab_calls can be run without a running service and typically mock requests.
- If pytest raises "attempted relative import with no known parent package", ensure you run pytest from the repository root or set PYTHONPATH=src.

## Endpoints
- GET /health — health check
- GET / — list endpoints
- POST /grant-role — grant or update GitLab user role (JSON: username, repo_or_group, role)
- POST /get-items — retrieve merge requests or issues by year (JSON: item_type, year)

## Implementation notes
- Role mapping: guest..owner -> access levels (10..50)
- grant_user_role: finds user id, determines project vs group, attempts PUT to update member, falls back to POST on 404
- get_items_by_year: validates year, queries GitLab with created_after/created_before, handles pagination

### Dockerfile
- initial Dockerfile created with 'docker init' and tuned thoroughly with help of 'docker compose'. 
- base image of choice is python3:slim instead of 'alpine'. The ground for the choice is 'apk' package manager in 'alpine' which I'm less experienced with.
- project uses 'uv' to manage dependencies and to run frontend server.

## Troubleshooting
- Run pytest from repository root to fix import issues.
- Ensure GITLAB_URL and GITLAB_TOKEN are set for integration tests against a real GitLab instance.

## License
Add license information here.