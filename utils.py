# utils.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from io import StringIO
import requests

def load_data_from_url(url):
    """
    Load CSV data from a URL.
    
    Args:
        url (str): URL pointing to CSV file
        
    Returns:
        tuple: (DataFrame, error_message) - DataFrame if successful, None if error
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        csv_data = StringIO(response.text)
        df = pd.read_csv(csv_data)
        return df, None
    except Exception as e:
        return None, str(e)

def load_data_from_file(uploaded_file):
    """
    Load CSV data from an uploaded file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        tuple: (DataFrame, error_message) - DataFrame if successful, None if error
    """
    try:
        df = pd.read_csv(uploaded_file)
        return df, None
    except Exception as e:
        return None, str(e)

def get_dataset_info(df):
    """
    Get comprehensive information about the dataset.
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        dict: Dictionary containing dataset statistics
    """
    info = {
        'rows': df.shape[0],
        'columns': df.shape[1],
        'missing_values': df.isnull().sum().sum(),
        'memory_usage_kb': df.memory_usage(deep=True).sum() / 1024,
        'dtypes': df.dtypes.to_dict(),
        'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
        'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
        'duplicates': df.duplicated().sum()
    }
    return info

def plot_confusion_matrix(conf_matrix):
    """
    Plot confusion matrix heatmap.
    
    Args:
        conf_matrix (np.ndarray): Confusion matrix from sklearn
        
    Returns:
        matplotlib.figure.Figure: Confusion matrix plot
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create heatmap
    sns.heatmap(conf_matrix, 
                annot=True, 
                fmt='d', 
                cmap='RdYlGn',
                linewidths=0.5,
                linecolor='white',
                square=True,
                cbar_kws={"shrink": 0.75},
                ax=ax)
    
    ax.set_xlabel('Predicted Labels', fontsize=14, fontweight='bold')
    ax.set_ylabel('True Labels', fontsize=14, fontweight='bold')
    ax.set_title('Confusion Matrix', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig

def plot_target_distribution(df, target_column):
    """
    Plot distribution of target variable.
    
    Args:
        df (pd.DataFrame): Input dataframe
        target_column (str): Name of target column
        
    Returns:
        matplotlib.figure.Figure: Distribution plot
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Count plot
    value_counts = df[target_column].value_counts()
    colors = plt.cm.Set3(np.linspace(0, 1, len(value_counts)))
    
    bars = ax1.bar(value_counts.index.astype(str), value_counts.values, 
                   color=colors, edgecolor='black', linewidth=2)
    
    ax1.set_xlabel('Depression Level', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax1.set_title('Class Distribution', fontsize=14, fontweight='bold', pad=15)
    ax1.tick_params(axis='x', rotation=45)
    
    # Add count labels on bars
    for bar in bars:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom',
                fontsize=10, fontweight='bold')
    
    # Pie chart
    wedges, texts, autotexts = ax2.pie(value_counts.values, 
                                       labels=value_counts.index.astype(str),
                                       autopct='%1.1f%%',
                                       colors=colors,
                                       startangle=90,
                                       explode=[0.05]*len(value_counts),
                                       shadow=True)
    
    ax2.set_title('Class Percentage', fontsize=14, fontweight='bold', pad=15)
    
    # Style pie chart text
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontsize(10)
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    return fig

def plot_correlation_matrix(df):
    """
    Plot correlation matrix heatmap for numeric columns.
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        matplotlib.figure.Figure: Correlation matrix plot or None
    """
    # Select only numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    
    if len(numeric_df.columns) < 2:
        return None
    
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Calculate correlation matrix
    corr_matrix = numeric_df.corr()
    
    # Create heatmap
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    sns.heatmap(corr_matrix, 
                mask=mask,
                annot=True, 
                fmt='.2f', 
                cmap='coolwarm',
                center=0,
                linewidths=0.5,
                linecolor='white',
                square=True,
                cbar_kws={"shrink": 0.8},
                ax=ax)
    
    ax.set_title('Feature Correlation Matrix', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    return fig

def plot_feature_importance(feature_importance_df, top_n=15):
    """
    Plot feature importance from trained model.
    
    Args:
        feature_importance_df (pd.DataFrame): DataFrame with Feature and Importance columns
        top_n (int): Number of top features to display
        
    Returns:
        matplotlib.figure.Figure: Feature importance plot
    """
    # Sort and select top N features
    sorted_df = feature_importance_df.sort_values('Importance', ascending=True).tail(top_n)
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create horizontal bar plot
    bars = ax.barh(range(len(sorted_df)), sorted_df['Importance'], 
                   color=plt.cm.viridis(np.linspace(0, 1, len(sorted_df))),
                   edgecolor='black', linewidth=1)
    
    ax.set_yticks(range(len(sorted_df)))
    ax.set_yticklabels(sorted_df['Feature'], fontsize=11)
    ax.set_xlabel('Importance Score', fontsize=12, fontweight='bold')
    ax.set_title(f'Top {top_n} Feature Importances', fontsize=14, fontweight='bold', pad=15)
    
    # Add value labels on bars
    for i, (bar, importance) in enumerate(zip(bars, sorted_df['Importance'])):
        width = bar.get_width()
        ax.text(width + 0.001, bar.get_y() + bar.get_height()/2,
                f'{importance:.4f}', va='center', fontsize=10, fontweight='bold')
    
    # Add grid
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    return fig

def plot_prediction_comparison(y_test, y_pred, target_encoder):
    """
    Plot comparison between actual and predicted values.
    
    Args:
        y_test (array): Actual target values (encoded)
        y_pred (array): Predicted target values (encoded)
        target_encoder: LabelEncoder used for target encoding
        
    Returns:
        matplotlib.figure.Figure: Comparison plot
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # Get all possible classes from the encoder
    all_classes = np.arange(len(target_encoder.classes_))
    
    # Count plot for actual vs predicted
    actual_counts = pd.Series(y_test).value_counts()
    predicted_counts = pd.Series(y_pred).value_counts()
    
    # Ensure all classes are represented (even with 0 counts)
    actual_counts = actual_counts.reindex(all_classes, fill_value=0)
    predicted_counts = predicted_counts.reindex(all_classes, fill_value=0)
    
    x = np.arange(len(all_classes))
    width = 0.35
    
    bars1 = ax1.bar(x - width/2, actual_counts.values, width, 
                    label='Actual', color='skyblue', edgecolor='black')
    bars2 = ax1.bar(x + width/2, predicted_counts.values, width, 
                    label='Predicted', color='lightcoral', edgecolor='black')
    
    ax1.set_xlabel('Class', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax1.set_title('Actual vs Predicted Distribution', fontsize=14, fontweight='bold', pad=15)
    ax1.set_xticks(x)
    ax1.set_xticklabels(target_encoder.classes_, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:  # Only show label if bar has height
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{int(height)}', ha='center', va='bottom', fontsize=9)
    
    # Scatter plot with jitter for individual predictions
    jitter_amount = 0.1
    x_jitter = np.random.normal(0, jitter_amount, len(y_test))
    y_jitter = np.random.normal(0, jitter_amount, len(y_pred))
    
    correct = y_test == y_pred
    incorrect = ~correct
    
    if np.any(correct):
        ax2.scatter(np.array(y_test)[correct] + x_jitter[correct], 
                   np.array(y_pred)[correct] + y_jitter[correct],
                   color='green', alpha=0.6, s=50, label='Correct', edgecolors='black')
    
    if np.any(incorrect):
        ax2.scatter(np.array(y_test)[incorrect] + x_jitter[incorrect], 
                   np.array(y_pred)[incorrect] + y_jitter[incorrect],
                   color='red', alpha=0.6, s=50, label='Incorrect', edgecolors='black')
    
    # Add diagonal line for perfect prediction
    min_val = min(all_classes.min(), all_classes.min())
    max_val = max(all_classes.max(), all_classes.max())
    ax2.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Perfect Prediction')
    
    ax2.set_xlabel('Actual Values', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Predicted Values', fontsize=12, fontweight='bold')
    ax2.set_title('Individual Predictions', fontsize=14, fontweight='bold', pad=15)
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Set tick labels to class names
    ax2.set_xticks(all_classes)
    ax2.set_yticks(all_classes)
    ax2.set_xticklabels(target_encoder.classes_, rotation=45, ha='right')
    ax2.set_yticklabels(target_encoder.classes_)
    
    plt.tight_layout()
    return fig

if __name__ == "__main__":
    print("Utils Module - Helper Functions for Mental Health AI Predictor")
    print("This module contains data loading and visualization functions.")