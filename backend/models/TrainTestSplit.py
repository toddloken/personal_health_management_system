from imblearn.over_sampling import SMOTE
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from Logging import LoggingConfig
import numpy as np


class TrainTestSplit:
    def __init__(self, df, target_column='status', test_size=0.2, random_state=20, smote_random_state=300):
        """
        Initialize the TrainTestSplit with a dataframe and parameters.

        :param df: Pandas DataFrame containing features and target.
        :param target_column: The name of the target column.
        :param test_size: Proportion of the dataset to be used for testing.
        :param random_state: Random state for reproducibility in train-test split.
        :param smote_random_state: Random state for SMOTE balancing.
        """
        self.df = df
        self.target_column = target_column
        self.test_size = test_size
        self.random_state = random_state
        self.smote_random_state = smote_random_state
        self.logger = LoggingConfig.get_class_logger('TrainTestSplit')

        self.logger.info(f"TrainTestSplit initialized - Target: {target_column}, Test size: {test_size}")
        self.logger.debug(f"Random states - Split: {random_state}, SMOTE: {smote_random_state}")

    def balance_and_split(self):
        """
        Balances the dataset using SMOTE, normalizes features, and splits into training and testing sets.

        :return: X_train, X_test, y_train, y_test
        """
        try:
            self.logger.info("Starting balance and split process")

            # Validate target column exists
            if self.target_column not in self.df.columns:
                raise ValueError(f"Target column '{self.target_column}' not found in DataFrame")

            # Separate features and target
            X = self.df.drop(columns=[self.target_column])
            y = self.df[self.target_column]

            self.logger.info(f'Feature (X) Shape Before Balancing: {X.shape}')
            self.logger.info(f'Target (y) Shape Before Balancing: {y.shape}')
            print('Feature (X) Shape Before Balancing:', X.shape)
            print('Target (y) Shape Before Balancing:', y.shape)

            # Log class distribution before balancing
            class_counts_before = y.value_counts().sort_index()
            self.logger.info(f"Class distribution before balancing: {class_counts_before.to_dict()}")
            for class_label, count in class_counts_before.items():
                self.logger.debug(f"Class {class_label}: {count} samples ({count / len(y) * 100:.2f}%)")

            # Apply SMOTE for oversampling
            self.logger.info("Applying SMOTE for class balancing")
            sm = SMOTE(random_state=self.smote_random_state)
            X_balanced, y_balanced = sm.fit_resample(X, y)

            self.logger.info(f'Feature (X) Shape After Balancing: {X_balanced.shape}')
            self.logger.info(f'Target (y) Shape After Balancing: {y_balanced.shape}')
            print('Feature (X) Shape After Balancing:', X_balanced.shape)
            print('Target (y) Shape After Balancing:', y_balanced.shape)

            # Log class distribution after balancing
            class_counts_after = np.bincount(y_balanced)
            self.logger.info(f"Class distribution after balancing: {dict(enumerate(class_counts_after))}")
            for i, count in enumerate(class_counts_after):
                if count > 0:
                    self.logger.debug(f"Class {i}: {count} samples ({count / len(y_balanced) * 100:.2f}%)")

            # Scale features between -1 and 1
            self.logger.info("Applying MinMax scaling to features")
            scaler = MinMaxScaler(feature_range=(-1, 1))
            X_scaled = scaler.fit_transform(X_balanced)

            # Log scaling statistics
            self.logger.debug(f"Scaling applied - Feature range: [{X_scaled.min():.4f}, {X_scaled.max():.4f}]")
            self.logger.debug(f"Original feature range: [{X_balanced.min().min():.4f}, {X_balanced.max().max():.4f}]")

            # Split dataset into training and testing sets
            self.logger.info(f"Splitting dataset - Test size: {self.test_size}, Random state: {self.random_state}")
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled, y_balanced, test_size=self.test_size, random_state=self.random_state,
                stratify=y_balanced  # Ensure balanced split
            )

            # Log final split information
            self.logger.info(f"Final split completed:")
            self.logger.info(f"  Training set: X={X_train.shape}, y={y_train.shape}")
            self.logger.info(f"  Test set: X={X_test.shape}, y={y_test.shape}")

            # Log class distribution in splits
            train_class_dist = np.bincount(y_train)
            test_class_dist = np.bincount(y_test)
            self.logger.debug(f"Training set class distribution: {dict(enumerate(train_class_dist))}")
            self.logger.debug(f"Test set class distribution: {dict(enumerate(test_class_dist))}")

            self.logger.info("Balance and split process completed successfully")
            return X_train, X_test, y_train, y_test

        except ValueError as e:
            self.logger.error(f"Value error in balance_and_split: {str(e)}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in balance_and_split: {str(e)}")
            raise