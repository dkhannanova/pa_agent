from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from app.agent.schemas import AgentResponse, ClarifyingQuestion, PlanStep, Finding
from app.agent.tools import catalog_search

class AgentState(TypedDict):
    session_id: str
    user_message: str
    response: Optional[AgentResponse]

def clarify_node(state: AgentState) -> AgentState:
    resp = AgentResponse(
        session_id=state["session_id"],
        clarifying_questions=[
            ClarifyingQuestion(id="period", question="Какой период сравниваем? (DoD/WoW/custom)")
        ],
        analysis_plan=[],
        findings=[],
        next_step="Ответь периодом — и я составлю план анализа."
    )
    state["response"] = resp
    return state

def plan_node(state: AgentState) -> AgentState:
    items = catalog_search(state["user_message"])
    plan = [
        PlanStep(step=1, goal="Зафиксировать определение метрики и период сравнения"),
        PlanStep(step=2, goal="Проверить динамику метрики по времени"),
        PlanStep(step=3, goal="Разложить по сегментам (platform/app_version/channel)"),
    ]
    findings = []
    if items:
        findings.append(Finding(
            finding=f"Нашла в каталоге: {items[0]['name']} — {items[0]['description']}",
            confidence="high"
        ))
    resp = state["response"]
    resp.analysis_plan = plan
    resp.findings = findings
    resp.next_step = "Скажи период — и продолжим. Позже подключим данные/RAG."
    state["response"] = resp
    return state

def build_graph():
    g = StateGraph(AgentState)
    g.add_node("clarify", clarify_node)
    g.add_node("plan", plan_node)
    g.set_entry_point("clarify")
    g.add_edge("clarify", "plan")
    g.add_edge("plan", END)
    return g.compile()
