import requests
import pandas as pd
from Logging import LoggingConfig


class DataframeDownloader:
    def __init__(self, url):
        """
    Initializes the DataframeDownloader with a URL.
    :param url: URL pointing to a CSV file
    """
        self.url = url
        self.filename = 'data.csv'
        self.logger = LoggingConfig.get_class_logger('DataframeDownloader')

        self.logger.info(f"DataframeDownloader initialized with URL: {url}")
        self.logger.debug(f"Default filename set to: {self.filename}")

    def download_csv(self):
        """
    Downloads the CSV file from the given URL and saves it locally.
    """
        try:
            self.logger.info(f"Starting download from URL: {self.url}")

            response = requests.get(self.url)
            response.raise_for_status()  # Raise an exception for bad status codes

            file_size = len(response.content)
            self.logger.info(f"Downloaded {file_size} bytes from {self.url}")

            with open(self.filename, 'wb') as data_file:
                data_file.write(response.content)

            self.logger.info(f"File saved successfully as {self.filename}")
            print(f"File downloaded successfully as {self.filename}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Network error during download: {str(e)}")
            print(f"Network error downloading file: {e}")
            raise
        except IOError as e:
            self.logger.error(f"File I/O error: {str(e)}")
            print(f"File I/O error: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error during download: {str(e)}")
            print(f"Error downloading file: {e}")
            raise

    def load_dataframe(self):
        """
    Loads the downloaded CSV file into a pandas DataFrame.
    :return: pandas DataFrame
    """
        try:
            self.logger.info(f"Loading DataFrame from {self.filename}")

            df = pd.read_csv(self.filename)

            self.logger.info(f"DataFrame loaded successfully - Shape: {df.shape}")
            self.logger.debug(f"DataFrame columns: {list(df.columns)}")
            self.logger.debug(f"DataFrame dtypes: {df.dtypes.to_dict()}")

            # Log basic statistics
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                self.logger.debug(f"Numeric columns found: {list(numeric_cols)}")

            missing_values = df.isnull().sum().sum()
            if missing_values > 0:
                self.logger.warning(f"DataFrame contains {missing_values} missing values")

            return df

        except FileNotFoundError:
            self.logger.error(f"File not found: {self.filename}")
            print(f"Error: File {self.filename} not found")
            return None
        except pd.errors.EmptyDataError:
            self.logger.error(f"Empty CSV file: {self.filename}")
            print(f"Error: Empty CSV file {self.filename}")
            return None
        except pd.errors.ParserError as e:
            self.logger.error(f"CSV parsing error: {str(e)}")
            print(f"Error parsing CSV file: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error loading DataFrame: {str(e)}")
            print(f"Error loading DataFrame: {e}")
            return None

    def get_dataframe(self):
        """
    Combines downloading and loading of CSV data into a DataFrame.
    :return: pandas DataFrame
    """
        self.logger.info("Starting combined download and load operation")

        self.download_csv()
        df = self.load_dataframe()

        if df is not None:
            self.logger.info("Combined download and load operation completed successfully")
        else:
            self.logger.error("Combined download and load operation failed")

        return df