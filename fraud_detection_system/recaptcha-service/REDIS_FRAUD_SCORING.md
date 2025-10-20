# 🛡️ FraudGuard® - Redis-Based Fraud Scoring System

## 📋 Overview

The FraudGuard® reCAPTCHA service now includes a **persistent fraud scoring system** using Redis. This system tracks suspicious behavior, automatically blocks high-risk IPs, and provides a real-time admin dashboard for monitoring and manual intervention.

### Key Features

✅ **Persistent Fraud Scores** - Survives server restarts
✅ **Automatic IP Blocking** - Based on configurable thresholds
✅ **Score Decay** - Automatic reduction of scores over time
✅ **Admin Dashboard** - Real-time visualization and management
✅ **Graceful Fallback** - Works with in-memory storage if Redis is unavailable

---

## 🚀 Quick Start

### 1. Start Redis

**Option A: Docker (Recommended)**
```bash
docker run -d -p 6379:6379 --name fraud guard-redis redis:alpine
```

**Option B: Local Installation**
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Windows
# Download from https://redis.io/download
```

### 2. Install Dependencies

```bash
cd recaptcha-service
npm install
```

This will install `ioredis` along with other dependencies.

### 3. Configure Environment

```bash
cp .env.example .env
nano .env
```

**Add Redis configuration:**
```env
REDIS_URL=redis://localhost:6379
BLOCK_THRESHOLD=100
BLOCK_TTL=900
SCORE_DECAY_INTERVAL=3600
SCORE_DECAY_AMOUNT=10
ADMIN_TOKEN=your-secure-admin-token-here
```

### 4. Start the Server

```bash
npm start
```

**Expected output:**
```
🔌 Initializing Redis connection...
📡 Connecting to Redis at redis://localhost:6379
✅ Redis connected and ready
🏓 Redis PING successful
🕐 Starting automatic score decay (every 3600s)

🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️
🚀 FraudGuard® reCAPTCHA + Fraud Prevention Service
📍 Server running on: http://localhost:3000
🔐 Security: CAPTCHA verification active
📊 Fraud Scoring: Redis
⏰ Started at: 2025-10-16T15:00:00.000Z
🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️
```

---

## 🔧 How It Works

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Request                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │  IP Fraud Check Middleware   │
        │  - Check if IP is blocked    │
        │  - Get current fraud score   │
        └──────────┬───────────────────┘
                   │
            ┌──────┴──────┐
            │             │
        BLOCKED?        ALLOWED?
            │             │
            ▼             ▼
        Return       Process
        403          Request
                         │
                         ▼
                  ┌─────────────┐
                  │ CAPTCHA OK? │
                  └──────┬──────┘
                         │
                    ┌────┴────┐
                    │         │
                  FAIL      SUCCESS
                    │         │
                    ▼         │
        ┌─────────────────┐   │
        │ Increment Score │   │
        │  +25 points     │   │
        └────────┬────────┘   │
                 │             │
                 ▼             ▼
          Score > 100?    Proceed
                 │
            ┌────┴────┐
            │         │
          YES        NO
            │         │
            ▼         ▼
        Block IP   Continue
```

### Fraud Score Events

| Event | Score Increase | Description |
|-------|----------------|-------------|
| `FAILED_CAPTCHA` | +25 | Failed CAPTCHA verification |
| `INVALID_CREDENTIALS` | +15 | Wrong username/password |
| `RATE_LIMIT_HIT` | +30 | Too many requests |
| `SUSPICIOUS_PATTERN` | +20 | Detected suspicious behavior |
| `AUTOMATED_BEHAVIOR` | +50 | Bot-like patterns detected |

### Automatic Blocking

When an IP's fraud score reaches the threshold (default: 100), it is automatically blocked for a configurable duration (default: 15 minutes).

**Block Response:**
```json
{
  "blocked": true,
  "reason": "Score exceeded threshold (125/100)",
  "score": 125,
  "expiresIn": "14 minutes",
  "message": "Your IP has been temporarily blocked due to suspicious activity"
}
```

### Score Decay

Fraud scores automatically decrease over time to allow legitimate users who made mistakes to regain access.

**Default Configuration:**
- **Interval:** Every 1 hour
- **Decay Amount:** -10 points per interval

Example:
```
Hour 0: Score = 80 (3 failed CAPTCHA attempts)
Hour 1: Score = 70 (automatic decay)
Hour 2: Score = 60 (automatic decay)
Hour 3: Score = 50 (automatic decay)
```

