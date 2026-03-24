# config.py - Configuration Settings

# Page Configuration
PAGE_TITLE = "🧠 Mental Health AI Predictor"
PAGE_ICON = "🧠"
LAYOUT = "wide"

# Model Configuration
MODEL_PARAMS = {
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 5,
    'random_state': 42,
    'n_jobs': -1
}

# Data Configuration
TARGET_COLUMN = 'Depression'
TEST_SIZE_DEFAULT = 0.2
RANDOM_STATE_DEFAULT = 42

# File Paths
MODEL_SAVE_PATH = 'models/depression_model.pkl'

# UI Configuration
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#43e97b',
    'warning': '#f093fb',
    'info': '#4facfe'
}

# Chart Configuration
CHART_COLORS = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b']
DEFAULT_FIGSIZE = (14, 8)

# Navigation Pages
PAGES = [
    "📁 Load Data",
    "🤖 Train Model", 
    "🔮 Make Predictions",
    "📊 Visualizations"
]

# Messages
MESSAGES = {
    'no_data': "⚠️ Please load data first from the 'Load Data' page!",
    'no_model': "⚠️ Please train the model first from the 'Train Model' page!",
    'no_depression_column': f"❌ '{TARGET_COLUMN}' column not found in dataset!",
    'model_ready': "✅ Model is ready for predictions!",
    'data_loaded': "✅ Data loaded successfully!",
    'model_trained': "✅ Model trained successfully!",
    'prediction_made': "✅ Prediction completed successfully!"
}