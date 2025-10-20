# ⚡ FraudGuard® reCAPTCHA - Quick Start Guide

**Get up and running in 5 minutes!**

---

## 🎯 Prerequisites

- ✅ Node.js 14+ installed
- ✅ npm or yarn
- ✅ Google account (for reCAPTCHA keys)

---

## 🚀 Step 1: Get reCAPTCHA Keys (2 minutes)

1. **Visit:** https://www.google.com/recaptcha/admin/create

2. **Fill the form:**
   - **Label:** `FraudGuard Development`
   - **reCAPTCHA type:** Select **"reCAPTCHA v2"** → **"I'm not a robot" Checkbox**
   - **Domains:** Add `localhost`

3. **Submit** and copy:
   - ✅ **Site Key** (starts with `6L...`)
   - ✅ **Secret Key** (starts with `6L...`)

---

## 📦 Step 2: Install Dependencies (1 minute)

```bash
# Navigate to the service directory
cd recaptcha-service

# Install packages
npm install
```

**Packages installed:**
- `express` - Web server
- `body-parser` - Parse requests
- `node-fetch` - HTTP client
- `dotenv` - Environment variables

---

## ⚙️ Step 3: Configure Environment (1 minute)

```bash
# Copy example file
cp .env.example .env

# Edit .env
nano .env
```

**Add your keys to `.env`:**

```env
PORT=3000
RECAPTCHA_SITE_KEY=6LdXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
RECAPTCHA_SECRET=6LdXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**Save and close** (Ctrl+X, then Y, then Enter)

---

## 🏃 Step 4: Start the Server (30 seconds)

```bash
npm start
```

**Expected output:**

```
🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️
🚀 FraudGuard® reCAPTCHA Service Started
📍 Server running on: http://localhost:3000
🔐 Security: CAPTCHA verification active
⏰ Started at: 2025-10-16T12:00:00.000Z
🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️

Available endpoints:
  GET  /              - Authentication page
  GET  /api/site-key  - Get public reCAPTCHA key
  POST /verify-captcha - Verify CAPTCHA token
  POST /api/login     - Login with CAPTCHA
  GET  /health        - Health check
```

✅ **Server is running!**

---

## 🧪 Step 5: Test It (30 seconds)

### Option A: Browser Test (Recommended)

1. **Open:** http://localhost:3000
2. **Fill the form:**
   - Email: `test@example.com`
   - Password: `password123`
3. **Complete the CAPTCHA** (check the box)
4. **Click** "Sign In Securely"
5. **See success message!** ✅

---

### Option B: Automated Tests

```bash
# Run test suite
npm test
# or
node test-captcha.js
```

**Expected output:**

```
🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️
🚀 FraudGuard® reCAPTCHA Service - Test Suite
🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️🛡️

📝 Test: Health Check
✅ PASS: Service is healthy

📝 Test: Missing CAPTCHA Token
✅ PASS: Correctly rejected missing token

📊 Test Summary
✅ Passed: 8
❌ Failed: 0
📝 Total: 8
```

---

### Option C: cURL Test

```bash
# Test health check
curl http://localhost:3000/health

# Test missing token (should fail)
curl -X POST http://localhost:3000/verify-captcha \
  -H "Content-Type: application/json" \
  -d '{}'

# Test invalid token (should fail)
curl -X POST http://localhost:3000/verify-captcha \
  -H "Content-Type: application/json" \
  -d '{"g-recaptcha-response":"invalid_token"}'
```

---

## ✅ You're Done!

Your reCAPTCHA service is now running and protecting against bots!

---

## 🎯 Next Steps

### 1. **Integrate with FraudGuard® Main API**

Connect this CAPTCHA service to your fraud detection API:

```javascript
// In your main fraud detection API
app.post('/api/transaction', async (req, res) => {
  // Step 1: Verify CAPTCHA
  const captchaResponse = await fetch('http://localhost:3000/verify-captcha', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      'g-recaptcha-response': req.body.captcha
    })
  });

  const captchaResult = await captchaResponse.json();

  if (!captchaResult.success) {
    return res.status(400).json({ error: 'CAPTCHA verification failed' });
  }

  // Step 2: Call FraudGuard® ML model
  const fraudScore = await fraudDetector.predict(req.body);

  // Step 3: Make decision
  if (fraudScore > 0.75) {
    return res.status(403).json({ error: 'Transaction blocked' });
  }

  // Approve transaction
  res.json({ success: true });
});
```

---

### 2. **Add to Your Frontend**

```html
<!-- Add to your existing HTML -->
<script src="https://www.google.com/recaptcha/api.js" async defer></script>

