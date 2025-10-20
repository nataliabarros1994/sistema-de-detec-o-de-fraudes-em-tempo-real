# 🚀 FraudGuard® Redis Fraud Scoring - Deployment Checklist

## ✅ Implementation Complete

All fraud scoring features have been implemented and are ready for deployment.

---

## 📋 Pre-Deployment Checklist

### 1. Install Dependencies

```bash
npm install
```

This will install the new `ioredis` dependency along with existing packages.

### 2. Start Redis Server

**Option A: Using Docker (Recommended)**
```bash
docker run -d --name fraudguard-redis -p 6379:6379 redis:alpine
```

**Option B: Local Redis Installation**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# macOS
brew install redis
brew services start redis

# Windows
# Download from: https://redis.io/download
```

**Verify Redis is Running:**
```bash
redis-cli ping
# Expected output: PONG
```

### 3. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env

# Edit .env and configure:
nano .env
```

**Required Configuration:**
```env
# Server
PORT=3000

# Google reCAPTCHA (get keys from https://www.google.com/recaptcha/admin/create)
RECAPTCHA_SITE_KEY=your_actual_site_key_here
RECAPTCHA_SECRET=your_actual_secret_key_here

# Redis
REDIS_URL=redis://localhost:6379

# Fraud Scoring
BLOCK_THRESHOLD=100           # Auto-block at 100 points
BLOCK_TTL=900                 # 15 minutes block duration
SCORE_DECAY_INTERVAL=3600     # Decay every 1 hour
SCORE_DECAY_AMOUNT=10         # Reduce by 10 points per decay

# Admin Dashboard
ADMIN_TOKEN=your_secure_random_token_here
```

**Generate a Secure Admin Token:**
```bash
# Linux/macOS
openssl rand -hex 32

# Or use Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

### 4. Start the Server

```bash
npm start
```

**Expected Console Output:**
```
✅ Environment variables loaded
🔌 Attempting to connect to Redis...
✅ Connected to Redis at localhost:6379
🏓 Redis PING successful
📊 Fraud scoring system initialized
🎯 Fraud score decay job started (runs every 3600 seconds)
🚀 FraudGuard® reCAPTCHA Service running on port 3000
📊 Fraud Scoring: Redis
🔗 Health check: http://localhost:3000/health
🎨 Demo page: http://localhost:3000
📊 Admin Dashboard: http://localhost:3000/admin/dashboard?token=YOUR_TOKEN
```

---

## 🧪 Testing

### Run Automated Tests

```bash
node test-fraud-scoring.js
```

**What the tests do:**
1. ✅ Simulate 3 failed CAPTCHA attempts (score = 75)
2. ✅ Simulate 5 failed attempts to trigger auto-block
3. ✅ Fetch admin dashboard statistics
4. ✅ Test manual IP unblock
5. ✅ Test score reset

**Expected test output:**
```
🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️
🚀 FraudGuard® Fraud Scoring Test Suite
🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️

✅ Server is running and healthy

======================================================================
🧪 Test: Failed CAPTCHA Attempts
======================================================================
Testing IP: 192.168.1.100
  Attempt 1/3: CAPTCHA failed (expected)
  → Fraud score should have increased by ~25 points
  ...
✅ Test complete. Checking fraud score...

📊 IP Status for 192.168.1.100:
  Fraud Score: 75
  Status: ✅ Active
```

### Manual Testing with curl

**Test Failed CAPTCHA:**
```bash
curl -X POST http://localhost:3000/verify-captcha \
  -H "Content-Type: application/json" \
  -H "X-Forwarded-For: 203.0.113.50" \
  -d '{"g-recaptcha-response": "invalid_token"}'
```

**Check Admin Stats:**
```bash
curl http://localhost:3000/admin/fraud-stats \
  -H "X-Admin-Token: YOUR_ADMIN_TOKEN"
```

**Unblock an IP:**
```bash
curl -X POST http://localhost:3000/admin/unblock/203.0.113.50 \
  -H "X-Admin-Token: YOUR_ADMIN_TOKEN"
```

---

## 🎨 Access the Admin Dashboard

Open in your browser:
```
http://localhost:3000/admin/dashboard?token=YOUR_ADMIN_TOKEN
```

**Dashboard Features:**
- 📊 Real-time statistics (Total IPs, Active, Blocked, High Risk)
- 📋 IP table with fraud scores and status
- 🔄 Auto-refresh every 10 seconds
- 🚫 Manual unblock buttons
- 🔄 Score reset buttons
- 🔍 Filter blocked IPs

---

## 🔍 Verify Redis Data

Connect to Redis CLI and inspect data:

```bash
redis-cli

# List all fraud score keys
KEYS fraud:score:*

# Check specific IP score
GET fraud:score:192.168.1.100

# List all blocked IPs
KEYS fraud:blocked:*

# Check if IP is blocked
GET fraud:blocked:192.168.1.100
TTL fraud:blocked:192.168.1.100

