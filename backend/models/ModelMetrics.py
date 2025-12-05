import pandas as pd
from sklearn.metrics import precision_score, recall_score, accuracy_score, f1_score, r2_score
from Logging import LoggingConfig
import numpy as np


class ModelMetrics:
    def __init__(self, y_test, predDT, predRFC, predlog, predSVC, predgnb, predKNN, predXGB):
        self.y_test = y_test
        self.predDT = predDT
        self.predRFC = predRFC
        self.predlog = predlog
        self.predSVC = predSVC
        self.predgnb = predgnb
        self.predKNN = predKNN
        self.predXGB = predXGB
        self.logger = LoggingConfig.get_class_logger('ModelMetrics')

        # Model names for better logging
        self.model_names = {
            'DT': 'Decision Tree',
            'RF': 'Random Forest',
            'LR': 'Logistic Regression',
            'SVM': 'Support Vector Machine',
            'NB': 'Naive Bayes',
            'KNN': 'K-Nearest Neighbors',
            'XGB': 'XGBoost'
        }

        self.predictions = {
            'DT': predDT,
            'RF': predRFC,
            'LR': predlog,
            'SVM': predSVC,
            'NB': predgnb,
            'KNN': predKNN,
            'XGB': predXGB
        }

        self.logger.info("ModelMetrics initialized for 7 models")
        self.logger.info(f"Test set size: {len(y_test)}")

        # Log test set class distribution
        unique_classes, class_counts = np.unique(y_test, return_counts=True)
        class_distribution = dict(zip(unique_classes, class_counts))
        self.logger.info(f"Test set class distribution: {class_distribution}")

    def calculate_metrics_for_model(self, model_key, predictions):
        """Calculate all metrics for a single model."""
        try:
            metrics = {
                'accuracy': accuracy_score(self.y_test, predictions),
                'f1_score': f1_score(self.y_test, predictions, average='weighted', zero_division=0),
                'recall': recall_score(self.y_test, predictions, average='weighted', zero_division=0),
                'precision': precision_score(self.y_test, predictions, average='weighted', zero_division=0),
                'r2_score': r2_score(self.y_test, predictions)
            }

            model_name = self.model_names[model_key]
            self.logger.info(f"{model_name} metrics calculated:")
            for metric_name, value in metrics.items():
                self.logger.info(f"  {metric_name}: {value:.4f}")

            # Log prediction distribution for this model
            unique_preds, pred_counts = np.unique(predictions, return_counts=True)
            pred_distribution = dict(zip(unique_preds, pred_counts))
            self.logger.debug(f"{model_name} prediction distribution: {pred_distribution}")

            return metrics

        except Exception as e:
            self.logger.error(f"Error calculating metrics for {self.model_names[model_key]}: {str(e)}")
            # Return default values in case of error
            return {
                'accuracy': 0.0,
                'f1_score': 0.0,
                'recall': 0.0,
                'precision': 0.0,
                'r2_score': 0.0
            }

    def generate_metrics_dataframe(self):
        """Generate a Pandas DataFrame containing evaluation metrics for different models."""
        self.logger.info("Generating comprehensive metrics DataFrame for all models")

        # Calculate metrics for all models
        all_metrics = {}
        for model_key, predictions in self.predictions.items():
            all_metrics[model_key] = self.calculate_metrics_for_model(model_key, predictions)

        # Create the metrics chart
        chart = {
            'Metric': ["Accuracy", "F1-Score", "Recall", "Precision", "R2-Score"]
        }

        # Add metrics for each model
        for model_key in ['DT', 'RF', 'LR', 'SVM', 'NB', 'KNN', 'XGB']:
            metrics = all_metrics[model_key]
            chart[model_key] = [
                metrics['accuracy'],
                metrics['f1_score'],
                metrics['recall'],
                metrics['precision'],
                metrics['r2_score']
            ]

        df_metrics = pd.DataFrame(chart)

        # Log summary statistics
        self.logger.info("Model comparison summary:")

        # Find best performing model for each metric
        for i, metric in enumerate(["Accuracy", "F1-Score", "Recall", "Precision", "R2-Score"]):
            metric_values = []
            for model_key in ['DT', 'RF', 'LR', 'SVM', 'NB', 'KNN', 'XGB']:
                metric_values.append(df_metrics[model_key].iloc[i])

            best_value = max(metric_values)
            best_model_idx = metric_values.index(best_value)
            best_model = ['DT', 'RF', 'LR', 'SVM', 'NB', 'KNN', 'XGB'][best_model_idx]
            best_model_name = self.model_names[best_model]

            self.logger.info(f"Best {metric}: {best_model_name} ({best_value:.4f})")

        # Log overall statistics
        accuracy_values = [df_metrics[col].iloc[0] for col in ['DT', 'RF', 'LR', 'SVM', 'NB', 'KNN', 'XGB']]
        avg_accuracy = np.mean(accuracy_values)
        std_accuracy = np.std(accuracy_values)

        self.logger.info(f"Accuracy:")
        self.logger.info(f"-Measure of how many predictions were correct overall")
        self.logger.info(f"-Use when classes are balanced(e.g. 50% spam 50% not spam)")
        self.logger.info(f"-Best for overall correctness")
        self.logger.info(f"")
        self.logger.info(f"Precision:")
        self.logger.info(f"-Measure of when the model says correct, how often correct")
        self.logger.info(f"-Use when false positives are costly")
        self.logger.info(f"-Best for avoiding false positives")
        self.logger.info(f"")
        self.logger.info(f"Recall:")
        self.logger.info(f"-Measure of how many positives identified correctly")
        self.logger.info(f"-Use when false negatives are costly")
        self.logger.info(f"-Best for catching all true positives")
        self.logger.info(f"")
        self.logger.info(f"F1:")
        self.logger.info(f"-Measure of balance between precision and recall")
        self.logger.info(f"-Use when you have unbalanced datasets")
        self.logger.info(f"-Best for balance between precision and recall")
        self.logger.info(f"")
        self.logger.info(f"Accuracy statistics across all models:")
        self.logger.info(f"  Mean: {avg_accuracy:.4f}")
        self.logger.info(f"  Std: {std_accuracy:.4f}")
        self.logger.info(f"  Min: {min(accuracy_values):.4f}")
        self.logger.info(f"  Max: {max(accuracy_values):.4f}")

        # Log model ranking by accuracy
        model_accuracy_pairs = list(zip(['DT', 'RF', 'LR', 'SVM', 'NB', 'KNN', 'XGB'], accuracy_values))
        model_accuracy_pairs.sort(key=lambda x: x[1], reverse=True)

        self.logger.info("Model ranking by accuracy:")
        for rank, (model_key, accuracy) in enumerate(model_accuracy_pairs, 1):
            model_name = self.model_names[model_key]
            self.logger.info(f"  {rank}. {model_name}: {accuracy:.4f}")

        # Log model ranking by F1-Score
        f1_values = [df_metrics[col].iloc[1] for col in ['DT', 'RF', 'LR', 'SVM', 'NB', 'KNN', 'XGB']]
        model_f1_pairs = list(zip(['DT', 'RF', 'LR', 'SVM', 'NB', 'KNN', 'XGB'], f1_values))
        model_f1_pairs.sort(key=lambda x: x[1], reverse=True)

        self.logger.info("Model ranking by F1-Score:")
        for rank, (model_key, f1_score) in enumerate(model_f1_pairs, 1):
            model_name = self.model_names[model_key]
            self.logger.info(f"  {rank}. {model_name}: {f1_score:.4f}")

        # Log model ranking by Recall
        recall_values = [df_metrics[col].iloc[2] for col in ['DT', 'RF', 'LR', 'SVM', 'NB', 'KNN', 'XGB']]
        model_recall_pairs = list(zip(['DT', 'RF', 'LR', 'SVM', 'NB', 'KNN', 'XGB'], recall_values))
        model_recall_pairs.sort(key=lambda x: x[1], reverse=True)

        self.logger.info("Model ranking by Recall:")
        for rank, (model_key, recall) in enumerate(model_recall_pairs, 1):
            model_name = self.model_names[model_key]
            self.logger.info(f"  {rank}. {model_name}: {recall:.4f}")

        # Log model ranking by Precision
        precision_values = [df_metrics[col].iloc[3] for col in ['DT', 'RF', 'LR', 'SVM', 'NB', 'KNN', 'XGB']]
        model_precision_pairs = list(zip(['DT', 'RF', 'LR', 'SVM', 'NB', 'KNN', 'XGB'], precision_values))
        model_precision_pairs.sort(key=lambda x: x[1], reverse=True)

        self.logger.info("Model ranking by Precision:")
        for rank, (model_key, precision) in enumerate(model_precision_pairs, 1):
            model_name = self.model_names[model_key]
            self.logger.info(f"  {rank}. {model_name}: {precision:.4f}")

        # Log model ranking by R2-Score
        r2_values = [df_metrics[col].iloc[4] for col in ['DT', 'RF', 'LR', 'SVM', 'NB', 'KNN', 'XGB']]
        model_r2_pairs = list(zip(['DT', 'RF', 'LR', 'SVM', 'NB', 'KNN', 'XGB'], r2_values))
        model_r2_pairs.sort(key=lambda x: x[1], reverse=True)

        self.logger.info("Model ranking by R2-Score:")
        for rank, (model_key, r2_score) in enumerate(model_r2_pairs, 1):
            model_name = self.model_names[model_key]
            self.logger.info(f"  {rank}. {model_name}: {r2_score:.4f}")

        # Check for potential issues
        if std_accuracy < 0.01:
            self.logger.warning("Very low accuracy variance - models perform very similarly")

        if max(accuracy_values) < 0.7:
            self.logger.warning("All models have accuracy below 0.7 - consider data quality or feature engineering")

        self.logger.info("Metrics DataFrame generation completed successfully")
        return df_metrics