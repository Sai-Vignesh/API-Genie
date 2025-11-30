from fastapi import APIRouter, HTTPException
from app.models import QueryRequest, QueryResponse
from app.services.nl2sql import NL2SQLService
import psycopg2
import os
from typing import List, Dict, Any

router = APIRouter()
nl2sql_service = NL2SQLService()

def get_conn():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "api_genie"),
        user=os.getenv("POSTGRES_USER", "api_genie"),
        password=os.getenv("POSTGRES_PASSWORD", "api_genie_pw"),
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )

@router.post("/", response_model=QueryResponse)
def run_query(request: QueryRequest):
    # 1. Generate SQL
    sql = nl2sql_service.generate_sql(request.query)
    
    if sql == "CANNOT_ANSWER":
        return QueryResponse(error="I cannot answer that question based on the available data.")
    if sql == "ERROR":
        return QueryResponse(error="An error occurred while processing your request.")
        
    # 2. Execute SQL
    results = []
    try:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute(sql)
            if cur.description:
                # Fetch column names
                colnames = [desc[0] for desc in cur.description]
                rows = cur.fetchall()
                for row in rows:
                    results.append(dict(zip(colnames, row)))
            else:
                # No results (e.g. INSERT/UPDATE, though we only expect SELECT)
                pass
    except Exception as e:
        return QueryResponse(sql=sql, error=f"Database error: {str(e)}")
        
    return QueryResponse(sql=sql, results=results)
