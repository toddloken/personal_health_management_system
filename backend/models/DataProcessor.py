import pandas as pd
from abc import ABC, abstractmethod
from Logging import LoggingConfig


class ParentDataProcessor(ABC):
    """
    Abstract base class for data processing with common utility methods.
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initializes the ParentDataProcessor with a Pandas DataFrame.

        :param df: Pandas DataFrame to process
        """
        self.df = df
        self.logger = LoggingConfig.get_class_logger(self.__class__.__name__)

    def check_duplicates(self):
        """Checks for duplicate rows in the dataset and prints the count."""
        duplicate_count = self.df.duplicated().sum()
        self.logger.info(f'Duplicate check completed - Found {duplicate_count} duplicate rows')
        print('Number of Duplicated Rows:', duplicate_count)

        if duplicate_count > 0:
            self.logger.warning(f"Dataset contains {duplicate_count} duplicate rows")

    def display_info(self):
        """Displays the number of features and instances in the dataset."""
        features = self.df.shape[1]
        instances = self.df.shape[0]

        self.logger.info(f'Dataset info - Features: {features}, Instances: {instances}')
        print('Number of Features In Dataset:', features)
        print('Number of Instances In Dataset:', instances)

    def drop_name_column(self):
        """Drops the 'name' column if it exists."""
        if 'name' in self.df.columns:
            self.df.drop(columns=['name'], inplace=True)
            self.logger.info("'name' column dropped successfully")
            print("'name' column dropped.")
        else:
            self.logger.debug("No 'name' column found to drop")
            print("No 'name' column found.")

    def drop_raw_notes_column(self):
        """Drops the 'raw_notes' column if it exists."""
        if 'raw_notes' in self.df.columns:
            self.df.drop(columns=['raw_notes'], inplace=True)
            self.logger.info("'raw_notes' column dropped successfully")
            print("'raw_notes' column dropped.")
        else:
            self.logger.debug("No 'raw_notes' column found to drop")
            print("No 'raw_notes' column found.")

    def fill_nan_with_mean(self):
        """
        Identifies numeric columns with NaN values and replaces them with column means.
        """
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        nan_cols = numeric_cols[self.df[numeric_cols].isnull().any()]

        if len(nan_cols) > 0:
            self.logger.info(f"Found NaN values in {len(nan_cols)} numeric columns: {list(nan_cols)}")

            # Log statistics before filling
            for col in nan_cols:
                nan_count = self.df[col].isnull().sum()
                mean_value = self.df[col].mean()
                self.logger.debug(f"Column '{col}': {nan_count} NaN values, mean: {mean_value:.4f}")

            self.df[numeric_cols] = self.df[numeric_cols].fillna(self.df[numeric_cols].mean())
            self.logger.info(f"NaN values filled with mean for columns: {list(nan_cols)}")
            print(f"NaN values filled with mean for columns: {list(nan_cols)}")
        else:
            self.logger.info("No NaN values found in numeric columns")
            print("No NaN values found in numeric columns.")

    @abstractmethod
    def process(self):
        """Abstract method for processing pipeline - must be implemented by subclasses."""
        pass


class DataProcessor(ParentDataProcessor):
    """
    Data processor for health metrics with status classification and date conversion.
    """

    def convert_pdate_to_sas_date(self):
        """
        Converts 'pdate' column to SAS date format (days since 1960-01-01).
        Replaces the pdate column with integer representation.
        """
        if 'pdate' in self.df.columns:
            try:
                # Convert to datetime if not already
                self.df['pdate'] = pd.to_datetime(self.df['pdate'])

                # SAS date origin: January 1, 1960
                sas_origin = pd.Timestamp('1960-01-01')

                # Calculate days from origin
                self.df['pdate'] = (self.df['pdate'] - sas_origin).dt.days

                # Convert to int32 for efficiency
                self.df['pdate'] = self.df['pdate'].astype('int32')

                min_date = self.df['pdate'].min()
                max_date = self.df['pdate'].max()

                self.logger.info(
                    f"'pdate' column converted to SAS date format. "
                    f"Range: {min_date} to {max_date} days since 1960-01-01"
                )
                print(f"'pdate' converted to SAS date. Range: {min_date} to {max_date}")

            except Exception as e:
                self.logger.error(f"Failed to convert 'pdate' to SAS date: {e}")
                print(f"Error converting 'pdate': {e}")
        else:
            self.logger.debug("No 'pdate' column found to convert")
            print("No 'pdate' column found.")

    def convert_status(self):
        """Converts the 'status' column to uint8 if it exists."""
        if 'status' in self.df.columns:
            original_dtype = self.df['status'].dtype
            self.df['status'] = self.df['status'].astype('uint8')
            self.logger.info(f"'status' column converted from {original_dtype} to uint8")
            print("'status' column converted to uint8.")
        else:
            self.logger.debug("No 'status' column found to convert")
            print("No 'status' column found.")

    def create_status_column(self):
        """
        Creates 'status' column based on sleep_index threshold.
        status = 1 if sleep_index >= 74, otherwise 0.
        """
        if 'sleep_index' in self.df.columns:
            self.df['status'] = (self.df['sleep_index'] >= 74).astype('uint8')

            status_counts = self.df['status'].value_counts().to_dict()
            self.logger.info(
                f"'status' column created based on sleep_index >= 74. "
                f"Distribution: {status_counts}"
            )
            print(f"'status' column created. Distribution: {status_counts}")
        else:
            self.logger.warning("'sleep_index' column not found. Cannot create 'status' column.")
            print("'sleep_index' column not found. Cannot create 'status' column.")

    def process(self):
        """Runs all processing steps on the dataset."""
        self.logger.info("Starting data processing pipeline")

        self.display_info()
        self.convert_pdate_to_sas_date()
        self.drop_name_column()
        self.drop_raw_notes_column()
        self.display_info()
        self.create_status_column()
        self.convert_status()
        self.check_duplicates()
        self.fill_nan_with_mean()

        self.logger.info("Data processing pipeline completed successfully")
        return self.df


class DataProcessTimeSeries(DataProcessor):
    """
    Time series data processor that ensures data is sorted chronologically by pdate.
    """

    def process(self):
        """Runs all processing steps with time series sorting."""
        self.logger.info("Starting time series data processing pipeline")

        self.display_info()
        self.convert_pdate_to_sas_date()
        self.drop_name_column()
        self.drop_raw_notes_column()
        self.display_info()
        self.create_status_column()
        self.convert_status()
        self.check_duplicates()
        self.fill_nan_with_mean()
        self.sort_by_pdate()

        self.logger.info("Time series data processing pipeline completed successfully")
        return self.df

    def sort_by_pdate(self):
        """Sorts the DataFrame by pdate in ascending order for time series analysis."""
        if 'pdate' in self.df.columns:
            original_order = self.df['pdate'].iloc[0] if len(self.df) > 0 else None
            self.df.sort_values(by='pdate', ascending=True, inplace=True)
            self.df.reset_index(drop=True, inplace=True)

            new_order = self.df['pdate'].iloc[0] if len(self.df) > 0 else None
            self.logger.info(
                f"DataFrame sorted by 'pdate' in ascending order. "
                f"First date changed from {original_order} to {new_order}"
            )
            print(f"DataFrame sorted by 'pdate' in ascending chronological order.")
        else:
            self.logger.warning("No 'pdate' column found to sort")
            print("No 'pdate' column found for sorting.")