# Check recent fraud events
ZRANGE fraud:events 0 -1 WITHSCORES
```

---

## 📊 Fraud Score Events

| Event Type | Score Increase | When It Happens |
|-----------|----------------|-----------------|
| `FAILED_CAPTCHA` | +25 | Invalid reCAPTCHA token |
| `INVALID_CREDENTIALS` | +15 | (Future) Login with wrong password |
| `RAPID_REQUESTS` | +20 | (Future) Rate limiting trigger |
| `SUSPICIOUS_PATTERN` | +30 | (Future) ML model detection |
| `MULTIPLE_ACCOUNTS` | +35 | (Future) Same IP, many accounts |

**Auto-Block Threshold:** 100 points
**Block Duration:** 15 minutes (configurable)
**Score Decay:** -10 points every hour

---

## 🔐 Security Checklist

- [ ] Generated secure ADMIN_TOKEN (32+ characters)
- [ ] Configured Redis password (if exposing Redis remotely)
- [ ] Set proper firewall rules (Redis port 6379 not public)
- [ ] ADMIN_TOKEN is in .env (NOT in .env.example)
- [ ] .env is in .gitignore (NOT committed to Git)
- [ ] Redis configured with persistence (RDB/AOF) for production
- [ ] Admin dashboard only accessible on trusted networks
- [ ] HTTPS enabled in production (reverse proxy)

---

## 🐛 Troubleshooting

### Redis Connection Failed

**Symptoms:**
```
❌ Failed to connect to Redis
⚠️  Running in IN-MEMORY fallback mode
```

**Solutions:**
1. Check Redis is running: `redis-cli ping`
2. Verify REDIS_URL in .env: `redis://localhost:6379`
3. Check firewall: `telnet localhost 6379`
4. Review Redis logs: `docker logs fraudguard-redis`

**Note:** System will continue working in fallback mode, but fraud scores won't persist across restarts.

### Admin Dashboard 401 Error

**Symptoms:**
```
Invalid admin token
```

**Solutions:**
1. Check ADMIN_TOKEN in .env matches URL token
2. Restart server after changing .env
3. Use header instead: `-H "X-Admin-Token: YOUR_TOKEN"`

### Scores Not Decaying

**Symptoms:**
Fraud scores remain high forever

**Solutions:**
1. Check console for decay job messages
2. Verify SCORE_DECAY_INTERVAL in .env (default: 3600)
3. Check Redis: `GET fraud:score:IP_ADDRESS`
4. Manually trigger: restart server (decay runs on startup)

### IP Not Getting Blocked

**Symptoms:**
Score exceeds 100 but IP still allowed

**Solutions:**
1. Check BLOCK_THRESHOLD in .env
2. Verify Redis connection (not in fallback mode)
3. Check console logs for block messages
4. Test: `GET fraud:blocked:IP_ADDRESS` in redis-cli

---

## 📈 Production Deployment

### Redis Production Setup

**Enable Persistence:**
```bash
# In redis.conf
save 900 1        # Save after 900s if 1 key changed
save 300 10       # Save after 300s if 10 keys changed
save 60 10000     # Save after 60s if 10000 keys changed

appendonly yes    # Enable AOF for durability
```

**Set Redis Password:**
```bash
# In redis.conf
requirepass YOUR_STRONG_PASSWORD_HERE

# Update .env
REDIS_URL=redis://:YOUR_PASSWORD@localhost:6379
```

### Scaling Considerations

**Multiple Server Instances:**
- ✅ Redis centralizes fraud scores across all instances
- ✅ All instances see the same blocked IPs
- ✅ Score increments are atomic (safe for concurrent access)

**Redis Cluster:**
- Update REDIS_URL to cluster nodes
- ioredis supports cluster mode automatically
- No code changes required

**High Availability:**
- Use Redis Sentinel for automatic failover
- Configure multiple Redis replicas
- ioredis reconnects automatically

---

## 🎯 Success Criteria

Your deployment is successful if:

1. ✅ Server starts without errors
2. ✅ Redis connection successful (no "fallback mode" warning)
3. ✅ Test suite passes all 5 tests
4. ✅ Admin dashboard loads and shows data
5. ✅ Failed CAPTCHA increases fraud score
6. ✅ Score >= 100 triggers auto-block
7. ✅ Blocked IP gets 403 on next request
8. ✅ Manual unblock works from dashboard
9. ✅ Scores decay over time
10. ✅ Redis data persists after server restart

---

## 📚 Documentation

- **REDIS_FRAUD_SCORING.md** - Complete technical documentation
- **REDIS_FRAUD_FEATURE_COMPLETE.md** - Implementation summary
- **README.md** - Original project documentation
- **INTEGRATION_GUIDE.md** - Integration with ML backend

---

## 🆘 Support

If you encounter issues:

1. Check server console logs
2. Check Redis connection: `redis-cli ping`
3. Review .env configuration
4. Run test suite: `node test-fraud-scoring.js`
5. Check Redis data: `redis-cli KEYS fraud:*`

---

## ✅ You're Ready!

All fraud scoring features are implemented and tested. Follow the checklist above to deploy.

**Quick Start Command:**
```bash
# Install, configure, and run
npm install && cp .env.example .env && nano .env && npm start
```

**Then open:**
- Main app: http://localhost:3000
- Admin dashboard: http://localhost:3000/admin/dashboard?token=YOUR_TOKEN

---

**FraudGuard® - Enterprise Fraud Detection** 🛡️
