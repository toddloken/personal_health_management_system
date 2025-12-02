import joblib
from sklearn import svm
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import GridSearchCV
from Logging import LoggingConfig


class SupportVectorMachineModel:
    def __init__(self, X_train, X_test, y_train, y_test):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.best_model = None
        self.logger = LoggingConfig.get_class_logger('SupportVectorMachineModel')
        self.logger.info(f"")
        self.logger.info(f"Support Vector Machine finds the best boundary to separate different classes in data.")
        self.logger.info(f"SVM grid search with:")
        self.logger.info(f"  kernel: type of decision boundary ['linear', 'rbf', 'poly']")
        self.logger.info(f"  C: regularization strength [0.5, 1, 10, 100]; higher values try to avoid misclassification")
        self.logger.info(f"  gamma: defines influence of single training points [1, 0.1, 0.01, 0.001, 0.0001]; lower means broader influence")


        self.logger.info(f"SVM Model initialized - Train shape: {X_train.shape}, Test shape: {X_test.shape}")

    def train_initial_model(self):
        """Train initial Support Vector Machine model with a linear kernel."""
        self.logger.info("Training initial SVM model with linear kernel")

        clf = svm.SVC(kernel='linear', random_state=42)
        clf.fit(self.X_train, self.y_train)
        y_pred = clf.predict(self.X_test)

        accuracy = accuracy_score(self.y_test, y_pred)
        self.logger.info(f"Initial SVM (linear kernel) - Test accuracy: {accuracy:.4f}")

        print(classification_report(self.y_test, y_pred))
        return clf

    def perform_grid_search(self):
        """Perform Grid Search to find the best hyperparameters."""
        self.logger.info("Starting Grid Search for SVM hyperparameters")

        param_grid = {
            'kernel': ['linear', 'rbf', 'poly'],
            'C': [0.5, 1, 10, 100],
            'gamma': [1, 0.1, 0.01, 0.001, 0.0001]
        }

        self.logger.debug(f"Grid search parameters: {param_grid}")
        total_combinations = (len(param_grid['kernel']) *
                              len(param_grid['C']) *
                              len(param_grid['gamma']))
        self.logger.info(f"Grid search will evaluate {total_combinations} parameter combinations")
        self.logger.info("Using F1-score as the optimization metric")

        grid_SVC = GridSearchCV(
            svm.SVC(random_state=42),
            param_grid,
            scoring='f1',
            cv=5,
            verbose=0,  # Set to 0 to reduce console output, logging handles verbosity
            n_jobs=-1
        )

        self.logger.info("Starting grid search fitting process...")
        grid_SVC.fit(self.X_train, self.y_train)

        best_score = grid_SVC.best_score_
        self.logger.info(f"Grid search completed - Best CV F1-score: {best_score:.4f}")
        self.logger.info(f"Best parameters: {grid_SVC.best_params_}")
        self.logger.info(f"Best estimator: {grid_SVC.best_estimator_}")

        # Log performance of different kernels
        results_df = grid_SVC.cv_results_
        kernel_scores = {}
        for i, params in enumerate(results_df['params']):
            kernel = params['kernel']
            score = results_df['mean_test_score'][i]
            if kernel not in kernel_scores:
                kernel_scores[kernel] = []
            kernel_scores[kernel].append(score)

        for kernel, scores in kernel_scores.items():
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            self.logger.debug(f"Kernel '{kernel}' - Average F1: {avg_score:.4f}, Best F1: {max_score:.4f}")

        print("\nBest Parameters: ", grid_SVC.best_params_)
        print("\n", grid_SVC.best_estimator_)

        self.best_params = grid_SVC.best_params_
        return grid_SVC

    def train_best_model(self):
        """Train an SVM model using the best hyperparameters."""
        self.logger.info("Training SVM with best hyperparameters")

        grid_SVC = self.perform_grid_search()
        self.best_model = grid_SVC.best_estimator_

        # Log final model parameters
        self.logger.info(f"Final SVM parameters:")
        self.logger.info(f"  Kernel: {self.best_model.kernel}")
        self.logger.info(f"  C: {self.best_model.C}")
        self.logger.info(f"  Gamma: {self.best_model.gamma}")

        if hasattr(self.best_model, 'support_'):
            n_support_vectors = len(self.best_model.support_)
            self.logger.info(f"  Number of support vectors: {n_support_vectors}")
            self.logger.debug(f"  Support vector ratio: {n_support_vectors / len(self.X_train):.4f}")

        predSVC = self.best_model.predict(self.X_test)

        # Log final performance
        accuracy = accuracy_score(self.y_test, predSVC)
        self.logger.info(f"Final SVM model - Test accuracy: {accuracy:.4f}")

        print("\n", classification_report(self.y_test, predSVC))
        self.save_model()
        return predSVC

    def save_model(self, filename='classification_support_vector_machine.pkl'):
        """Save the trained SVM model."""
        try:
            joblib.dump(self.best_model, filename)
            self.logger.info(f'SVM model saved successfully as {filename}')
            print(f'Model saved as {filename}')
        except Exception as e:
            self.logger.error(f'Failed to save SVM model: {str(e)}')
            raise