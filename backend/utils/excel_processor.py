"""
Excel Data Processor for PythonPHMS

Handles CRUD operations for Excel files (.xlsx, .xls).

Location: backend/utils/excel_processor.py
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from backend.logger import logger
from backend.utils.data_processor import DataProcessor


class ExcelDataProcessor(DataProcessor):
    """Data processor for Excel files with full CRUD operations."""

    def __init__(self):
        """Initialize Excel data processor."""
        super().__init__()
        self.sheet_name: Optional[str] = None
        self.file_path: Optional[Path] = None

    def connect(self, source: Union[str, Path], sheet_name: Union[str, int] = 0, **kwargs) -> bool:
        """
        Connect to Excel file.

        Args:
            source: Path to Excel file
            sheet_name: Sheet name or index to use (default: 0)
            **kwargs: Additional parameters for pd.read_excel

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.file_path = Path(source)
            self.source = self.file_path
            self.sheet_name = sheet_name

            if not self.file_path.exists():
                logger.error(f"Excel file not found: {self.file_path}")
                return False

            if self.file_path.suffix.lower() not in ['.xlsx', '.xls', '.xlsm']:
                logger.error(f"Invalid Excel file format: {self.file_path.suffix}")
                return False

            logger.info(f"Connected to Excel file: {self.file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Excel file: {e}")
            return False

    def create(self, data: Union[pd.DataFrame, Dict, List], sheet_name: Optional[str] = None,
               mode: str = 'append', **kwargs) -> bool:
        """
        Create/write new data to Excel file.

        Args:
            data: Data to write (DataFrame, dict, or list)
            sheet_name: Sheet name (uses connected sheet if None)
            mode: 'append' to add to existing, 'replace' to overwrite sheet
            **kwargs: Additional parameters for DataFrame.to_excel

        Returns:
            bool: True if creation successful, False otherwise
        """
        try:
            if self.file_path is None:
                logger.error("No Excel file connected. Call connect() first.")
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

            target_sheet = sheet_name or self.sheet_name or 'Sheet1'

            if mode == 'append' and self.file_path.exists():
                # Append to existing file
                with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a',
                                    if_sheet_exists='overlay') as writer:
                    # Read existing data
                    try:
                        existing_df = pd.read_excel(self.file_path, sheet_name=target_sheet)
                        combined_df = pd.concat([existing_df, df], ignore_index=True)
                    except ValueError:
                        # Sheet doesn't exist, create new
                        combined_df = df

                    combined_df.to_excel(writer, sheet_name=target_sheet, index=False, **kwargs)
            else:
                # Replace or create new
                with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='w') as writer:
                    df.to_excel(writer, sheet_name=target_sheet, index=False, **kwargs)

            logger.info(f"Created/wrote {len(df)} rows to Excel sheet '{target_sheet}'")
            return True

        except Exception as e:
            logger.error(f"Failed to create data in Excel: {e}")
            return False

    def delete(self, criteria: Optional[Dict[str, Any]] = None, sheet_name: Optional[str] = None, **kwargs) -> bool:
        """
        Delete data from Excel file based on criteria.

        Args:
            criteria: Dictionary of column:value pairs to match for deletion
                     None deletes all data (clears sheet)
            sheet_name: Sheet name (uses connected sheet if None)
            **kwargs: Additional parameters

        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            if self.file_path is None:
                logger.error("No Excel file connected. Call connect() first.")
                return False

            target_sheet = sheet_name or self.sheet_name

            # Read current data
            df = pd.read_excel(self.file_path, sheet_name=target_sheet)
            original_count = len(df)

            if criteria is None:
                # Delete all data (keep headers)
                df = pd.DataFrame(columns=df.columns)
            else:
                # Delete rows matching criteria
                mask = pd.Series([True] * len(df))
                for column, value in criteria.items():
                    if column in df.columns:
                        mask &= (df[column] == value)

                df = df[~mask]

            # Write back to Excel
            with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a',
                                if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=target_sheet, index=False)

            deleted_count = original_count - len(df)
            logger.info(f"Deleted {deleted_count} rows from Excel sheet '{target_sheet}'")
            return True

        except Exception as e:
            logger.error(f"Failed to delete data from Excel: {e}")
            return False

    def disconnect(self) -> bool:
        """
        Disconnect from Excel file.

        Returns:
            bool: True if disconnection successful
        """
        try:
            self.data = None
            self.file_path = None
            self.sheet_name = None
            self.source = None
            logger.info("Disconnected from Excel file")
            return True
        except Exception as e:
            logger.error(f"Error during disconnection: {e}")
            return False

    def read(self, criteria: Optional[Dict[str, Any]] = None, sheet_name: Optional[str] = None, **kwargs) -> Optional[
        pd.DataFrame]:
        """
        Read data from Excel file.

        Args:
            criteria: Dictionary of column:value pairs to filter data
            sheet_name: Sheet name (uses connected sheet if None)
            **kwargs: Additional parameters for pd.read_excel

        Returns:
            pd.DataFrame: Data read from Excel, None if error
        """
        try:
            if self.file_path is None:
                logger.error("No Excel file connected. Call connect() first.")
                return None

            target_sheet = sheet_name or self.sheet_name

            # Read Excel file
            df = pd.read_excel(self.file_path, sheet_name=target_sheet, **kwargs)

            # Apply criteria if provided
            if criteria:
                mask = pd.Series([True] * len(df))
                for column, value in criteria.items():
                    if column in df.columns:
                        mask &= (df[column] == value)
                    else:
                        logger.warning(f"Column '{column}' not found in data")

                df = df[mask]

            self.data = df
            logger.info(f"Read {len(df)} rows from Excel sheet '{target_sheet}'")
            return df

        except Exception as e:
            logger.error(f"Failed to read Excel file: {e}")
            return None

    def update(self, data: Union[pd.DataFrame, Dict], criteria: Optional[Dict[str, Any]] = None,
               sheet_name: Optional[str] = None, **kwargs) -> bool:
        """
        Update existing data in Excel file.

        Args:
            data: New data values (dict of column:value pairs to update)
            criteria: Dictionary of column:value pairs to identify rows to update
            sheet_name: Sheet name (uses connected sheet if None)
            **kwargs: Additional parameters

        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            if self.file_path is None:
                logger.error("No Excel file connected. Call connect() first.")
                return False

            target_sheet = sheet_name or self.sheet_name

            # Read current data
            df = pd.read_excel(self.file_path, sheet_name=target_sheet)

            if criteria is None:
                logger.error("Criteria required for update operation")
                return False

            # Find rows matching criteria
            mask = pd.Series([True] * len(df))
            for column, value in criteria.items():
                if column in df.columns:
                    mask &= (df[column] == value)

            # Update matching rows
            if isinstance(data, dict):
                for column, value in data.items():
                    if column in df.columns:
                        df.loc[mask, column] = value
            elif isinstance(data, pd.DataFrame):
                df.loc[mask] = data.values

            # Write back to Excel
            with pd.ExcelWriter(self.file_path, engine='openpyxl', mode='a',
                                if_sheet_exists='replace') as writer:
                df.to_excel(writer, sheet_name=target_sheet, index=False)

            updated_count = mask.sum()
            logger.info(f"Updated {updated_count} rows in Excel sheet '{target_sheet}'")
            return True

        except Exception as e:
            logger.error(f"Failed to update Excel data: {e}")
            return False

    def get_sheet_names(self) -> Optional[List[str]]:
        """
        Get list of sheet names in Excel file.

        Returns:
            List[str]: List of sheet names, None if error
        """
        try:
            if self.file_path is None:
                logger.error("No Excel file connected")
                return None

            excel_file = pd.ExcelFile(self.file_path)
            return excel_file.sheet_names

        except Exception as e:
            logger.error(f"Failed to get sheet names: {e}")
            return None

    def load_csv(self, filepath: Union[str, Path], **kwargs) -> Optional[pd.DataFrame]:
        """
        Load CSV file (legacy compatibility method).

        Args:
            filepath: Path to CSV file
            **kwargs: Additional parameters for pd.read_csv

        Returns:
            pd.DataFrame: Loaded data, None if error
        """
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                logger.error(f"CSV file not found: {filepath}")
                return None

            df = pd.read_csv(filepath, **kwargs)
            self.data = df
            self.source = filepath
            logger.info(f"Loaded {len(df)} rows from CSV file")
            return df

        except Exception as e:
            logger.error(f"Failed to load CSV file: {e}")
            return None

    def load_excel(self, filepath: Union[str, Path], sheet_name: Union[str, int] = 0, **kwargs) -> Optional[
        pd.DataFrame]:
        """
        Load Excel file (legacy compatibility method).

        Args:
            filepath: Path to Excel file
            sheet_name: Sheet name or index
            **kwargs: Additional parameters for pd.read_excel

        Returns:
            pd.DataFrame: Loaded data, None if error
        """
        if self.connect(filepath, sheet_name):
            return self.read(sheet_name=sheet_name, **kwargs)
        return None

    def load_tsv(self, filepath: Union[str, Path], **kwargs) -> Optional[pd.DataFrame]:
        """
        Load TSV file (legacy compatibility method).

        Args:
            filepath: Path to TSV file
            **kwargs: Additional parameters for pd.read_csv

        Returns:
            pd.DataFrame: Loaded data, None if error
        """
        try:
            filepath = Path(filepath)
            if not filepath.exists():
                logger.error(f"TSV file not found: {filepath}")
                return None

            df = pd.read_csv(filepath, sep='\t', **kwargs)
            self.data = df
            self.source = filepath
            logger.info(f"Loaded {len(df)} rows from TSV file")
            return df

        except Exception as e:
            logger.error(f"Failed to load TSV file: {e}")
            return None