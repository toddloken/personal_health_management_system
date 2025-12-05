# ml_time_series.py

from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import numpy as np
import logging
import sys
from pathlib import Path

from DataProcessor import DataProcessTimeSeries
from Logging import LoggingConfig

# Time series specific imports
from statsmodels.tsa.statespace.sarimax import SARIMAX
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_absolute_percentage_error


@dataclass
class TimeSeriesConfig:
    """Configuration for time series pipeline."""
    table_name: str = "personal_data"
    target_column: str = "sleep_index"
    forecast_periods: int = 7
    output_csv: bool = True
    output_dir: str = "."
    log_mode: str = "both"
    log_level: str = "INFO"


class TimeSeriesPipeline:
    """Simplified time series forecasting pipeline using SARIMA and Prophet."""

    def __init__(self, config: TimeSeriesConfig):
        self.config = config
        self.logger = self._setup_logger()

        # Internal state
        self.df: pd.DataFrame | None = None
        self.train_df: pd.DataFrame | None = None
        self.test_df: pd.DataFrame | None = None
        self.predictions: dict = {}
        self.metrics: dict = {}

    def _setup_logger(self) -> logging.Logger:
        """Initialize logging configuration."""
        log_config = LoggingConfig(log_level=getattr(logging, self.config.log_level))
        logger = log_config.setup_logging(mode=self.config.log_mode)
        logger.info("Starting Time Series Pipeline execution")
        return logger

    def evaluate_forecast(self, actual: pd.Series, predicted: pd.Series, model_name: str) -> dict:
        """
        Calculate forecast metrics.

        Args:
            actual: Actual values
            predicted: Predicted values
            model_name: Name of the model

        Returns:
            dict: Dictionary of metrics
        """
        try:
            mae = mean_absolute_error(actual, predicted)
            mse = mean_squared_error(actual, predicted)
            rmse = np.sqrt(mse)
            mape = mean_absolute_percentage_error(actual, predicted) * 100

            metrics = {
                'Model': model_name,
                'MAE': round(mae, 4),
                'MSE': round(mse, 4),
                'RMSE': round(rmse, 4),
                'MAPE': round(mape, 2)
            }

            self.logger.info(
                f"{model_name} - MAE: {mae:.4f}, RMSE: {rmse:.4f}, MAPE: {mape:.2f}%"
            )

            return metrics

        except Exception as e:
            self.logger.error(f"Error evaluating {model_name}: {e}")
            return {'Model': model_name, 'Error': str(e)}

    def forecast_prophet(self) -> pd.Series:
        """
        Train Prophet model and generate forecasts.

        Returns:
            pd.Series: Forecasted values
        """
        self.logger.info("Training Prophet model")

        try:
            # Prepare data for Prophet (requires 'ds' and 'y' columns)
            prophet_train = pd.DataFrame({
                'ds': pd.to_datetime(
                    self.train_df['pdate'],
                    origin=pd.Timestamp('1960-01-01'),
                    unit='D'
                ),
                'y': self.train_df[self.config.target_column]
            })

            # Train model
            model = Prophet(
                yearly_seasonality=True,
                weekly_seasonality=True,
                daily_seasonality=False,
                changepoint_prior_scale=0.05
            )
            model.fit(prophet_train)

            # Generate forecast
            future_dates = pd.DataFrame({
                'ds': pd.to_datetime(
                    self.test_df['pdate'],
                    origin=pd.Timestamp('1960-01-01'),
                    unit='D'
                )
            })

            forecast = model.predict(future_dates)
            predictions = forecast['yhat'].values

            self.logger.info(f"Prophet forecast completed for {len(predictions)} periods")
            return pd.Series(predictions, index=self.test_df.index)

        except Exception as e:
            self.logger.error(f"Prophet forecasting failed: {e}")
            raise

    def forecast_sarima(self) -> pd.Series:
        """
        Train SARIMA model and generate forecasts.

        Returns:
            pd.Series: Forecasted values
        """
        self.logger.info("Training SARIMA model")

        try:
            # SARIMA parameters (p,d,q)(P,D,Q,s)
            # Using simple defaults - should be optimized for production
            order = (1, 1, 1)
            seasonal_order = (1, 1, 1, 7)  # weekly seasonality

            model = SARIMAX(
                self.train_df[self.config.target_column],
                order=order,
                seasonal_order=seasonal_order,
                enforce_stationarity=False,
                enforce_invertibility=False
            )

            results = model.fit(disp=False)

            # Generate forecast
            forecast = results.forecast(steps=len(self.test_df))

            self.logger.info(f"SARIMA forecast completed for {len(forecast)} periods")
            return pd.Series(forecast.values, index=self.test_df.index)

        except Exception as e:
            self.logger.error(f"SARIMA forecasting failed: {e}")
            raise

    def load_and_process_data(self) -> pd.DataFrame:
        """
        Load data from database and process for time series analysis.

        Returns:
            pd.DataFrame: Processed time series data
        """
        self.logger.info(f"Loading data from table '{self.config.table_name}'")

        try:
            from backend.utils.database_processor import DatabaseDataProcessor

            processor = DatabaseDataProcessor()

            if not processor.connect():
                raise ValueError("Failed to connect to database")

            # Load all data from table
            self.df = processor.read(table_name=self.config.table_name)

            if self.df is None or self.df.empty:
                raise ValueError(f"No data retrieved from table '{self.config.table_name}'")

            self.logger.info(f"Dataset loaded with shape: {self.df.shape}")

            # Process with time series processor
            ts_processor = DataProcessTimeSeries(self.df)
            self.df = ts_processor.process()

            self.logger.info("Time series data processing completed")

            processor.disconnect()

            return self.df

        except Exception as e:
            self.logger.error(f"Failed to load and process data: {e}")
            raise

    def run_all(self) -> pd.DataFrame:
        """
        Execute complete time series forecasting pipeline.

        Returns:
            pd.DataFrame: Metrics comparison of models
        """
        try:
            # Load and process data
            self.load_and_process_data()

            # Split data
            self.split_train_test()

            # Train models and forecast
            self.train_and_forecast()

            # Generate metrics
            metrics_df = self.summarize_metrics()

            # Optional CSV output
            if self.config.output_csv:
                self.save_to_csv()

            self.logger.info("Time Series Pipeline execution completed successfully")
            return metrics_df

        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}", exc_info=True)
            raise

    def save_to_csv(self):
        """Save processed data and predictions to CSV files."""
        try:
            output_dir = Path(self.config.output_dir)
            output_dir.mkdir(exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save processed data
            data_file = output_dir / f"ts_data_{timestamp}.csv"
            self.df.to_csv(data_file, index=False)
            self.logger.info(f"Processed data saved to {data_file}")

            # Save predictions if available
            if self.predictions:
                pred_df = pd.DataFrame({
                    'pdate': self.test_df['pdate'],
                    'actual': self.test_df[self.config.target_column].values,
                    **{name: preds.values for name, preds in self.predictions.items()}
                })

                pred_file = output_dir / f"ts_predictions_{timestamp}.csv"
                pred_df.to_csv(pred_file, index=False)
                self.logger.info(f"Predictions saved to {pred_file}")

            # Save metrics if available
            if self.metrics:
                metrics_df = pd.DataFrame(list(self.metrics.values()))
                metrics_file = output_dir / f"ts_metrics_{timestamp}.csv"
                metrics_df.to_csv(metrics_file, index=False)
                self.logger.info(f"Metrics saved to {metrics_file}")

        except Exception as e:
            self.logger.error(f"Error saving CSV files: {e}")

    def split_train_test(self):
        """Split data into train and test sets (80/20 split for time series)."""
        if self.df is None:
            raise ValueError("DataFrame is None. Call load_and_process_data() first.")

        # Check if target column exists
        if self.config.target_column not in self.df.columns:
            raise ValueError(
                f"Target column '{self.config.target_column}' not found in dataset"
            )

        # Remove rows with NaN in target column
        valid_df = self.df[self.df[self.config.target_column].notna()].copy()

        split_idx = int(len(valid_df) * 0.8)
        self.train_df = valid_df.iloc[:split_idx]
        self.test_df = valid_df.iloc[split_idx:]

        self.logger.info(
            f"Data split - Train: {len(self.train_df)} rows, Test: {len(self.test_df)} rows"
        )

    def summarize_metrics(self) -> pd.DataFrame:
        """
        Create summary DataFrame of all model metrics.

        Returns:
            pd.DataFrame: Metrics comparison
        """
        if not self.metrics:
            raise ValueError("No metrics available. Call train_and_forecast() first.")

        metrics_df = pd.DataFrame(list(self.metrics.values()))

        self.logger.info("\n" + "=" * 60)
        self.logger.info("MODEL PERFORMANCE COMPARISON")
        self.logger.info("=" * 60)
        self.logger.info("\n" + metrics_df.to_string(index=False))
        self.logger.info("=" * 60)

        return metrics_df

    def train_and_forecast(self):
        """Train all models and generate forecasts."""
        if self.train_df is None or self.test_df is None:
            raise ValueError("Train/test data not available. Call split_train_test() first.")

        actual = self.test_df[self.config.target_column]

        # SARIMA
        try:
            sarima_preds = self.forecast_sarima()
            self.predictions['SARIMA'] = sarima_preds
            self.metrics['SARIMA'] = self.evaluate_forecast(actual, sarima_preds, 'SARIMA')
        except Exception as e:
            self.logger.error(f"SARIMA model failed: {e}")
            self.metrics['SARIMA'] = {'Model': 'SARIMA', 'Error': str(e)}

        # Prophet
        try:
            prophet_preds = self.forecast_prophet()
            self.predictions['Prophet'] = prophet_preds
            self.metrics['Prophet'] = self.evaluate_forecast(actual, prophet_preds, 'Prophet')
        except Exception as e:
            self.logger.error(f"Prophet model failed: {e}")
            self.metrics['Prophet'] = {'Model': 'Prophet', 'Error': str(e)}


def run_time_series_pipeline(
        target_column: str = "sleep_index",
        forecast_periods: int = 7,
        output_csv: bool = True,
        output_dir: str = ".",
        log_mode: str = "both",
        log_level: str = "INFO"
) -> pd.DataFrame:
    """
    Run time series forecasting pipeline.

    Args:
        target_column: Column to forecast
        forecast_periods: Number of periods to forecast
        output_csv: Whether to save outputs to CSV
        output_dir: Directory for CSV outputs
        log_mode: Logging mode (file/console/both)
        log_level: Logging level (DEBUG/INFO/WARNING/ERROR)

    Returns:
        pd.DataFrame: Metrics comparison
    """
    config = TimeSeriesConfig(
        target_column=target_column,
        forecast_periods=forecast_periods,
        output_csv=output_csv,
        output_dir=output_dir,
        log_mode=log_mode,
        log_level=log_level
    )

    pipeline = TimeSeriesPipeline(config)
    return pipeline.run_all()


if __name__ == "__main__":
    try:
        # Run pipeline with default settings
        metrics_df = run_time_series_pipeline(
            target_column="sleep_index",
            output_csv=True,
            output_dir=".",
            log_level="INFO"
        )

        print("\n✓ Time Series Pipeline completed successfully")
        print(f"\nMetrics Summary:")
        print(metrics_df.to_string(index=False))

    except Exception as e:
        print(f"\n✗ Pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)



metrics_df = run_time_series_pipeline()

# Forecast different column
metrics_df = run_time_series_pipeline(
    target_column="heart_rate",
    output_csv=True
)

# Or use the class directly
config = TimeSeriesConfig(
    target_column="recovery_score",
    output_csv=True,
    output_dir="./forecasts"
)
pipeline = TimeSeriesPipeline(config)
results = pipeline.run_all()