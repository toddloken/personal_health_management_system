import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import RandomizedSearchCV
from Logging import LoggingConfig


class RandomForestModel:
    def __init__(self, X_train, X_test, y_train, y_test):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.best_model = None
        self.logger = LoggingConfig.get_class_logger('RandomForestModel')
        self.logger.info(f"")
        self.logger.info(f"Random Forest is an ensemble model using many decision trees for predictions.")
        self.logger.info(f"")
        self.logger.info(f"RandomForestClassifier grid search with:")
        self.logger.info(f"  n_estimators: number of trees in the forest, values from 100 to 275 in steps of 25")
        self.logger.info(f"  max_features: number of features to consider at each split ['sqrt', 'log2']")
        self.logger.info(f"  max_depth: maximum tree depth, values from 1 to 9")
        self.logger.info(f"  random_state: seed for reproducibility, values from 100 to 200 in steps of 50")
        self.logger.info(f"  criterion: function to measure split quality ['gini', 'entropy']")
        self.logger.info(f"")
        self.logger.info(f"RandomForestModel initialized - Train shape: {X_train.shape}, Test shape: {X_test.shape}")

    def train_initial_model(self):
        """Train initial Random Forest model."""
        self.logger.info("Training initial Random Forest model with default parameters")

        rfc = RandomForestClassifier(random_state=42)
        rfc.fit(self.X_train, self.y_train)
        predRF = rfc.predict(self.X_test)

        accuracy = accuracy_score(self.y_test, predRF)
        self.logger.info(f"Initial Random Forest model - Test accuracy: {accuracy:.4f}")

        print(classification_report(self.y_test, predRF))
        return rfc

    def perform_random_search(self):
        """Perform Randomized Search to find the best hyperparameters."""
        self.logger.info("Starting Randomized Search for Random Forest hyperparameters")

        param_grid = {
            'n_estimators': range(100, 300, 25),
            'max_features': ['sqrt', 'log2'],
            'max_depth': range(1, 10),
            'random_state': range(100, 250, 50),
            'criterion': ['gini', 'entropy']
        }

        self.logger.debug(f"Random search parameters: {param_grid}")
        self.logger.info("Random search will evaluate 10 parameter combinations with 5-fold CV")

        rfc = self.train_initial_model()
        grid_search = RandomizedSearchCV(
            estimator=rfc,
            param_distributions=param_grid,
            n_iter=10,
            cv=5,
            n_jobs=-1,
            random_state=42,
            verbose=0
        )
        grid_search.fit(self.X_train, self.y_train)

        self.best_params = grid_search.best_params_
        best_score = grid_search.best_score_

        self.logger.info(f"Random search completed - Best CV score: {best_score:.4f}")
        self.logger.info(f"Best parameters: {self.best_params}")

        return self.best_params

    def train_best_model(self):
        """Train a Random Forest model using the best hyperparameters."""
        if not hasattr(self, 'best_params'):
            self.perform_random_search()

        self.logger.info("Training Random Forest with optimized parameters")

        # Using hardcoded best parameters as in original code
        best_params = {
            'random_state': 200,
            'max_features': 'sqrt',
            'n_estimators': 125,
            'max_depth': 7,
            'criterion': 'entropy'
        }

        self.logger.info(f"Using optimized parameters: {best_params}")

        self.best_model = RandomForestClassifier(
            random_state=best_params['random_state'],
            max_features=best_params['max_features'],
            n_estimators=best_params['n_estimators'],
            max_depth=best_params['max_depth'],
            criterion=best_params['criterion']
        )

        self.best_model.fit(self.X_train, self.y_train)
        predRFC = self.best_model.predict(self.X_test)

        # Log model performance
        accuracy = accuracy_score(self.y_test, predRFC)
        self.logger.info(f"Optimized Random Forest model - Test accuracy: {accuracy:.4f}")

        # Log feature importance statistics
        if hasattr(self.best_model, 'feature_importances_'):
            feature_importances = self.best_model.feature_importances_
            n_features = len(feature_importances)
            mean_importance = feature_importances.mean()
            max_importance = feature_importances.max()

            self.logger.info(
                f"Feature importance stats - Features: {n_features}, Mean: {mean_importance:.4f}, Max: {max_importance:.4f}")

            # Log top 5 most important features
            top_features = sorted(enumerate(feature_importances), key=lambda x: x[1], reverse=True)[:5]
            self.logger.debug(f"Top 5 feature importances: {[(f'Feature_{i}', imp) for i, imp in top_features]}")

        # Log model parameters
        self.logger.debug(f"Final model parameters: n_estimators={self.best_model.n_estimators}, "
                          f"max_depth={self.best_model.max_depth}, max_features={self.best_model.max_features}")

        print(classification_report(self.y_test, predRFC))
        self.save_model()
        return predRFC

    def save_model(self, filename='classification_random_forest.pkl'):
        """Save the trained Random Forest model."""
        try:
            joblib.dump(self.best_model, filename)
            self.logger.info(f'Random Forest model saved successfully as {filename}')
            print(f'Model saved as {filename}')
        except Exception as e:
            self.logger.error(f'Failed to save Random Forest model: {str(e)}')
            raise