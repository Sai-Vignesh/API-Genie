import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_conn():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "api_genie"),
        user=os.getenv("POSTGRES_USER", "api_genie"),
        password=os.getenv("POSTGRES_PASSWORD", "api_genie_pw"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )

DDL = """
-- Application Metadata Schema
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    name TEXT,
    email TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS database_schema (
    schema_id SERIAL PRIMARY KEY,
    version_number INT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS table_metadata (
    table_id SERIAL PRIMARY KEY,
    schema_id INT REFERENCES database_schema(schema_id),
    table_name TEXT
);

CREATE TABLE IF NOT EXISTS column_metadata (
    column_id SERIAL PRIMARY KEY,
    table_id INT REFERENCES table_metadata(table_id),
    column_name TEXT,
    data_type TEXT
);

CREATE TABLE IF NOT EXISTS nl_query (
    query_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    query_text TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS clarification (
    clarification_id SERIAL PRIMARY KEY,
    query_id INT REFERENCES nl_query(query_id),
    question_text TEXT,
    user_response_text TEXT
);

CREATE TABLE IF NOT EXISTS generated_sql (
    sql_id SERIAL PRIMARY KEY,
    query_id INT REFERENCES nl_query(query_id),
    sql_text TEXT,
    used_schema_version INT REFERENCES database_schema(schema_id),
    status TEXT
);

CREATE TABLE IF NOT EXISTS sql_execution_result (
    result_id SERIAL PRIMARY KEY,
    sql_id INT REFERENCES generated_sql(sql_id),
    success_flag BOOLEAN,
    error_message TEXT,
    output_summary TEXT
);
"""

def init_db():
    print("Initializing Application Metadata Schema...")
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(DDL)
            conn.commit()
        print("Schema initialized successfully.")
    except Exception as e:
        print(f"Error initializing schema: {e}")

if __name__ == "__main__":
    init_db()
