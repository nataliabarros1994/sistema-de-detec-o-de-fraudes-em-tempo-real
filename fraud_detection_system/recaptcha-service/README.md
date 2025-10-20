# 🛡️ FraudGuard® reCAPTCHA Integration

**Production-ready Google reCAPTCHA v2 implementation for bot protection in authentication and API requests.**

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Testing](#testing)
- [API Documentation](#api-documentation)
- [Security Best Practices](#security-best-practices)
- [Migration Guides](#migration-guides)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This Node.js Express service adds **Google reCAPTCHA v2** protection to FraudGuard®'s authentication flows and sensitive API endpoints. It prevents automated bot attacks, credential stuffing, and brute-force attempts.

**Technology Stack:**
- Node.js 14+
- Express.js 4.x
- Google reCAPTCHA v2 (Checkbox)
- dotenv for environment management

---

## ✨ Features

- ✅ **Server-side CAPTCHA verification** with Google's API
- ✅ **Secure credential management** via environment variables
- ✅ **Production-ready error handling** with user-friendly messages
- ✅ **Comprehensive logging** for security monitoring
- ✅ **Beautiful, responsive frontend** with real-time validation
- ✅ **IP tracking** for enhanced fraud detection
- ✅ **Easy migration** to reCAPTCHA v3 or hCaptcha
- ✅ **Health check endpoint** for monitoring

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Browser                        │
│  ┌────────────────────────────────────────────────┐     │
│  │  1. User fills login form                      │     │
│  │  2. Completes reCAPTCHA challenge             │     │
│  │  3. Submits form with token                   │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ POST /api/login
                       │ { username, password, g-recaptcha-response }
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Express Server (Node.js)                    │
│  ┌────────────────────────────────────────────────┐     │
│  │  1. Extract CAPTCHA token                      │     │
│  │  2. Validate token format                      │     │
│  │  3. Send to Google for verification           │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ POST https://www.google.com/recaptcha/api/siteverify
                       │ { secret, response, remoteip }
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Google reCAPTCHA API                        │
│  ┌────────────────────────────────────────────────┐     │
│  │  Verifies token validity                       │     │
│  │  Returns: { success: true/false }             │     │
│  └────────────────────────────────────────────────┘     │
└──────────────────────┬──────────────────────────────────┘
                       │
                       │ Response: { success: true }
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│              Express Server                              │
│  ┌────────────────────────────────────────────────┐     │
│  │  If success:                                   │     │
│  │    - Proceed with authentication              │     │
│  │    - Apply FraudGuard fraud detection        │     │
│  │    - Create session/JWT                       │     │
│  │                                                │     │
│  │  If failure:                                   │     │
│  │    - Return 400 error                         │     │
│  │    - Log attempt                              │     │
│  └────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- Node.js 14+ installed
- npm or yarn
- Google account for reCAPTCHA

### 1. Get reCAPTCHA Keys

1. Go to https://www.google.com/recaptcha/admin/create
2. Fill in the registration form:
   - **Label:** FraudGuard Production
   - **reCAPTCHA type:** Select "reCAPTCHA v2" → "I'm not a robot" Checkbox
   - **Domains:** Add `localhost` (for testing) and your production domain
3. Accept terms and click **Submit**
4. Copy the **Site Key** and **Secret Key**

### 2. Clone and Install

```bash
# Navigate to the recaptcha-service directory
cd recaptcha-service

# Install dependencies
npm install
```

### 3. Configure Environment

```bash
# Copy the example .env file
cp .env.example .env

# Edit .env and add your keys
nano .env
```

Update `.env` with your actual keys:

```env
PORT=3000
RECAPTCHA_SITE_KEY=6LdXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
RECAPTCHA_SECRET=6LdXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### 4. Run the Server

```bash
# Start the server
npm start

# Or use nodemon for development (auto-restart)
npm run dev
```

The server will start at **http://localhost:3000**

### 5. Test in Browser

Open http://localhost:3000 in your browser and you'll see the login page with reCAPTCHA.

---

## 📦 Installation

### Standard Installation

```bash
npm install
```

### Development Installation (with nodemon)

```bash
npm install --include=dev
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `express` | ^4.18.2 | Web server framework |
| `body-parser` | ^1.20.2 | Parse request bodies |
| `node-fetch` | ^2.7.0 | HTTP client for Google API |
| `dotenv` | ^16.3.1 | Environment variable management |
| `nodemon` | ^3.0.1 | Development auto-restart (dev only) |

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Server Configuration
PORT=3000

# Google reCAPTCHA v2 Credentials
RECAPTCHA_SITE_KEY=your_site_key_here
RECAPTCHA_SECRET=your_secret_key_here

# Optional: Node Environment
NODE_ENV=production
```

### Important Notes

- **Never commit `.env` to version control** (already in `.gitignore`)
- **Site Key** is public (safe to expose in frontend)
- **Secret Key** must remain private (server-side only)
- Use different keys for development and production

---

## 🧪 Testing

### Manual Testing with Browser

1. Start the server: `npm start`
2. Open http://localhost:3000
3. Fill in the form
4. Complete the reCAPTCHA
5. Click "Sign In Securely"
6. Check console logs for verification details

### Testing with cURL

#### Test Missing Token

```bash
curl -X POST http://localhost:3000/verify-captcha \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected Response:**
```json
{
  "success": false,
  "errors": ["missing-input-response"],
  "message": "Please complete the CAPTCHA challenge"
}
```

#### Test Invalid Token

```bash
curl -X POST http://localhost:3000/verify-captcha \
  -H "Content-Type: application/json" \
  -d '{"g-recaptcha-response":"invalid_token_12345"}'
```

**Expected Response:**
```json
{
  "success": false,
  "errors": ["invalid-input-response"],
  "message": "CAPTCHA expired or invalid. Please try again."
}
```

#### Test with Google's API Directly

```bash
curl -X POST "https://www.google.com/recaptcha/api/siteverify" \
  -d "secret=YOUR_SECRET_KEY" \
  -d "response=YOUR_TOKEN"
```

### Health Check

```bash
# Check server health
curl http://localhost:3000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "FraudGuard® reCAPTCHA Service",
  "timestamp": "2025-10-16T12:00:00.000Z",
  "recaptcha_configured": true
}
```

### Testing Valid Tokens

To test with a real valid token:

1. Open http://localhost:3000 in browser
2. Open browser DevTools → Network tab
3. Complete the CAPTCHA and submit
4. Check the request payload for the `g-recaptcha-response` value
5. Use that token in cURL (must be used within 2 minutes)

---

## 📖 API Documentation

### Endpoints

#### `GET /`

Serves the authentication page with reCAPTCHA widget.

**Response:** HTML page

---

#### `GET /api/site-key`

Returns the public reCAPTCHA site key.

**Response:**
```json
{
  "siteKey": "6LdXXXXXXXXXXX",
  "version": "v2-checkbox"
}
```

---

#### `POST /verify-captcha`

Verifies a reCAPTCHA token.

**Request Body:**
```json
{
  "g-recaptcha-response": "token_from_google",
  "username": "user@example.com",  // optional
  "action": "login"                 // optional
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "CAPTCHA verified successfully",
  "timestamp": "2025-10-16T12:00:00.000Z",
  "duration_ms": 245
}
```

**Error Response (400):**
```json
{
  "success": false,
  "errors": ["invalid-input-response"],
  "message": "CAPTCHA expired or invalid. Please try again."
}
```

**Error Codes:**

| Code | Meaning |
|------|---------|
| `missing-input-secret` | Server config error - secret not provided |
| `invalid-input-secret` | Server config error - secret is invalid |
| `missing-input-response` | User didn't complete CAPTCHA |
| `invalid-input-response` | Token is invalid or expired |
| `timeout-or-duplicate` | Token was already used or expired |

---

#### `POST /api/login`

Example protected endpoint with CAPTCHA verification.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "securePassword123",
  "g-recaptcha-response": "token_from_google"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "username": "user@example.com"
  },
  "token": "jwt_token_here"
}
```

**Error Responses:**
- **400:** CAPTCHA failed or missing credentials
- **500:** Server error

---

#### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "FraudGuard® reCAPTCHA Service",
  "timestamp": "2025-10-16T12:00:00.000Z",
  "recaptcha_configured": true
}
```

---

## 🔒 Security Best Practices

### 1. Environment Variables

✅ **DO:**
- Store secrets in `.env` file
- Use different keys for dev/staging/production
- Keep `.env` in `.gitignore`
- Use secret management services in production (AWS Secrets Manager, Azure Key Vault)

❌ **DON'T:**
- Hardcode secrets in code
- Commit `.env` to Git
- Share secrets in chat/email
- Use production keys in development

### 2. Server-Side Validation

✅ **Always verify CAPTCHA on the server**, never trust client-side validation alone.

```javascript
// ✅ CORRECT: Server-side verification
app.post('/login', async (req, res) => {
  const captchaToken = req.body['g-recaptcha-response'];
  const result = await verifyRecaptcha(captchaToken);

  if (!result.success) {
    return res.status(400).json({ error: 'Invalid CAPTCHA' });
  }

  // Proceed with authentication...
});

// ❌ WRONG: Client-side only
// if (grecaptcha.getResponse()) {
//   // Login without server verification
// }
```

### 3. Token Expiration

- CAPTCHA tokens expire after **2 minutes**
- Tokens can only be used **once**
- Always handle `timeout-or-duplicate` errors gracefully
- Reset CAPTCHA after failed submission

### 4. IP Tracking

The service logs client IPs for security monitoring:

```javascript
const clientIP = req.headers['x-forwarded-for'] || req.connection.remoteAddress;
```

Use this data to:
- Detect distributed attacks
- Apply rate limiting
- Integrate with FraudGuard® fraud scoring

### 5. HTTPS in Production

Always use HTTPS in production:

```bash
# Use a reverse proxy (nginx, Apache)
# Or use Node.js HTTPS:
const https = require('https');
const fs = require('fs');

const options = {
  key: fs.readFileSync('key.pem'),
  cert: fs.readFileSync('cert.pem')
};

https.createServer(options, app).listen(443);
```

### 6. Rate Limiting

Add rate limiting to prevent abuse:

```bash
npm install express-rate-limit
```

```javascript
const rateLimit = require('express-rate-limit');

const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // 5 attempts per window
  message: 'Too many login attempts, please try again later'
});

app.post('/api/login', limiter, async (req, res) => {
  // ...
});
```

---

## 🔄 Migration Guides

### Switching to reCAPTCHA v3 (Invisible)

**reCAPTCHA v3** runs invisibly and returns a **score (0.0-1.0)** instead of a challenge.

#### 1. Get v3 Keys

1. Go to https://www.google.com/recaptcha/admin/create
2. Select **reCAPTCHA v3**
3. Copy new Site Key and Secret

#### 2. Update Frontend (`public/index.html`)

```html
<!-- Change the script -->
<script src="https://www.google.com/recaptcha/api.js?render=YOUR_V3_SITE_KEY"></script>

<!-- Remove the visible widget div -->
<!-- Delete: <div class="g-recaptcha" ...></div> -->

<!-- Execute on form submit -->
<script>
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Execute reCAPTCHA v3
    const token = await grecaptcha.execute('YOUR_V3_SITE_KEY', {
      action: 'login'
    });

    // Send token to server
    const response = await fetch('/api/login', {
      method: 'POST',
      body: JSON.stringify({
        username: username.value,
        password: password.value,
        'g-recaptcha-response': token
      })
    });
  });
</script>
```

#### 3. Update Backend (`server.js`)

```javascript
// v3 returns a score instead of success/fail
const verificationResult = await verifyRecaptcha(token, clientIP);

if (verificationResult.success) {
  const score = verificationResult.score; // 0.0 to 1.0

  if (score >= 0.5) {
    // Likely human
    console.log(`✅ CAPTCHA score: ${score} (likely human)`);
    // Proceed...
  } else {
    // Likely bot
    console.warn(`⚠️ CAPTCHA score: ${score} (likely bot)`);
    return res.status(400).json({
      success: false,
      message: 'Suspicious activity detected'
    });
  }
}
```

**Recommended Score Thresholds:**
- **≥ 0.7:** Almost certainly human → Allow
- **0.5 - 0.7:** Probably human → Allow with monitoring
- **0.3 - 0.5:** Suspicious → Challenge with v2 or block
- **< 0.3:** Almost certainly bot → Block

---

### Switching to hCaptcha (Privacy-Focused)

**hCaptcha** is a privacy-focused alternative to Google reCAPTCHA.

#### 1. Get hCaptcha Keys

1. Sign up at https://www.hcaptcha.com/
2. Create a new site
3. Copy Site Key and Secret Key

#### 2. Update Frontend

```html
<!-- Change script -->
<script src="https://js.hcaptcha.com/1/api.js" async defer></script>

<!-- Change widget class -->
<div class="h-captcha" data-sitekey="YOUR_HCAPTCHA_SITE_KEY"></div>
```

#### 3. Update Backend

```javascript
async function verifyHcaptcha(token, remoteIP = null) {
  const verifyUrl = 'https://hcaptcha.com/siteverify'; // Changed URL

  const params = new URLSearchParams({
    secret: process.env.HCAPTCHA_SECRET, // Use hCaptcha secret
    response: token,
    remoteip: remoteIP
  });

  const response = await fetch(verifyUrl, {
    method: 'POST',
    body: params
  });

  return await response.json();
}
```

#### 4. Update `.env`

```env
HCAPTCHA_SITE_KEY=your_hcaptcha_site_key
HCAPTCHA_SECRET=your_hcaptcha_secret
```

---

## 🔧 Troubleshooting

### Problem: "RECAPTCHA_SECRET not found"

**Cause:** Missing `.env` file or incorrect variable name

**Solution:**
```bash
# Copy example file
cp .env.example .env

# Edit and add your keys
nano .env
```

### Problem: "invalid-input-response" Error

**Causes:**
- Token expired (>2 minutes old)
- Token already used
- Invalid token format

**Solutions:**
- Use `grecaptcha.reset()` after errors
- Generate a new token for each attempt
- Check for JavaScript errors blocking CAPTCHA

### Problem: CAPTCHA Widget Not Appearing

**Causes:**
- Script blocked by ad blocker
- JavaScript errors
- Wrong site key

**Solutions:**
```javascript
// Check console for errors
// Verify site key in .env matches Google admin panel
// Try in incognito mode (disable extensions)
```

### Problem: "missing-input-secret" in Production

**Cause:** Environment variables not loaded in production

**Solutions:**
```bash
# For PM2
pm2 start server.js --env production

# For Docker
docker run -e RECAPTCHA_SECRET=xxx -e RECAPTCHA_SITE_KEY=xxx ...

# For systemd
# Add to /etc/systemd/system/fraudguard.service:
Environment="RECAPTCHA_SECRET=xxx"
Environment="RECAPTCHA_SITE_KEY=xxx"
```

### Problem: CORS Errors

If integrating with a separate frontend:

```javascript
const cors = require('cors');

app.use(cors({
  origin: 'https://your-frontend-domain.com',
  credentials: true
}));
```

---

## 🚀 Production Deployment

### Using PM2

```bash
# Install PM2
npm install -g pm2

# Start with PM2
pm2 start server.js --name fraudguard-recaptcha

# Save process list
pm2 save

# Auto-start on reboot
pm2 startup
```

### Using Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci --only=production

COPY . .

EXPOSE 3000

CMD ["node", "server.js"]
```

```bash
# Build
docker build -t fraudguard-recaptcha .

# Run
docker run -d \
  -p 3000:3000 \
  -e RECAPTCHA_SITE_KEY=xxx \
  -e RECAPTCHA_SECRET=xxx \
  --name fraudguard-recaptcha \
  fraudguard-recaptcha
```

### Using systemd

Create `/etc/systemd/system/fraudguard-recaptcha.service`:

```ini
[Unit]
Description=FraudGuard reCAPTCHA Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/fraudguard-recaptcha
ExecStart=/usr/bin/node server.js
Restart=always
Environment="NODE_ENV=production"
Environment="PORT=3000"
Environment="RECAPTCHA_SITE_KEY=xxx"
Environment="RECAPTCHA_SECRET=xxx"

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable fraudguard-recaptcha
sudo systemctl start fraudguard-recaptcha
```

---

## 📊 Monitoring

### Log Management

Logs are written to console. Redirect to file:

```bash
# Using PM2
pm2 start server.js --log /var/log/fraudguard/recaptcha.log

# Using systemd
# Logs available via journalctl:
journalctl -u fraudguard-recaptcha -f
```

### Metrics to Track

- **CAPTCHA verification rate** (success vs. failure)
- **Response time** from Google API
- **Failed attempts per IP**
- **Token expiration rate**

Example with Prometheus:

```javascript
const prometheus = require('prom-client');

const captchaVerifications = new prometheus.Counter({
  name: 'captcha_verifications_total',
  help: 'Total CAPTCHA verifications',
  labelNames: ['result']
});

// In verification code:
if (result.success) {
  captchaVerifications.inc({ result: 'success' });
} else {
  captchaVerifications.inc({ result: 'failure' });
}
```

---

## 📞 Support

For issues or questions:

- **GitHub Issues:** https://github.com/your-org/fraudguard/issues
- **Email:** support@fraudguard.com
- **Documentation:** https://docs.fraudguard.com

---

## 📄 License

MIT License - see LICENSE file for details

---

## 🙏 Credits

Developed with ❤️ by the FraudGuard® Team

**Powered by:**
- Google reCAPTCHA
- Node.js & Express
- Open Source Community

---

**🛡️ FraudGuard® - Protecting Your Business from Fraud**
