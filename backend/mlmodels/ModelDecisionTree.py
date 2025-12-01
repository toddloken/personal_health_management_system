import joblib
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import classification_report, accuracy_score
from Logging import LoggingConfig


class DecisionTreeModel:
    def __init__(self, X_train, y_train, X_test, y_test):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.best_model = None
        self.best_params = None
        self.logger = LoggingConfig.get_class_logger('DecisionTreeModel')

        self.logger.info(f"DecisionTreeModel initialized - Train shape: {X_train.shape}, Test shape: {X_test.shape}")

    def perform_grid_search(self):
        """Perform Grid Search to find the best hyperparameters."""
        self.logger.info("Starting Grid Search for Decision Tree hyperparameters")
        self.logger.info("")
        self.logger.info("A decision tree splits data into branches based on features to make predictions or decision")
        self.logger.info("")
        self.logger.info("parameter info:")
        self.logger.info("max_features: Determines how many features to consider when looking for the best split.")
        self.logger.info("max_depth: Sets the maximum depth the tree can grow to control complexity.")
        self.logger.info("random_state: Ensures reproducibility by fixing the randomness in tree building.")
        self.logger.info("criterion: Defines the function used to measure the quality of a split.")
        self.logger.info("  - gini - measures the probability of incorrectly classifying a randomly chosen element")
        self.logger.info("  - entropy - measures the level of disorder or uncertainty in the dataset - always increasing :)")

        param_grid = {
            'max_features': ['sqrt', 'log2', 0.5],
            'max_depth': range(1, 10),
            'random_state': range(30, 210, 30),
            'criterion': ['gini', 'entropy']
        }

        self.logger.debug(f"Grid search parameters: {param_grid}")
        total_combinations = (len(param_grid['max_features']) *
                              len(param_grid['max_depth']) *
                              len(param_grid['random_state']) *
                              len(param_grid['criterion']))
        self.logger.info(f"Grid search will evaluate {total_combinations} parameter combinations with 5-fold CV")

        grid_search = GridSearchCV(estimator=DecisionTreeClassifier(), param_grid=param_grid, cv=5, verbose=0)
        grid_search.fit(self.X_train, self.y_train)

        self.best_params = grid_search.best_params_
        best_score = grid_search.best_score_

        self.logger.info(f"Grid search completed - Best CV score: {best_score:.4f}")
        self.logger.info(f"Best parameters: {self.best_params}")

        return self.best_params

    def train_best_model(self):
        """Train a Decision Tree model using the best hyperparameters."""
        if self.best_params is None:
            self.perform_grid_search()

        self.logger.info("Training Decision Tree with best parameters")

        self.best_model = DecisionTreeClassifier(
            random_state=self.best_params['random_state'],
            max_features=self.best_params['max_features'],
            max_depth=self.best_params['max_depth'],
            criterion=self.best_params['criterion']
        )

        self.best_model.fit(self.X_train, self.y_train)
        predictions = self.best_model.predict(self.X_test)

        # Log model performance
        accuracy = accuracy_score(self.y_test, predictions)
        self.logger.info(f"Decision Tree model trained - Test accuracy: {accuracy:.4f}")

        # Log feature importance if available
        if hasattr(self.best_model, 'feature_importances_'):
            n_features = len(self.best_model.feature_importances_)
            self.logger.debug(f"Model uses {n_features} features")
            top_features = sorted(enumerate(self.best_model.feature_importances_),
                                  key=lambda x: x[1], reverse=True)[:5]
            self.logger.debug(f"Top 5 feature importances: {top_features}")

        print(classification_report(self.y_test, predictions))
        self.save_model()
        return predictions

    def save_model(self, filename='classification_decision_tree.pkl'):
        """Save the trained Decision Tree model."""
        try:
            joblib.dump(self.best_model, filename)
            self.logger.info(f'Decision Tree model saved successfully as {filename}')
            print(f'Model saved as {filename}')
        except Exception as e:
            self.logger.error(f'Failed to save model: {str(e)}')
            raise