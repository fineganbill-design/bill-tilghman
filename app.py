import os
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from agents import Agent, Runner, SQLiteSession, WebSearchTool

BASE = Path(__file__).resolve().parent
DB_PATH = str(BASE / "data" / "conversations.db")
Path(BASE / "data").mkdir(exist_ok=True)

INSTRUCTIONS = (BASE / "instructions.txt").read_text(encoding="utf-8")

app = FastAPI(title="Bill Tilghman")
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")

bill = Agent(
    name="Bill Tilghman",
    instructions=INSTRUCTIONS,
    tools=[WebSearchTool()],
)

# Version 1 intentionally has no financial, email, wallet, or marketplace tools.
# The only capability is conversation with persistent session history.
SESSION_ID = "owner-primary"
session = SQLiteSession(SESSION_ID, DB_PATH)

@app.get("/", response_class=HTMLResponse)
async def home():
    return (BASE / "templates" / "index.html").read_text(encoding="utf-8")

@app.get("/health")
async def health():
    return {"status": "ok", "agent": "Bill Tilghman", "version": "1.0"}

@app.post("/chat")
async def chat(request: Request):
    body = await request.json()
    message = str(body.get("message", "")).strip()
    if not message:
        return JSONResponse({"error": "Message is required."}, status_code=400)

   try:

    result = await Runner.run(bill, message, session=session)

    return {"reply": result.final_output}

except Exception as exc:

    import traceback

    traceback.print_exc()
return JSONResponse({"error": str(exc)}, status_code=500)
    


