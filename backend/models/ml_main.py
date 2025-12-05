# ml_main.py

from dataclasses import dataclass

from DataProcessor import DataProcessor
from TrainTestSplit import TrainTestSplit
from ModelDecisionTree import DecisionTreeModel
from ModelRandomForest import RandomForestModel
from ModelSVM import SupportVectorMachineModel
from ModelLogisticRegression import LogisticRegressionModel
from ModelNaiveBayes import NaiveBayesModel
from ModelKNearestNeighbors import KNNModel
from ModelXGBoost import XGBoostModel
from ModelMetrics import ModelMetrics
from Logging import LoggingConfig

from scipy.stats import logistic  # keep if used elsewhere
import pandas as pd
import logging
import argparse
import sys

@dataclass
class PipelineConfig:
    data_path: str = "data.csv"
    output_file: str = "model_output.xlsx"
    log_mode: str = "both"
    log_level: str = "INFO"
    log_dir: str = "logs"
    log_filename: str | None = None

    # Database options
    data_source: str = "csv"  # csv | database
    table_name: str = "personal_data"
    db_criteria: dict | None = None
    db_columns: list[str] | None = None
    db_limit: int | None = None

def parse_args():
    parser = argparse.ArgumentParser(description='ML Pipeline with Configurable Logging')
    parser.add_argument('--log-mode', choices=['file', 'console', 'both'],
                        default='both', help='Logging output mode')
    parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        default='INFO', help='Logging level')
    parser.add_argument('--log-dir', default='logs', help='Log directory')
    parser.add_argument('--log-filename', help='Custom log filename')

    parser.add_argument('--data-path', default='data.csv',
                        help='Path to the input CSV file')
    parser.add_argument('--output-file', default='model_output.xlsx',
                        help='Path to save the metrics Excel file')

    # Database options
    parser.add_argument('--data-source', choices=['csv', 'database'],
                        default='csv', help='Data source type')
    parser.add_argument('--table-name', default='personal_data',
                        help='Database table name')
    parser.add_argument('--db-limit', type=int, help='Limit database rows')

    return parser.parse_args()

def setup_logger(config: PipelineConfig) -> logging.Logger:
    log_config = LoggingConfig(log_level=getattr(logging, config.log_level))
    logger = log_config.setup_logging(
        mode=config.log_mode,
        log_dir=config.log_dir,
        log_filename=config.log_filename
    )
    logger.info("Starting ML Pipeline execution")
    logger.info(
        f"Configuration - Log Mode: {config.log_mode}, "
        f"Log Level: {config.log_level}, "
        f"Data Path: {config.data_path}, Output File: {config.output_file}"
    )
    return logger

class MLPipeline:
    def __init__(self, config: PipelineConfig, logger: logging.Logger):
        self.config = config
        self.logger = logger

        # internal state
        self.df: pd.DataFrame | None = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.predictions: dict | None = None
        self.metrics_df: pd.DataFrame | None = None

    def load_data(self) -> pd.DataFrame:
        """
        Load data from configured source (CSV or database).

        Returns:
            pd.DataFrame: Loaded dataset

        Raises:
            ValueError: If data source is invalid or loading fails
        """
        if self.config.data_source == "database":
            return self.load_data_from_database()
        elif self.config.data_source == "csv":
            self.logger.info(f"Loading dataset from {self.config.data_path}")
            self.df = pd.read_csv(self.config.data_path)
            self.logger.info(f"Dataset loaded with shape: {self.df.shape}")
            return self.df
        else:
            raise ValueError(
                f"Invalid data source: {self.config.data_source}. "
                "Must be 'csv' or 'database'"
            )

    def load_data_from_database(self) -> pd.DataFrame:
        """
        Load data from PostgreSQL database.

        Returns:
            pd.DataFrame: Loaded dataset

        Raises:
            ValueError: If database connection fails
            Exception: If data loading fails
        """
        from backend.utils.database_processor import DatabaseDataProcessor

        self.logger.info(
            f"Loading dataset from database table '{self.config.table_name}'"
        )

        processor = DatabaseDataProcessor()

        try:
            if not processor.connect():
                raise ValueError("Failed to connect to database")

            self.df = processor.read(
                table_name=self.config.table_name,
                criteria=self.config.db_criteria,
                columns=self.config.db_columns,
                limit=self.config.db_limit
            )

            if self.df is None or self.df.empty:
                raise ValueError(
                    f"No data retrieved from table '{self.config.table_name}'"
                )

            self.logger.info(f"Dataset loaded with shape: {self.df.shape}")
            return self.df

        except Exception as e:
            self.logger.error(f"Failed to load data from database: {e}")
            raise

        finally:
            processor.disconnect()

    def process_data(self) -> pd.DataFrame:
        if self.df is None:
            raise ValueError("DataFrame is None. Call load_data() first.")

        self.logger.info("Starting data preprocessing")
        processor = DataProcessor(self.df)
        self.df = processor.process()
        self.logger.info("Data preprocessing completed")
        return self.df

    def split_data(self):
        if self.df is None:
            raise ValueError("DataFrame is None. Call load_data()/process_data() first.")

        self.logger.info("Performing train-test split with balancing")
        splitter = TrainTestSplit(self.df)
        self.X_train, self.X_test, self.y_train, self.y_test = splitter.balance_and_split()
        self.logger.info(
            f"Train set shape: {self.X_train.shape}, Test set shape: {self.X_test.shape}"
        )
        return self.X_train, self.X_test, self.y_train, self.y_test

    def train_models(self) -> dict:
        if any(v is None for v in (self.X_train, self.X_test, self.y_train, self.y_test)):
            raise ValueError("Train/test data not set. Call split_data() first.")

        self.logger.info("Starting model training phase")

        self.logger.info("Training Decision Tree model")
        dt_model = DecisionTreeModel(self.X_train, self.y_train, self.X_test, self.y_test)
        decision_tree_preds = dt_model.train_best_model()

        self.logger.info("Training Random Forest model")
        rf_model = RandomForestModel(self.X_train, self.X_test, self.y_train, self.y_test)
        random_forest_preds = rf_model.train_best_model()

        self.logger.info("Training Support Vector Machine model")
        svm_model = SupportVectorMachineModel(self.X_train, self.X_test, self.y_train, self.y_test)
        svm_preds = svm_model.train_best_model()

        self.logger.info("Training Logistic Regression model")
        lr_model = LogisticRegressionModel(self.X_train, self.X_test, self.y_train, self.y_test)
        logistic_regression_preds = lr_model.train_model()

        self.logger.info("Training Naive Bayes model")
        nb_model = NaiveBayesModel(self.X_train, self.X_test, self.y_train, self.y_test)
        naive_bayes_preds = nb_model.train_model()

        self.logger.info("Training K-Nearest Neighbors model")
        knn_model = KNNModel(self.X_train, self.X_test, self.y_train, self.y_test)
        knn_preds = knn_model.train_model()

        self.logger.info("Training XGBoost model")
        xgb_model = XGBoostModel(self.X_train, self.X_test, self.y_train, self.y_test)
        xgb_preds = xgb_model.train_model()

        self.predictions = {
            "decision_tree": decision_tree_preds,
            "random_forest": random_forest_preds,
            "svm": svm_preds,
            "logistic_regression": logistic_regression_preds,
            "naive_bayes": naive_bayes_preds,
            "knn": knn_preds,
            "xgboost": xgb_preds,
        }

        return self.predictions

    def evaluate_models(self) -> pd.DataFrame:
        if self.y_test is None or self.predictions is None:
            raise ValueError("Need y_test and predictions. Call split_data() and train_models() first.")

        self.logger.info("Generating model metrics")
        metrics_model = ModelMetrics(
            self.y_test,
            self.predictions["decision_tree"],
            self.predictions["random_forest"],
            self.predictions["logistic_regression"],
            self.predictions["svm"],
            self.predictions["naive_bayes"],
            self.predictions["knn"],
            self.predictions["xgboost"],
        )

        self.metrics_df = metrics_model.generate_metrics_dataframe()
        self.logger.info("Model metrics DataFrame generated")
        return self.metrics_df

    def save_metrics(self):
        if self.metrics_df is None:
            raise ValueError("metrics_df is None. Call evaluate_models() first.")

        self.metrics_df.to_excel(self.config.output_file, index=False)
        self.logger.info(f"Model metrics saved to {self.config.output_file}")

    def run_all(self) -> pd.DataFrame:
        self.load_data()
        self.process_data()
        self.split_data()
        self.train_models()
        self.evaluate_models()
        self.save_metrics()
        self.logger.info("ML Pipeline execution completed successfully")
        return self.metrics_df

