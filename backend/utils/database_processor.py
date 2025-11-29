"""
Database Data Processor for PythonPHMS

Handles CRUD operations for PostgreSQL database.

Location: backend/utils/database_processor.py
"""

from typing import Any, Dict, List, Optional, Union
from dotenv import load_dotenv
import pandas as pd
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
import os

from backend.logger import logger
from backend.utils.data_processor import DataProcessor


class DatabaseDataProcessor(DataProcessor):
    """Data processor for PostgreSQL database with full CRUD operations."""

    def __init__(self):
        """Initialize database data processor."""
        super().__init__()
        self.connection = None
        self.connection_pool = None
        self.current_table: Optional[str] = None

    def connect(self, source: Optional[str] = None, use_pool: bool = True, min_conn: int = 1,
                max_conn: int = 10, **kwargs) -> bool:
        try:
            if source:
                conn_params = source
            else:
                conn_params = {
                    'host': os.getenv('DB_HOST', 'localhost'),
                    'port': os.getenv('DB_PORT', '5432'),
                    'database': os.getenv('DB_NAME', 'postgres'),
                    'user': os.getenv('DB_USER', 'postgres'),
                    'password': os.getenv('DB_PASSWORD', '')
                }
                conn_params.update(kwargs)

            if use_pool:
                # Create connection pool
                self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                    min_conn, max_conn, **conn_params if isinstance(conn_params, dict) else {'dsn': conn_params}
                )
                self.connection = self.connection_pool.getconn()
            else:
                # Single connection
                if isinstance(conn_params, dict):
                    self.connection = psycopg2.connect(**conn_params)
                else:
                    self.connection = psycopg2.connect(conn_params)

            self.source = "PostgreSQL Database"
            logger.info("Successfully connected to PostgreSQL database")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    def create(self, data: Union[pd.DataFrame, Dict, List], table_name: str,
               if_exists: str = 'append', **kwargs) -> bool:
        try:
            if self.connection is None:
                logger.error("No database connection. Call connect() first.")
                return False

            # Convert data to DataFrame
            if isinstance(data, dict):
                df = pd.DataFrame([data]) if not isinstance(list(data.values())[0], list) else pd.DataFrame(data)
            elif isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, pd.DataFrame):
                df = data
            else:
                logger.error(f"Unsupported data type: {type(data)}")
                return False

            if not self.validate_data(df):
                logger.error("Invalid data provided for creation")
                return False

            # Use pandas to_sql for insertion
            from sqlalchemy import create_engine

            # Build SQLAlchemy connection string
            db_url = self._get_sqlalchemy_url()
            engine = create_engine(db_url)

            df.to_sql(table_name, engine, if_exists=if_exists, index=False, **kwargs)

            logger.info(f"Created/inserted {len(df)} rows into table '{table_name}'")
            return True

        except Exception as e:
            logger.error(f"Failed to create data in database: {e}")
            return False

    def delete(self, criteria: Optional[Dict[str, Any]] = None, table_name: Optional[str] = None, **kwargs) -> bool:

        try:
            if self.connection is None:
                logger.error("No database connection. Call connect() first.")
                return False

            target_table = table_name or self.current_table
            if not target_table:
                logger.error("No table specified for deletion")
                return False

            cursor = self.connection.cursor()

            if criteria is None:
                # Delete all data
                query = sql.SQL("TRUNCATE TABLE {}").format(sql.Identifier(target_table))
                cursor.execute(query)
            else:
                # Delete with WHERE clause
                where_clauses = []
                values = []

                for column, value in criteria.items():
                    where_clauses.append(sql.SQL("{} = %s").format(sql.Identifier(column)))
                    values.append(value)

                query = sql.SQL("DELETE FROM {} WHERE {}").format(
                    sql.Identifier(target_table),
                    sql.SQL(" AND ").join(where_clauses)
                )
                cursor.execute(query, values)

            self.connection.commit()
            deleted_count = cursor.rowcount
            cursor.close()

            logger.info(f"Deleted {deleted_count} rows from table '{target_table}'")
            return True

        except Exception as e:
            if self.connection:
                self.connection.rollback()
            logger.error(f"Failed to delete data from database: {e}")
            return False

    def disconnect(self) -> bool:

        try:
            if self.connection:
                if self.connection_pool:
                    self.connection_pool.putconn(self.connection)
                    self.connection_pool.closeall()
                else:
                    self.connection.close()

                self.connection = None
                self.connection_pool = None
                self.data = None
                self.current_table = None
                self.source = None

                logger.info("Disconnected from database")
            return True

        except Exception as e:
            logger.error(f"Error during disconnection: {e}")
            return False

    def execute_query(self, query: str, params: Optional[tuple] = None, **kwargs) -> Optional[pd.DataFrame]:

        try:
            if self.connection is None:
                logger.error("No database connection. Call connect() first.")
                return None

            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)

            # Check if query returns results
            if cursor.description:
                results = cursor.fetchall()
                df = pd.DataFrame(results)
                cursor.close()
                logger.info(f"Query returned {len(df)} rows")
                return df
            else:
                # Query didn't return results (INSERT, UPDATE, etc.)
                self.connection.commit()
                cursor.close()
                logger.info("Query executed successfully")
                return pd.DataFrame()

        except Exception as e:
            if self.connection:
                self.connection.rollback()
            logger.error(f"Failed to execute query: {e}")
            return None

    def load_table(self, table_name: str, **kwargs) -> Optional[pd.DataFrame]:

        self.current_table = table_name
        return self.read(table_name=table_name, **kwargs)

    def read(self, criteria: Optional[Dict[str, Any]] = None, table_name: Optional[str] = None,
             columns: Optional[List[str]] = None, limit: Optional[int] = None, **kwargs) -> Optional[pd.DataFrame]:
        try:
            if self.connection is None:
                logger.error("No database connection. Call connect() first.")
                return None

            target_table = table_name or self.current_table
            if not target_table:
                logger.error("No table specified for reading")
                return None

            # Build SELECT clause
            if columns:
                select_clause = sql.SQL(", ").join([sql.Identifier(col) for col in columns])
            else:
                select_clause = sql.SQL("*")

            # Build WHERE clause
            where_clause = sql.SQL("")
            values = []

            if criteria:
                where_parts = []
                for column, value in criteria.items():
                    where_parts.append(sql.SQL("{} = %s").format(sql.Identifier(column)))
                    values.append(value)

                where_clause = sql.SQL(" WHERE {}").format(sql.SQL(" AND ").join(where_parts))

            # Build LIMIT clause
            limit_clause = sql.SQL("")
            if limit:
                limit_clause = sql.SQL(" LIMIT {}").format(sql.Literal(limit))

            # Construct full query
            query = sql.SQL("SELECT {} FROM {}{}{}").format(
                select_clause,
                sql.Identifier(target_table),
                where_clause,
                limit_clause
            )

            cursor = self.connection.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, values)
            results = cursor.fetchall()

            df = pd.DataFrame(results)
            cursor.close()

            self.data = df
            self.current_table = target_table

            logger.info(f"Read {len(df)} rows from table '{target_table}'")
            return df

        except Exception as e:
            logger.error(f"Failed to read from database: {e}")
            return None

    def update(self, data: Union[pd.DataFrame, Dict], criteria: Optional[Dict[str, Any]] = None,
               table_name: Optional[str] = None, **kwargs) -> bool:
        try:
            if self.connection is None:
                logger.error("No database connection. Call connect() first.")
                return False

            target_table = table_name or self.current_table
            if not target_table:
                logger.error("No table specified for update")
                return False

            if criteria is None:
                logger.error("Criteria required for update operation")
                return False

            # Convert data to dict if needed
            if isinstance(data, pd.DataFrame):
                if len(data) != 1:
                    logger.error("DataFrame must have exactly one row for update")
                    return False
                data = data.iloc[0].to_dict()
            elif not isinstance(data, dict):
                logger.error("Data must be dict or single-row DataFrame")
                return False

            # Build SET clause
            set_parts = []
            set_values = []
            for column, value in data.items():
                set_parts.append(sql.SQL("{} = %s").format(sql.Identifier(column)))
                set_values.append(value)

            # Build WHERE clause
            where_parts = []
            where_values = []
            for column, value in criteria.items():
                where_parts.append(sql.SQL("{} = %s").format(sql.Identifier(column)))
                where_values.append(value)

            # Construct full query
            query = sql.SQL("UPDATE {} SET {} WHERE {}").format(
                sql.Identifier(target_table),
                sql.SQL(", ").join(set_parts),
                sql.SQL(" AND ").join(where_parts)
            )

            cursor = self.connection.cursor()
            cursor.execute(query, set_values + where_values)
            self.connection.commit()

            updated_count = cursor.rowcount
            cursor.close()

            logger.info(f"Updated {updated_count} rows in table '{target_table}'")
            return True

        except Exception as e:
            if self.connection:
                self.connection.rollback()
            logger.error(f"Failed to update database: {e}")
            return False

    def _get_sqlalchemy_url(self) -> str:
        """
        Get SQLAlchemy connection URL.

        Returns:
            str: SQLAlchemy connection string
        """
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 'pythonphms')
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', '')

        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    def close_database(self):
        """Close database connection (legacy compatibility method)."""
        return self.disconnect()

    def connect_database(self):
        """Connect to database (legacy compatibility method)."""
        if self.connect():
            return self.connection
        return None

    def get_tables(self) -> Optional[List[str]]:
        """
        Get list of tables in database.

        Returns:
            List[str]: List of table names, None if error
        """
        try:
            query = """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name \
                    """
            df = self.execute_query(query)
            return df['table_name'].tolist() if df is not None and not df.empty else []

        except Exception as e:
            logger.error(f"Failed to get table list: {e}")
            return None



load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

cursor = conn.cursor()
cursor.execute("SELECT version();")
print(cursor.fetchone()[0])
cursor.execute("select * from personal_data")
print(cursor.fetchall())
cursor.close()
conn.close()