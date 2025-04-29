import os
import sys
import pyodbc
import random
import time
import socket
from datetime import datetime, timedelta
from faker import Faker

# --- 🎨 Color Helpers ---
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"

# --- 🔵 Hardcoded Connection Details ---
server ="INSERT SERVER"
port = 1433
user = "INSERT USERNAME"
password = "INSERT PASSWORD"
database = "INSERT DB NAME"

# --- 🔵 Safe Connection Test ---
def safe_test_connection(server, port, user, password, database):
    print("\n🔵 --- Safe Connection Test ---")

    # DNS resolution check
    try:
        lookup_server = server.split(",")[0]  # remove ,port if present
        print(f"🔎 Resolving server '{lookup_server}'...")
        ip = socket.gethostbyname(lookup_server)
        print(f"{GREEN}✅ Server resolved to IP: {ip}{RESET}")
    except socket.gaierror as e:
        print(f"{RED}❌ DNS resolution failed for server '{server}': {e}{RESET}")
        raise ConnectionError(f"DNS resolution failed for server '{server}': {e}")

    # Build connection string
    server_with_port = server if port == 1433 else f"{server},{port}"
    connection_string = (
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server_with_port};'
        f'DATABASE={database};'
        f'UID={user};'
        f'PWD={password};'
        'Encrypt=Yes;'
        'TrustServerCertificate=No;'
    )

    # Try to connect
    try:
        print(f"🔎 Attempting database connection to '{database}' as '{user}'...")
        start_time = time.time()
        conn = pyodbc.connect(connection_string, timeout=10)
        duration_ms = (time.time() - start_time) * 1000
        print(f"{GREEN}✅ Database connection successful! (Connected in {duration_ms:.2f} ms){RESET}")
        conn.close()
    except pyodbc.Error as e:
        print(f"{RED}❌ Database connection failed: {e}{RESET}")
        raise ConnectionError(f"Database connection failed: {e}")

    print(f"{GREEN}✅ All checks passed!{RESET}\n")

# --- 🔵 Test connection first ---
safe_test_connection(server, port, user, password, database)

# --- 🔵 Build connection string for main connection ---
server_with_port = server if port == 1433 else f"{server},{port}"
connection_string = (
    f'DRIVER={{ODBC Driver 17 for SQL Server}};'
    f'SERVER={server_with_port};'
    f'DATABASE={database};'
    f'UID={user};'
    f'PWD={password};'
    'Encrypt=Yes;'
    'TrustServerCertificate=No;'
)

# --- 🔵 Main connection ---
try:
    print(f"🔵 Attempting main connection to {server_with_port} as {user} ...")
    db = pyodbc.connect(connection_string, timeout=10)
    print(f"{GREEN}✅ Main database connection established!{RESET}\n")
except Exception as e:
    print(f"{RED}❌ Main database connection failed: {e}{RESET}")
    raise

cursor = db.cursor()

# --- 🔵 Initialize Faker ---
fake = Faker()

# --- 🔵 Seeder Class ---
class Seeder:
    def __init__(self, cursor, db):
        self.cursor = cursor
        self.db = db

    def create_tables(self):
        with open("create_tables.sql") as f:
            self.cursor.execute(f.read())
            self.db.commit()

    def create_views(self):
        with open("create_views_sql.sql") as f:
            sql_script = f.read()

        # Split the script into individual commands
        statements = [stmt.strip() for stmt in sql_script.split('GO') if stmt.strip()]

        for stmt in statements:
            try:
                self.cursor.execute(stmt)
                self.db.commit()
                print("✅ Executed view statement successfully.")
            except Exception as e:
                self.db.rollback()
                print(f"❌ Error executing view statement:\n{stmt}\nError: {e}")

    def create_stored_procedures(self):
        with open("stored_procedures.sql") as f:
            sql_script = f.read()

        # Split the script into individual commands
        statements = [stmt.strip() for stmt in sql_script.split('GO') if stmt.strip()]

        for stmt in statements:
            try:
                self.cursor.execute(stmt)
                self.db.commit()
                print("✅ Executed stored procedure statement successfully.")
            except Exception as e:
                self.db.rollback()
                print(f"❌ Error executing stored procedure statement:\n{stmt}\nError: {e}")


    def bulk_insert(self, table_name: str, columns: list, data: list, batch_size: int = 1000):
        if not data:
            print(f"⚠️ No data to insert into {table_name}. Skipping...")
            return

        placeholders = ", ".join(["?"] * len(columns))
        columns_joined = ", ".join(columns)
        sql = f"INSERT INTO {table_name} ({columns_joined}) VALUES ({placeholders})"

        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]
            try:
                self.cursor.fast_executemany = True
                self.cursor.executemany(sql, batch)
                self.db.commit()
                print(f"{GREEN}✅ Inserted batch {i//batch_size + 1} into {table_name}{RESET}")
            except Exception as e:
                self.db.rollback()
                print(f"{RED}❌ Error inserting batch {i//batch_size + 1} into {table_name}: {e}{RESET}")

    def bulk_upsert(self, table_name: str, key_columns: list, update_columns: list, data: list):
        if not data:
            print(f"⚠️ No data to upsert into {table_name}. Skipping...")
            return

        for row in data:
            where_clause = " AND ".join([f"{col} = ?" for col in key_columns])
            update_clause = ", ".join([f"{col} = ?" for col in update_columns])
            insert_columns = ", ".join(key_columns + update_columns)
            insert_placeholders = ", ".join(["?"] * (len(key_columns) + len(update_columns)))

            sql_check = f"SELECT COUNT(*) FROM {table_name} WHERE {where_clause}"
            sql_update = f"UPDATE {table_name} SET {update_clause} WHERE {where_clause}"
            sql_insert = f"INSERT INTO {table_name} ({insert_columns}) VALUES ({insert_placeholders})"

            key_values = [row[col] for col in key_columns]
            update_values = [row[col] for col in update_columns]
            full_values = key_values + update_values

            try:
                self.cursor.execute(sql_check, key_values)
                exists = self.cursor.fetchone()[0]

                if exists:
                    self.cursor.execute(sql_update, update_values + key_values)
                else:
                    self.cursor.execute(sql_insert, full_values)

            except Exception as e:
                print(f"{RED}❌ Error upserting record {row}: {e}{RESET}")
                self.db.rollback()
                continue

        self.db.commit()
        print(f"{GREEN}✅ Finished upsert into {table_name}{RESET}")

