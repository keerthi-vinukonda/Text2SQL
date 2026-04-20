# llm.py

import os
import anthropic
from dotenv import load_dotenv
from schema import TABLE_SCHEMA

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


# ── LLM Call 1: Natural Language → SQL ──────────────────────────────────────

def generate_sql(user_question: str, conversation_history: list) -> dict:
    """
    Converts a plain English question into a Snowflake SQL query.
    Uses conversation history for follow-up question support.

    Returns: { "sql": "...", "explanation": "..." }
    """

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

    # Build messages with conversation history (supports follow-ups)
    messages = []

    # Inject past conversation turns for context (last 6 turns max)
    for turn in conversation_history[-6:]:
        messages.append({"role": "user",      "content": turn["question"]})
        messages.append({"role": "assistant",  "content": turn["sql"]})

    # Add current question
    messages.append({"role": "user", "content": user_question})

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        system=system_prompt,
        messages=messages
    )

    import json
    raw = response.content[0].text.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback if Claude adds extra text
        import re
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            return json.loads(match.group())
        return {"sql": "INVALID", "explanation": "Failed to parse LLM response"}


# ── LLM Call 2: Raw DB Results → Natural Language ───────────────────────────

def explain_results(
    user_question: str,
    sql_query: str,
    columns: list,
    rows: list
) -> str:
    """
    Converts raw Snowflake query results into a natural language answer.
    """

    # Format results for the LLM
    if not rows:
        data_str = "The query returned no results."
    else:
        # Build a simple text table
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
- Speak directly to the user (use "you" / "there are" etc.)
- Be conversational but precise
- Include key numbers and names from the results
- If no results, say so clearly
- Keep it to 2-4 sentences max
"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text.strip()