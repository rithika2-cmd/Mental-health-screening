import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.impute import SimpleImputer
import warnings
warnings.filterwarnings('ignore')


class DepressionModelTrainer:
    """
    A class to handle training of depression prediction models.
    """
    
    def __init__(self, test_size=0.2, random_state=42):
        """
        Initialize the model trainer.
        
        Args:
            test_size (float): Proportion of dataset to include in test split
            random_state (int): Random state for reproducibility
        """
        self.test_size = test_size
        self.random_state = random_state
        self.model = None
        self.scaler = None
        self.label_encoders = {}
        self.target_encoder = None
        self.feature_names = None
        self.metrics = None
        
    def prepare_data(self, df):
        """
        Prepare data for training by handling missing values and encoding.
        
        Args:
            df (pd.DataFrame): Input dataframe with 'Depression' column
            
        Returns:
            tuple: X_train, X_test, y_train, y_test
        """
        if 'Depression' not in df.columns:
            raise ValueError("Dataset must contain 'Depression' column as target variable")
        
        # Separate features and target
        X = df.drop('Depression', axis=1)
        y = df['Depression']
        
        # Identify column types
        numeric_features = X.select_dtypes(include=[np.number]).columns
        categorical_features = X.select_dtypes(include=['object']).columns
        
        # Handle missing values
        if len(numeric_features) > 0:
            num_imputer = SimpleImputer(strategy='mean')
            X[numeric_features] = num_imputer.fit_transform(X[numeric_features])
        
        if len(categorical_features) > 0:
            cat_imputer = SimpleImputer(strategy='most_frequent')
            X[categorical_features] = cat_imputer.fit_transform(X[categorical_features])
        
        # Encode categorical features
        for col in categorical_features:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            self.label_encoders[col] = le
        
        # Encode target variable
        self.target_encoder = LabelEncoder()
        y_encoded = self.target_encoder.fit_transform(y)
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, 
            test_size=self.test_size, 
            random_state=self.random_state,
            stratify=y_encoded
        )
        
        return X_train, X_test, y_train, y_test
    
    def train(self, X_train, y_train):
        """
        Train the Random Forest model.
        
        Args:
            X_train: Training features
            y_train: Training target
        """
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Initialize and train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            random_state=self.random_state,
            max_depth=10,
            min_samples_split=5,
            n_jobs=-1
        )
        
        self.model.fit(X_train_scaled, y_train)
        self.X_train = X_train
        
    def evaluate(self, X_test, y_test):
        """
        Evaluate model performance.
        
        Args:
            X_test: Test features
            y_test: Test target
            
        Returns:
            dict: Dictionary containing evaluation metrics
        """
        X_test_scaled = self.scaler.transform(X_test)
        y_pred = self.model.predict(X_test_scaled)
        
        accuracy = accuracy_score(y_test, y_pred)
        conf_matrix = confusion_matrix(y_test, y_pred)
        class_report = classification_report(y_test, y_pred, output_dict=True)
        
        self.metrics = {
            'accuracy': accuracy,
            'confusion_matrix': conf_matrix,
            'classification_report': class_report,
            'y_test': y_test,
            'y_pred': y_pred
        }
        
        return self.metrics
    
    def train_and_evaluate(self, df):
        """
        Complete training pipeline: prepare, train, and evaluate.
        
        Args:
            df (pd.DataFrame): Input dataframe
            
        Returns:
            dict: Evaluation metrics
        """
        X_train, X_test, y_train, y_test = self.prepare_data(df)
        self.train(X_train, y_train)
        metrics = self.evaluate(X_test, y_test)
        
        return metrics
    
    def predict(self, input_data):
        # Convert to DataFrame if dict
        if isinstance(input_data, dict):
            input_df = pd.DataFrame([input_data])
        else:
            input_df = input_data.copy()

        # ✅ ENSURE SAME COLUMN ORDER
        input_df = input_df[self.feature_names]

        # Encode categoricals & scale
        for col in self.label_encoders:
            if col in input_df.columns:
                input_df[col] = self.label_encoders[col].transform(input_df[col].astype(str))

        input_scaled = self.scaler.transform(input_df)

        # Predict
        prediction = self.model.predict(input_scaled)
        prediction_proba = self.model.predict_proba(input_scaled)

        # Decode prediction
        predicted_class = self.target_encoder.inverse_transform(prediction)[0]
        return predicted_class, prediction_proba[0]
    
    def get_feature_importance(self):
        """
        Get feature importance scores.
        
        Returns:
            pd.DataFrame: Feature importance dataframe
        """
        if self.model is None:
            raise ValueError("Model has not been trained yet")
        
        importance = self.model.feature_importances_
        feature_importance_df = pd.DataFrame({
            'Feature': self.feature_names,
            'Importance': importance
        }).sort_values('Importance', ascending=False)
        
        return feature_importance_df
    
    def save_model(self, filepath='model_artifacts.pkl'):
        """
        Save model and all artifacts to file.
        
        Args:
            filepath (str): Path to save the model
        """
        if self.model is None:
            raise ValueError("Model has not been trained yet")
        
        artifacts = {
            'model': self.model,
            'scaler': self.scaler,
            'label_encoders': self.label_encoders,
            'target_encoder': self.target_encoder,
            'feature_names': self.feature_names,
            'metrics': self.metrics
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(artifacts, f)
        
        print(f"Model saved successfully to {filepath}")
    
    def load_model(self, filepath='model_artifacts.pkl'):
        """
        Load model and all artifacts from file.
        
        Args:
            filepath (str): Path to load the model from
        """
        with open(filepath, 'rb') as f:
            artifacts = pickle.load(f)
        
        self.model = artifacts['model']
        self.scaler = artifacts['scaler']
        self.label_encoders = artifacts['label_encoders']
        self.target_encoder = artifacts['target_encoder']
        self.feature_names = artifacts['feature_names']
        self.metrics = artifacts['metrics']
        
        print(f"Model loaded successfully from {filepath}")


if __name__ == "__main__":
    # Example usage
    print("Depression Model Trainer Module")
    print("This module should be imported and used within the Streamlit app")
    print("\nExample usage:")
    print("from train_model import DepressionModelTrainer")
    print("trainer = DepressionModelTrainer()")
    print("metrics = trainer.train_and_evaluate(df)")