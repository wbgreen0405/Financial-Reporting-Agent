import os
import pandas as pd
import json
import re
from datetime import datetime

from Helper.FabricsConnection import FabricSQLConnection
from Helper.database_service import DatabaseService
#from Helper.VannaObject import MyVanna
from Helper.Credentials import Credentials

# ─── Configuration ───────────────────────────────────────────────────────────
PREVIEW_ONLY   = False
METADATA_FILE  = "table_metadata.json"
TARGET_SCHEMA  = "dbo"

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# ─── Setup Connections ────────────────────────────────────────────────────────
creds       = Credentials()
conn_mgr    = FabricSQLConnection()
engine      = conn_mgr.connect_sqlalchemy()
db_service  = DatabaseService(engine)

# ─── Load Metadata & Build Prompt ────────────────────────────────────────────
with open(METADATA_FILE) as f:
    metadata = json.load(f)

table_descriptions = []
known_tables = []

for table in metadata:
    tn = table["table_name"]
    cols = [c["name"] for c in table.get("columns", [])]
    known_tables.append(tn)
    table_descriptions.append(f"{tn}: {', '.join(cols)}")

table_summary = "\\n".join(table_descriptions)

# ─── Initialize Vanna ────────────────────────────────────────────────────────
vn = MyVanna(config={
    "api_key": creds.openai_api_key,
    "model":    "gpt-3.5-turbo"
})
vn.set_system_message(
    "You are a SQL expert. Use only Microsoft SQL Server (T-SQL) syntax. "
    "Use SELECT TOP instead of LIMIT. Available tables and columns:\\n\\n"
    + table_summary
)
vn.run_sql = db_service.run_sql
vn.run_sql_is_set = True

# ─── Helpers ──────────────────────────────────────────────────────────────────
def fix_sql_for_tsql(sql: str) -> str:
    if not isinstance(sql, str):
        raise ValueError("SQL must be a string.")
    sql = re.sub(r"\\bLIMIT\\s+\\d+", "", sql, flags=re.IGNORECASE)
    sql = sql.replace("`", "[").replace("]", "]")
    sql = re.sub(r"\\bILIKE\\b", "LIKE", sql, flags=re.IGNORECASE)
    return sql.strip().rstrip(";") + ";"

def qualify_table_names(sql: str, schema=TARGET_SCHEMA) -> str:
    for tbl in known_tables:
        sql = re.sub(fr"\\bFROM\\s+{tbl}\\b", f"FROM {schema}.{tbl}", sql, flags=re.IGNORECASE)
    return sql

def log_sql(question: str, raw_sql: str, final_sql: str, prefix=""):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(log_dir, f"{prefix}sql_log_{ts}.log")
    with open(path, "w") as f:
        f.write(f"QUESTION:\\n{question}\\n\\nRAW SQL:\\n{raw_sql}\\n\\nFINAL SQL:\\n{final_sql}")
    print("Logged to", path)

# ─── Queries Configuration ───────────────────────────────────────────────────
queries = {
    "TopPortfolios":       "Show the top 10 best-selling portfolios in terms of its value",
    "ClientAUM":           "Show the total value of all portfolios managed for each client",
    "AssetAllocation":     "Show how each portfolio is allocated across asset types",
    "PerformanceTrends":   "Show historical total portfolio value by date for each portfolio",
    "RecentTransactions":  "List the 10 most recent transactions for each advisor"
}

# ─── Execute Loop ─────────────────────────────────────────────────────────────
for table_name, question in queries.items():
    print(f"\\n--- Processing: {table_name} ---")
    # Generate SQL
    raw_sql = vn.generate_sql(question)
    print("Raw SQL:\\n", raw_sql)

    # Fix and qualify
    final_sql = fix_sql_for_tsql(raw_sql)
    final_sql = qualify_table_names(final_sql)
    print("Final SQL:\\n", final_sql)

    # Log SQL
    log_sql(question, raw_sql, final_sql, prefix=f"{table_name}_")

    # Execute and push result
    try:
        df = pd.read_sql(final_sql, engine)
        print("Result DataFrame:\\n", df.head())

        df.to_sql(
            name=table_name,
            con=engine,
            schema=TARGET_SCHEMA,
            if_exists="replace",
            index=False
        )
        print(f"Pushed results to {TARGET_SCHEMA}.{table_name}")
    except Exception as e:
        print(f"❌ Error executing {table_name}: {e}")

print("\\nAll queries processed.")
