import os
import pandas as pd

import os
import pandas as pd

from Helper.FabricsConnection import FabricSQLConnection
from Helper.database_service import DatabaseService
from Helper.VannaObject import MyVanna
from Helper.Credentials import Credentials

from vanna.flask import VannaFlaskApp

# =========================================
# ✅ Environment Setup
# =========================================
os.environ["TOKENIZERS_PARALLELISM"] = "false"

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

# Attach the run_sql function
vn.run_sql = db_service.run_sql
vn.run_sql_is_set = True

# (Optional but recommended) Train Vanna with some examples
# vn.train([...])  # <- if you have examples, you can preload

# =========================================
# ✅ Launch Vanna Flask App
# =========================================
if __name__ == "__main__":
    app = VannaFlaskApp(vn)
    app.run(host="0.0.0.0", port=5000, debug=True)  # Added host, port, debug
