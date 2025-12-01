import joblib
from sklearn.neighbors import KNeighborsClassifier
from sklearn import metrics
from Logging import LoggingConfig


class KNNModel:
    def __init__(self, X_train, X_test, y_train, y_test):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test
        self.best_n_neighbors = 5
        self.model = None
        self.logger = LoggingConfig.get_class_logger('KNNModel')

        self.logger.info(f"KNNModel initialized - Train shape: {X_train.shape}, Test shape: {X_test.shape}")
        self.logger.info(f"")
        self.logger.info(f"K-Nearest Neighbors predicts a label based on the majority of nearby data points.")
        self.logger.info(f"")

    def find_best_k(self, Ks=10):
        """Find the best k value based on accuracy."""
        self.logger.info(f"Finding best k value by testing k from 2 to {Ks - 1}")

        mean_acc = []
        k_values = range(2, Ks)

        for n in k_values:
            self.logger.debug(f"Testing k={n}")

            neigh = KNeighborsClassifier(n_neighbors=n)
            neigh.fit(self.X_train, self.y_train)
            yhat = neigh.predict(self.X_test)
            accuracy = metrics.accuracy_score(self.y_test, yhat)
            mean_acc.append(accuracy)

            self.logger.debug(f"k={n} achieved accuracy: {accuracy:.4f}")

        self.logger.info('Neighbor Accuracy List')
        self.logger.info(str(mean_acc))
        print('Neighbor Accuracy List')
        print(mean_acc)

        # Find best k
        best_accuracy = max(mean_acc)
        best_k_index = mean_acc.index(best_accuracy)
        self.best_n_neighbors = best_k_index + 2  # +2 because we start from k=2

        self.logger.info(f"Best k value found: {self.best_n_neighbors} with accuracy: {best_accuracy:.4f}")

        # Log performance trends
        if len(mean_acc) > 2:
            early_avg = sum(mean_acc[:3]) / 3 if len(mean_acc) >= 3 else mean_acc[0]
            late_avg = sum(mean_acc[-3:]) / 3 if len(mean_acc) >= 3 else mean_acc[-1]
            self.logger.debug(f"Accuracy trend - Early k values avg: {early_avg:.4f}, "
                              f"Late k values avg: {late_avg:.4f}")

        # Log all k values and their accuracies for reference
        for i, acc in enumerate(mean_acc):
            k_val = i + 2
            self.logger.debug(f"k={k_val}: accuracy={acc:.4f}")

    def train_model(self):
        """Train the KNN model with the best k value."""
        self.logger.info("Starting KNN model training")
        self.logger.info("")
        self.logger.info("n_neighbors: Number of nearest neighbors to consider for making predictions (e.g., majority vote).")
        self.logger.info("weights: Typically Uniform - All neighbors contribute equally to the vote (no distance weighting).")
        self.logger.info("algorithm: Typically auto - Scikit-learn chooses the best algorithm ('ball_tree', 'kd_tree', or 'brute') based on data.")
        self.logger.info("metric: Distance metric used for neighbors; general form that includes Euclidean and Manhattan distances.")
        self.logger.info(" - Manhattan: Better for high - dimensional data, categorical features")
        self.logger.info(" - Euclidean: Good for continuous features, natural clustering")
        self.logger.info("p=2: p2 = Euclidean, p1 = Manhattan")
        self.find_best_k()

        self.logger.info(f"Training KNN model with k={self.best_n_neighbors}")

        self.model = KNeighborsClassifier(
            n_neighbors=self.best_n_neighbors,
            weights='uniform',  # Default, but explicit
            algorithm='auto',  # Let sklearn choose the best algorithm
            metric='minkowski',  # Default
            p=2  # Euclidean distance
        )

        self.logger.debug(f"KNN parameters: n_neighbors={self.best_n_neighbors}, "
                          f"weights='uniform', algorithm='auto', metric='minkowski', p=2")

        self.model.fit(self.X_train, self.y_train)
        predKNN = self.model.predict(self.X_test)

        # Log model performance
        accuracy = metrics.accuracy_score(self.y_test, predKNN)
        self.logger.info(f"Final KNN model - Test accuracy: {accuracy:.4f}")

        # Log additional metrics
        precision = metrics.precision_score(self.y_test, predKNN, average='weighted', zero_division=0)
        recall = metrics.recall_score(self.y_test, predKNN, average='weighted', zero_division=0)
        f1 = metrics.f1_score(self.y_test, predKNN, average='weighted', zero_division=0)

        self.logger.info(f"Additional metrics - Precision: {precision:.4f}, "
                         f"Recall: {recall:.4f}, F1-score: {f1:.4f}")

        # Log prediction statistics
        import numpy as np
        unique_predictions, pred_counts = np.unique(predKNN, return_counts=True)
        pred_distribution = dict(zip(unique_predictions, pred_counts))
        self.logger.info(f"Prediction distribution: {pred_distribution}")

        # Log distance statistics if possible
        if hasattr(self.model, 'kneighbors'):
            # Get distances to nearest neighbors for a sample of test points
            sample_size = min(10, len(self.X_test))
            distances, indices = self.model.kneighbors(self.X_test[:sample_size])
            avg_distance = distances.mean()
            max_distance = distances.max()
            min_distance = distances.min()

            self.logger.debug(f"Neighbor distances (sample) - Mean: {avg_distance:.4f}, "
                              f"Min: {min_distance:.4f}, Max: {max_distance:.4f}")

        self.save_model()
        return predKNN

    def save_model(self, filename='classification_K_nearest_neighbors.pkl'):
        """Save the trained KNN model."""
        try:
            joblib.dump(self.model, filename)
            self.logger.info(f'KNN model saved successfully as {filename}')
            print(f'Model saved as {filename}')
        except Exception as e:
            self.logger.error(f'Failed to save KNN model: {str(e)}')
            raise