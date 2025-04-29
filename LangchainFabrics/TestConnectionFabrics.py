
import os
import struct
import time
from itertools import chain, repeat
import pyodbc
from dotenv import load_dotenv
from azure.identity import InteractiveBrowserCredential

# =========================================
# ✅ Load and validate environment variables
# =========================================

load_dotenv()

required_vars = ["OPENAI_API_KEY", "SQL_ENDPOINT", "DATABASE_NAME", "RESOURCE_URL"]
missing_vars = [var for var in required_vars if os.getenv(var) is None]

if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# =========================================
# ✅ Load variables from .env
# =========================================

openai_api_key = os.getenv("OPENAI_API_KEY")
sql_endpoint = os.getenv("SQL_ENDPOINT")
database = os.getenv("DATABASE_NAME")
resource_url = os.getenv("RESOURCE_URL")

# =========================================
# ✅ Authenticate with Azure
# =========================================

credential = InteractiveBrowserCredential()
token_object = credential.get_token(resource_url)
token = token_object.token

# =========================================
# ✅ Create ODBC Connection String
# =========================================

connection_string = (
    f"Driver={{ODBC Driver 18 for SQL Server}};"
    f"Server={sql_endpoint},1433;"
    f"Database={database};"
    "Encrypt=Yes;"
    "TrustServerCertificate=No;"
)

# Prepare token for SQL Server
token_as_bytes = bytes(token, "UTF-8")
encoded_bytes = bytes(chain.from_iterable(zip(token_as_bytes, repeat(0))))
token_bytes = struct.pack("<i", len(encoded_bytes)) + encoded_bytes
attrs_before = {1256: token_bytes}  # SQL_COPT_SS_ACCESS_TOKEN

# =========================================
# ✅ Connect to Fabric SQL and Test
# =========================================

try:
    # Measure connection time
    connect_start = time.time()
    connection = pyodbc.connect(connection_string, attrs_before=attrs_before)
    connect_end = time.time()

    cursor = connection.cursor()

    print(f"✅ Connected successfully in {connect_end - connect_start:.2f} seconds.")

    # Test Query
    query_start = time.time()
    test_query = "SELECT TOP (3) * FROM [wealth_data].[dbo].[Accounts]"
    cursor.execute(test_query)
    rows = cursor.fetchall()
    query_end = time.time()

    print(f"✅ Query executed in {query_end - query_start:.2f} seconds.\n")

    for row in rows:
        print(row)

except Exception as e:
    print(f"❌ Connection or query failed: {e}")

finally:
    try:
        cursor.close()
        connection.close()
        print("✅ Connection closed.")
    except:
        pass