---

## 📊 Admin Dashboard

### Accessing the Dashboard

**URL:**
```
http://localhost:3000/admin/dashboard?token=YOUR_ADMIN_TOKEN
```

Replace `YOUR_ADMIN_TOKEN` with the value from your `.env` file.

### Dashboard Features

**Statistics Cards:**
- Total IPs Tracked
- Active IPs (not blocked)
- Blocked IPs
- High Risk IPs (score > 50)

**System Information:**
- Redis connection status
- Block threshold setting
- Average fraud score

**IP Table:**
- Real-time list of all tracked IPs
- Current fraud scores
- Block status and details
- Manual unblock/reset actions

**Auto-Refresh:**
- Dashboard updates every 10 seconds
- Manual refresh button available

### Screenshots

```
┌──────────────────────────────────────────────────────────────┐
│  FraudGuard® Admin Dashboard                      🔄 Refresh │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐            │
│  │   45   │  │   42   │  │    3   │  │    5   │            │
│  │ Total  │  │ Active │  │Blocked │  │HighRisk│            │
│  └────────┘  └────────┘  └────────┘  └────────┘            │
│                                                               │
│  Redis: Connected (Redis) | Threshold: 100 | Avg: 32.5      │
│                                                               │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ IP Address      │ Score │ Status  │ Actions            │  │
│  ├────────────────────────────────────────────────────────┤  │
│  │ 192.168.1.100  │  125  │BLOCKED  │ [Unblock]         │  │
│  │ 10.0.0.50      │   75  │ Active  │ [Reset]           │  │
│  │ 172.16.0.10    │   45  │ Active  │ [Reset]           │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🧪 Testing

### Automated Test Suite

```bash
node test-fraud-scoring.js
```

**Test Scenarios:**

1. **Failed CAPTCHA Test**
   - Simulates 3 failed CAPTCHA attempts
   - Verifies fraud score increases

2. **IP Blocking Test**
   - Simulates 5 failed attempts
   - Verifies automatic blocking at threshold

3. **Admin Dashboard Test**
   - Checks admin endpoint authentication
   - Displays current statistics

4. **Manual Unblock Test**
   - Tests unblocking a previously blocked IP
   - Verifies score persistence

5. **Score Reset Test**
   - Tests manual score reset
   - Confirms score returns to 0

### Manual Testing

**Test 1: Simulate Failed CAPTCHA**
```bash
curl -X POST http://localhost:3000/verify-captcha \
  -H "Content-Type: application/json" \
  -H "X-Forwarded-For: 192.168.1.100" \
  -d '{"g-recaptcha-response":"invalid_token"}'
```

**Test 2: Check Fraud Stats**
```bash
curl http://localhost:3000/admin/fraud-stats \
  -H "X-Admin-Token: YOUR_ADMIN_TOKEN"
```

**Test 3: Unblock an IP**
```bash
curl -X POST http://localhost:3000/admin/unblock/192.168.1.100 \
  -H "X-Admin-Token: YOUR_ADMIN_TOKEN"
```

**Test 4: Reset Score**
```bash
curl -X POST http://localhost:3000/admin/reset-score/192.168.1.100 \
  -H "X-Admin-Token: YOUR_ADMIN_TOKEN"
```

---

## 🔒 Security Considerations

### Admin Token Security

**Generate a Secure Token:**
```bash
# macOS/Linux
openssl rand -hex 32

# Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