def run_full_pipeline_from_cli():
    args = parse_args()

    config = PipelineConfig(
        data_path=args.data_path,
        output_file=args.output_file,
        log_mode=args.log_mode,
        log_level=args.log_level,
        log_dir=args.log_dir,
        log_filename=args.log_filename,
        data_source=args.data_source,
        table_name=args.table_name,
        db_limit=args.db_limit,
    )

    logger = setup_logger(config)

    try:
        pipeline = MLPipeline(config, logger)
        pipeline.run_all()
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
        sys.exit(1)

def main():
    run_full_pipeline_from_cli()


def run_pipeline_with_csv(
        data_path: str = "data.csv",
        output_file: str = "model_output.xlsx",
        log_mode: str = "both",
        log_level: str = "INFO"
) -> pd.DataFrame:
    """
    Run ML pipeline with CSV data source.

    Args:
        data_path: Path to CSV file
        output_file: Path for output Excel file
        log_mode: Logging mode (file/console/both)
        log_level: Logging level (DEBUG/INFO/WARNING/ERROR)

    Returns:
        pd.DataFrame: Metrics dataframe
    """
    config = PipelineConfig(
        data_source="csv",
        data_path=data_path,
        output_file=output_file,
        log_mode=log_mode,
        log_level=log_level
    )

    logger = setup_logger(config)

    try:
        pipeline = MLPipeline(config, logger)
        return pipeline.run_all()
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
        raise


def run_pipeline_with_database(
        table_name: str = "personal_data",
        output_file: str = "model_output_db.xlsx",
        db_criteria: dict | None = None,
        db_columns: list[str] | None = None,
        db_limit: int | None = None,
        log_mode: str = "both",
        log_level: str = "INFO"
) -> pd.DataFrame:
    config = PipelineConfig(
        data_source="database",
        table_name=table_name,
        output_file=output_file,
        db_criteria=db_criteria,
        db_columns=db_columns,
        db_limit=db_limit,
        log_mode=log_mode,
        log_level=log_level
    )

    logger = setup_logger(config)

    try:
        pipeline = MLPipeline(config, logger)
        return pipeline.run_all()
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    USE_DATABASE = True  # True = database, False = CSV

    if USE_DATABASE:
        metrics_df = run_pipeline_with_database(
            table_name="personal_data",
            output_file="model_output_db.xlsx"
        )
        print("\n✓ Pipeline completed with database data")
        print(f"Results shape: {metrics_df.shape}")

    else:
        # Run with CSV
        metrics_df = run_pipeline_with_csv(
            data_path="data.csv",
            output_file="model_output_csv.xlsx"
        )
        print("\n✓ Pipeline completed with CSV data")
        print(f"Results shape: {metrics_df.shape}")