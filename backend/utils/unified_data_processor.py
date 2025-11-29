"""
Unified Data Processor Interface for PythonPHMS

Provides a single interface to work with multiple data sources:
- Excel files (.xlsx, .xls)
- CSV/TSV text files
- PostgreSQL database

This module provides both the new CRUD-based interface and legacy compatibility methods.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from backend.logger import logger
from backend.utils.excel_processor import ExcelDataProcessor
from backend.utils.database_processor import DatabaseDataProcessor


class DataProcessor:
    """
    Unified data processor interface supporting multiple data sources.

    This class provides a simplified interface to work with different data sources
    while maintaining the ability to use specialized processors for advanced operations.
    """

    def __init__(self):
        """Initialize unified data processor."""
        self.excel_processor = ExcelDataProcessor()
        self.database_processor = DatabaseDataProcessor()
        self.current_processor = None
        logger.info("Initialized unified DataProcessor")

    # ========================
    # Legacy Compatibility Methods (for test compatibility)
    # ========================

    def close_database(self) -> bool:
        """Close database connection (legacy method)."""
        return self.database_processor.disconnect()

    def connect_database(self):
        """Connect to database (legacy method)."""
        if self.database_processor.connect():
            self.current_processor = self.database_processor
            return self.database_processor.connection
        return None

    def execute_query(self, query: str, params: Optional[tuple] = None) -> Optional[pd.DataFrame]:
        """Execute SQL query (legacy method)."""
        return self.database_processor.execute_query(query, params)

    def load_csv(self, filepath: Union[str, Path], **kwargs) -> Optional[pd.DataFrame]:
        """
        Load CSV file.

        Args:
            filepath: Path to CSV file
            **kwargs: Additional parameters for pd.read_csv

        Returns:
            pd.DataFrame: Loaded data, None if error
        """
        return self.excel_processor.load_csv(filepath, **kwargs)

    def load_data(self, source: Union[str, Path], source_type: Optional[str] = None, **kwargs) -> Optional[
        pd.DataFrame]:
        """
        Load data from any supported source with auto-detection.

        Args:
            source: Path to file or connection string
            source_type: 'csv', 'tsv', 'excel', 'database', or None for auto-detect
            **kwargs: Additional parameters

        Returns:
            pd.DataFrame: Loaded data, None if error
        """
        try:
            source_path = Path(source) if isinstance(source, str) else source

            # Auto-detect if not specified
            if source_type is None:
                if isinstance(source_path, Path):
                    suffix = source_path.suffix.lower()
                    if suffix == '.csv':
                        source_type = 'csv'
                    elif suffix == '.tsv':
                        source_type = 'tsv'
                    elif suffix in ['.xlsx', '.xls', '.xlsm']:
                        source_type = 'excel'
                else:
                    logger.error("Cannot auto-detect source type")
                    return None

            # Route to appropriate loader
            if source_type == 'csv':
                return self.load_csv(source_path, **kwargs)
            elif source_type == 'tsv':
                return self.load_tsv(source_path, **kwargs)
            elif source_type == 'excel':
                return self.load_excel(source_path, **kwargs)
            elif source_type == 'database':
                return self.load_table(source, **kwargs)
            else:
                logger.error(f"Unsupported source type: {source_type}")
                return None

        except Exception as e:
            logger.error(f"Failed to load data: {e}")
            return None

    def load_excel(self, filepath: Union[str, Path], sheet_name: Union[str, int] = 0, **kwargs) -> Optional[
        pd.DataFrame]:
        """
        Load Excel file.

        Args:
            filepath: Path to Excel file
            sheet_name: Sheet name or index
            **kwargs: Additional parameters

        Returns:
            pd.DataFrame: Loaded data, None if error
        """
        result = self.excel_processor.load_excel(filepath, sheet_name, **kwargs)
        if result is not None:
            self.current_processor = self.excel_processor
        return result

    def load_table(self, table_name: str, **kwargs) -> Optional[pd.DataFrame]:
        """
        Load table from database.

        Args:
            table_name: Table name
            **kwargs: Additional parameters

        Returns:
            pd.DataFrame: Table data, None if error
        """
        result = self.database_processor.load_table(table_name, **kwargs)
        if result is not None:
            self.current_processor = self.database_processor
        return result

    def load_tsv(self, filepath: Union[str, Path], **kwargs) -> Optional[pd.DataFrame]:
        """
        Load TSV file.

        Args:
            filepath: Path to TSV file
            **kwargs: Additional parameters

        Returns:
            pd.DataFrame: Loaded data, None if error
        """
        return self.excel_processor.load_tsv(filepath, **kwargs)

    # ========================
    # Excel CRUD Operations
    # ========================

    def excel_connect(self, filepath: Union[str, Path], sheet_name: Union[str, int] = 0, **kwargs) -> bool:
        """
        Connect to Excel file.

        Args:
            filepath: Path to Excel file
            sheet_name: Sheet name or index
            **kwargs: Additional parameters

        Returns:
            bool: True if successful
        """
        result = self.excel_processor.connect(filepath, sheet_name, **kwargs)
        if result:
            self.current_processor = self.excel_processor
        return result

    def excel_create(self, data: Union[pd.DataFrame, Dict, List], sheet_name: Optional[str] = None,
                     mode: str = 'append', **kwargs) -> bool:
        """
        Create/write data to Excel file.

        Args:
            data: Data to write
            sheet_name: Sheet name
            mode: 'append' or 'replace'
            **kwargs: Additional parameters

        Returns:
            bool: True if successful
        """
        return self.excel_processor.create(data, sheet_name, mode, **kwargs)

    def excel_delete(self, criteria: Optional[Dict[str, Any]] = None, sheet_name: Optional[str] = None,
                     **kwargs) -> bool:
        """
        Delete data from Excel file.

        Args:
            criteria: Criteria for deletion
            sheet_name: Sheet name
            **kwargs: Additional parameters

        Returns:
            bool: True if successful
        """
        return self.excel_processor.delete(criteria, sheet_name, **kwargs)

    def excel_disconnect(self) -> bool:
        """Disconnect from Excel file."""
        return self.excel_processor.disconnect()

    def excel_read(self, criteria: Optional[Dict[str, Any]] = None, sheet_name: Optional[str] = None, **kwargs) -> \
    Optional[pd.DataFrame]:
        """
        Read data from Excel file.

        Args:
            criteria: Filter criteria
            sheet_name: Sheet name
            **kwargs: Additional parameters

        Returns:
            pd.DataFrame: Data read from Excel
        """
        return self.excel_processor.read(criteria, sheet_name, **kwargs)

    def excel_update(self, data: Union[pd.DataFrame, Dict], criteria: Optional[Dict[str, Any]] = None,
                     sheet_name: Optional[str] = None, **kwargs) -> bool:
        """
        Update data in Excel file.

        Args:
            data: New data values
            criteria: Criteria for rows to update
            sheet_name: Sheet name
            **kwargs: Additional parameters

        Returns:
            bool: True if successful
        """
        return self.excel_processor.update(data, criteria, sheet_name, **kwargs)

    # ========================
    # Database CRUD Operations
    # ========================

    def db_connect(self, source: Optional[str] = None, use_pool: bool = True, **kwargs) -> bool:
        """
        Connect to database.

        Args:
            source: Connection string or None for env variables
            use_pool: Use connection pooling
            **kwargs: Additional parameters

        Returns:
            bool: True if successful
        """
        result = self.database_processor.connect(source, use_pool, **kwargs)
        if result:
            self.current_processor = self.database_processor
        return result

    def db_create(self, data: Union[pd.DataFrame, Dict, List], table_name: str,
                  if_exists: str = 'append', **kwargs) -> bool:
        """
        Create/insert data into database table.

        Args:
            data: Data to insert
            table_name: Target table
            if_exists: 'append', 'replace', or 'fail'
            **kwargs: Additional parameters

        Returns:
            bool: True if successful
        """
        return self.database_processor.create(data, table_name, if_exists, **kwargs)

    def db_delete(self, criteria: Optional[Dict[str, Any]] = None, table_name: Optional[str] = None, **kwargs) -> bool:
        """
        Delete data from database table.

        Args:
            criteria: Criteria for deletion
            table_name: Target table
            **kwargs: Additional parameters

        Returns:
            bool: True if successful
        """
        return self.database_processor.delete(criteria, table_name, **kwargs)

    def db_disconnect(self) -> bool:
        """Disconnect from database."""
        return self.database_processor.disconnect()

    def db_read(self, criteria: Optional[Dict[str, Any]] = None, table_name: Optional[str] = None,
                columns: Optional[List[str]] = None, limit: Optional[int] = None, **kwargs) -> Optional[pd.DataFrame]:
        """
        Read data from database table.

        Args:
            criteria: Filter criteria
            table_name: Target table
            columns: Columns to select
            limit: Maximum rows
            **kwargs: Additional parameters

        Returns:
            pd.DataFrame: Data read from database
        """
        return self.database_processor.read(criteria, table_name, columns, limit, **kwargs)

    def db_update(self, data: Union[pd.DataFrame, Dict], criteria: Optional[Dict[str, Any]] = None,
                  table_name: Optional[str] = None, **kwargs) -> bool:
        """
        Update data in database table.

        Args:
            data: New data values
            criteria: Criteria for rows to update
            table_name: Target table
            **kwargs: Additional parameters

        Returns:
            bool: True if successful
        """
        return self.database_processor.update(data, criteria, table_name, **kwargs)

    # ========================
    # Utility Methods
    # ========================

    def get_current_data(self) -> Optional[pd.DataFrame]:
        """Get currently loaded data from active processor."""
        if self.current_processor:
            return self.current_processor.get_data()
        return None

    def get_excel_sheets(self) -> Optional[List[str]]:
        """Get list of sheets in connected Excel file."""
        return self.excel_processor.get_sheet_names()

    def get_info(self) -> Dict[str, Any]:
        """Get information about currently loaded data."""
        if self.current_processor:
            return self.current_processor.get_info()
        return {"status": "No processor active"}

    def get_tables(self) -> Optional[List[str]]:
        """Get list of tables in connected database."""
        return self.database_processor.get_tables()