**Add to `.env`:**
```env
ADMIN_TOKEN=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

**Never expose the admin token:**
- ❌ Don't hardcode in frontend code
- ❌ Don't commit to version control
- ❌ Don't share in chat/email
- ✅ Use environment variables
- ✅ Rotate tokens regularly
- ✅ Use HTTPS in production

### Redis Security

**Best Practices:**

1. **Bind to localhost only** (if Redis is on same server)
   ```bash
   # In redis.conf
   bind 127.0.0.1
   ```

2. **Require password authentication**
   ```bash
   # In redis.conf
   requirepass YOUR_STRONG_PASSWORD

   # Update .env
   REDIS_URL=redis://:YOUR_STRONG_PASSWORD@localhost:6379
   ```

3. **Use SSL/TLS for remote connections**
   ```env
   REDIS_URL=rediss://username:password@redis-server.com:6380
   ```

4. **Disable dangerous commands**
   ```bash
   # In redis.conf
   rename-command FLUSHDB ""
   rename-command FLUSHALL ""
   rename-command CONFIG ""
   ```

---

## 📈 Fraud Score Persistence Benefits

### 1. Survives Server Restarts

**Without Redis (In-Memory):**
```
Server Start → Score: 0
3 Failed CAPTCHAs → Score: 75
Server Restart → Score: 0 ❌ (data lost)
3 More Failed → Score: 75 (attacker bypasses block)
```

**With Redis (Persistent):**
```
Server Start → Score: 0
3 Failed CAPTCHAs → Score: 75
Server Restart → Score: 75 ✅ (data persists)
3 More Failed → Score: 150 → BLOCKED
```

### 2. Cross-Instance Consistency

When running multiple server instances (load balancer), Redis ensures all instances see the same fraud scores.

```
Instance 1: IP 1.2.3.4 fails CAPTCHA → Score: 25 (saved to Redis)
Instance 2: IP 1.2.3.4 tries again → Reads score: 25 from Redis
Instance 2: IP 1.2.3.4 fails again → Score: 50 (updated in Redis)
Instance 1: IP 1.2.3.4 tries again → Reads score: 50 from Redis
```

### 3. Forensic Analysis

Persistent scores enable long-term fraud pattern analysis:

- Track attack patterns over days/weeks
- Identify coordinated attacks from IP ranges
- Generate reports on fraud trends
- Export data for ML model training

---

## 🔄 Graceful Fallback

If Redis is unavailable, the system automatically falls back to in-memory storage:

```
📡 Connecting to Redis at redis://localhost:6379
❌ Redis error: ECONNREFUSED
⚠️  Running in IN-MEMORY fallback mode

📊 Fraud Scoring: In-Memory
```

**Fallback Behavior:**
- ✅ All fraud scoring features work
- ✅ Blocking still functions
- ⚠️ Data lost on server restart
- ⚠️ No cross-instance synchronization

**Production Recommendation:** Always use Redis for reliability.

---

## 📊 Redis Data Structure

### Keys Used

```
fraud:score:<IP>         # Fraud score for IP
fraud:blocked:<IP>       # Block status and metadata
fraud:meta:<IP>          # Additional metadata
fraud:events:<IP>        # Last fraud event
```

### Example Data

**Score:**
```bash
redis-cli> GET fraud:score:192.168.1.100
"125"
```

**Block Details:**
```bash
redis-cli> GET fraud:blocked:192.168.1.100
"{\"blockedAt\":\"2025-10-16T15:30:00.000Z\",\"reason\":\"Score exceeded threshold (125/100)\",\"score\":125}"
```

**TTL (Time-to-Live):**
```bash
redis-cli> TTL fraud:blocked:192.168.1.100
897  # seconds remaining
```

### Manual Redis Commands

**View all fraud scores:**
```bash
redis-cli KEYS "fraud:score:*"
```

**View all blocked IPs:**
```bash
redis-cli KEYS "fraud:blocked:*"
```

**Get score for specific IP:**
```bash
redis-cli GET "fraud:score:192.168.1.100"
```

**Manually block an IP:**
```bash
redis-cli SETEX "fraud:blocked:192.168.1.100" 900 "{\"blockedAt\":\"$(date -Iseconds)\",\"reason\":\"Manual block\",\"score\":100}"
```

**Clear all fraud data (DANGEROUS):**
```bash
redis-cli KEYS "fraud:*" | xargs redis-cli DEL
```

---

## 🔧 Configuration Reference

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_URL` | `redis://localhost:6379` | Redis connection string |
| `BLOCK_THRESHOLD` | `100` | Score threshold for auto-blocking |
| `BLOCK_TTL` | `900` (15 min) | Block duration in seconds |
| `SCORE_DECAY_INTERVAL` | `3600` (1 hour) | Decay frequency in seconds |
| `SCORE_DECAY_AMOUNT` | `10` | Points to remove per decay |
| `ADMIN_TOKEN` | `admin-secret-token` | Admin dashboard auth token |

### Customization Examples

**Stricter Blocking (block faster):**
```env
BLOCK_THRESHOLD=50      # Block after 2 failed CAPTCHAs
BLOCK_TTL=1800          # Block for 30 minutes
```

**Lenient Scoring (for testing):**
```env
BLOCK_THRESHOLD=200     # Require 8 failed CAPTCHAs
SCORE_DECAY_INTERVAL=300  # Decay every 5 minutes
SCORE_DECAY_AMOUNT=25     # Faster decay
```

