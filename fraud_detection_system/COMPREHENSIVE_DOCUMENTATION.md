# FraudGuard® - Comprehensive Documentation

## 📚 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Quick Start Guide](#quick-start-guide)
4. [Installation & Setup](#installation--setup)
5. [API Documentation](#api-documentation)
6. [User Guide](#user-guide)
7. [Administrator Guide](#administrator-guide)
8. [Security Documentation](#security-documentation)
9. [Deployment Guide](#deployment-guide)
10. [Contributing Guidelines](#contributing-guidelines)
11. [Troubleshooting](#troubleshooting)
12. [FAQ](#faq)

---

## 📌 Project Overview

### Purpose

**FraudGuard®** is a real-time fraud detection and prevention system designed to protect web applications from fraudulent activities, bot attacks, and suspicious transactions. The system combines machine learning algorithms, behavioral analysis, and reCAPTCHA integration to provide comprehensive protection.

### Key Features

- ✅ **Real-Time Fraud Detection** - ML-powered analysis of user behavior
- ✅ **reCAPTCHA Integration** - Google reCAPTCHA v2 bot protection
- ✅ **Fraud Scoring System** - IP-based risk scoring with Redis/in-memory storage
- ✅ **Admin Dashboard** - Comprehensive monitoring and management interface
- ✅ **Auto-Blocking** - Automatic IP blocking based on fraud scores
- ✅ **Multiple Interfaces** - Streamlit dashboard + Web admin panel
- ✅ **RESTful API** - Complete API for integration
- ✅ **Audit Logging** - Complete activity tracking
- ✅ **Scalable Architecture** - Docker support and horizontal scaling

### Target Audience

- **E-commerce Platforms** - Protect transactions and user accounts
- **Financial Services** - Prevent fraudulent transactions
- **SaaS Applications** - Protect user registration and login
- **API Providers** - Protect API endpoints from abuse
- **Enterprise Systems** - Comprehensive fraud prevention

### Technology Stack

#### Backend
- **Node.js (Express)** - reCAPTCHA service and fraud API
- **Python (FastAPI/Streamlit)** - ML models and dashboard
- **Redis** - Distributed fraud score storage
- **PostgreSQL** - Persistent data storage (optional)

#### Frontend
- **Streamlit** - Python-based analytics dashboard
- **Vanilla JavaScript** - Web admin interface
- **Bootstrap 5** - UI framework
- **Chart.js** - Data visualization

#### Machine Learning
- **Scikit-learn** - Fraud detection models
- **Pandas** - Data processing
- **NumPy** - Numerical computations

#### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Git** - Version control
- **PM2** - Process management (optional)

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                         │
├─────────────────────────────────────────────────────────────┤
│  Web Browser  │  Mobile App  │  Third-party Integration    │
└────────┬────────────┬────────────────┬──────────────────────┘
         │            │                │
         ▼            ▼                ▼
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────┐         │
│  │  reCAPTCHA       │         │   Streamlit      │         │
│  │  Service         │         │   Dashboard      │         │
│  │  (Node.js/Express│         │   (Python)       │         │
│  │   Port 3000)     │         │   (Port 8501)    │         │
│  └────────┬─────────┘         └────────┬─────────┘         │
│           │                            │                    │
│           └────────────┬───────────────┘                    │
│                        │                                    │
└────────────────────────┼────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Services Layer                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Fraud      │  │  reCAPTCHA   │  │  User Auth   │     │
│  │   Scoring    │  │  Verifier    │  │  Manager     │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                 │              │
└─────────┼─────────────────┼─────────────────┼──────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                       Data Layer                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Redis     │  │  In-Memory   │  │  PostgreSQL  │     │
│  │   (Primary)  │  │  (Fallback)  │  │  (Optional)  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Component Details

#### 1. reCAPTCHA Service (Node.js)
- **Port:** 3000
- **Purpose:** Bot protection and fraud detection
- **Key Files:**
  - `server.js` - Main Express server
  - `fraudScoreManager.js` - Fraud scoring logic
  - `redisClient.js` - Redis connection management

#### 2. Streamlit Dashboard (Python)
- **Port:** 8501
- **Purpose:** Analytics and monitoring interface
- **Key Files:**
  - `frontend/app.py` - Main dashboard application

#### 3. Fraud Detection API (Python)
- **Port:** 8000 (FastAPI)
- **Purpose:** ML-based fraud prediction
- **Key Files:**
  - `app/main.py` - API endpoints
  - `app/ml_model.py` - ML model logic

### Data Flow

```
User Request
     │
     ▼
┌────────────────┐
│  reCAPTCHA     │
│  Validation    │
└────┬───────────┘
     │
     ▼
┌────────────────┐
│  Fraud Score   │
│  Check         │
└────┬───────────┘
     │
     ├──[Score < Threshold]──> Allow Request
     │
     └──[Score ≥ Threshold]──> Block Request
                                      │
                                      ▼
                                ┌─────────────┐
                                │  Log Event  │
                                └─────────────┘
```

### Fraud Scoring Algorithm

```javascript
// Score increments based on event type
SCORE_INCREMENTS = {
    FAILED_CAPTCHA: 20,      // Failed reCAPTCHA
    FAILED_LOGIN: 15,        // Failed login attempt
    SUSPICIOUS_PATTERN: 25,   // Detected bot pattern
    VELOCITY_CHECK: 30,      // Too many requests
    BLOCK_DURATION: 900      // 15 minutes in seconds
}

// Auto-blocking threshold
BLOCK_THRESHOLD = 100

// Score decay
DECAY_INTERVAL = 3600        // 1 hour
DECAY_AMOUNT = 10           // Points reduced per interval
```

---

## 🚀 Quick Start Guide

### Prerequisites

- **Node.js** 16+ and npm
- **Python** 3.8+
- **Redis** (optional, will fall back to in-memory)
- **Git**
- Modern web browser

### 5-Minute Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd fraud_detection_system

# 2. Install Node.js dependencies (reCAPTCHA service)
cd recaptcha-service
npm install

# 3. Configure environment variables
cp .env.example .env
# Edit .env with your reCAPTCHA keys

# 4. Start the reCAPTCHA service
npm start
# Service runs on http://localhost:3000

# 5. (Optional) Install Python dependencies
cd ..
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 6. (Optional) Start Streamlit dashboard
streamlit run frontend/app.py
# Dashboard runs on http://localhost:8501
```

### Quick Test

```bash
# Test the health endpoint
curl http://localhost:3000/health

# Access the login page
open http://localhost:3000/fraudguard.html

# Access admin dashboard (requires token)
open http://localhost:3000/admin-dashboard-comprehensive.html
```

---

## 📦 Installation & Setup

### Detailed Installation Steps

#### Step 1: System Requirements

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB free space
- OS: Linux, macOS, or Windows

**Recommended Requirements:**
- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 20+ GB SSD
- OS: Ubuntu 20.04+ or similar

#### Step 2: Install Dependencies

**On Ubuntu/Debian:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Python
sudo apt install -y python3 python3-pip python3-venv

# Install Redis (optional)
sudo apt install -y redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Install Git
sudo apt install -y git
```

**On macOS:**
```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install node
brew install python@3
brew install redis
brew install git

# Start Redis
brew services start redis
```

**On Windows:**
```powershell
# Install using Chocolatey
choco install nodejs python git redis-64 -y

# Or download installers:
# Node.js: https://nodejs.org/
# Python: https://www.python.org/downloads/
# Git: https://git-scm.com/download/win
# Redis: https://github.com/microsoftarchive/redis/releases
```

#### Step 3: Clone and Configure

```bash
# Clone repository
git clone <your-repo-url>
cd fraud_detection_system

# Create environment file
cd recaptcha-service
cp .env.example .env
```

#### Step 4: Get reCAPTCHA Keys

1. Visit https://www.google.com/recaptcha/admin/create
2. Select "reCAPTCHA v2" → "I'm not a robot" Checkbox
3. Add domains: `localhost`, `127.0.0.1`, your production domain
4. Copy the **Site Key** and **Secret Key**
5. Update `.env` file:

```bash
RECAPTCHA_SITE_KEY=your_site_key_here
RECAPTCHA_SECRET=your_secret_key_here
```

#### Step 5: Install Project Dependencies

```bash
# Install Node.js dependencies
cd recaptcha-service
npm install

# Install Python dependencies
cd ..
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 6: Database Setup (Optional)

**Start Redis:**
```bash
# Using Docker
docker run -d -p 6379:6379 --name fraudguard-redis redis:alpine

# Or use system Redis
sudo systemctl start redis-server
```

**Verify Redis:**
```bash
redis-cli ping
# Should return: PONG
```

#### Step 7: Start Services

**Terminal 1 - reCAPTCHA Service:**
```bash
cd recaptcha-service
npm start
```

**Terminal 2 - Streamlit Dashboard (Optional):**
```bash
source venv/bin/activate
streamlit run frontend/app.py
```

#### Step 8: Verify Installation

```bash
# Test reCAPTCHA service
curl http://localhost:3000/health

# Expected response:
# {
#   "status": "healthy",
#   "service": "FraudGuard® reCAPTCHA Service",
#   "recaptcha_configured": true,
#   "redis": { "connected": true }
# }
```

### Environment Variables Reference

**.env file configuration:**

```bash
# Server Configuration
PORT=3000

# Google reCAPTCHA v2 Credentials
RECAPTCHA_SITE_KEY=your_site_key_here
RECAPTCHA_SECRET=your_secret_key_here

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Fraud Scoring Configuration
BLOCK_THRESHOLD=100           # Score threshold for blocking
BLOCK_TTL=900                 # Block duration (seconds)
SCORE_DECAY_INTERVAL=3600     # Decay interval (seconds)
SCORE_DECAY_AMOUNT=10         # Decay amount (points)

# Admin Dashboard Authentication
ADMIN_TOKEN=your_secure_random_token_here

# Node Environment
NODE_ENV=development          # or 'production'
```

---

## 📡 API Documentation

### Base URL

```
http://localhost:3000
```

### Authentication

Admin endpoints require authentication via:
- **Header:** `X-Admin-Token: your_admin_token`
- **Query Parameter:** `?token=your_admin_token`

### Public Endpoints

#### 1. Get reCAPTCHA Site Key

```http
GET /api/site-key
```

**Response:**
```json
{
  "siteKey": "6LcXXXXXXXXXXXXXXXXXXXXXXXXXX",
  "version": "v2-checkbox"
}
```

---

#### 2. Verify reCAPTCHA Token

```http
POST /verify-captcha
Content-Type: application/json
```

**Request Body:**
```json
{
  "g-recaptcha-response": "token_from_google_recaptcha",
  "username": "user@example.com",
  "action": "login"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "CAPTCHA verified successfully",
  "timestamp": "2024-12-20T10:30:00.000Z",
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

**Blocked Response (403):**
```json
{
  "blocked": true,
  "reason": "Score exceeded threshold",
  "score": 120,
  "expiresIn": "14 minutes",
  "message": "Your IP has been temporarily blocked due to suspicious activity"
}
```

---

#### 3. User Login

```http
POST /api/login
Content-Type: application/json
```

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "your_password",
  "g-recaptcha-response": "token_from_recaptcha"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "username": "user@example.com",
    "email": "user@example.com",
    "loginTime": "2024-12-20T10:30:00.000Z"
  },
  "token": "base64_encoded_token"
}
```

**Error Response (400):**
```json
{
  "success": false,
  "message": "CAPTCHA verification failed. Please try again."
}
```

---

#### 4. User Registration

```http
POST /api/register
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepassword123",
  "g-recaptcha-response": "token_from_recaptcha"
}
```

**Success Response (200):**
```json
{
  "success": true,
  "message": "Registration successful",
  "user": {
    "name": "John Doe",
    "username": "john@example.com",
    "email": "john@example.com",
    "registeredAt": "2024-12-20T10:30:00.000Z"
  },
  "token": "base64_encoded_token"
}
```

---

#### 5. Health Check

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "FraudGuard® reCAPTCHA Service",
  "timestamp": "2024-12-20T10:30:00.000Z",
  "recaptcha_configured": true,
  "redis": {
    "connected": true,
    "fallbackMode": false
  }
}
```

---

### Admin Endpoints

#### 1. Get Fraud Statistics

```http
GET /admin/fraud-stats
X-Admin-Token: your_admin_token
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "totalIPs": 45,
    "activeCount": 38,
    "blockedCount": 7,
    "highRiskCount": 12,
    "threshold": 100,
    "averageScore": 35.2,
    "redisStatus": {
      "connected": true,
      "fallbackMode": false
    }
  },
  "activeIPs": [
    {
      "ip": "192.168.1.100",
      "score": 85,
      "blocked": false,
      "lastActivity": "2024-12-20T10:25:00.000Z"
    }
  ],
  "timestamp": "2024-12-20T10:30:00.000Z"
}
```

---

#### 2. Unblock IP Address

```http
POST /admin/unblock/:ip
X-Admin-Token: your_admin_token
```

**Example:**
```bash
curl -X POST \
  http://localhost:3000/admin/unblock/192.168.1.100 \
  -H 'X-Admin-Token: your_admin_token'
```

**Success Response:**
```json
{
  "success": true,
  "message": "IP 192.168.1.100 has been unblocked",
  "ip": "192.168.1.100"
}
```

---

#### 3. Reset Fraud Score

```http
POST /admin/reset-score/:ip
X-Admin-Token: your_admin_token
```

**Success Response:**
```json
{
  "success": true,
  "message": "Fraud score reset for IP 192.168.1.100",
  "ip": "192.168.1.100"
}
```

---

### Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `missing-input-response` | reCAPTCHA token missing |
| 400 | `invalid-input-response` | Invalid or expired reCAPTCHA |
| 401 | `unauthorized` | Invalid admin token |
| 403 | `ip-blocked` | IP blocked due to high fraud score |
| 404 | `not-found` | Endpoint not found |
| 500 | `server-error` | Internal server error |

---

## 👥 User Guide

### For End Users

#### Accessing the System

1. **Navigate to the login page:**
   ```
   http://localhost:3000/fraudguard.html
   ```

2. **Complete the reCAPTCHA challenge:**
   - Check the "I'm not a robot" box
   - Complete any image challenges if prompted

3. **Enter your credentials:**
   - Email address
   - Password

4. **Click "Login" or "Register"**

#### Understanding Fraud Protection

The system protects you by:
- Detecting bot attacks automatically
- Preventing account takeovers
- Blocking suspicious IP addresses
- Requiring CAPTCHA verification

#### Troubleshooting for Users

**Issue: "Your IP has been temporarily blocked"**
- **Cause:** Too many failed login attempts or suspicious activity
- **Solution:** Wait 15 minutes or contact administrator
- **Prevention:** Ensure correct password, avoid rapid requests

**Issue: "CAPTCHA verification failed"**
- **Cause:** Expired or invalid CAPTCHA token
- **Solution:** Complete the CAPTCHA again
- **Prevention:** Submit the form promptly after solving CAPTCHA

---

## 👨‍💼 Administrator Guide

### Admin Dashboard Access

```
http://localhost:3000/admin-dashboard-comprehensive.html
```

### Dashboard Features

#### 1. Overview Section
- Total fraud attempts counter
- Blocked transactions count
- Detection accuracy percentage
- Active cases tracker
- Real-time fraud trends chart
- Threat category distribution

#### 2. Analytics & Reporting
- Geographic threat distribution
- Detection performance metrics
- Time-based analysis (24-hour patterns)
- Top threat sources table
- Export capabilities (CSV)

#### 3. Case Management
- View all fraud cases
- Filter by priority/status
- Assign cases to team members
- Track investigation progress
- Add notes and evidence

#### 4. User Management
- View all admin users
- Manage roles and permissions
- Track user activity
- Control access levels

#### 5. System Settings
- Configure fraud detection thresholds
- Toggle features (monitoring, geo-blocking, etc.)
- Manage API keys
- Update system parameters

#### 6. Detection Rules
- Create custom detection rules
- Set conditions and actions
- View rule trigger statistics
- Enable/disable rules

#### 7. Reports
- Generate custom reports
- Select date ranges
- Choose export formats (PDF, Excel, CSV)
- Schedule automated reports

#### 8. Audit Logs
- View all system activities
- Filter by user/action/date
- Export audit trails
- Compliance reporting

### Admin Tasks

#### Unblock an IP Address

```bash
# Using curl
curl -X POST \
  http://localhost:3000/admin/unblock/192.168.1.100 \
  -H 'X-Admin-Token: your_admin_token'

# Using the dashboard
1. Navigate to Analytics section
2. Find the IP in the "Top Threat Sources" table
3. Click the "Unblock" button
```

#### Reset Fraud Score

```bash
curl -X POST \
  http://localhost:3000/admin/reset-score/192.168.1.100 \
  -H 'X-Admin-Token: your_admin_token'
```

#### Monitor System Health

```bash
# Check system status
curl http://localhost:3000/health

# View fraud statistics
curl http://localhost:3000/admin/fraud-stats \
  -H 'X-Admin-Token: your_admin_token'
```

### Best Practices

1. **Regular Monitoring:**
   - Check dashboard daily
   - Review fraud trends weekly
   - Analyze patterns monthly

2. **Threshold Tuning:**
   - Start with default threshold (100)
   - Adjust based on false positives
   - Monitor impact of changes

3. **Security:**
   - Rotate admin tokens monthly
   - Review audit logs regularly
   - Keep reCAPTCHA keys secure

4. **Performance:**
   - Monitor Redis connection
   - Check response times
   - Scale horizontally if needed

---

## 🔒 Security Documentation

### Security Measures Implemented

#### 1. reCAPTCHA Protection
- **Google reCAPTCHA v2** integration
- Server-side token verification
- Challenge-response validation
- Bot detection and prevention

#### 2. Fraud Scoring System
- IP-based risk scoring
- Automatic blocking at threshold
- Score decay over time
- Redis persistence with in-memory fallback

#### 3. HTTP Security Headers
```javascript
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

#### 4. Input Validation
- Email format validation
- Password strength requirements
- Token format verification
- SQL injection prevention

#### 5. Authentication & Authorization
- Admin token-based authentication
- Role-based access control (RBAC)
- Session management
- Secure password handling

### Data Protection

#### Sensitive Data Handling
- **Environment Variables:** Secrets stored in `.env` (never committed)
- **Password Storage:** Should use bcrypt hashing (implement in production)
- **Session Tokens:** Base64 encoded, time-limited
- **API Keys:** Rotation supported, access logging

#### Data Encryption
- **In Transit:** HTTPS recommended for production
- **At Rest:** Redis password protection optional
- **Backups:** Encrypted backups recommended

### Compliance

#### GDPR Compliance
- User consent for data processing
- Right to erasure (implement delete functionality)
- Data portability (export functionality)
- Audit logging of data access

#### PCI DSS (if handling payments)
- Fraud detection requirement (Requirement 11)
- Access control (Requirement 7)
- Logging and monitoring (Requirement 10)

### Security Best Practices

#### For Administrators

1. **Secure the Admin Token:**
   ```bash
   # Generate a strong random token
   node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"

   # Store in .env
   ADMIN_TOKEN=91cc29f33505f7f6856f5412faa79a3b8a19fc8b481d649feaca7b33f5523b9f
   ```

2. **Enable HTTPS in Production:**
   ```javascript
   // Use a reverse proxy (Nginx, Apache) with SSL
   // Or use Let's Encrypt certificates
   ```

3. **Firewall Configuration:**
   ```bash
   # Allow only necessary ports
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw deny 3000/tcp  # Block direct access to Node.js
   sudo ufw enable
   ```

4. **Regular Updates:**
   ```bash
   # Update dependencies
   npm audit fix
   pip list --outdated
   ```

#### For Developers

1. **Never Commit Secrets:**
   ```bash
   # Ensure .gitignore includes
   .env
   .env.local
   .env.*.local
   ```

2. **Use Prepared Statements:**
   ```javascript
   // Prevent SQL injection
   const query = 'SELECT * FROM users WHERE email = ?';
   db.query(query, [email]);
   ```

3. **Validate All Input:**
   ```javascript
   // Email validation
   const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
   if (!emailRegex.test(email)) {
     return res.status(400).json({ error: 'Invalid email' });
   }
   ```

4. **Rate Limiting:**
   ```javascript
   // Implement rate limiting
   const rateLimit = require('express-rate-limit');
   const limiter = rateLimit({
     windowMs: 15 * 60 * 1000, // 15 minutes
     max: 100 // limit each IP to 100 requests per windowMs
   });
   app.use('/api/', limiter);
   ```

### Incident Response

#### If a Security Breach Occurs:

1. **Immediate Actions:**
   - Isolate affected systems
   - Change all passwords and tokens
   - Review access logs
   - Document the incident

2. **Investigation:**
   - Check audit logs
   - Identify attack vector
   - Assess data exposure
   - Determine timeline

3. **Remediation:**
   - Patch vulnerabilities
   - Update security measures
   - Restore from clean backups
   - Monitor for recurrence

4. **Communication:**
   - Notify affected users
   - Report to authorities if required
   - Document lessons learned
   - Update security policies

### Audit Logging

All security-relevant events are logged:

```javascript
// Logged events
- Failed login attempts
- CAPTCHA failures
- IP blocking events
- Admin actions (unblock, reset score)
- Configuration changes
- Suspicious patterns detected
```

Access logs via:
```bash
# View Node.js logs
pm2 logs fraudguard

# Or check console output
tail -f /var/log/fraudguard/app.log
```

---

## 🚀 Deployment Guide

### Production Deployment Checklist

- [ ] Update `.env` with production reCAPTCHA keys
- [ ] Set `NODE_ENV=production`
- [ ] Generate strong `ADMIN_TOKEN`
- [ ] Configure production Redis instance
- [ ] Set up SSL/HTTPS certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting
- [ ] Configure backups
- [ ] Test all endpoints
- [ ] Load testing completed
- [ ] Security audit passed

### Deployment Options

#### Option 1: Traditional Server Deployment

**1. Prepare the Server:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 18 LTS
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Install Redis
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Install Nginx (reverse proxy)
sudo apt install -y nginx
sudo systemctl enable nginx
```

**2. Clone and Configure:**
```bash
# Clone repository
cd /var/www
sudo git clone <your-repo-url> fraudguard
cd fraudguard

# Install dependencies
cd recaptcha-service
npm install --production

# Configure environment
sudo nano .env
# Update with production values
```

**3. Configure Nginx:**
```nginx
# /etc/nginx/sites-available/fraudguard

server {
    listen 80;
    server_name fraudguard.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name fraudguard.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/fraudguard.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/fraudguard.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security Headers
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Proxy to Node.js
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Static files caching
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        proxy_pass http://localhost:3000;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**4. Enable and Start:**
```bash
# Enable Nginx configuration
sudo ln -s /etc/nginx/sites-available/fraudguard /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Install PM2 for process management
sudo npm install -g pm2

# Start application with PM2
cd /var/www/fraudguard/recaptcha-service
pm2 start server.js --name fraudguard
pm2 save
pm2 startup
```

**5. SSL Certificate (Let's Encrypt):**
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d fraudguard.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

#### Option 2: Docker Deployment

**1. Create Dockerfile:**
```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY recaptcha-service/package*.json ./
RUN npm install --production

# Copy application code
COPY recaptcha-service/ .

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health', (r) => { process.exit(r.statusCode === 200 ? 0 : 1) })"

# Start application
CMD ["node", "server.js"]
```

**2. Create docker-compose.yml:**
```yaml
version: '3.8'

services:
  fraudguard:
    build: .
    container_name: fraudguard-app
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - REDIS_URL=redis://redis:6379
    env_file:
      - ./recaptcha-service/.env
    depends_on:
      - redis
    networks:
      - fraudguard-network

  redis:
    image: redis:7-alpine
    container_name: fraudguard-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes
    networks:
      - fraudguard-network

  nginx:
    image: nginx:alpine
    container_name: fraudguard-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - fraudguard
    networks:
      - fraudguard-network

volumes:
  redis-data:

networks:
  fraudguard-network:
    driver: bridge
```

**3. Deploy with Docker Compose:**
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f fraudguard

# Stop services
docker-compose down

# Update and restart
git pull
docker-compose up -d --build
```

---

#### Option 3: Kubernetes Deployment

**1. Create Deployment:**
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fraudguard
  labels:
    app: fraudguard
spec:
  replicas: 3
  selector:
    matchLabels:
      app: fraudguard
  template:
    metadata:
      labels:
        app: fraudguard
    spec:
      containers:
      - name: fraudguard
        image: your-registry/fraudguard:latest
        ports:
        - containerPort: 3000
        env:
        - name: NODE_ENV
          value: "production"
        - name: REDIS_URL
          valueFrom:
            configMapKeyRef:
              name: fraudguard-config
              key: redis-url
        - name: RECAPTCHA_SITE_KEY
          valueFrom:
            secretKeyRef:
              name: fraudguard-secrets
              key: recaptcha-site-key
        - name: RECAPTCHA_SECRET
          valueFrom:
            secretKeyRef:
              name: fraudguard-secrets
              key: recaptcha-secret
        - name: ADMIN_TOKEN
          valueFrom:
            secretKeyRef:
              name: fraudguard-secrets
              key: admin-token
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 30
        readinessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 10
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

**2. Create Service:**
```yaml
# k8s/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: fraudguard-service
spec:
  selector:
    app: fraudguard
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: LoadBalancer
```

**3. Create Secrets:**
```bash
kubectl create secret generic fraudguard-secrets \
  --from-literal=recaptcha-site-key='your_site_key' \
  --from-literal=recaptcha-secret='your_secret' \
  --from-literal=admin-token='your_admin_token'
```

**4. Deploy:**
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check status
kubectl get pods -l app=fraudguard
kubectl logs -f deployment/fraudguard
```

---

### Monitoring and Maintenance

#### Application Monitoring

**PM2 Monitoring:**
```bash
# View status
pm2 status

# View logs
pm2 logs fraudguard

# Monitor resources
pm2 monit

# Restart on file changes
pm2 restart fraudguard
```

**Health Check Script:**
```bash
#!/bin/bash
# health-check.sh

HEALTH_URL="http://localhost:3000/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL)

if [ $RESPONSE -eq 200 ]; then
  echo "✅ Service is healthy"
  exit 0
else
  echo "❌ Service is unhealthy (HTTP $RESPONSE)"
  # Send alert (email, Slack, PagerDuty, etc.)
  exit 1
fi
```

**Cron job for monitoring:**
```bash
# Add to crontab
*/5 * * * * /var/www/fraudguard/health-check.sh
```

#### Database Backup

**Redis Backup:**
```bash
#!/bin/bash
# redis-backup.sh

BACKUP_DIR="/var/backups/redis"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/redis_backup_$TIMESTAMP.rdb"

# Create backup directory
mkdir -p $BACKUP_DIR

# Save Redis data
redis-cli --rdb $BACKUP_FILE

# Compress
gzip $BACKUP_FILE

# Keep only last 7 days of backups
find $BACKUP_DIR -name "redis_backup_*.rdb.gz" -mtime +7 -delete

echo "✅ Redis backup completed: $BACKUP_FILE.gz"
```

**Automated backups:**
```bash
# Add to crontab - daily at 2 AM
0 2 * * * /var/www/fraudguard/redis-backup.sh
```

#### Log Rotation

**Configure logrotate:**
```bash
# /etc/logrotate.d/fraudguard

/var/log/fraudguard/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        pm2 reloadLogs
    endscript
}
```

### Scaling Strategies

#### Horizontal Scaling

**Load Balancer Configuration:**
```nginx
# Nginx upstream
upstream fraudguard_backend {
    least_conn;
    server app1.internal:3000;
    server app2.internal:3000;
    server app3.internal:3000;
}

server {
    listen 443 ssl http2;
    server_name fraudguard.yourdomain.com;

    location / {
        proxy_pass http://fraudguard_backend;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

#### Redis Cluster

**For high availability:**
```yaml
# docker-compose.yml with Redis Sentinel

services:
  redis-master:
    image: redis:7-alpine
    command: redis-server --appendonly yes

  redis-slave1:
    image: redis:7-alpine
    command: redis-server --slaveof redis-master 6379 --appendonly yes

  redis-slave2:
    image: redis:7-alpine
    command: redis-server --slaveof redis-master 6379 --appendonly yes

  redis-sentinel1:
    image: redis:7-alpine
    command: redis-sentinel /etc/redis/sentinel.conf
    depends_on:
      - redis-master
      - redis-slave1
      - redis-slave2
```

---

## 🤝 Contributing Guidelines

### Development Workflow

#### 1. Fork and Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/fraud_detection_system.git
cd fraud_detection_system

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/fraud_detection_system.git
```

#### 2. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

#### 3. Make Changes

**Code Style Guidelines:**

**JavaScript (Node.js):**
- Use ES6+ features
- 4-space indentation
- Semicolons required
- Descriptive variable names
- JSDoc comments for functions

```javascript
/**
 * Verify reCAPTCHA token with Google's API
 * @param {string} token - The g-recaptcha-response token
 * @param {string} remoteIP - Client's IP address
 * @returns {Promise<Object>} Verification result
 */
async function verifyRecaptcha(token, remoteIP = null) {
    // Implementation
}
```

**Python:**
- PEP 8 style guide
- Type hints where appropriate
- Docstrings for all functions
- 4-space indentation

```python
def detect_fraud(transaction: dict) -> tuple[bool, float]:
    """
    Detect fraud in a transaction.

    Args:
        transaction: Dictionary containing transaction details

    Returns:
        Tuple of (is_fraud, confidence_score)
    """
    # Implementation
    pass
```

#### 4. Test Your Changes

```bash
# Run tests
npm test  # Node.js tests
pytest    # Python tests

# Manual testing
npm start
# Test all affected endpoints
```

#### 5. Commit Changes

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(api): add fraud score reset endpoint

Add POST /admin/reset-score/:ip endpoint that allows
administrators to manually reset the fraud score for a
specific IP address.

Closes #123"
```

```bash
git commit -m "fix(recaptcha): handle expired tokens gracefully

Improve error handling for expired reCAPTCHA tokens by
returning a more descriptive error message and logging
the event for monitoring.

Fixes #456"
```

#### 6. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create PR on GitHub with description:
# - What changes were made
# - Why the changes are needed
# - How to test the changes
# - Screenshots if UI changes
```

### Code Review Process

1. **Automated Checks:**
   - CI/CD pipeline runs tests
   - Code style linting
   - Security vulnerability scan

2. **Peer Review:**
   - At least one approval required
   - Address reviewer comments
   - Keep discussions professional

3. **Merge:**
   - Squash commits if multiple small commits
   - Merge to main branch
   - Delete feature branch

### Testing Requirements

**All PRs must include:**
- Unit tests for new functions
- Integration tests for new endpoints
- Manual testing checklist

**Example Test:**
```javascript
// tests/fraudScore.test.js
const assert = require('assert');
const fraudScore = require('../fraudScoreManager');

describe('FraudScore Manager', function() {
    it('should increment score correctly', async function() {
        const ip = '192.168.1.100';
        await fraudScore.resetScore(ip);

        await fraudScore.incrementScore(ip, 'FAILED_LOGIN');
        const score = await fraudScore.getScore(ip);

        assert.strictEqual(score, 15);
    });

    it('should block IP when threshold exceeded', async function() {
        const ip = '192.168.1.101';
        await fraudScore.resetScore(ip);

        // Increment score above threshold
        for (let i = 0; i < 10; i++) {
            await fraudScore.incrementScore(ip, 'FAILED_CAPTCHA');
        }

        const check = await fraudScore.checkRequest(ip);
        assert.strictEqual(check.allowed, false);
        assert.strictEqual(check.reason, 'Score exceeded threshold');
    });
});
```

### Documentation Requirements

**All code must be documented:**
- JSDoc comments for functions
- README updates for new features
- API documentation updates
- User guide updates if UI changes

---

## 🔧 Troubleshooting

### Common Issues

#### Issue 1: reCAPTCHA "for testing purposes only" Warning

**Symptoms:**
- Warning message appears in reCAPTCHA widget
- Message: "This reCAPTCHA is for testing purposes only"

**Cause:**
Using Google's test keys in `.env` file

**Solution:**
1. Get production keys from https://www.google.com/recaptcha/admin/create
2. Update `.env` file with production keys
3. Restart server
4. Clear browser cache (Ctrl + Shift + R)

**Detailed Steps:** See `COMO_OBTER_CHAVES_PRODUCAO.md`

---

#### Issue 2: Redis Connection Failed

**Symptoms:**
```
❌ Redis connection error: ECONNREFUSED
⚠️ Falling back to in-memory storage
```

**Cause:**
- Redis server not running
- Wrong REDIS_URL configuration
- Firewall blocking connection

**Solution:**

**Option A: Start Redis**
```bash
# On Ubuntu/Debian
sudo systemctl start redis-server
sudo systemctl status redis-server

# Using Docker
docker run -d -p 6379:6379 redis:alpine

# Verify
redis-cli ping  # Should return PONG
```

**Option B: Use In-Memory Mode**
```bash
# System will automatically fall back
# Check logs for confirmation
```

**Option C: Update REDIS_URL**
```bash
# In .env file
REDIS_URL=redis://localhost:6379

# For remote Redis
REDIS_URL=redis://username:password@host:port
```

---

#### Issue 3: "Invalid admin token" Error

**Symptoms:**
```json
{
  "error": "Unauthorized",
  "message": "Valid admin token required"
}
```

**Cause:**
- Missing or incorrect admin token
- Token not set in environment

**Solution:**

**Generate New Token:**
```bash
# Generate secure random token
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

**Update .env:**
```bash
ADMIN_TOKEN=your_new_secure_token_here
```

**Restart Server:**
```bash
pm2 restart fraudguard
# Or
npm start
```

**Use Token in Requests:**
```bash
# Method 1: Header
curl -H "X-Admin-Token: your_token" http://localhost:3000/admin/fraud-stats

# Method 2: Query parameter
curl http://localhost:3000/admin/fraud-stats?token=your_token
```

---

#### Issue 4: High Memory Usage

**Symptoms:**
- Server becomes slow
- Out of memory errors
- System crashes

**Cause:**
- Too many IPs tracked in memory
- Memory leak
- No score decay running

**Solution:**

**Check Memory Usage:**
```bash
# PM2
pm2 monit

# Or
top
htop
```

**Enable Score Decay:**
```javascript
// Already enabled in server.js
fraudScore.startScoreDecay();
```

**Limit Tracked IPs:**
```javascript
// Implement in fraudScoreManager.js
const MAX_TRACKED_IPS = 10000;

// Clean old entries
async function cleanOldEntries() {
    const allScores = await getAllScores();
    if (allScores.length > MAX_TRACKED_IPS) {
        // Remove lowest scores
        allScores.sort((a, b) => a.score - b.score);
        const toRemove = allScores.slice(0, allScores.length - MAX_TRACKED_IPS);
        for (const entry of toRemove) {
            await resetScore(entry.ip);
        }
    }
}
```

**Restart with Memory Limit:**
```bash
pm2 start server.js --name fraudguard --max-memory-restart 500M
```

---

#### Issue 5: CAPTCHA Verification Fails

**Symptoms:**
```json
{
  "success": false,
  "errors": ["invalid-input-response"],
  "message": "CAPTCHA expired or invalid"
}
```

**Possible Causes:**
1. Expired CAPTCHA token
2. Wrong secret key
3. Network connectivity issues
4. Domain mismatch

**Solutions:**

**1. Check Secret Key:**
```bash
# Verify in .env
cat .env | grep RECAPTCHA_SECRET

# Test with curl
curl -X POST \
  'https://www.google.com/recaptcha/api/siteverify' \
  -d "secret=YOUR_SECRET" \
  -d "response=test_token"
```

**2. Check Domain Configuration:**
- Log into https://www.google.com/recaptcha/admin
- Verify domain is listed (localhost, your domain)
- Check if keys match site

**3. Enable Detailed Logging:**
```javascript
// In server.js, add more logging
console.log('Full verification response:', JSON.stringify(verificationResult, null, 2));
```

**4. Test with Fresh Token:**
- Solve CAPTCHA again
- Submit immediately (tokens expire)

---

#### Issue 6: IP Blocked Permanently

**Symptoms:**
- User cannot access even after waiting
- Score doesn't decay

**Cause:**
- Score decay not running
- Threshold set too low
- Multiple block events

**Solution:**

**Manual Unblock:**
```bash
curl -X POST \
  http://localhost:3000/admin/unblock/192.168.1.100 \
  -H "X-Admin-Token: your_token"
```

**Reset Score:**
```bash
curl -X POST \
  http://localhost:3000/admin/reset-score/192.168.1.100 \
  -H "X-Admin-Token: your_token"
```

**Check Decay Settings:**
```bash
# In .env
SCORE_DECAY_INTERVAL=3600  # 1 hour
SCORE_DECAY_AMOUNT=10      # Points per decay
```

**Verify Decay is Running:**
```bash
# Check logs for
# "🔄 Applying fraud score decay..."
pm2 logs fraudguard | grep decay
```

---

### Diagnostic Commands

```bash
# Check all services status
systemctl status nginx
systemctl status redis-server
pm2 status

# View real-time logs
pm2 logs fraudguard --lines 50

# Check port availability
netstat -tulpn | grep 3000
netstat -tulpn | grep 6379

# Test Redis connection
redis-cli ping
redis-cli KEYS "*"

# Check environment variables
cat recaptcha-service/.env

# Test API health
curl http://localhost:3000/health | jq

# Check fraud statistics
curl -H "X-Admin-Token: YOUR_TOKEN" \
  http://localhost:3000/admin/fraud-stats | jq

# Monitor system resources
htop
iotop
iftop

# Check disk space
df -h

# View network connections
ss -tunap | grep 3000
```

---

## ❓ FAQ

### General Questions

**Q: What is FraudGuard®?**
A: FraudGuard® is a real-time fraud detection and prevention system that uses machine learning, behavioral analysis, and reCAPTCHA to protect web applications from fraudulent activities and bot attacks.

**Q: Is FraudGuard® free?**
A: The core system is open-source. However, you need to provide your own Google reCAPTCHA keys (free with usage limits) and infrastructure (servers, Redis, etc.).

**Q: What programming languages are used?**
A: The system uses Node.js (JavaScript) for the reCAPTCHA service and Python for the ML models and Streamlit dashboard.

**Q: Can I use this in production?**
A: Yes, but ensure you:
- Use production reCAPTCHA keys
- Enable HTTPS
- Set strong admin tokens
- Configure proper firewalls
- Set up monitoring and backups

### Technical Questions

**Q: Do I need Redis?**
A: No, the system automatically falls back to in-memory storage if Redis is unavailable. However, Redis is recommended for production use for persistence and scalability.

**Q: How does the fraud scoring work?**
A: Each IP address is assigned a score. Failed CAPTCHAs, failed logins, and suspicious patterns increase the score. When the score exceeds the threshold (default 100), the IP is temporarily blocked. Scores decay over time.

**Q: Can I customize the blocking threshold?**
A: Yes, edit the `.env` file:
```bash
BLOCK_THRESHOLD=150  # Increase to 150
```

**Q: How long are IPs blocked?**
A: Default is 15 minutes (900 seconds). Configure in `.env`:
```bash
BLOCK_TTL=1800  # 30 minutes
```

**Q: Can I whitelist specific IPs?**
A: Currently not implemented. You can modify `fraudScoreManager.js` to add whitelist logic:
```javascript
const WHITELIST = ['192.168.1.1', '10.0.0.1'];

async function checkRequest(ip) {
    if (WHITELIST.includes(ip)) {
        return { allowed: true, score: 0 };
    }
    // ... existing logic
}
```

**Q: Does this work with v3 reCAPTCHA?**
A: The current implementation uses reCAPTCHA v2 (checkbox). For v3 (score-based), you would need to modify the implementation.

**Q: Can I integrate this with my existing application?**
A: Yes! The system provides:
- RESTful API endpoints
- Standalone fraud scoring service
- Embeddable reCAPTCHA verification
- Admin dashboard

### Security Questions

**Q: Where are the reCAPTCHA keys stored?**
A: In the `.env` file, which should never be committed to version control. The secret key never leaves the server.

**Q: Is user data encrypted?**
A: The current implementation doesn't store user credentials. For production, implement:
- bcrypt password hashing
- HTTPS for data in transit
- Database encryption at rest

**Q: How secure is the admin token?**
A: The security depends on:
- Token strength (use crypto.randomBytes)
- Never exposing it in logs or client-side code
- Regular rotation
- HTTPS in production

**Q: Does this comply with GDPR?**
A: The system logs IP addresses and user activity. For GDPR compliance, you must:
- Inform users about data collection
- Provide data export functionality
- Implement data deletion on request
- Document data retention policies

### Deployment Questions

**Q: Can I deploy on shared hosting?**
A: Probably not. You need:
- Node.js support
- Ability to run background processes
- Access to Redis (or fallback to in-memory)
- VPS or dedicated server recommended

**Q: What are the minimum server requirements?**
A:
- 2 CPU cores
- 4 GB RAM
- 10 GB disk space
- Ubuntu 20.04+ or similar
- Node.js 16+, Python 3.8+

**Q: Can I use Docker?**
A: Yes! A Dockerfile and docker-compose.yml are provided. Run:
```bash
docker-compose up -d
```

**Q: How do I scale horizontally?**
A: Use:
- Load balancer (Nginx) distributing traffic to multiple Node.js instances
- Shared Redis instance for all application servers
- Session persistence if needed

### Troubleshooting Questions

**Q: Why is the reCAPTCHA showing a test warning?**
A: You're using Google's test keys. Get production keys from https://www.google.com/recaptcha/admin/create and update your `.env` file.

**Q: Why can't users log in after multiple attempts?**
A: Their IP exceeded the fraud score threshold and was auto-blocked. Administrators can manually unblock via the admin dashboard or API.

**Q: Why is Redis showing "ECONNREFUSED"?**
A: Redis is not running. Start it with:
```bash
sudo systemctl start redis-server
```
Or the system will automatically fall back to in-memory mode.

**Q: How do I view logs?**
A:
```bash
# PM2
pm2 logs fraudguard

# Docker
docker-compose logs -f fraudguard

# Direct execution
# Logs appear in console
```

### Integration Questions

**Q: Can I use this with React/Vue/Angular?**
A: Yes! Use the API endpoints:
```javascript
// Fetch site key
const { siteKey } = await fetch('/api/site-key').then(r => r.json());

// Verify CAPTCHA
const response = await fetch('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        username, password,
        'g-recaptcha-response': captchaToken
    })
});
```

**Q: Can I integrate with WordPress?**
A: Yes, create a WordPress plugin that:
1. Calls FraudGuard API for verification
2. Embeds reCAPTCHA on login forms
3. Handles blocked IPs

**Q: Does this work with mobile apps?**
A: The backend API works with any client. For mobile:
- Use reCAPTCHA Android/iOS SDKs
- Send tokens to `/verify-captcha` endpoint

**Q: Can I add custom fraud detection rules?**
A: Yes, modify `fraudScoreManager.js`:
```javascript
// Add custom rule
async function checkCustomRules(data) {
    if (data.country !== 'expected_country') {
        return { fraudulent: true, score: 50 };
    }
    return { fraudulent: false, score: 0 };
}
```

---

## 📄 License

FraudGuard® Fraud Detection System

**Copyright © 2024 FraudGuard®**

This software is provided for demonstration and educational purposes.

For production use, proper licensing and agreements must be established.

**Third-Party Licenses:**
- Node.js - MIT License
- Express - MIT License
- Redis - BSD 3-Clause License
- Python - PSF License
- Streamlit - Apache License 2.0
- Bootstrap - MIT License
- Chart.js - MIT License

---

## 📞 Support & Contact

### Getting Help

1. **Documentation:** Read this comprehensive guide
2. **GitHub Issues:** Report bugs and request features
3. **Community Forum:** Ask questions and share solutions
4. **Email Support:** support@fraudguard.com (if available)

### Contributing

We welcome contributions! See [Contributing Guidelines](#contributing-guidelines) above.

### Reporting Security Issues

If you discover a security vulnerability:
1. **Do NOT** open a public issue
2. Email: security@fraudguard.com
3. Include detailed description and steps to reproduce
4. Allow time for patching before public disclosure

---

## 🎓 Additional Resources

### Documentation Files

This repository includes additional specialized documentation:

- `START_HERE.md` - Quick start guide for beginners
- `SETUP.md` - Detailed installation instructions
- `API.md` - Complete API reference
- `DEPLOYMENT.md` - Production deployment guide
- `SECURITY.md` - Security best practices
- `ARCHITECTURE.md` - System architecture details
- `CONTRIBUTING.md` - How to contribute
- `TROUBLESHOOTING.md` - Common issues and solutions

### External Resources

- [Google reCAPTCHA Documentation](https://developers.google.com/recaptcha/docs/display)
- [Node.js Best Practices](https://github.com/goldbergyoni/nodebestpractices)
- [Redis Documentation](https://redis.io/documentation)
- [Express.js Guide](https://expressjs.com/en/guide/routing.html)
- [Streamlit Documentation](https://docs.streamlit.io/)

---

## 🔄 Version History

### Version 1.0.0 (Current)
- Initial release
- reCAPTCHA v2 integration
- Fraud scoring system
- Redis support with in-memory fallback
- Admin dashboard
- Streamlit analytics dashboard
- RESTful API
- Comprehensive documentation

### Roadmap

**Version 1.1.0 (Planned):**
- Machine learning model improvements
- Advanced behavioral analysis
- Email notifications for admins
- Webhook support
- API rate limiting improvements

**Version 1.2.0 (Future):**
- reCAPTCHA v3 support
- Device fingerprinting
- Geo-blocking capabilities
- Multi-factor authentication
- Enhanced reporting

---

**Last Updated:** December 20, 2024
**Document Version:** 1.0
**Status:** ✅ Production Ready

---

*Thank you for using FraudGuard®! Together, we're making the internet safer.* 🛡️
