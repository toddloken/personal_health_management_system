import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
from Logging import LoggingConfig
import warnings


class LogisticRegressionModel:
    def __init__(self, X_train, X_test, y_train, y_test):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.model = None
        self.logger = LoggingConfig.get_class_logger('LogisticRegressionModel')

        self.logger.info(f"LogisticRegressionModel initialized - Train shape: {X_train.shape}, Test shape: {X_test.shape}")
        self.logger.info("")
        self.logger.info("Training Logistic Regression model")
        self.logger.info("Logistic regression models binary outcomes using the sigmoid function, which maps values to [0, 1].")
        self.logger.info("Random State: 42")
        self.logger.info("Max Iter = 1000 helps prevent convergence warnings on challenging datasets")
        self.logger.info("solver='liblinear': Uses the liblinear algorithm, which is efficient for small datasets and supports L1 and L2 regularization.")


    def train_model(self):
        """Train Logistic Regression model."""
        self.logger.info("Training Logistic Regression model")

        # Suppress convergence warnings for cleaner output
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            self.model = LogisticRegression(
                random_state=42,
                max_iter=1000,  # Increase max_iter to help with convergence
                solver='liblinear'  # Good for small datasets
            )

            self.logger.debug(f"Model parameters: max_iter=1000, solver='liblinear', random_state=42")

            self.model.fit(self.X_train, self.y_train)

        # Check if model converged
        if hasattr(self.model, 'n_iter_'):
            if isinstance(self.model.n_iter_, int):
                iterations = self.model.n_iter_
            else:
                iterations = self.model.n_iter_[0] if len(self.model.n_iter_) > 0 else "Unknown"
            self.logger.info(f"Model converged after {iterations} iterations")

        predlog = self.model.predict(self.X_test)

        # Log model performance
        accuracy = accuracy_score(self.y_test, predlog)
        self.logger.info(f"Logistic Regression model - Test accuracy: {accuracy:.4f}")

        # Log model coefficients information
        if hasattr(self.model, 'coef_'):
            n_features = self.model.coef_.shape[1]
            n_classes = len(self.model.classes_)
            self.logger.info(f"Model coefficients shape: {self.model.coef_.shape}")
            self.logger.info(f"Number of features: {n_features}, Number of classes: {n_classes}")

            # Log coefficient statistics
            coef_flat = self.model.coef_.flatten()
            self.logger.debug(f"Coefficient statistics - Mean: {coef_flat.mean():.4f}, "
                              f"Std: {coef_flat.std():.4f}, "
                              f"Min: {coef_flat.min():.4f}, Max: {coef_flat.max():.4f}")

            # Log top positive and negative coefficients
            if n_classes == 2:  # Binary classification
                coef_abs = abs(coef_flat)
                top_indices = coef_abs.argsort()[-5:][::-1]  # Top 5 by absolute value
                self.logger.debug("Top 5 coefficients by absolute value:")
                for i, idx in enumerate(top_indices):
                    self.logger.debug(f"  Feature {idx}: {coef_flat[idx]:.4f}")

        # Log intercept information
        if hasattr(self.model, 'intercept_'):
            self.logger.debug(f"Model intercept: {self.model.intercept_}")

        print(classification_report(self.y_test, predlog))
        self.save_model()
        return predlog

    def save_model(self, filename='classification_logistic_regression.pkl'):
        """Save the trained Logistic Regression model."""
        try:
            joblib.dump(self.model, filename)
            self.logger.info(f'Logistic Regression model saved successfully as {filename}')
            print(f'Model saved as {filename}')
        except Exception as e:
            self.logger.error(f'Failed to save Logistic Regression model: {str(e)}')
            raise