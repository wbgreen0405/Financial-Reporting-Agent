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
# ✅ Load environment variables from .env
# =========================================

load_dotenv()

# =========================================
# ✅ Validate required environment variables
# =========================================

required_vars = ["SQL_ENDPOINT", "DATABASE_NAME", "RESOURCE_URL", "OPENAI_API_KEY"]
missing_vars = [var for var in required_vars if os.getenv(var) is None]

if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# =========================================
# ✅ Credentials Class with Lazy Token + Connections
# =========================================

class Credentials:
    """Securely load credentials from environment variables, refresh token automatically, and create database connections."""

    def __init__(self):
        self.sql_endpoint = os.getenv("SQL_ENDPOINT")
        self.database = os.getenv("DATABASE_NAME")
        self.resource_url = os.getenv("RESOURCE_URL")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-3.5-turbo-16k"

        # Azure Authentication
        self.credential = InteractiveBrowserCredential()

        # Initialize token fields
        self._token = None
        self._token_expiry = 0  # seconds since epoch

    def _refresh_token(self):
        """Private method to refresh the Azure token."""
        token_object = self.credential.get_token(self.resource_url)
        self._token = token_object.token
        self._token_expiry = time.time() + token_object.expires_on - 60  # refresh 1 minute early
        print("🔄 Azure token refreshed.")

    @property
    def token(self):
        """Get a valid Azure token, refreshing if needed."""
        current_time = time.time()
        if self._token is None or current_time >= self._token_expiry:
            self._refresh_token()
        return self._token

    def get_connection_string(self):
        """Return the standard ODBC connection string."""
        return (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server={self.sql_endpoint},1433;"
            f"Database={self.database};"
            "Encrypt=Yes;"
            "TrustServerCertificate=No;"
        )

    def connect_odbc(self):
        """Create a live pyodbc connection with token authentication."""
        connection_string = self.get_connection_string()

        # Prepare token
        token_as_bytes = bytes(self.token, "UTF-8")
        encoded_bytes = bytes(chain.from_iterable(zip(token_as_bytes, repeat(0))))
        token_bytes = struct.pack("<i", len(encoded_bytes)) + encoded_bytes
        attrs_before = {1256: token_bytes}  # SQL_COPT_SS_ACCESS_TOKEN

        connection = pyodbc.connect(connection_string, attrs_before=attrs_before)
        print("✅ pyodbc connection established.")
        return connection

    def connect_sqlalchemy(self):
        """Create a live SQLAlchemy engine with token authentication."""
        connection_string = self.get_connection_string()

        # Prepare token
        token_as_bytes = bytes(self.token, "UTF-8")
        encoded_bytes = bytes(chain.from_iterable(zip(token_as_bytes, repeat(0))))
        token_bytes = struct.pack("<i", len(encoded_bytes)) + encoded_bytes
        attrs_before = {1256: token_bytes}

        params = urllib.parse.quote_plus(connection_string)

        engine = sa.create_engine(
            f"mssql+pyodbc:///?odbc_connect={params}",
            connect_args={"attrs_before": attrs_before}
        )
        print("✅ SQLAlchemy engine established.")
        return engine

    def __str__(self):
        return (
            f"Credentials("
            f"sql_endpoint='{self.sql_endpoint}', "
            f"database='{self.database}', "
            f"resource_url='{self.resource_url}', "
            f"token='[DYNAMIC]', "
            f"openai_api_key='[HIDDEN]', "
            f"model='{self.model}')"
        )




