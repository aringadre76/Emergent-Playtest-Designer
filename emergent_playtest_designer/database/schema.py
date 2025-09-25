"""
Database schema initialization and management
"""

from sqlalchemy import create_engine
from loguru import logger
from .models import Base
from .connection import get_database_manager

def create_tables(engine=None):
    """Create all database tables"""
    if engine is None:
        db_manager = get_database_manager()
        engine = db_manager.engine
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        return False

def drop_tables(engine=None):
    """Drop all database tables (use with caution!)"""
    if engine is None:
        db_manager = get_database_manager()
        engine = db_manager.engine
    
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("⚠️ All database tables dropped")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to drop database tables: {e}")
        return False

def init_database(force_recreate: bool = False):
    """Initialize database with tables and initial data"""
    db_manager = get_database_manager()
    
    # Test connection first
    if not db_manager.test_connection():
        logger.error("❌ Cannot initialize database - connection failed")
        return False
    
    # Create tables
    if force_recreate:
        logger.warning("🔄 Force recreating database tables...")
        drop_tables(db_manager.engine)
    
    success = create_tables(db_manager.engine)
    
    if success:
        logger.info("🚀 Database initialization complete!")
        
        # Log connection pool info
        pool_info = db_manager.get_connection_info()
        logger.info(f"📊 Connection pool: {pool_info}")
        
    return success

def get_table_info():
    """Get information about database tables"""
    db_manager = get_database_manager()
    
    table_info = {}
    for table_name, table in Base.metadata.tables.items():
        table_info[table_name] = {
            'columns': [col.name for col in table.columns],
            'primary_keys': [col.name for col in table.primary_key.columns],
            'foreign_keys': [f"{fk.parent.name} -> {fk.column.table.name}.{fk.column.name}" 
                           for fk in table.foreign_keys]
        }
    
    return table_info
