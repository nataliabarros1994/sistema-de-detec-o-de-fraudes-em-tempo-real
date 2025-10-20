/**
 * FraudGuard® - Redis Client Module
 *
 * Provides Redis connection with automatic reconnection, graceful fallback,
 * and health monitoring for fraud score persistence.
 */

const Redis = require('ioredis');

// Configuration from environment
const REDIS_URL = process.env.REDIS_URL || 'redis://localhost:6379';
const REDIS_MAX_RETRIES = 3;
const REDIS_RETRY_DELAY = 1000; // 1 second

// Connection state
let redisClient = null;
let isConnected = false;
let connectionAttempts = 0;
let fallbackMode = false;

// In-memory fallback storage (used when Redis is unavailable)
const memoryStore = new Map();

/**
 * Create and configure Redis client
 */
function createRedisClient() {
    console.log(`📡 Connecting to Redis at ${REDIS_URL.replace(/:[^:]*@/, ':****@')}`);

    const client = new Redis(REDIS_URL, {
        maxRetriesPerRequest: REDIS_MAX_RETRIES,
        retryStrategy(times) {
            if (times > REDIS_MAX_RETRIES) {
                console.error(`❌ Redis connection failed after ${REDIS_MAX_RETRIES} attempts`);
                console.warn('⚠️  Switching to IN-MEMORY fallback mode');
                fallbackMode = true;
                return null; // Stop retrying
            }

            const delay = Math.min(times * REDIS_RETRY_DELAY, 5000);
            console.log(`🔄 Redis retry attempt ${times}/${REDIS_MAX_RETRIES} in ${delay}ms...`);
            return delay;
        },
        reconnectOnError(err) {
            console.error('🔴 Redis error:', err.message);
            return true; // Attempt to reconnect
        },
        lazyConnect: true, // Don't connect immediately
        enableReadyCheck: true,
        showFriendlyErrorStack: true
    });

    // Event handlers
    client.on('connect', () => {
        console.log('🔗 Redis connecting...');
        connectionAttempts++;
    });

    client.on('ready', () => {
        console.log('✅ Redis connected and ready');
        isConnected = true;
        fallbackMode = false;
        connectionAttempts = 0;
    });

    client.on('error', (err) => {
        console.error('❌ Redis error:', err.message);
        isConnected = false;
    });

    client.on('close', () => {
        console.warn('🔌 Redis connection closed');
        isConnected = false;
    });

    client.on('reconnecting', () => {
        console.log('🔄 Redis reconnecting...');
    });

    return client;
}

/**
 * Initialize Redis connection
 */
async function connect() {
    try {
        redisClient = createRedisClient();
        await redisClient.connect();

        // Test connection
        await redisClient.ping();
        console.log('🏓 Redis PING successful');

        return true;
    } catch (error) {
        console.error('❌ Failed to connect to Redis:', error.message);
        console.warn('⚠️  Running in IN-MEMORY fallback mode');
        fallbackMode = true;
        return false;
    }
}

/**
 * Get a value from Redis (with fallback to memory)
 */
async function get(key) {
    if (fallbackMode || !isConnected) {
        return memoryStore.get(key) || null;
    }

    try {
        return await redisClient.get(key);
    } catch (error) {
        console.error(`❌ Redis GET error for key ${key}:`, error.message);
        return memoryStore.get(key) || null;
    }
}

/**
 * Set a value in Redis (with fallback to memory)
 */
async function set(key, value, expirySeconds = null) {
    if (fallbackMode || !isConnected) {
        memoryStore.set(key, value);

        // Handle expiry in memory
        if (expirySeconds) {
            setTimeout(() => {
                memoryStore.delete(key);
            }, expirySeconds * 1000);
        }

        return 'OK';
    }

    try {
        if (expirySeconds) {
            return await redisClient.setex(key, expirySeconds, value);
        } else {
            return await redisClient.set(key, value);
        }
    } catch (error) {
        console.error(`❌ Redis SET error for key ${key}:`, error.message);

        // Fallback to memory
        memoryStore.set(key, value);
        return 'OK (memory)';
    }
}

/**
 * Increment a value in Redis (with fallback to memory)
 */
async function incr(key) {
    if (fallbackMode || !isConnected) {
        const current = parseInt(memoryStore.get(key) || '0');
        const newValue = current + 1;
        memoryStore.set(key, String(newValue));
        return newValue;
    }

    try {
        return await redisClient.incr(key);
    } catch (error) {
        console.error(`❌ Redis INCR error for key ${key}:`, error.message);

        // Fallback to memory
        const current = parseInt(memoryStore.get(key) || '0');
        const newValue = current + 1;
        memoryStore.set(key, String(newValue));
        return newValue;
    }
}

