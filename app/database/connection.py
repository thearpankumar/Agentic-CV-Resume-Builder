from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import streamlit as st
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import settings

Base = declarative_base()

class DatabaseConnection:
    def __init__(self):
        self.database_config = settings.database_config
        self.engine = None
        self.SessionLocal = None
        self._initialize_connection()

    def _initialize_connection(self):
        try:
            # Add SSL configuration for cloud databases
            connect_args = {}
            if "localhost" not in self.database_config["url"]:
                connect_args["sslmode"] = "require"
            
            self.engine = create_engine(
                self.database_config["url"],
                pool_pre_ping=True,
                pool_recycle=300,
                echo=self.database_config["echo"],
                connect_args=connect_args
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        except Exception as e:
            st.error(f"Failed to connect to database: {e}")
            raise
    
    def get_session(self):
        """Get database session"""
        if self.SessionLocal is None:
            self._initialize_connection()
        return self.SessionLocal()
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                return True
        except SQLAlchemyError as e:
            st.error(f"Database connection test failed: {e}")
            return False
    
    def close_connection(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()

# Global database instance
@st.cache_resource
def get_db_connection():
    return DatabaseConnection()

# Dependency for getting database session
def get_db_session():
    db_conn = get_db_connection()
    session = db_conn.get_session()
    try:
        yield session
    finally:
        session.close()