import os
import pandas as pd
from Helper.VannaObject import MyVanna
from Helper.Credentials import Credentials

print("🔵 Starting InferenceRAG.py...")

# Set environment
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load credentials
creds = Credentials()
print("✅ Credentials loaded.")

# Initialize Vanna
vn = MyVanna(config={
    'api_key': creds.openai_api_key,
    'model': creds.model
})
print("✅ Vanna object created.")

# Set run_sql
def run_sql(sql: str):
    print(f"🔵 Running SQL:\n{sql}")
    from Helper.FabricsConnection import get_connection
    conn = get_connection()
    df = None
    try:
        df = pd.read_sql_query(sql, conn)
        conn.close()
    except Exception as e:
        print(f"❌ Error running SQL: {e}")
    return df

vn.run_sql = run_sql
vn.run_sql_is_set = True
print("✅ run_sql attached to Vanna.")

# Now ask a question
question = "Tell me the top client with highest portfolio."
print(f"🔵 Asking question: {question}")

try:
    generated_sql = vn.generate_sql(question)
    print(f"✅ SQL generated successfully.")
except Exception as e:
    print(f"❌ Error generating SQL: {e}")
    raise

if not generated_sql:
    print("⚠️ No SQL was generated.")
else:
    print(f"🧠 Generated SQL:\n{generated_sql}")

    print("🔵 Running generated SQL...")
    result_df = vn.run_sql(generated_sql)

    if result_df is not None and not result_df.empty:
        print("✅ Query result:")
        print(result_df)
    else:
        print("⚠️ No results found or error executing query.")



