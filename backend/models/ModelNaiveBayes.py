import joblib
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import classification_report, accuracy_score
from Logging import LoggingConfig
import numpy as np


class NaiveBayesModel:
    def __init__(self, X_train, X_test, y_train, y_test):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.model = None
        self.logger = LoggingConfig.get_class_logger('NaiveBayesModel')
        self.logger.info(f"")
        self.logger.info("Naive Bayes is a fast classification method that uses probability and assumes features are independent.")
        self.logger.info(f"")
        self.logger.info(f"Logging class distribution before training Naive Bayes...")
        self.logger.info(f"Naive Bayes uses class priors, so checking class balance is important.")
        self.logger.info(f"Class distribution gives insight into how many training samples exist for each class.")
        self.logger.info(f"")
        self.logger.info(f"NaiveBayesModel initialized - Train shape: {X_train.shape}, Test shape: {X_test.shape}")

    def train_model(self):
        """Train Naive Bayes model."""
        self.logger.info("Training Gaussian Naive Bayes model")

        self.model = GaussianNB()

        # Log training data statistics
        self.logger.debug(f"Training data statistics:")
        self.logger.debug(f"  Feature means: min={self.X_train.mean(axis=0).min():.4f}, "
                          f"max={self.X_train.mean(axis=0).max():.4f}")
        self.logger.debug(f"  Feature stds: min={self.X_train.std(axis=0).min():.4f}, "
                          f"max={self.X_train.std(axis=0).max():.4f}")

        # Log class distribution
        unique_classes, class_counts = np.unique(self.y_train, return_counts=True)
        class_distribution = dict(zip(unique_classes, class_counts))
        self.logger.info(f"Training class distribution: {class_distribution}")
        for class_label, count in class_distribution.items():
            percentage = (count / len(self.y_train)) * 100
            self.logger.debug(f"  Class {class_label}: {count} samples ({percentage:.2f}%)")

        self.model.fit(self.X_train, self.y_train)

        # Log model parameters after fitting
        if hasattr(self.model, 'classes_'):
            n_classes = len(self.model.classes_)
            self.logger.info(f"Model fitted with {n_classes} classes: {self.model.classes_}")

        # Log feature statistics learned by the model
        if hasattr(self.model, 'theta_') and hasattr(self.model, 'sigma_'):
            n_features = self.model.theta_.shape[1]
            self.logger.info(f"Model learned parameters for {n_features} features")

            # Log mean and variance statistics for each class
            for i, class_label in enumerate(self.model.classes_):
                class_means = self.model.theta_[i]
                class_vars = self.model.sigma_[i]
                self.logger.debug(f"Class {class_label} - Feature means: min={class_means.min():.4f}, "
                                  f"max={class_means.max():.4f}, avg={class_means.mean():.4f}")
                self.logger.debug(f"Class {class_label} - Feature vars: min={class_vars.min():.4f}, "
                                  f"max={class_vars.max():.4f}, avg={class_vars.mean():.4f}")

        predgnb = self.model.predict(self.X_test)

        # Log model performance
        accuracy = accuracy_score(self.y_test, predgnb)
        self.logger.info(f"Gaussian Naive Bayes model - Test accuracy: {accuracy:.4f}")

        # Log prediction statistics
        unique_predictions, pred_counts = np.unique(predgnb, return_counts=True)
        pred_distribution = dict(zip(unique_predictions, pred_counts))
        self.logger.info(f"Prediction distribution: {pred_distribution}")

        # Log prediction probabilities statistics if available
        if hasattr(self.model, 'predict_proba'):
            pred_proba = self.model.predict_proba(self.X_test)
            max_proba = pred_proba.max(axis=1)
            mean_confidence = max_proba.mean()
            min_confidence = max_proba.min()
            self.logger.debug(f"Prediction confidence - Mean: {mean_confidence:.4f}, "
                              f"Min: {min_confidence:.4f}, Max: {max_proba.max():.4f}")

            # Log low confidence predictions
            low_confidence_mask = max_proba < 0.6
            if low_confidence_mask.sum() > 0:
                self.logger.warning(f"{low_confidence_mask.sum()} predictions have confidence < 0.6")

        print(classification_report(self.y_test, predgnb))
        self.save_model()
        return predgnb

    def save_model(self, filename='classification_naive_bayes.pkl'):
        """Save the trained Naive Bayes model."""
        try:
            joblib.dump(self.model, filename)
            self.logger.info(f'Naive Bayes model saved successfully as {filename}')
            print(f'Model saved as {filename}')
        except Exception as e:
            self.logger.error(f'Failed to save Naive Bayes model: {str(e)}')
            raise