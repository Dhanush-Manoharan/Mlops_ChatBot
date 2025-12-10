"""Cloud SQL connection for production"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

def get_db_url():
    """Get database URL for Cloud SQL or local"""
    
    # For Cloud Run with Cloud SQL
    if os.getenv('ENVIRONMENT') == 'production':
        db_user = os.getenv('DB_USER', 'postgres')
        db_pass = os.getenv('DB_PASS')
        db_name = os.getenv('DB_NAME', 'propbot')
        instance_connection_name = os.getenv('INSTANCE_CONNECTION_NAME')
        
        # Cloud SQL connection string
        return f"postgresql+psycopg2://{db_user}:{db_pass}@/{db_name}?host=/cloudsql/{instance_connection_name}"
    else:
        # Local development
        return os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/propbot')

DATABASE_URL = get_db_url()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()