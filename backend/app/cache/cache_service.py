"""
Cache Service Module
====================
High-level caching service for chatbot Q&A responses.

WHY: Abstracts caching logic from business logic
WHERE: Used by chat routes to cache and retrieve answers
HOW: Uses Redis client for storage, SHA256 for cache keys

FEATURES:
    - Question normalization for consistent cache keys
    - SHA256-based cache key generation
    - Response time tracking
    - JSON serialization for complex objects
    - TTL-based automatic expiration
"""

import hashlib
import json
import time
from typing import Optional, Tuple
from app.cache.redis_client import RedisClient
from app.core.logger import get_logger
from app.core.config import settings

logger = get_logger(__name__)


class CacheService:
    """
    Cache service for chatbot Q&A responses.
    
    This service provides high-level caching operations specifically
    designed for chatbot question-answer pairs.
    
    Cache Key Format: chatbot:qa:<sha256_hash_of_normalized_question>
    
    Attributes:
        redis_client: Redis client instance for cache operations
        enabled: Whether caching is enabled (from settings)
        ttl: Cache time-to-live in seconds (from settings)
    """
    
    def __init__(self, redis_client: RedisClient):
        """
        Initialize cache service.
        
        Args:
            redis_client: RedisClient instance for cache operations
        """
        self.redis_client = redis_client
        self.enabled = settings.CACHE_ENABLED
        self.ttl = settings.CACHE_TTL
        
        logger.info(f"Cache Service initialized (enabled={self.enabled}, ttl={self.ttl}s)")
    
    def _normalize_question(self, question: str) -> str:
        """
        Normalize question text for consistent cache keys.
        
        WHY: Different case/whitespace should map to same cache entry
        WHERE: Called before generating cache key
        HOW: Lowercase + strip whitespace
        
        Args:
            question: Raw question text
            
        Returns:
            Normalized question text
            
        Example:
            "  What is AI?  " -> "what is ai?"
            "WHAT IS AI?" -> "what is ai?"
        """
        # Convert to lowercase and strip leading/trailing whitespace
        # WHY: Ensures "Hello" and "hello" use same cache key
        normalized = question.lower().strip()
        
        # Replace multiple spaces with single space
        # WHY: "What  is  AI?" and "What is AI?" should match
        normalized = " ".join(normalized.split())
        
        return normalized
    
    def _generate_cache_key(self, question: str) -> str:
        """
        Generate cache key from question using SHA256 hash.
        
        WHY: 
            - Hash ensures consistent key length regardless of question length
            - SHA256 virtually eliminates collision risk
            - Normalized questions produce same hash
        
        WHERE: Called before cache GET/SET operations
        HOW: SHA256 hash of normalized question
        
        Args:
            question: Raw question text
            
        Returns:
            Cache key in format: chatbot:qa:<64-char-hash>
            
        Example:
            "What is AI?" -> "chatbot:qa:a7b3c8d9e1f2..."
        """
        # Normalize question first
        normalized = self._normalize_question(question)
        
        # Generate SHA256 hash
        # WHY: SHA256 provides excellent distribution and low collision probability
        hash_obj = hashlib.sha256(normalized.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        
        # Construct cache key with prefix
        # WHY: Prefix allows easy identification and bulk operations
        cache_key = f"{settings.CACHE_KEY_PREFIX}:{hash_hex}"
        
        logger.debug(f"Cache key generated: '{normalized}' -> '{cache_key}'")
        
        return cache_key
    
    async def get_cached_answer(self, question: str) -> Tuple[Optional[str], float]:
        """
        Retrieve cached answer for a question.
        
        WHY: Avoid expensive database/RAG queries for repeated questions
        WHERE: Called at start of chat endpoint before database lookup
        HOW: Generate cache key, retrieve from Redis, track retrieval time
        
        Args:
            question: User's question text
            
        Returns:
            Tuple of (cached_answer, retrieval_time_ms)
            - cached_answer: JSON string of ChatResponse or None if not cached
            - retrieval_time_ms: Time taken to retrieve cache (milliseconds)
            
        Example:
            answer, time_ms = await cache_service.get_cached_answer("What is AI?")
            if answer:
                print(f"Cache HIT in {time_ms}ms")
        """
        # Track retrieval time for performance monitoring
        start_time = time.time()
        
        try:
            # Check if caching is enabled
            if not self.enabled:
                logger.debug("Caching disabled - skipping cache check")
                return None, 0.0
            
            # Check if Redis is connected
            if not self.redis_client.is_connected:
                logger.debug("Redis not connected - cache unavailable")
                return None, 0.0
            
            # Generate cache key
            cache_key = self._generate_cache_key(question)
            
            # Retrieve from Redis
            cached_value = await self.redis_client.get(cache_key)
            
            # Calculate retrieval time
            retrieval_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            
            if cached_value:
                logger.debug(f"Cache HIT for key: {cache_key} (retrieved in {retrieval_time:.2f}ms)")
                return cached_value, retrieval_time
            else:
                logger.debug(f"Cache MISS for key: {cache_key}")
                return None, retrieval_time
                
        except Exception as e:
            retrieval_time = (time.time() - start_time) * 1000
            logger.warning(f"Error retrieving from cache: {e}")
            return None, retrieval_time
    
    async def cache_answer(self, question: str, answer: str) -> bool:
        """
        Store answer in cache with TTL.
        
        WHY: Speed up future requests for the same question
        WHERE: Called after successfully generating answer
        HOW: Generate cache key, serialize answer, store in Redis with TTL
        
        Args:
            question: User's question text
            answer: Answer to cache (JSON string or plain text)
            
        Returns:
            True if successfully cached, False otherwise
            
        Example:
            success = await cache_service.cache_answer(
                "What is AI?",
                '{"reply": "AI is artificial intelligence..."}'
            )
        """
        try:
            # Check if caching is enabled
            if not self.enabled:
                logger.debug("Caching disabled - skipping cache storage")
                return False
            
            # Check if Redis is connected
            if not self.redis_client.is_connected:
                logger.debug("Redis not connected - cannot cache answer")
                return False
            
            # Generate cache key
            cache_key = self._generate_cache_key(question)
            
            # Store in Redis with TTL
            # WHY: TTL ensures stale answers are automatically removed
            success = await self.redis_client.set(
                key=cache_key,
                value=answer,
                ttl=self.ttl
            )
            
            if success:
                logger.debug(f"Answer cached successfully (key: {cache_key}, TTL: {self.ttl}s)")
            else:
                logger.warning(f"Failed to cache answer (key: {cache_key})")
            
            return success
            
        except Exception as e:
            logger.warning(f"Error caching answer: {e}")
            return False
    
    async def invalidate_cache(self, question: str) -> bool:
        """
        Manually invalidate (delete) cached answer for a question.
        
        WHY: Allow manual cache invalidation when answer changes
        WHERE: Called by admin endpoints or update operations
        HOW: Generate cache key, delete from Redis
        
        Args:
            question: Question whose cached answer should be invalidated
            
        Returns:
            True if cache entry was deleted, False otherwise
        """
        try:
            if not self.enabled or not self.redis_client.is_connected:
                return False
            
            cache_key = self._generate_cache_key(question)
            
            success = await self.redis_client.delete(cache_key)
            
            if success:
                logger.info(f"Cache invalidated for question: '{question}'")
            else:
                logger.debug(f"No cache entry found for question: '{question}'")
            
            return success
            
        except Exception as e:
            logger.warning(f"Error invalidating cache: {e}")
            return False
    
    def _generate_option_cache_key(self, from_node_id: str, option_text: str) -> str:
        """
        Generate cache key for option-based navigation.
        
        WHY: Option selections from same node should be cached
        WHERE: Called when user clicks an option button
        HOW: SHA256 hash of node_id + option_text combination
        
        Args:
            from_node_id: UUID of the current node
            option_text: Text of the selected option
            
        Returns:
            Cache key in format: chatbot:option:<64-char-hash>
            
        Example:
            node_id="abc-123" + option="Learn More" -> "chatbot:option:a7b3c8..."
        """
        # Normalize option text (same as question normalization)
        normalized_option = self._normalize_question(option_text)
        
        # Combine node_id and option text for unique cache key
        # WHY: Same option from different nodes should have different responses
        cache_input = f"{from_node_id}:{normalized_option}"
        
        # Generate SHA256 hash
        hash_obj = hashlib.sha256(cache_input.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        
        # Use different prefix for option-based cache
        # WHY: Allows separate management of question cache vs option cache
        cache_key = f"chatbot:option:{hash_hex}"
        
        logger.debug(f"Option cache key generated: node={from_node_id}, option='{normalized_option}' -> '{cache_key}'")
        
        return cache_key
    
    async def get_cached_option_response(self, from_node_id: str, option_text: str) -> Tuple[Optional[str], float]:
        """
        Retrieve cached response for an option selection.
        
        WHY: Avoid database queries for repeated option selections
        WHERE: Called when user clicks an option button
        HOW: Generate option cache key, retrieve from Redis
        
        Args:
            from_node_id: UUID of the current node (as string)
            option_text: Text of the selected option
            
        Returns:
            Tuple of (cached_response, retrieval_time_ms)
            - cached_response: JSON string of ChatResponse or None
            - retrieval_time_ms: Time taken to retrieve (milliseconds)
        """
        start_time = time.time()
        
        try:
            if not self.enabled or not self.redis_client.is_connected:
                return None, 0.0
            
            # Generate option-specific cache key
            cache_key = self._generate_option_cache_key(from_node_id, option_text)
            
            # Retrieve from Redis
            cached_value = await self.redis_client.get(cache_key)
            
            retrieval_time = (time.time() - start_time) * 1000
            
            if cached_value:
                logger.debug(f"Option cache HIT for key: {cache_key} (retrieved in {retrieval_time:.2f}ms)")
                return cached_value, retrieval_time
            else:
                logger.debug(f"Option cache MISS for key: {cache_key}")
                return None, retrieval_time
                
        except Exception as e:
            retrieval_time = (time.time() - start_time) * 1000
            logger.warning(f"Error retrieving option cache: {e}")
            return None, retrieval_time
    
    async def cache_option_response(self, from_node_id: str, option_text: str, response: str) -> bool:
        """
        Store option selection response in cache.
        
        WHY: Speed up future selections of the same option
        WHERE: Called after navigating through option edge
        HOW: Generate option cache key, store in Redis with TTL
        
        Args:
            from_node_id: UUID of the current node (as string)
            option_text: Text of the selected option
            response: Response to cache (JSON string)
            
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            if not self.enabled or not self.redis_client.is_connected:
                return False
            
            # Generate option-specific cache key
            cache_key = self._generate_option_cache_key(from_node_id, option_text)
            
            # Store in Redis with TTL
            success = await self.redis_client.set(
                key=cache_key,
                value=response,
                ttl=self.ttl
            )
            
            if success:
                logger.debug(f"Option response cached (key: {cache_key}, TTL: {self.ttl}s)")
            else:
                logger.warning(f"Failed to cache option response (key: {cache_key})")
            
            return success
            
        except Exception as e:
            logger.warning(f"Error caching option response: {e}")
            return False
    
    async def clear_all_cache(self) -> bool:
        """
        Clear all chatbot Q&A cache entries.
        
        WARNING: This will delete ALL cached answers!
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.enabled or not self.redis_client.is_connected:
                return False
            
            # This would require scanning all keys with prefix
            # For now, logging a warning that this is a destructive operation
            logger.warning("clear_all_cache called - implement key scanning if needed")
            
            # Note: Implementation requires SCAN command to avoid blocking Redis
            # Left as future enhancement if needed
            
            return False
            
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
