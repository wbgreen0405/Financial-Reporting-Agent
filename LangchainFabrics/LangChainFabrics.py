import os
import struct
from itertools import chain, repeat
import urllib
import sqlalchemy as sa
import pyodbc
from dotenv import load_dotenv

from azure.identity import InteractiveBrowserCredential
from langchain import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool

class FabricSQLAgent:
    def __init__(self):
        # Load and validate environment variables
        load_dotenv("INSERT PATH")

        required_vars = ["OPENAI_API_KEY", "SQL_ENDPOINT", "DATABASE_NAME", "RESOURCE_URL"]
        missing_vars = [var for var in required_vars if os.getenv(var) is None]

        if missing_vars:
            raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

        # Load environment variables
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.sql_endpoint = os.getenv("SQL_ENDPOINT")
        self.database = os.getenv("DATABASE_NAME")
        self.resource_url = os.getenv("RESOURCE_URL")

        # Setup database connection
        self.db = self._setup_database()

        # Setup LLM
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=self.openai_api_key
        )

        # Setup LangChain chains
        self.query_generator = create_sql_query_chain(self.llm, self.db)
        self.query_executor = QuerySQLDataBaseTool(db=self.db)

        # Setup simple in-memory cache
        self.cache = {}

    def _setup_database(self):
        # Azure Authentication
        credential = InteractiveBrowserCredential()
        token_object = credential.get_token(self.resource_url)
        token = token_object.token

        # Build connection string
        connection_string = (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server={self.sql_endpoint},1433;"
            f"Database={self.database};"
            "Encrypt=Yes;"
            "TrustServerCertificate=No;"
        )

        # Prepare token for SQL Server
        token_as_bytes = bytes(token, "UTF-8")
        encoded_bytes = bytes(chain.from_iterable(zip(token_as_bytes, repeat(0))))
        token_bytes = struct.pack("<i", len(encoded_bytes)) + encoded_bytes
        attrs_before = {1256: token_bytes}

        params = urllib.parse.quote_plus(connection_string)

        engine = sa.create_engine(
            f"mssql+pyodbc:///?odbc_connect={params}",
            connect_args={"attrs_before": attrs_before}
        )

        return SQLDatabase(engine)

    def ask(self, question: str):
        """Generates and executes a SQL query based on a natural language question."""

        if question in self.cache:
            print(f"⚡ Fetching from cache for: '{question}'")
            return self.cache[question]

        print(f"🧠 Generating SQL query for: '{question}'")
        sql_query = self.query_generator.invoke({"question": question})
        print(f"📝 Generated SQL Query:\n{sql_query}")

        print("🔎 Executing query...")
        result = self.query_executor.invoke(sql_query)

        # Store result in cache
        self.cache[question] = result

        return result


agent = FabricSQLAgent()

# First time - will generate and execute
result1 = agent.ask("List the top 3 clients with the highest portfolio value.")
print(result1)

# Second time - super fast from memory
result2 = agent.ask("List the top 3 clients with the highest portfolio value.")
print(result2)
