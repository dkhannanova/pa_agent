import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM = """You generate ONE ClickHouse SELECT query to compute the requested metric.
Rules:
- ONLY SELECT (no INSERT/ALTER/DROP).
- No semicolons.
- Must include a time filter if the user mentions a period.
- Use LIMIT 2000 if returning raw rows.
Return JSON with keys:
sql (string), assumptions (string), needs_clarification (boolean), clarification_question (string).
"""

SCHEMA = """SCHEMA (edit later):
You will be given tables and columns later. For now, ask clarification if schema is missing.
"""

def generate_sql(user_request: str) -> dict:
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    msg = f"{SCHEMA}\n\nUSER REQUEST:\n{user_request}\n"

    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": msg},
        ],
        response_format={"type": "json_object"},
        max_output_tokens=600,
    )
    return resp.output[0].content[0].json
