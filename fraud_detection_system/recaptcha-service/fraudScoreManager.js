/**
 * FraudGuard® - Fraud Score Manager
 *
 * Manages fraud scoring, IP blocking, and automatic score decay
 * with Redis persistence for reliability across restarts.
 */

const redis = require('./redisClient');

// Configuration from environment
const BLOCK_THRESHOLD = parseInt(process.env.BLOCK_THRESHOLD) || 100;
const BLOCK_TTL = parseInt(process.env.BLOCK_TTL) || 900; // 15 minutes in seconds
const SCORE_DECAY_INTERVAL = parseInt(process.env.SCORE_DECAY_INTERVAL) || 3600; // 1 hour
const SCORE_DECAY_AMOUNT = parseInt(process.env.SCORE_DECAY_AMOUNT) || 10;

// Score increments for different fraud events
const SCORE_INCREMENTS = {
    FAILED_CAPTCHA: 25,
    INVALID_CREDENTIALS: 15,
    RATE_LIMIT_HIT: 30,
    SUSPICIOUS_PATTERN: 20,
    AUTOMATED_BEHAVIOR: 50
};

// Redis key prefixes
const KEYS = {
    SCORE: (ip) => `fraud:score:${ip}`,
    BLOCKED: (ip) => `fraud:blocked:${ip}`,
    METADATA: (ip) => `fraud:meta:${ip}`,
    EVENT_LOG: (ip) => `fraud:events:${ip}`
};

/**
 * Get fraud score for an IP
 */
async function getScore(ip) {
    try {
        const score = await redis.get(KEYS.SCORE(ip));
        return parseInt(score) || 0;
    } catch (error) {
        console.error(`Error getting score for ${ip}:`, error);
        return 0;
    }
}

/**
 * Increment fraud score for an IP
 */
async function incrementScore(ip, eventType = 'UNKNOWN', incrementAmount = null) {
    try {
        const increment = incrementAmount || SCORE_INCREMENTS[eventType] || 10;
        const newScore = await redis.incrby(KEYS.SCORE(ip), increment);

        // Set expiry on score (auto-cleanup after 24 hours of inactivity)
        await redis.expire(KEYS.SCORE(ip), 86400);

        // Log the event
        await logEvent(ip, eventType, increment, newScore);

        console.log(`📈 Fraud score for ${ip}: ${newScore} (+${increment}) [${eventType}]`);

        // Check if threshold exceeded
        if (newScore >= BLOCK_THRESHOLD) {
            await blockIP(ip, `Score exceeded threshold (${newScore}/${BLOCK_THRESHOLD})`);
        }

        return newScore;
    } catch (error) {
        console.error(`Error incrementing score for ${ip}:`, error);
        return 0;
    }
}

/**
 * Block an IP address
 */
async function blockIP(ip, reason = 'High fraud score') {
    try {
        const blockData = JSON.stringify({
            blockedAt: new Date().toISOString(),
            reason: reason,
            score: await getScore(ip)
        });

        await redis.set(KEYS.BLOCKED(ip), blockData, BLOCK_TTL);

        console.log(`🚫 IP BLOCKED: ${ip} - ${reason} (TTL: ${BLOCK_TTL}s)`);

        return true;
    } catch (error) {
        console.error(`Error blocking IP ${ip}:`, error);
        return false;
    }
}

/**
 * Check if an IP is blocked
 */
async function isBlocked(ip) {
    try {
        const blocked = await redis.get(KEYS.BLOCKED(ip));
        return blocked !== null;
    } catch (error) {
        console.error(`Error checking if IP ${ip} is blocked:`, error);
        return false;
    }
}

/**
 * Get block details for an IP
 */
async function getBlockDetails(ip) {
    try {
        const blockData = await redis.get(KEYS.BLOCKED(ip));

        if (!blockData) {
            return null;
        }

        const data = JSON.parse(blockData);
        const ttl = await redis.ttl(KEYS.BLOCKED(ip));

        return {
            ...data,
            ttl: ttl,
            expiresIn: ttl > 0 ? `${Math.floor(ttl / 60)} minutes` : 'N/A'
        };
    } catch (error) {
        console.error(`Error getting block details for ${ip}:`, error);
        return null;
    }
}

/**
 * Unblock an IP address (manual intervention)
 */
async function unblockIP(ip) {
    try {
        const deleted = await redis.del(KEYS.BLOCKED(ip));

        if (deleted > 0) {
            console.log(`✅ IP UNBLOCKED: ${ip}`);
            await logEvent(ip, 'MANUAL_UNBLOCK', 0, await getScore(ip));
            return true;
        }

        return false;
    } catch (error) {
        console.error(`Error unblocking IP ${ip}:`, error);
        return false;
    }
}

/**
 * Reset fraud score for an IP (manual intervention)
 */
async function resetScore(ip) {
    try {
        await redis.del(KEYS.SCORE(ip));
        await redis.del(KEYS.METADATA(ip));

        console.log(`🔄 Score reset for IP: ${ip}`);
        await logEvent(ip, 'MANUAL_RESET', 0, 0);

        return true;
    } catch (error) {
        console.error(`Error resetting score for ${ip}:`, error);
        return false;
    }
}

/**
 * Log a fraud event
 */
