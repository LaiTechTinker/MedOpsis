Backend setup
=============

Copy `.env.example` to `ai_services/.env`, set `GEMINI_API_KEY`, and install:

```powershell
.\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
```

Start:

```powershell
$env:PYTHONPATH=".\\backend;."
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The health endpoint is `http://127.0.0.1:8000/health`.