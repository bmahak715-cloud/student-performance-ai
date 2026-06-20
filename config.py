import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

class Config:
    # Flask Security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-student-performance')
    
    # Database Settings
    DB_DIR = BASE_DIR / 'database'
    # Ensure database directory exists
    DB_DIR.mkdir(exist_ok=True)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f'sqlite:///{DB_DIR}/student_performance.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Machine Learning Model Paths
    MODELS_DIR = BASE_DIR / 'models'
    MODELS_DIR.mkdir(exist_ok=True)
    
    RISK_MODEL_PATH = MODELS_DIR / 'risk_model.pkl'
    MARKS_MODEL_PATH = MODELS_DIR / 'marks_model.pkl'
    PREPROCESSOR_PATH = MODELS_DIR / 'preprocessing_pipeline.pkl'
    FEATURE_NAMES_PATH = MODELS_DIR / 'feature_names.pkl'
    
    # Datasets
    DATASETS_DIR = BASE_DIR / 'datasets'
    DATASETS_DIR.mkdir(exist_ok=True)
    DATASET_PATH = DATASETS_DIR / 'student_data.csv'
    
    # Model Thresholds
    RISK_LOW_THRESHOLD = float(os.environ.get('RISK_LOW_THRESHOLD', 0.30))
    RISK_HIGH_THRESHOLD = float(os.environ.get('RISK_HIGH_THRESHOLD', 0.60))
    
    # GenAI API Configuration (Optional)
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', None)
