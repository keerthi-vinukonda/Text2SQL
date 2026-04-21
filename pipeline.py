# pipeline.py

from llm import generate_sql, explain_results
from database import execute_query
from tabulate import tabulate


def run_pipeline(user_question: str, conversation_history: list) -> dict:
    """
    Full Text-to-SQL pipeline:
    1. Generate SQL from question
    2. Execute SQL on Snowflake
    3. Explain results in plain English

    Returns a result dict with all intermediate steps (great for debugging).
    """

    result = {
        "question":    user_question,
        "sql":         None,
        "sql_explain": None,
        "columns":     None,
        "rows":        None,
        "answer":      None,
        "error":       None,
        "status":      None
    }

    # ── Step 1: Generate SQL ─────────────────────────────────────────────────
    print("\n  Step 1: Generating SQL with Generative AI...")
    llm_response = generate_sql(user_question, conversation_history)

    result["sql"]         = llm_response.get("sql")
    result["sql_explain"] = llm_response.get("explanation")

    if result["sql"] == "INVALID":
        result["status"] = "invalid_question"
        result["answer"] = f"I couldn't answer that: {result['sql_explain']}"
        return result

    print(f"    SQL Generated: {result['sql']}")

    # ── Step 2: Execute SQL ──────────────────────────────────────────────────
    print("\n  Step 2: Running query on Snowflake...")
    columns, rows, error = execute_query(result["sql"])

    if error:
        result["status"] = "db_error"
        result["error"]  = error
        result["answer"] = f"The query ran into a database error: {error}"
        print(f"    DB Error: {error}")
        return result

    result["columns"] = columns
    result["rows"]    = rows
    print(f"    Query returned {len(rows)} row(s)")

    # ── Step 3: Explain Results ──────────────────────────────────────────────
    print("\n  Step 3: Generating natural language answer...")
    result["answer"] = explain_results(
        user_question,
        result["sql"],
        columns,
        rows
    )

    result["status"] = "success"
    return result


def display_result(result: dict):
    """Pretty print the full result to terminal."""

    print("\n" + "=" * 60)

    # Show SQL
    print(f"\n SQL Query:\n   {result['sql']}")
    print(f"   ({result['sql_explain']})")

    # Show raw table if results exist
    if result["rows"] and result["columns"]:
        print(f"\n Raw Results ({len(result['rows'])} rows):")
        table = tabulate(
            result["rows"][:10],
            headers=result["columns"],
            tablefmt="rounded_outline"
        )
        print(table)
        if len(result["rows"]) > 10:
            print(f"   ... and {len(result['rows']) - 10} more rows")

    # Show natural language answer
    print(f"\n🤖 Answer:\n   {result['answer']}")
    print("\n" + "=" * 60)