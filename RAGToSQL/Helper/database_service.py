import pandas as pd
from sqlalchemy.engine import Engine

class DatabaseService:
    """Reusable service to run SQL queries using a SQLAlchemy engine."""

    def __init__(self, engine: Engine):
        """
        Initialize the DatabaseService.

        Args:
            engine (sqlalchemy.Engine): SQLAlchemy engine object.
        """
        self.engine = engine

    def run_sql(self, sql: str) -> pd.DataFrame:
        """
        Execute a SQL query and return the results as a pandas DataFrame.

        Args:
            sql (str): SQL query string.

        Returns:
            pd.DataFrame: Query results.
        """
        try:
            with self.engine.connect() as connection:
                df = pd.read_sql_query(sql, connection)
                return df
        except Exception as e:
            print(f"❌ Error executing SQL: {e}")
            raise

