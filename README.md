# MediAudit-AI

A React and FastAPI application for analyzing medical audit claims data.

## Structure

- `frontend/` - React and Vite user interface
- `backend/` - FastAPI service and machine-learning modules
- `data/` - Local datasets, including `claims.csv`
- `reports/` - Generated audit reports

## Run the backend

```powershell
pip install -r backend/requirements.txt
uvicorn backend.app.main:app --reload
```

## Run the frontend

```powershell
cd frontend
npm install
npm run dev
```
