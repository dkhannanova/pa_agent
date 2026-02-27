from fastapi import FastAPI
from pydantic import BaseModel
import os
from supabase import create_client
from app.agent.graph import build_graph

app = FastAPI()
graph = build_graph()

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None

def supabase_client():
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]  # только сервер!
    return create_client(url, key)

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/chat")
def chat(req: ChatRequest):
    sb = supabase_client()

    # 1) session
    if req.session_id is None:
        res = sb.table("agent_sessions").insert({"title": "Product Analytics Agent"}).execute()
        session_id = res.data[0]["id"]
    else:
        session_id = req.session_id

    # 2) save user message
    sb.table("agent_messages").insert({
        "session_id": session_id, "role": "user", "content": req.message
    }).execute()

    # 3) run workflow
    out = graph.invoke({"session_id": session_id, "user_message": req.message, "response": None})
    resp = out["response"].model_dump()

    # 4) save assistant message + artifact
    sb.table("agent_messages").insert({
        "session_id": session_id, "role": "assistant", "content": str(resp)
    }).execute()

    sb.table("agent_artifacts").insert({
        "session_id": session_id, "type": "plan_report", "title": "Run result",
        "content": resp, "metadata": {"mvp": True}
    }).execute()

    return resp
