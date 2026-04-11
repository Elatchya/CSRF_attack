import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

def train_and_evaluate():
    print("Loading data...")
    # Load the dataset
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'flood.csv')
    df = pd.read_csv(data_path)
    
    # Define features and target
    X = df.drop('FloodProbability', axis=1)
    y = df['FloodProbability']
    
    print("Splitting dataset...")
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print("Training Linear Regression...")
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)
    lr_preds = lr_model.predict(X_test)
    
    lr_r2 = r2_score(y_test, lr_preds)
    lr_rmse = np.sqrt(mean_squared_error(y_test, lr_preds))
    print(f"Linear Regression - R2: {lr_r2:.4f}, RMSE: {lr_rmse:.4f}")
    
    print("Training Random Forest...")
    rf_model = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    rf_preds = rf_model.predict(X_test)
    
    rf_r2 = r2_score(y_test, rf_preds)
    rf_rmse = np.sqrt(mean_squared_error(y_test, rf_preds))
    print(f"Random Forest - R2: {rf_r2:.4f}, RMSE: {rf_rmse:.4f}")
    
    # Select best model based on higher R2
    if rf_r2 > lr_r2:
        print("Selecting Random Forest as the best model.")
        best_model = rf_model
        
        # Extract feature importance
        importances = rf_model.feature_importances_
        features = X.columns
        feature_importance = {features[i]: float(importances[i]) for i in range(len(features))}
    else:
        print("Selecting Linear Regression as the best model.")
        best_model = lr_model
        # For LR, we can use coefficients as a proxy for feature importance, 
        # though RF is explicitly asked in the prompt.
        # But if RF is somehow worse (unlikely here), we'll gracefully fallback:
        coeffs = np.abs(lr_model.coef_)
        total = np.sum(coeffs)
        features = X.columns
        feature_importance = {features[i]: float(coeffs[i]/total) for i in range(len(features))}

    print("Saving model and feature importance...")
    model_data = {
        'model': best_model,
        'feature_importance': feature_importance,
        'features': list(X.columns)
    }
    
    model_out_path = os.path.join(os.path.dirname(__file__), 'model.joblib')
    joblib.dump(model_data, model_out_path)
    print(f"Model successfully saved to {model_out_path}")

if __name__ == '__main__':
    train_and_evaluate()