# --- 🔵 Instantiate Seeder ---
seeder = Seeder(cursor, db)

# --- 🔵 Constants ---
NUM_CLIENTS = 1000
NUM_ADVISORS = 100
NUM_ACCOUNTS = 2000
NUM_ASSETS = 1000
NUM_TRANSACTIONS = 5000
NUM_PORTFOLIOS = 1000
NUM_PORTFOLIO_ASSETS = 3000
NUM_PROJECTIONS = 2000

# --- 🔵 Insert Data ---
advisors = [(fake.name(), fake.phone_number()) for _ in range(NUM_ADVISORS)]
seeder.bulk_insert("Advisors", ["Name", "ContactInfo"], advisors)

clients = [
    (fake.name(), fake.phone_number(), random.randint(1, NUM_ADVISORS), random.choice(['High', 'Medium', 'Low']))
    for _ in range(NUM_CLIENTS)
]
seeder.bulk_insert("Clients", ["Name", "ContactInfo", "AdvisorID", "RiskProfile"], clients)

accounts = [
    (random.choice(['Savings', 'Checking', 'Investment']), random.randint(1, NUM_CLIENTS))
    for _ in range(NUM_ACCOUNTS)
]
seeder.bulk_insert("Accounts", ["AccountType", "ClientID"], accounts)

assets = [
    (fake.company(), random.choice(['Stock', 'Bond', 'Real Estate', 'Commodity', 'Cash']), round(random.uniform(10, 1000), 2))
    for _ in range(NUM_ASSETS)
]
seeder.bulk_insert("Assets", ["Name", "AssetType", "CurrentValue"], assets)

portfolios = [
    (random.randint(1, NUM_CLIENTS), f"Portfolio {fake.word()}", random.choice(['High', 'Medium', 'Low']))
    for _ in range(NUM_PORTFOLIOS)
]
seeder.bulk_insert("Portfolios", ["ClientID", "Name", "RiskLevel"], portfolios)

portfolio_assets = [
    (random.randint(1, NUM_PORTFOLIOS), random.randint(1, NUM_ASSETS), round(random.uniform(1, 100), 2))
    for _ in range(NUM_PORTFOLIO_ASSETS)
]
seeder.bulk_insert("PortfolioAssets", ["PortfolioID", "AssetID", "Allocation"], portfolio_assets)

start_date = datetime(2020, 1, 1)
transactions = [
    (random.randint(1, NUM_ACCOUNTS), random.randint(1, NUM_ASSETS), start_date + timedelta(days=random.randint(1, 365 * 4)),
     random.choice(['Buy', 'Sell', 'Deposit', 'Withdraw']), round(random.uniform(100, 10000), 2))
    for _ in range(NUM_TRANSACTIONS)
]
seeder.bulk_insert("Transactions", ["AccountID", "AssetID", "Date", "Type", "Amount"], transactions)

projections = [
    (random.randint(1, NUM_PORTFOLIOS), round(random.uniform(1000, 100000), 2), start_date + timedelta(days=random.randint(1, 365 * 10)))
    for _ in range(NUM_PROJECTIONS)
]
seeder.bulk_insert("Projections", ["PortfolioID", "FutureValue", "ProjectionDate"], projections)

# --- 🔵 Create Views and Stored Procedures ---
seeder.create_views()
seeder.create_stored_procedures()

# --- 🔵 Close Connection ---
cursor.close()
db.close()
print(f"{GREEN}✅ Data seeding complete!{RESET}")
