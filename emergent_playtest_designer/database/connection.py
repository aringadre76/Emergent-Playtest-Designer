"""
Database connection management for PostgreSQL and Redis
"""

import os
import asyncio
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import redis
from loguru import logger

class DatabaseManager:
    """Manages PostgreSQL connections with connection pooling"""
    
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or self._get_database_url()
        self.engine = None
        self.SessionLocal = None
        self._initialize_engine()
    
    def _get_database_url(self) -> str:
        """Get database URL from environment variables"""
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        database = os.getenv('POSTGRES_DATABASE', 'emergent_playtest')
        username = os.getenv('POSTGRES_USERNAME', 'postgres')
        password = os.getenv('POSTGRES_PASSWORD', 'password')
        
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    def _initialize_engine(self):
        """Initialize SQLAlchemy engine with connection pooling"""
        self.engine = create_engine(
            self.database_url,
            poolclass=QueuePool,
            pool_size=20,          # Number of connections to maintain in pool
            max_overflow=30,       # Additional connections beyond pool_size
            pool_pre_ping=True,    # Validate connections before use
            pool_recycle=3600,     # Recycle connections every hour
            echo=False             # Set to True for SQL debugging
        )
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        logger.info(f"Database engine initialized with URL: {self.database_url.split('@')[1]}")
    
    @contextmanager
    def get_session(self):
        """Get a database session with automatic cleanup"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """Test database connectivity"""
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("✅ PostgreSQL connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            return False
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection pool information"""
        if not self.engine:
            return {}
        
        pool = self.engine.pool
        return {
            'pool_size': pool.size(),
            'connections_checked_in': pool.checkedin(),
            'connections_checked_out': pool.checkedout(),
            'connections_overflow': pool.overflow(),
            'connections_invalidated': pool.invalidated(),
        }

class RedisCache:
    """Redis cache manager for high-speed data access"""
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or self._get_redis_url()
        self.client = None
        self._initialize_client()
    
    def _get_redis_url(self) -> str:
        """Get Redis URL from environment variables"""
        host = os.getenv('REDIS_HOST', 'localhost')
        port = os.getenv('REDIS_PORT', '6379')
        password = os.getenv('REDIS_PASSWORD', '')
        database = os.getenv('REDIS_DATABASE', '0')
        
        if password:
            return f"redis://:{password}@{host}:{port}/{database}"
        return f"redis://{host}:{port}/{database}"
    
    def _initialize_client(self):
        """Initialize Redis client with connection pooling"""
        # Create connection pool first
        pool = redis.ConnectionPool.from_url(
            self.redis_url,
            max_connections=50,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True
        )
        
        self.client = redis.Redis(
            connection_pool=pool,
            decode_responses=True    # Automatically decode byte responses
        )
        
        logger.info(f"Redis client initialized: {self.redis_url.split('@')[1] if '@' in self.redis_url else self.redis_url}")
    
    def test_connection(self) -> bool:
        """Test Redis connectivity"""
        try:
            response = self.client.ping()
            if response:
                logger.info("✅ Redis connection successful")
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            return False
    
    def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration"""
        try:
            import json
            if not isinstance(value, str):
                value = json.dumps(value)
            
            result = self.client.set(key, value, ex=expire)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis SET error for key '{key}': {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value by key, with automatic JSON decoding"""
        try:
            value = self.client.get(key)
            if value is None:
                return None
            
            # Try to parse as JSON, fall back to string
            try:
                import json
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Redis GET error for key '{key}': {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete a key"""
        try:
            result = self.client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis DELETE error for key '{key}': {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return bool(self.client.exists(key))
        except Exception as e:
            logger.error(f"Redis EXISTS error for key '{key}': {e}")
            return False
    
    def expire(self, key: str, seconds: int) -> bool:
        """Set expiration for a key"""
        try:
            return bool(self.client.expire(key, seconds))
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key '{key}': {e}")
            return False
    
    def flush_all(self) -> bool:
        """Clear all Redis data (use with caution!)"""
        try:
            self.client.flushall()
            logger.warning("Redis FLUSHALL executed - all data cleared")
            return True
        except Exception as e:
            logger.error(f"Redis FLUSHALL error: {e}")
            return False
    
    def get_info(self) -> Dict[str, Any]:
        """Get Redis server information"""
        try:
            info = self.client.info()
            return {
                'redis_version': info.get('redis_version'),
                'connected_clients': info.get('connected_clients'),
                'used_memory_human': info.get('used_memory_human'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses'),
            }
        except Exception as e:
            logger.error(f"Redis INFO error: {e}")
            return {}

# Global instances (singleton pattern)
_database_manager: Optional[DatabaseManager] = None
_redis_cache: Optional[RedisCache] = None

def get_database_manager() -> DatabaseManager:
    """Get global database manager instance"""
    global _database_manager
    if _database_manager is None:
        _database_manager = DatabaseManager()
    return _database_manager

def get_redis_cache() -> RedisCache:
    """Get global Redis cache instance"""
    global _redis_cache
    if _redis_cache is None:
        _redis_cache = RedisCache()
    return _redis_cache
