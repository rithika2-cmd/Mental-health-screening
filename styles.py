def get_custom_css():
    """
    Return custom CSS styles for the application with modern FoodPriceAI-inspired design.
    
    Returns:
        str: CSS styles as a string
    """
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Main App Background */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    }
    
    .main {
        background: transparent;
        padding: 20px;
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Typography */
    h1 {
        font-size: 3.5em !important;
        font-weight: 800 !important;
        color: white !important;
        text-align: center;
        margin-bottom: 10px !important;
        letter-spacing: -1px;
    }
    
    h2 {
        font-size: 2em !important;
        font-weight: 700 !important;
        color: white;
        margin-top: 30px !important;
        margin-bottom: 25px !important;
    }
    
    h3 {
        font-size: 1.5em !important;
        font-weight: 600 !important;
        color: #e2e8f0;
        margin: 20px 0 15px 0 !important;
    }
    
    p, .stMarkdown, .stText {
        font-size: 1.1em !important;
        line-height: 1.6 !important;
        color: #94a3b8;
    }
    
    label {
        font-size: 1em !important;
        font-weight: 500 !important;
        color: #cbd5e1 !important;
    }
    
    /* Hero Section */
    .hero-subtitle {
        text-align: center;
        color: #94a3b8;
        font-size: 1.3em !important;
        margin-bottom: 10px;
        font-weight: 400;
    }
    
    .hero-description {
        text-align: center;
        color: #64748b;
        font-size: 1.1em !important;
        margin-bottom: 50px;
        max-width: 800px;
        margin-left: auto;
        margin-right: auto;
    }
    
    .gradient-text {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Cards */
    .feature-card {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 16px;
        padding: 30px;
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        background: rgba(30, 41, 59, 0.7);
        border-color: rgba(59, 130, 246, 0.5);
        transform: translateY(-5px);
    }
    
    .icon-wrapper {
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
        font-size: 24px;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
        color: white !important;
        border: none;
        padding: 14px 32px !important;
        font-size: 1em !important;
        font-weight: 600 !important;
        border-radius: 12px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 14px rgba(6, 182, 212, 0.4);
        letter-spacing: 0.3px;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(6, 182, 212, 0.6);
    }
    
    .primary-button {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
    }
    
    .secondary-button {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(148, 163, 184, 0.3) !important;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: rgba(15, 23, 42, 0.95);
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(148, 163, 184, 0.1);
        padding: 20px;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        font-size: 1em !important;
        font-weight: 500 !important;
        padding: 12px 16px !important;
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(59, 130, 246, 0.1);
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        font-size: 2.5em !important;
        font-weight: 700 !important;
        color: white !important;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 1em !important;
        font-weight: 500 !important;
        color: #94a3b8 !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .metric-card-custom {
        background: rgba(30, 41, 59, 0.5);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(148, 163, 184, 0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    
    /* Input Fields */
    .stTextInput input, .stNumberInput input, .stSelectbox select {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(148, 163, 184, 0.2) !important;
        border-radius: 8px !important;
        color: white !important;
        font-size: 1em !important;
        padding: 12px !important;
    }
    
    .stTextInput input:focus, .stNumberInput input:focus, .stSelectbox select:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Alerts */
    .stSuccess, .stWarning, .stError, .stInfo {
        background: rgba(30, 41, 59, 0.5) !important;
        backdrop-filter: blur(10px);
        border-radius: 12px !important;
        border-left: 4px solid !important;
        font-size: 1em !important;
        padding: 16px 20px !important;
    }
    
    .stSuccess {
        border-left-color: #10b981 !important;
        color: #d1fae5 !important;
    }
    
    .stWarning {
        border-left-color: #f59e0b !important;
        color: #fef3c7 !important;
    }
    
    .stError {
        border-left-color: #ef4444 !important;
        color: #fee2e2 !important;
    }
    
    .stInfo {
        border-left-color: #3b82f6 !important;
        color: #dbeafe !important;
    }
    
    /* DataFrames */
    .dataframe {
        background: rgba(30, 41, 59, 0.5) !important;
        border-radius: 12px !important;
        overflow: hidden;
    }
    
    .dataframe th {
        background: rgba(15, 23, 42, 0.8) !important;
        color: white !important;
        font-size: 0.95em !important;
        font-weight: 600 !important;
        padding: 12px !important;
        border-bottom: 1px solid rgba(148, 163, 184, 0.2) !important;
    }
    
    .dataframe td {
        padding: 10px !important;
        font-size: 0.9em !important;
        color: #cbd5e1 !important;
        border-bottom: 1px solid rgba(148, 163, 184, 0.1) !important;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
        height: 12px !important;
        border-radius: 6px;
    }
    
    .stProgress > div {
        background: rgba(30, 41, 59, 0.5) !important;
        border-radius: 6px;
    }
    
    /* File uploader */
    [data-testid="stFileUploader"] {
        background: rgba(30, 41, 59, 0.3);
        padding: 30px;
        border-radius: 16px;
        border: 2px dashed rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(59, 130, 246, 0.6);
        background: rgba(30, 41, 59, 0.5);
    }
    
    [data-testid="stFileUploader"] label {
        color: #cbd5e1 !important;
        font-size: 1.1em !important;
        font-weight: 500 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(30, 41, 59, 0.3);
        color: #94a3b8;
        font-size: 1em !important;
        font-weight: 500 !important;
        padding: 12px 24px !important;
        border-radius: 8px;
        border: 1px solid rgba(148, 163, 184, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%) !important;
        color: white !important;
    }
    
    /* Slider */
    .stSlider label {
        color: #cbd5e1 !important;
        font-size: 1em !important;
        font-weight: 500 !important;
    }
    
    .stSlider [data-baseweb="slider"] {
        background: rgba(148, 163, 184, 0.2);
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background: rgba(30, 41, 59, 0.5) !important;
        border: 1px solid rgba(148, 163, 184, 0.1) !important;
        border-radius: 12px !important;
        color: white !important;
        font-size: 1em !important;
        font-weight: 500 !important;
        padding: 14px !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(30, 41, 59, 0.7) !important;
        border-color: rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Prediction result box */
    .prediction-box {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 20px 50px rgba(6, 182, 212, 0.4);
        margin: 30px 0;
    }
    
    .prediction-box h2 {
        color: white !important;
        font-size: 1.5em !important;
        margin-bottom: 15px !important;
        opacity: 0.9;
    }
    
    .prediction-box h1 {
        color: white !important;
        font-size: 4em !important;
        margin: 20px 0 !important;
        font-weight: 800 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    /* Loading animation */
    .stSpinner > div {
        border-top-color: #3b82f6 !important;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: rgba(148, 163, 184, 0.2);
        margin: 30px 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 40px 20px;
        margin-top: 60px;
        border-top: 1px solid rgba(148, 163, 184, 0.1);
        color: #64748b;
    }
    
    .footer h2 {
        background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #8b5cf6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px !important;
    }
    </style>
    """