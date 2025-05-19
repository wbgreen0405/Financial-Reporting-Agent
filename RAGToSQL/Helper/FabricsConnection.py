import os
import struct
import time
import urllib
from itertools import chain, repeat

import pyodbc
import sqlalchemy as sa
from dotenv import load_dotenv
from azure.identity import InteractiveBrowserCredential

# =========================================
# ✅ Load and validate environment variables
# =========================================

load_dotenv()

required_vars = ["SQL_ENDPOINT", "DATABASE_NAME", "RESOURCE_URL", "OPENAI_API_KEY"]
missing_vars = [var for var in required_vars if os.getenv(var) is None]

if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# =========================================
# ✅ FabricSQLConnection Class
# =========================================

class FabricSQLConnection:
    """Manage Azure Fabric SQL connections with auto-refreshing token and retry logic."""

    def __init__(self):
        self.sql_endpoint = os.getenv("SQL_ENDPOINT")
        self.database = os.getenv("DATABASE_NAME")
        self.resource_url = os.getenv("RESOURCE_URL")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-3.5-turbo-16k"

        self.credential = InteractiveBrowserCredential()
        self._token = None
        self._token_expiry = 0  # seconds since epoch

    def _refresh_token(self):
        """Private method to refresh the Azure token."""
        token_object = self.credential.get_token(self.resource_url)
        self._token = token_object.token
        self._token_expiry = time.time() + token_object.expires_on - 60  # refresh 1 min early
        print("🔄 Azure token refreshed.")

    @property
    def token(self):
        """Return a valid Azure token, refreshing if expired."""
        current_time = time.time()
        if self._token is None or current_time >= self._token_expiry:
            self._refresh_token()
        return self._token

    def _get_connection_string(self):
        """Return ODBC connection string."""
        return (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server={self.sql_endpoint},1433;"
            f"Database={self.database};"
            "Encrypt=Yes;"
            "TrustServerCertificate=No;"
        )

    def _get_token_bytes(self):
        """Convert Azure token to ODBC expected bytes format."""
        token_as_bytes = bytes(self.token, "UTF-8")
        encoded_bytes = bytes(chain.from_iterable(zip(token_as_bytes, repeat(0))))
        token_bytes = struct.pack("<i", len(encoded_bytes)) + encoded_bytes
        return token_bytes

    def connect_odbc(self, retries: int = 3, delay: int = 2):
        """Create a pyodbc connection to Fabric with retry logic."""
        attempt = 0
        while attempt < retries:
            try:
                connection_string = self._get_connection_string()
                attrs_before = {1256: self._get_token_bytes()}
                connection = pyodbc.connect(connection_string, attrs_before=attrs_before)
                print(f"✅ pyodbc connection established on attempt {attempt + 1}.")
                return connection
            except pyodbc.Error as ex:
                print(f"⚠️ pyodbc attempt {attempt + 1} failed: {ex}")
                attempt += 1
                if attempt < retries:
                    print(f"🔄 Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"❌ All {retries} attempts failed for pyodbc connection.")
                    raise

    def connect_sqlalchemy(self, retries: int = 3, delay: int = 2):
        """Create a SQLAlchemy engine for Fabric with retry logic."""
        attempt = 0
        while attempt < retries:
            try:
                connection_string = self._get_connection_string()
                attrs_before = {1256: self._get_token_bytes()}
                params = urllib.parse.quote_plus(connection_string)
                engine = sa.create_engine(
                    f"mssql+pyodbc:///?odbc_connect={params}",
                    connect_args={"attrs_before": attrs_before}
                )
                # Simple test to make sure connection is valid
                with engine.connect() as conn:
                    pass
                print(f"✅ SQLAlchemy engine established on attempt {attempt + 1}.")
                return engine
            except Exception as ex:
                print(f"⚠️ SQLAlchemy attempt {attempt + 1} failed: {ex}")
                attempt += 1
                if attempt < retries:
                    print(f"🔄 Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    print(f"❌ All {retries} attempts failed for SQLAlchemy connection.")
                    raise