**Production (strict):**
```env
BLOCK_THRESHOLD=75      # Block after 3 failed CAPTCHAs
BLOCK_TTL=3600          # Block for 1 hour
SCORE_DECAY_INTERVAL=7200  # Decay every 2 hours
SCORE_DECAY_AMOUNT=5       # Slower decay
```

---

## 🐛 Troubleshooting

### Problem: Redis connection refused

**Error:**
```
❌ Redis error: ECONNREFUSED
⚠️  Running in IN-MEMORY fallback mode
```

**Solutions:**
```bash
# Check if Redis is running
redis-cli ping
# Should return: PONG

# If not running, start Redis
docker start fraudguard-redis
# or
brew services start redis
# or
sudo systemctl start redis
```

### Problem: Admin dashboard shows "Unauthorized"

**Cause:** Invalid or missing admin token

**Solutions:**
1. Check `.env` file has `ADMIN_TOKEN` set
2. Use token in URL: `http://localhost:3000/admin/dashboard?token=YOUR_TOKEN`
3. Or use header: `curl -H "X-Admin-Token: YOUR_TOKEN" ...`

### Problem: Scores not persisting

**Cause:** Redis not connected or in fallback mode

**Check:**
```bash
curl http://localhost:3000/health
```

Look for:
```json
{
  "redis": {
    "connected": true,
    "fallbackMode": false,
    "mode": "REDIS"
  }
}
```

### Problem: IPs not getting blocked

**Causes:**
1. Threshold too high
2. Score not incrementing
3. Middleware not applied

**Debug:**
1. Check server logs for `📈 Fraud score for X.X.X.X: ...`
2. Lower threshold: `BLOCK_THRESHOLD=25`
3. Verify middleware is applied to routes

---

## 📚 API Endpoints Reference

### Public Endpoints

**All public endpoints automatically check fraud scores:**

```
POST /verify-captcha    - Increments score on failure
POST /api/login         - Checks blocking before processing
```

### Admin Endpoints

**All require `X-Admin-Token` header or `?token=` parameter:**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/admin/fraud-stats` | Get all fraud statistics (JSON) |
| `GET` | `/admin/dashboard?token=XXX` | Admin dashboard (HTML) |
| `POST` | `/admin/unblock/:ip` | Manually unblock an IP |
| `POST` | `/admin/reset-score/:ip` | Reset fraud score to 0 |

---

## 🎯 Integration with FraudGuard® ML Model

The fraud scoring system complements your existing ML-based fraud detection:

### Use Fraud Score as ML Feature

```javascript
// In your main FraudGuard® API
app.post('/api/transaction', async (req, res) => {
  // Step 1: Get fraud score from reCAPTCHA service
  const fraudScoreResponse = await fetch('http://localhost:3000/admin/fraud-stats', {
    headers: { 'X-Admin-Token': process.env.ADMIN_TOKEN }
  });
  const scoreData = await fraudScoreResponse.json();

  const ipFraudScore = scoreData.activeIPs.find(ip => ip.ip === req.ip)?.score || 0;

  // Step 2: Call ML model with fraud score as feature
  const mlResponse = await fetch('http://localhost:8000/predict', {
    method: 'POST',
    body: JSON.stringify({
      user_id: req.user.id,
      amount: req.body.amount,
      ip_fraud_score: ipFraudScore,  // ← Add as ML feature
      // ... other features
    })
  });

  const mlResult = await mlResponse.json();

  // Step 3: Combined decision
  if (ipFraudScore > 75 || mlResult.fraud_probability > 0.85) {
    return res.status(403).json({ error: 'Transaction blocked' });
  }

  res.json({ success: true });
});
```

---

## 🎉 Conclusion

The Redis-based fraud scoring system provides:

✅ **Persistent Protection** - Scores survive restarts
✅ **Automatic Blocking** - No manual intervention needed
✅ **Real-Time Monitoring** - Admin dashboard visibility
✅ **Graceful Degradation** - Works without Redis
✅ **Production-Ready** - Battle-tested security

**Next Steps:**
1. Start Redis: `docker run -d -p 6379:6379 redis:alpine`
2. Configure `.env` with your settings
3. Start server: `npm start`
4. Run tests: `node test-fraud-scoring.js`
5. Access dashboard: `http://localhost:3000/admin/dashboard?token=YOUR_TOKEN`

---

**🛡️ FraudGuard® - Enterprise Fraud Prevention**

*For questions: Check main README.md or INTEGRATION_GUIDE.md*
