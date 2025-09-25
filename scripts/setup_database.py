#!/usr/bin/env python3
"""
Database setup and initialization script
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from emergent_playtest_designer.database import (
    get_database_manager, 
    get_redis_cache, 
    init_database,
    get_table_info
)
from loguru import logger

def test_redis_connection():
    """Test Redis connection and basic operations"""
    logger.info("🔧 Testing Redis connection...")
    
    try:
        cache = get_redis_cache()
        
        if not cache.test_connection():
            return False
        
        # Test basic operations
        test_key = "test_key_setup"
        test_value = {"message": "Hello from setup!", "timestamp": 12345}
        
        cache.set(test_key, test_value, expire=60)
        retrieved = cache.get(test_key)
        
        if retrieved == test_value:
            logger.info("✅ Redis read/write test successful")
            cache.delete(test_key)
            return True
        else:
            logger.error(f"❌ Redis data mismatch: {retrieved} != {test_value}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Redis test failed: {e}")
        return False

def test_postgresql_connection():
    """Test PostgreSQL connection and operations"""
    logger.info("🔧 Testing PostgreSQL connection...")
    
    try:
        db_manager = get_database_manager()
        
        if not db_manager.test_connection():
            return False
        
        # Show connection pool info
        pool_info = db_manager.get_connection_info()
        logger.info(f"📊 PostgreSQL pool info: {pool_info}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ PostgreSQL test failed: {e}")
        return False

def setup_environment_variables():
    """Guide user through environment variable setup"""
    logger.info("🔧 Checking environment variables...")
    
    required_vars = [
        ('POSTGRES_HOST', 'localhost'),
        ('POSTGRES_PORT', '5432'),
        ('POSTGRES_DATABASE', 'emergent_playtest'),
        ('POSTGRES_USERNAME', 'postgres'),
        ('POSTGRES_PASSWORD', 'password'),
        ('REDIS_HOST', 'localhost'),
        ('REDIS_PORT', '6379'),
        ('REDIS_PASSWORD', ''),
        ('REDIS_DATABASE', '0')
    ]
    
    env_file_content = []
    missing_vars = []
    
    for var_name, default_value in required_vars:
        current_value = os.getenv(var_name)
        
        if current_value is None:
            missing_vars.append(var_name)
            env_file_content.append(f"{var_name}={default_value}")
            logger.info(f"📝 {var_name}: using default '{default_value}'")
        else:
            logger.info(f"✅ {var_name}: configured")
    
    if missing_vars:
        logger.info(f"⚠️ Missing environment variables: {', '.join(missing_vars)}")
        
        env_file_path = Path.cwd() / '.env'
        if not env_file_path.exists():
            with open(env_file_path, 'w') as f:
                f.write("# Database Configuration\n")
                f.write("\n".join(env_file_content))
            
            logger.info(f"📄 Created .env file with defaults: {env_file_path}")
            logger.info("🔧 Please update .env with your actual database credentials")
        else:
            logger.info("📄 .env file already exists - please verify database settings")
    else:
        logger.info("✅ All environment variables configured")

def main():
    """Main setup function"""
    logger.info("🚀 EMERGENT PLAYTEST DESIGNER - DATABASE SETUP")
    logger.info("=" * 60)
    
    # Step 1: Environment variables
    setup_environment_variables()
    
    # Step 2: Test connections
    redis_ok = test_redis_connection()
    postgres_ok = test_postgresql_connection()
    
    if not redis_ok:
        logger.error("❌ Redis connection failed!")
        logger.info("🔧 Make sure Redis is running: redis-server")
        logger.info("🔧 Or use Docker: docker run -d -p 6379:6379 redis:7-alpine")
        return False
    
    if not postgres_ok:
        logger.error("❌ PostgreSQL connection failed!")
        logger.info("🔧 Make sure PostgreSQL is running")
        logger.info("🔧 Or use Docker: docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=password postgres:15")
        return False
    
    # Step 3: Initialize database
    logger.info("🔧 Initializing database schema...")
    
    init_success = init_database(force_recreate=False)
    
    if not init_success:
        logger.error("❌ Database initialization failed!")
        return False
    
    # Step 4: Show table information
    logger.info("📊 Database tables created:")
    table_info = get_table_info()
    for table_name, info in table_info.items():
        logger.info(f"  📋 {table_name}: {len(info['columns'])} columns")
    
    # Step 5: Final verification
    logger.info("🔧 Running final verification...")
    
    # Test Redis info
    redis_info = get_redis_cache().get_info()
    if redis_info:
        logger.info(f"📊 Redis info: {redis_info.get('redis_version', 'N/A')} - {redis_info.get('connected_clients', 0)} clients")
    
    logger.info("=" * 60)
    logger.info("🎉 DATABASE SETUP COMPLETE!")
    logger.info("✅ Redis: Ready for real-time caching")
    logger.info("✅ PostgreSQL: Ready for persistent storage")  
    logger.info("🚀 Your ML-Agents system is now production-ready!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
