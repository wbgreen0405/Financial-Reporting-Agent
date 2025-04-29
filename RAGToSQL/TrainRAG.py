import json
import os
import pandas as pd
from datetime import datetime

from Helper.FabricsConnection import FabricSQLConnection
from Helper.database_service import DatabaseService
from Helper.VannaObject import MyVanna
from Helper.Credentials import Credentials
# =========================================
# ✅ Environment Setup
# =========================================

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# =========================================
# ✅ Logging Setup (Rotating + Subfolder)
# =========================================

# Create a logs/ directory if it doesn't exist
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Timestamped log file inside logs/ folder
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
LOG_FILE = os.path.join(LOG_DIR, f"training_log_{timestamp}.txt")

def log_message(message: str):
    """Append a timestamped message to the training log file."""
    log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{log_time}] {message}\n")
    print(message)

# =========================================
# ✅ Setup Connections
# =========================================

creds = Credentials()
conn_mgr = FabricSQLConnection()
engine = conn_mgr.connect_sqlalchemy()
db_service = DatabaseService(engine)

# =========================================
# ✅ Setup Vanna
# =========================================

vn = MyVanna(config={
   'api_key': creds.openai_api_key,     # FIXED typo here: 'api_key', not 'api_keye68009ba56ad489d93a24e371afa3aee'
    'model': 'gpt-3.5-turbo'                 # FIXED typo here: 'model', not 'fasqlagent'
})

vn.run_sql = db_service.run_sql
vn.run_sql_is_set = True

log_message("✅ Connection to Fabric SQL successful.")

# =========================================
# ✅ Helper Functions
# =========================================

def get_ddls():
    """Load DDL commands from JSON artifacts."""
    try:
        with open('TrainingRAG-Artifact/Proc.json', 'r') as file:
            proc = json.load(file)
        with open('TrainingRAG-Artifact/Tables.json', 'r') as file:
            tables = json.load(file)
        with open('TrainingRAG-Artifact/Views.json', 'r') as file:
            views = json.load(file)

        data = []
        data.extend(tables)
        data.extend(views)
        data.extend(proc)
        return data

    except Exception as e:
        log_message(f"❌ Error loading DDL JSON files: {e}")
        raise

# =========================================
# ✅ Training Step 1: Information Schema
# =========================================

log_message("🔵 Training with Information Schema...")
df_information_schema = vn.run_sql("SELECT * FROM INFORMATION_SCHEMA.COLUMNS")
plan = vn.get_training_plan_generic(df_information_schema)
vn.train(plan=plan)
log_message("✅ Information Schema trained successfully.")

# =========================================
# ✅ Training Step 2: DDL Commands
# =========================================

log_message("🔵 Training with DDLs (Tables, Views, Procedures)...")
for query in get_ddls():
    vn.train(ddl=query["command"])
log_message("✅ DDLs trained successfully.")

# =========================================
# ✅ Training Step 3: Documentation
# =========================================

log_message("🔵 Training with Documentation...")
try:
    with open("TrainingRAG-Artifact/Documentation.txt", "r") as f:
        documentation = f.read()
    vn.train(documentation=documentation)
    log_message("✅ Documentation trained successfully.")
except Exception as e:
    log_message(f"❌ Error reading documentation file: {e}")
    raise

# =========================================
# ✅ Save Trained Data Summary
# =========================================

log_message("🔵 Saving training summary...")
trained_data = vn.get_training_data()
trained_data.to_csv("training_summary.csv")
log_message("✅ Training summary saved to training_summary.csv.")