/**
 * Increment by a specific amount
 */
async function incrby(key, amount) {
    if (fallbackMode || !isConnected) {
        const current = parseInt(memoryStore.get(key) || '0');
        const newValue = current + amount;
        memoryStore.set(key, String(newValue));
        return newValue;
    }

    try {
        return await redisClient.incrby(key, amount);
    } catch (error) {
        console.error(`❌ Redis INCRBY error for key ${key}:`, error.message);

        const current = parseInt(memoryStore.get(key) || '0');
        const newValue = current + amount;
        memoryStore.set(key, String(newValue));
        return newValue;
    }
}

/**
 * Delete a key from Redis (with fallback to memory)
 */
async function del(key) {
    if (fallbackMode || !isConnected) {
        return memoryStore.delete(key) ? 1 : 0;
    }

    try {
        return await redisClient.del(key);
    } catch (error) {
        console.error(`❌ Redis DEL error for key ${key}:`, error.message);
        return memoryStore.delete(key) ? 1 : 0;
    }
}

/**
 * Get all keys matching a pattern
 */
async function keys(pattern) {
    if (fallbackMode || !isConnected) {
        const allKeys = Array.from(memoryStore.keys());

        // Simple pattern matching for memory store
        if (pattern === '*') {
            return allKeys;
        }

        // Convert Redis pattern to regex
        const regex = new RegExp('^' + pattern.replace(/\*/g, '.*') + '$');
        return allKeys.filter(key => regex.test(key));
    }

    try {
        return await redisClient.keys(pattern);
    } catch (error) {
        console.error(`❌ Redis KEYS error for pattern ${pattern}:`, error.message);
        return [];
    }
}

/**
 * Set expiry on a key
 */
async function expire(key, seconds) {
    if (fallbackMode || !isConnected) {
        // Implement expiry in memory
        setTimeout(() => {
            memoryStore.delete(key);
        }, seconds * 1000);
        return 1;
    }

    try {
        return await redisClient.expire(key, seconds);
    } catch (error) {
        console.error(`❌ Redis EXPIRE error for key ${key}:`, error.message);
        return 0;
    }
}

/**
 * Get time-to-live for a key
 */
async function ttl(key) {
    if (fallbackMode || !isConnected) {
        return -1; // No TTL tracking in memory mode
    }

    try {
        return await redisClient.ttl(key);
    } catch (error) {
        console.error(`❌ Redis TTL error for key ${key}:`, error.message);
        return -1;
    }
}

/**
 * Check if Redis is connected
 */
function isRedisConnected() {
    return isConnected && !fallbackMode;
}

/**
 * Get connection status
 */
function getStatus() {
    return {
        connected: isConnected,
        fallbackMode: fallbackMode,
        connectionAttempts: connectionAttempts,
        mode: fallbackMode ? 'MEMORY' : 'REDIS',
        memoryStoreSize: memoryStore.size
    };
}

/**
 * Clear all data (use with caution!)
 */
async function flushAll() {
    if (fallbackMode || !isConnected) {
        memoryStore.clear();
        return 'OK';
    }

    try {
        return await redisClient.flushall();
    } catch (error) {
        console.error('❌ Redis FLUSHALL error:', error.message);
        memoryStore.clear();
        return 'OK (memory)';
    }
}

/**
 * Get multiple values at once
 */
async function mget(...keys) {
    if (fallbackMode || !isConnected) {
        return keys.map(key => memoryStore.get(key) || null);
    }

    try {
        return await redisClient.mget(...keys);
    } catch (error) {
        console.error('❌ Redis MGET error:', error.message);
        return keys.map(key => memoryStore.get(key) || null);
    }
}

/**
 * Gracefully close Redis connection
 */
async function disconnect() {
    if (redisClient && isConnected) {
        console.log('📴 Closing Redis connection...');
        await redisClient.quit();
        console.log('✅ Redis connection closed gracefully');
    }

    memoryStore.clear();
}

// Export all functions
module.exports = {
    connect,
    disconnect,
    get,
    set,
    incr,
    incrby,
    del,
    keys,
    expire,
    ttl,
    mget,
    flushAll,
    isRedisConnected,
    getStatus
};