async function logEvent(ip, eventType, scoreChange, newScore) {
    try {
        const event = JSON.stringify({
            timestamp: new Date().toISOString(),
            eventType: eventType,
            scoreChange: scoreChange,
            newScore: newScore
        });

        // Store last 10 events (using Redis list)
        const key = KEYS.EVENT_LOG(ip);
        await redis.set(key, event, 86400); // 24 hour expiry

        return true;
    } catch (error) {
        console.error(`Error logging event for ${ip}:`, error);
        return false;
    }
}

/**
 * Get all active IPs with fraud scores
 */
async function getAllScores() {
    try {
        const scoreKeys = await redis.keys(KEYS.SCORE('*'));
        const scores = [];

        for (const key of scoreKeys) {
            const ip = key.replace('fraud:score:', '');
            const score = parseInt(await redis.get(key)) || 0;
            const blocked = await isBlocked(ip);
            const blockDetails = blocked ? await getBlockDetails(ip) : null;

            scores.push({
                ip,
                score,
                blocked,
                blockDetails
            });
        }

        // Sort by score (highest first)
        scores.sort((a, b) => b.score - a.score);

        return scores;
    } catch (error) {
        console.error('Error getting all scores:', error);
        return [];
    }
}

/**
 * Get all blocked IPs
 */
async function getAllBlocked() {
    try {
        const blockedKeys = await redis.keys(KEYS.BLOCKED('*'));
        const blocked = [];

        for (const key of blockedKeys) {
            const ip = key.replace('fraud:blocked:', '');
            const details = await getBlockDetails(ip);
            const score = await getScore(ip);

            blocked.push({
                ip,
                score,
                ...details
            });
        }

        return blocked;
    } catch (error) {
        console.error('Error getting all blocked IPs:', error);
        return [];
    }
}

/**
 * Get comprehensive stats
 */
async function getStats() {
    try {
        const allScores = await getAllScores();
        const allBlocked = await getAllBlocked();

        const totalIPs = allScores.length;
        const blockedCount = allBlocked.length;
        const activeCount = totalIPs - blockedCount;

        // Calculate average score
        const avgScore = totalIPs > 0
            ? allScores.reduce((sum, item) => sum + item.score, 0) / totalIPs
            : 0;

        // Get high-risk IPs (score > 50 but not blocked)
        const highRisk = allScores.filter(item => item.score > 50 && !item.blocked);

        return {
            totalIPs,
            activeCount,
            blockedCount,
            highRiskCount: highRisk.length,
            averageScore: Math.round(avgScore * 10) / 10,
            threshold: BLOCK_THRESHOLD,
            blockTTL: BLOCK_TTL,
            redisStatus: redis.getStatus(),
            timestamp: new Date().toISOString()
        };
    } catch (error) {
        console.error('Error getting stats:', error);
        return {
            error: error.message,
            timestamp: new Date().toISOString()
        };
    }
}

/**
 * Apply score decay to all IPs
 * Called periodically to reduce scores over time
 */
async function applyScoreDecay() {
    try {
        console.log('🔄 Applying fraud score decay...');

        const scoreKeys = await redis.keys(KEYS.SCORE('*'));
        let decayedCount = 0;

        for (const key of scoreKeys) {
            const ip = key.replace('fraud:score:', '');
            const currentScore = await getScore(ip);

            if (currentScore > 0) {
                const newScore = Math.max(0, currentScore - SCORE_DECAY_AMOUNT);

                if (newScore === 0) {
                    await redis.del(key);
                } else {
                    await redis.set(key, String(newScore), 86400);
                }

                await logEvent(ip, 'SCORE_DECAY', -SCORE_DECAY_AMOUNT, newScore);
                decayedCount++;

                console.log(`  📉 ${ip}: ${currentScore} → ${newScore}`);
            }
        }

        console.log(`✅ Score decay complete: ${decayedCount} IPs processed`);

        return decayedCount;
    } catch (error) {
        console.error('Error applying score decay:', error);
        return 0;
    }
}

/**
 * Start automatic score decay interval
 */
function startScoreDecay() {
    console.log(`🕐 Starting automatic score decay (every ${SCORE_DECAY_INTERVAL}s)`);

    setInterval(async () => {
        await applyScoreDecay();
    }, SCORE_DECAY_INTERVAL * 1000);
}

/**
 * Middleware to check if request should be blocked
 */
async function checkRequest(ip) {
    const blocked = await isBlocked(ip);

    if (blocked) {
        const details = await getBlockDetails(ip);
        return {
            allowed: false,
            blocked: true,
            reason: details?.reason || 'IP is blocked',
            score: await getScore(ip),
            expiresIn: details?.expiresIn || 'N/A',
            ttl: details?.ttl || 0
        };
    }

    const score = await getScore(ip);

    return {
        allowed: true,
        blocked: false,
        score: score,
        threshold: BLOCK_THRESHOLD,
        warning: score > 50 ? 'High fraud score' : null
    };
}

// Export all functions
module.exports = {
    // Score management
    getScore,
    incrementScore,
    resetScore,

    // Blocking
    blockIP,
    unblockIP,
    isBlocked,
    getBlockDetails,

    // Stats and monitoring
    getAllScores,
    getAllBlocked,
    getStats,

    // Decay
    applyScoreDecay,
    startScoreDecay,

    // Middleware
    checkRequest,

    // Event types for scoring
    SCORE_EVENTS: SCORE_INCREMENTS
};