<form id="transaction-form">
  <!-- Your existing fields -->

  <!-- Add CAPTCHA widget -->
  <div class="g-recaptcha" data-sitekey="YOUR_SITE_KEY"></div>

  <button type="submit">Submit Transaction</button>
</form>

<script>
  document.getElementById('transaction-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    // Get CAPTCHA token
    const captchaToken = grecaptcha.getResponse();

    if (!captchaToken) {
      alert('Please complete the CAPTCHA');
      return;
    }

    // Send to your API
    const response = await fetch('/api/transaction', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        // ... your data
        captcha: captchaToken
      })
    });

    // Handle response
    const result = await response.json();
    console.log(result);
  });
</script>
```

---

### 3. **Switch to reCAPTCHA v3** (Invisible - Better UX)

See `README.md` → "Migration Guides" section for detailed instructions.

**Quick overview:**
- No checkbox (invisible)
- Runs on page load or specific actions
- Returns a score (0.0-1.0) instead of pass/fail
- Better user experience

---

### 4. **Deploy to Production**

**Using PM2:**
```bash
npm install -g pm2
pm2 start server.js --name fraudguard-recaptcha
pm2 save
pm2 startup
```

**Using Docker:**
```bash
docker build -t fraudguard-recaptcha .
docker run -d -p 3000:3000 \
  -e RECAPTCHA_SITE_KEY=xxx \
  -e RECAPTCHA_SECRET=xxx \
  fraudguard-recaptcha
```

**Using systemd:** See `README.md` → "Production Deployment"

---

### 5. **Monitor & Alert**

Track these metrics:
- ✅ CAPTCHA verification rate (success vs. failure)
- ✅ API response time
- ✅ Failed attempts per IP
- ✅ Bot traffic blocked

Use tools like:
- **Prometheus** + **Grafana** (metrics & dashboards)
- **Sentry** (error tracking)
- **CloudWatch** / **Datadog** (APM)

---

## 🐛 Troubleshooting

### Problem: "RECAPTCHA_SECRET not found"

**Solution:**
```bash
# Make sure .env file exists
ls -la .env

# If not, create it
cp .env.example .env
nano .env
```

---

### Problem: CAPTCHA widget not showing

**Causes:**
- Ad blocker enabled
- JavaScript error
- Wrong site key

**Solution:**
```javascript
// Check browser console for errors
// Try in incognito mode
// Verify site key matches Google admin panel
```

---

### Problem: "invalid-input-response" error

**Causes:**
- Token expired (>2 minutes old)
- Token already used
- Server/client key mismatch

**Solution:**
```javascript
// Reset CAPTCHA after error
grecaptcha.reset();
```

---

## 📚 Documentation

- **Full README:** `README.md`
- **Integration Guide:** `INTEGRATION_GUIDE.md`
- **API Documentation:** Inside `README.md`

---

## 📞 Support

- **GitHub Issues:** https://github.com/your-org/fraudguard/issues
- **Email:** support@fraudguard.com

---

## 🎉 Success!

You now have a production-ready reCAPTCHA service protecting FraudGuard®!

**Security Stack:**
```
┌─────────────────────────────┐
│ reCAPTCHA (Bot Prevention)  │ ← YOU ARE HERE ✅
├─────────────────────────────┤
│ FraudGuard® ML (Fraud)      │
├─────────────────────────────┤
│ Rate Limiting (DDoS)        │
├─────────────────────────────┤
│ Business Rules              │
└─────────────────────────────┘
```

**Next:** Integrate with your main fraud detection API (see step 1 above)

---

**🛡️ FraudGuard® - Protecting Your Business from Fraud**
