# Blocks Game

## Backend

```powershell
cd backend
Copy-Item .env.example .env
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

API documentation: http://localhost:8000/docs

The SQLite database is created automatically on startup. For MySQL, set `DATABASE_URL=mysql+pymysql://user:password@localhost/blocks_game` and execute `schema.sql`.

Run tests:

```powershell
python -m pytest -q
```
