# 🚀 FraudGuard® - Quick Access Guide

## ✅ Server Status: RUNNING

Your FraudGuard® reCAPTCHA + Fraud Scoring system is now live!

---

## 🔗 Access URLs

### 🎨 Admin Dashboard
**Click here to access the admin dashboard:**

```
http://localhost:3000/admin/dashboard?token=91cc29f33505f7f6856f5412faa79a3b8a19fc8b481d649feaca7b33f5523b9f
```

### 🌐 Public Pages
- **Demo Page:** http://localhost:3000
- **FraudGuard Login:** http://localhost:3000/fraudguard.html
- **Health Check:** http://localhost:3000/health

---

## 🔑 Your Admin Token

```
91cc29f33505f7f6856f5412faa79a3b8a19fc8b481d649feaca7b33f5523b9f
```

**Keep this secure!** This token gives full access to:
- View fraud statistics
- Unblock IPs
- Reset fraud scores
- Access admin dashboard

---

## 📊 System Status

✅ **Node.js Server:** Running on port 3000
✅ **Redis:** Connected and operational
✅ **Fraud Scoring:** Active (Redis mode)
✅ **reCAPTCHA:** Configured with test keys
✅ **Auto-Block Threshold:** 100 points
✅ **Block Duration:** 15 minutes
✅ **Score Decay:** -10 points/hour

---

## 🧪 Test the System

### Run Automated Tests
```bash
cd /home/nataliabarros1994/Downloads/"🚀 Sistema de Detecção de Fraudes em Tempo Real - Guia Completo"/fraud_detection_system/recaptcha-service
node test-fraud-scoring.js
```

### Test with curl

**Failed CAPTCHA (increases score by 25):**
```bash
curl -X POST http://localhost:3000/verify-captcha \
  -H "Content-Type: application/json" \
  -H "X-Forwarded-For: 192.168.1.100" \
  -d '{"g-recaptcha-response": "invalid_token"}'
```

**Check Fraud Stats:**
```bash
curl http://localhost:3000/admin/fraud-stats \
  -H "X-Admin-Token: 91cc29f33505f7f6856f5412faa79a3b8a19fc8b481d649feaca7b33f5523b9f"
```

**Unblock an IP:**
```bash
curl -X POST http://localhost:3000/admin/unblock/192.168.1.100 \
  -H "X-Admin-Token: 91cc29f33505f7f6856f5412faa79a3b8a19fc8b481d649feaca7b33f5523b9f"
```

---

## 📡 API Endpoints

### Public Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main demo page |
| GET | `/health` | Health check |
| POST | `/verify-captcha` | Verify CAPTCHA (increments score on fail) |
| GET | `/api/site-key` | Get public reCAPTCHA key |

### Admin Endpoints (require token)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/fraud-stats` | Get all fraud statistics (JSON) |
| GET | `/admin/dashboard` | Admin dashboard (HTML) |
| POST | `/admin/unblock/:ip` | Manually unblock an IP |
| POST | `/admin/reset-score/:ip` | Reset fraud score to 0 |

**Authentication:** Include `X-Admin-Token` header or `?token=` query parameter

---

## 🎯 Fraud Score Events

| Event Type | Score Increase | When It Triggers |
|------------|----------------|------------------|
| `FAILED_CAPTCHA` | +25 points | Invalid reCAPTCHA token |
| `INVALID_CREDENTIALS` | +15 points | Wrong login (future) |
| `RAPID_REQUESTS` | +20 points | Rate limit (future) |
| `SUSPICIOUS_PATTERN` | +30 points | ML detection (future) |

**Automatic Blocking:**
- Threshold: 100 points
- Block Duration: 15 minutes
- Score Decay: -10 points every hour

---

## 🔍 Check Redis Data

**View fraud scores in Redis:**
```bash
docker exec fraud-detection-redis redis-cli KEYS "fraud:*"
docker exec fraud-detection-redis redis-cli GET "fraud:score:192.168.1.100"
```

---

## 🛑 Stop/Restart Server

**Stop the server:**
```bash
# Find the process
ps aux | grep "node server.js"

# Kill it (use the PID from above)
kill <PID>
```

**Restart the server:**
```bash
cd /home/nataliabarros1994/Downloads/"🚀 Sistema de Detecção de Fraudes em Tempo Real - Guia Completo"/fraud_detection_system/recaptcha-service
npm start
```

---

## 📚 Documentation

- **Complete Guide:** `REDIS_FRAUD_SCORING.md`
- **Deployment:** `DEPLOYMENT_CHECKLIST.md`
- **Summary:** `FEATURE_COMPLETE.md`
- **File Structure:** `FILE_STRUCTURE.txt`

---

## ⚙️ Configuration (.env)

Current configuration:
```env
PORT=3000
REDIS_URL=redis://localhost:6379
BLOCK_THRESHOLD=100
BLOCK_TTL=900
SCORE_DECAY_INTERVAL=3600
SCORE_DECAY_AMOUNT=10
ADMIN_TOKEN=91cc29f33505f7f6856f5412faa79a3b8a19fc8b481d649feaca7b33f5523b9f
```

**To change configuration:**
1. Edit `.env` file
2. Restart server for changes to take effect

---

## 🎉 What's Working

✅ Persistent fraud score storage (Redis)
✅ Automatic IP blocking at 100 points
✅ Score decay system (-10 points/hour)
✅ Real-time admin dashboard
✅ Manual unblock functionality
✅ Score reset capability
✅ Graceful fallback to in-memory
✅ Token-based admin authentication
✅ Health monitoring

---

## 🚀 Next Steps

1. **Access the dashboard** using the URL above
2. **Run the test suite** to see fraud scoring in action
3. **Integrate with your frontend** using the API endpoints
4. **Monitor fraud activity** in real-time via dashboard

For production deployment:
- Get real reCAPTCHA keys from https://www.google.com/recaptcha/admin/create
- Update `RECAPTCHA_SITE_KEY` and `RECAPTCHA_SECRET` in `.env`
- Configure Redis password for remote connections
- Set up HTTPS reverse proxy (nginx/caddy)

---

**FraudGuard® - Enterprise Fraud Detection** 🛡️

*Server started: 2025-10-20*
*Status: Fully Operational*
