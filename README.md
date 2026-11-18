# Blocks Game – FastAPI + Angular

A responsive 10×10 block puzzle game. FastAPI owns board validation, placement, scoring, game-over checks, authentication, leaderboards, history, and statistics. Angular provides the playable drag-free click/tap interface and is responsive for desktop and mobile.

## Project structure

- `backend/app/main.py` – application setup, CORS, logging, startup
- `backend/app/database.py` – SQLAlchemy engine/session
- `backend/app/models/entities.py` – database entities
- `backend/app/schemas/game.py` – Pydantic request/response validation
- `backend/app/services/game_engine.py` – board, placement, clearing, and scoring rules
- `backend/app/routers/auth.py` – registration/login
- `backend/app/routers/game.py` – game, leaderboard, history, and statistics APIs
- `backend/schema.sql` – MySQL schema
- `frontend/src/app/game.component.*` – responsive game interface
- `frontend/src/app/game.service.ts` – REST API integration

## Run

### 1. Backend

```powershell
cd backend
Copy-Item .env.example .env
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Open http://localhost:8000/docs

### 2. Frontend

```powershell
cd frontend
npm install
npm start
```

Open http://localhost:4200

Create a player by entering username and password. The backend creates a secure account and automatically logs it in (login is attempted after registration).

## Test

```powershell
cd backend
python -m pytest -q
cd ../frontend
npm run build
```

## Gameplay

Select one of the three displayed shapes, then click or tap a 10×10 board cell. The server validates the placement. A placed block awards one point per occupied cell; completed rows/columns award 100 points each plus combo bonuses. Used shapes are replaced from the tray, and the server declares game over when no tray shape fits.
