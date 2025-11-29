"""
Base DataProcessor class for PythonPHMS

Provides abstract base class for data processing with CRUD operations.
All data processors inherit from this base class.

Location: backend/utils/data_processor.py
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import pandas as pd

from backend.logger import logger


class DataProcessor(ABC):
    """Abstract base class for all data processors."""

    def __init__(self):
        """Initialize the data processor."""
        self.data: Optional[pd.DataFrame] = None
        self.source: Optional[Union[str, Path]] = None
        logger.info(f"Initialized {self.__class__.__name__}")

    @abstractmethod
    def connect(self, source: Union[str, Path], **kwargs) -> bool:
        """
        Connect to data source.

        Args:
            source: Data source location (file path, connection string, etc.)
            **kwargs: Additional connection parameters

        Returns:
            bool: True if connection successful, False otherwise
        """
        pass

    @abstractmethod
    def create(self, data: Union[pd.DataFrame, Dict, List], **kwargs) -> bool:
        """
        Create new data in the source.

        Args:
            data: Data to create (DataFrame, dict, or list)
            **kwargs: Additional parameters

        Returns:
            bool: True if creation successful, False otherwise
        """
        pass

    @abstractmethod
    def delete(self, criteria: Optional[Dict[str, Any]] = None, **kwargs) -> bool:
        """
        Delete data from the source.

        Args:
            criteria: Criteria for deletion (None deletes all)
            **kwargs: Additional parameters

        Returns:
            bool: True if deletion successful, False otherwise
        """
        pass

    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from data source.

        Returns:
            bool: True if disconnection successful, False otherwise
        """
        pass

    @abstractmethod
    def read(self, criteria: Optional[Dict[str, Any]] = None, **kwargs) -> Optional[pd.DataFrame]:
        """
        Read data from the source.

        Args:
            criteria: Filter criteria for reading
            **kwargs: Additional parameters

        Returns:
            pd.DataFrame: Data read from source, None if error
        """
        pass

    @abstractmethod
    def update(self, data: Union[pd.DataFrame, Dict], criteria: Optional[Dict[str, Any]] = None, **kwargs) -> bool:
        """
        Update existing data in the source.

        Args:
            data: New data values
            criteria: Criteria for which records to update
            **kwargs: Additional parameters

        Returns:
            bool: True if update successful, False otherwise
        """
        pass

    def get_data(self) -> Optional[pd.DataFrame]:
        """
        Get currently loaded data.

        Returns:
            pd.DataFrame: Currently loaded data
        """
        return self.data

    def get_info(self) -> Dict[str, Any]:
        """
        Get information about currently loaded data.

        Returns:
            dict: Information about the data
        """
        if self.data is None:
            return {"status": "No data loaded"}

        return {
            "rows": len(self.data),
            "columns": len(self.data.columns),
            "column_names": list(self.data.columns),
            "dtypes": self.data.dtypes.to_dict(),
            "memory_usage": self.data.memory_usage(deep=True).sum(),
            "source": str(self.source) if self.source else "Unknown"
        }

    def validate_data(self, data: Union[pd.DataFrame, Dict, List]) -> bool:
        """
        Validate input data.

        Args:
            data: Data to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            if isinstance(data, pd.DataFrame):
                return not data.empty
            elif isinstance(data, (dict, list)):
                return len(data) > 0
            return False
        except Exception as e:
            logger.error(f"Data validation error: {e}")
            return False