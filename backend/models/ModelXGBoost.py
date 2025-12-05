import joblib
from xgboost import XGBClassifier
from sklearn.model_selection import RandomizedSearchCV
from sklearn.metrics import accuracy_score
from Logging import LoggingConfig


class XGBoostModel:
    def __init__(self, X_train, X_test, y_train, y_test):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.best_model = None
        self.logger = LoggingConfig.get_class_logger('XGBoostModel')
        self.logger.info(f"")
        self.logger.info(f"XGBoost is a fast, scalable boosting algorithm that builds trees to minimize errors.")
        self.logger.info(f"")
        self.logger.info(f"XGBoost grid search with:")
        self.logger.info(f"  max_depth: controls tree depth, values from 4 to 7 for complexity tuning")
        self.logger.info(f"  eta: learning rate [0.1 to 0.5]; lower values slow learning for better accuracy")
        self.logger.info(f"  reg_lambda: L2 regularization strength [0.8 to 1.2] to reduce overfitting")
        self.logger.info(f"  random_state: seed values [300, 600, 900] for reproducible model training")

        self.logger.info(f"XGBoostModel initialized - Train shape: {X_train.shape}, Test shape: {X_test.shape}")

    def train_model(self):
        """Train XGBoost model with hyperparameter tuning."""
        self.logger.info("Training XGBoost model with hyperparameter optimization")

        param_dict = {
            'max_depth': range(4, 8),
            'eta': [0.1, 0.2, 0.3, 0.4, 0.5],
            'reg_lambda': [0.8, 0.9, 1, 1.1, 1.2],
            'random_state': [300, 600, 900]
        }

        self.logger.debug(f"Hyperparameter search space: {param_dict}")
        total_combinations = (len(param_dict['max_depth']) *
                              len(param_dict['eta']) *
                              len(param_dict['reg_lambda']) *
                              len(param_dict['random_state']))
        self.logger.info(f"Total possible combinations: {total_combinations}")
        self.logger.info("Using RandomizedSearchCV with 50 iterations, 3-fold CV, F1 scoring")

        clf = RandomizedSearchCV(
            XGBClassifier(
                use_label_encoder=False,
                eval_metric='logloss',  # Suppress warning
                verbosity=0  # Reduce XGBoost verbosity
            ),
            param_distributions=param_dict,
            n_iter=50,
            scoring='f1',
            cv=3,
            verbose=0,  # Reduce sklearn verbosity
            random_state=42,
            n_jobs=-1
        )

        self.logger.info("Starting hyperparameter search...")
        clf.fit(self.X_train, self.y_train)

        self.best_model = clf.best_estimator_
        best_score = clf.best_score_
        best_params = clf.best_params_

        self.logger.info(f"Hyperparameter search completed - Best CV F1-score: {best_score:.4f}")
        self.logger.info(f"Best parameters: {best_params}")

        # Log parameter analysis
        if hasattr(clf, 'cv_results_'):
            results = clf.cv_results_

            # Analyze parameter impact
            param_analysis = {}
            for param in param_dict.keys():
                param_values = [params[param] for params in results['params']]
                param_scores = results['mean_test_score']

                unique_values = list(set(param_values))
                for value in unique_values:
                    scores_for_value = [score for pv, score in zip(param_values, param_scores) if pv == value]
                    if scores_for_value:
                        avg_score = sum(scores_for_value) / len(scores_for_value)
                        if param not in param_analysis:
                            param_analysis[param] = {}
                        param_analysis[param][value] = avg_score

            # Log parameter impact
            for param, value_scores in param_analysis.items():
                self.logger.debug(f"Parameter '{param}' impact:")
                for value, avg_score in sorted(value_scores.items(), key=lambda x: x[1], reverse=True):
                    self.logger.debug(f"  {value}: avg F1 = {avg_score:.4f}")

        # Make predictions
        predXGB = self.best_model.predict(self.X_test)

        # Log final model performance
        accuracy = accuracy_score(self.y_test, predXGB)
        self.logger.info(f"Final XGBoost model - Test accuracy: {accuracy:.4f}")

        # Log model-specific information
        if hasattr(self.best_model, 'feature_importances_'):
            feature_importances = self.best_model.feature_importances_
            n_features = len(feature_importances)
            mean_importance = feature_importances.mean()
            max_importance = feature_importances.max()

            self.logger.info(f"Feature importance stats - Features: {n_features}, "
                             f"Mean: {mean_importance:.4f}, Max: {max_importance:.4f}")

            # Log top features
            top_features = sorted(enumerate(feature_importances), key=lambda x: x[1], reverse=True)[:5]
            self.logger.debug("Top 5 most important features:")
            for i, (feature_idx, importance) in enumerate(top_features):
                self.logger.debug(f"  Feature {feature_idx}: {importance:.4f}")

        # Log final model parameters
        final_params = {
            'max_depth': self.best_model.max_depth,
            'learning_rate': self.best_model.learning_rate,
            'reg_lambda': self.best_model.reg_lambda,
            'n_estimators': self.best_model.n_estimators,
            'random_state': self.best_model.random_state
        }
        self.logger.info(f"Final model parameters: {final_params}")

        # Log training information
        if hasattr(self.best_model, 'evals_result_'):
            self.logger.debug("XGBoost training completed with evaluation results")

        self.save_model()
        return predXGB

    def save_model(self, filename='classification_xg_boost.pkl'):
        """Save the trained XGBoost model."""
        try:
            joblib.dump(self.best_model, filename)
            self.logger.info(f'XGBoost model saved successfully as {filename}')
            print(f'Model saved as {filename}')
        except Exception as e:
            self.logger.error(f'Failed to save XGBoost model: {str(e)}')
            raise