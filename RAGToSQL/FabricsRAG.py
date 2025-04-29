import os
import pandas as pd
import re

from Helper.FabricsConnection import FabricSQLConnection
from Helper.database_service import DatabaseService
from Helper.VannaObject import MyVanna
from Helper.Credentials import Credentials

# ✅ Setup Environment
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ✅ Credentials and Connection
creds = Credentials()
conn_mgr = FabricSQLConnection()
engine = conn_mgr.connect_sqlalchemy()
db_service = DatabaseService(engine)

# ✅ Setup Vanna with correct config keys
vn = MyVanna(config={
    'api_key': creds.openai_api_key,
    'model': 'gpt-3.5-turbo'
})

vn.run_sql = db_service.run_sql
vn.run_sql_is_set = True

# ✅ SQL Fixer for T-SQL
def fix_sql_for_tsql(sql: str) -> str:
    if not isinstance(sql, str):
        raise ValueError("Input SQL must be a string. Got: None or invalid type.")

    # Replace LIMIT N with TOP N
    limit_match = re.search(r'LIMIT\s+(\d+)', sql, re.IGNORECASE)
    if limit_match:
        limit_value = limit_match.group(1)
        sql = re.sub(r'\bSELECT\b', f'SELECT TOP {limit_value}', sql, count=1, flags=re.IGNORECASE)
        sql = re.sub(r'LIMIT\s+\d+;?', '', sql, flags=re.IGNORECASE)

    sql = sql.replace('`', '[').replace(']', ']')  # Backticks → brackets
    sql = re.sub(r'\btrue\b', '1', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bfalse\b', '0', sql, flags=re.IGNORECASE)
    sql = re.sub(r'\bILIKE\b', 'LIKE', sql, flags=re.IGNORECASE)

    sql = sql.strip()
    if not sql.endswith(';'):
        sql += ';'

    return sql

# ✅ Ask Question → Fix SQL → Run
raw_sql = vn.ask(question="Show the top 10 best-selling portfolios in terms of its value")
print("🧠 Raw SQL:\n", raw_sql)

if raw_sql and isinstance(raw_sql, str):
    fixed_sql = fix_sql_for_tsql(raw_sql)
    print("🛠️ Fixed SQL:\n", fixed_sql)

    response = db_service.run_sql(fixed_sql)
    print("📊 Query Result:\n", response)
else:
    print("❌ No SQL was returned from vn.ask(). Please check your API key, quota, or model response.")
