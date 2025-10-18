from fastapi import APIRouter
from typing import Optional
import os, psycopg2

router = APIRouter()

def get_conn():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "api_genie"),
        user=os.getenv("POSTGRES_USER", "api_genie"),
        password=os.getenv("POSTGRES_PASSWORD", "api_genie_pw"),
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=os.getenv("POSTGRES_PORT", "5432"),
    )

@router.get("/ping")
def ping():
    return {"ok": True, "where": "catalog"}

@router.get("/search")
def search(
    q: Optional[str] = None,
    category: Optional[str] = None,
    https: Optional[bool] = None,
    auth: Optional[str] = None,
    cors: Optional[bool] = None,
):
    sql = """
    SELECT a.api_id, a.api_name, a.description, a.base_url, a.auth_type,
           a.https_supported, a.cors_supported, a.pricing_tier, c.category_name
    FROM api_catalog.api a
    LEFT JOIN api_catalog.category c ON a.category_id = c.category_id
    WHERE 1=1
    """
    params = []
    if q:
        sql += " AND (a.api_name ILIKE %s OR a.description ILIKE %s)"
        like = f"%{q}%"
        params += [like, like]
    if category:
        sql += " AND c.category_name ILIKE %s"
        params += [f"%{category}%"]
    if https is not None:
        sql += " AND a.https_supported = %s"
        params += [https]
    if cors is not None:
        sql += " AND a.cors_supported = %s"
        params += [cors]
    if auth:
        sql += " AND a.auth_type ILIKE %s"
        params += [f"%{auth}%"]

    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()
    keys = ["api_id","api_name","description","base_url","auth_type",
            "https_supported","cors_supported","pricing_tier","category"]
    return [dict(zip(keys, r)) for r in rows]