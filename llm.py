# llm.py

import os
import json
import re
from google import genai
from google.genai import types
from dotenv import load_dotenv
from schema import TABLE_SCHEMA

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))


# ── LLM Call 1: Natural Language → SQL ──────────────────────────────────────

def generate_sql(user_question: str, conversation_history: list) -> dict:

    system_prompt = f"""
You are an expert SQL engineer working with Snowflake databases.
Your ONLY job is to convert user questions into valid SQL queries.

{TABLE_SCHEMA}

RESPONSE FORMAT — respond ONLY with this exact JSON structure, nothing else:
{{
  "sql": "SELECT ... FROM EMPLOYEES ...",
  "explanation": "One line explaining what this query does"
}}

IMPORTANT:
- Return raw JSON only — no markdown, no code blocks, no extra text
- If the question is unclear or unanswerable, return:
  {{"sql": "INVALID", "explanation": "Reason why the question cannot be answered"}}
"""

    # Build conversation history in new SDK format
    history = []
    for turn in conversation_history[-6:]:
        history.append(types.Content(
            role="user",
            parts=[types.Part(text=turn["question"])]
        ))
        history.append(types.Content(
            role="model",
            parts=[types.Part(text=turn["sql"])]
        ))

    # Add current question
    history.append(types.Content(
        role="user",
        parts=[types.Part(text=user_question)]
    ))

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt
        ),
        contents=history
    )

    raw = response.text.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"sql": "INVALID", "explanation": "Failed to parse LLM response"}


# ── LLM Call 2: Raw DB Results → Natural Language ───────────────────────────

def explain_results(user_question, sql_query, columns, rows) -> str:

    if not rows:
        data_str = "The query returned no results."
    else:
        header = " | ".join(columns)
        separator = "-" * len(header)
        data_rows = "\n".join([" | ".join(str(v) for v in row) for row in rows[:20]])
        data_str = f"{header}\n{separator}\n{data_rows}"
        if len(rows) > 20:
            data_str += f"\n... and {len(rows) - 20} more rows"

    prompt = f"""
The user asked: "{user_question}"

We ran this SQL query:
{sql_query}

The database returned these results:
{data_str}

Now write a clear, concise natural language answer to the user's question based on these results.

Rules:
- Speak directly to the user
- Be conversational but precise
- Include key numbers and names from the results
- If no results, say so clearly
- Keep it to 2-4 sentences max
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text.strip()