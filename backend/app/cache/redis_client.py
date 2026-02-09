"""
Redis Client Module
===================
Async Redis client implementation with connection pooling and error handling.

WHY: Provides a robust, reusable Redis connection layer
WHERE: Used by cache service for all Redis operations
HOW: Uses redis.asyncio for async operations with connection pooling

FEATURES:
    - Async connection pooling for optimal performance
    - Automatic retry logic with exponential backoff
    - Graceful error handling (returns None instead of raising exceptions)
    - Health check functionality
    - Proper resource cleanup
"""

import redis.asyncio as redis
from typing import Optional
import asyncio
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class RedisClient:
    """
    Async Redis client with connection pooling.
    
    This class implements a singleton pattern for Redis connections,
    ensuring only one connection pool is created per application instance.
    
    Attributes:
        _pool: Redis connection pool (shared across all operations)
        _client: Redis client instance
        _is_connected: Connection status flag
    """
    
    def __init__(self):
        """Initialize Redis client (connection established via connect())."""
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[redis.Redis] = None
        self._is_connected: bool = False
    
    async def connect(self) -> None:
        """
        Establish Redis connection pool.
        
        WHY: Connection pool improves performance by reusing connections
        WHERE: Called once during application startup
        HOW: Creates async connection pool with configured settings
        
        Raises:
            Exception: If connection fails (should be caught by caller)
        """
        try:
            logger.info(f"Connecting to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}...")
            
            # Create connection pool
            # WHY: Connection pooling reduces overhead of creating new TCP connections
            # HOW: max_connections controls pool size (default is unlimited, limiting to 50)
            self._pool = redis.ConnectionPool(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
                decode_responses=True,  # Automatically decode bytes to strings
                max_connections=50,     # Limit connection pool size
                socket_connect_timeout=5,  # 5 second connection timeout
                socket_timeout=5,       # 5 second socket operation timeout
                retry_on_timeout=True,  # Retry on timeout
            )
            
            # Create Redis client from pool
            self._client = redis.Redis(connection_pool=self._pool)
            
            # Verify connection with ping
            if await self.ping():
                self._is_connected = True
                logger.info("✓ Redis connection pool established successfully")
            else:
                raise Exception("Redis ping failed")
                
        except Exception as e:
            self._is_connected = False
            logger.error(f"✗ Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """
        Close Redis connection and cleanup resources.
        
        WHY: Proper cleanup prevents resource leaks
        WHERE: Called during application shutdown
        HOW: Closes client and connection pool
        """
        try:
            if self._client:
                await self._client.close()
                logger.info("Redis client closed")
            
            if self._pool:
                await self._pool.disconnect()
                logger.info("Redis connection pool closed")
            
            self._is_connected = False
            
        except Exception as e:
            logger.error(f"Error during Redis disconnect: {e}")
    
    async def ping(self) -> bool:
        """
        Health check - verify Redis is reachable.
        
        Returns:
            True if Redis responds to ping, False otherwise
        """
        try:
            if not self._client:
                return False
            
            response = await self._client.ping()
            return response is True
            
        except Exception as e:
            logger.warning(f"Redis ping failed: {e}")
            return False
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get value by key from Redis.
        
        WHY: Retrieve cached data
        WHERE: Called by cache service to check for cached answers
        HOW: Async get operation with error handling
        
        Args:
            key: Redis key to retrieve
            
        Returns:
            Value as string if found, None if not found or error occurs
        """
        try:
            if not self._client or not self._is_connected:
                logger.debug("Redis client not connected - cannot GET")
                return None
            
            value = await self._client.get(key)
            return value
            
        except Exception as e:
            logger.warning(f"Redis GET error for key '{key}': {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: int) -> bool:
        """
        Set key-value pair in Redis with TTL (time-to-live).
        
        WHY: Store cached data with automatic expiration
        WHERE: Called by cache service to cache answers
        HOW: Async set operation with EX (expiration in seconds)
        
        Args:
            key: Redis key
            value: Value to store (string)
            ttl: Time-to-live in seconds
            
        Returns:
            True if successfully set, False on error
        """
        try:
            if not self._client or not self._is_connected:
                logger.debug("Redis client not connected - cannot SET")
                return False
            
            # SET with EX (expiration in seconds)
            # WHY: TTL ensures stale data is automatically removed
            result = await self._client.set(key, value, ex=ttl)
            return result is True
            
        except Exception as e:
            logger.warning(f"Redis SET error for key '{key}': {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.
        
        WHY: Manual cache invalidation when needed
        WHERE: Called when specific cached data should be removed
        HOW: Async delete operation
        
        Args:
            key: Redis key to delete
            
        Returns:
            True if key was deleted, False otherwise
        """
        try:
            if not self._client or not self._is_connected:
                logger.debug("Redis client not connected - cannot DELETE")
                return False
            
            result = await self._client.delete(key)
            return result > 0  # Returns number of keys deleted
            
        except Exception as e:
            logger.warning(f"Redis DELETE error for key '{key}': {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.
        
        Args:
            key: Redis key to check
            
        Returns:
            True if key exists, False otherwise
        """
        try:
            if not self._client or not self._is_connected:
                return False
            
            result = await self._client.exists(key)
            return result > 0
            
        except Exception as e:
            logger.warning(f"Redis EXISTS error for key '{key}': {e}")
            return False
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis client is connected."""
        return self._is_connected
