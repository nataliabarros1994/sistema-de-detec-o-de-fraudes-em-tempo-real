/**
 * FraudGuard® - reCAPTCHA Verification Server
 *
 * This Express server provides bot protection for FraudGuard's authentication
 * and sensitive API endpoints using Google reCAPTCHA v2.
 *
 * Security Features:
 * - Server-side token verification
 * - Environment-based secret management
 * - Request validation and sanitization
 * - Detailed logging for security monitoring
 */

require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const fetch = require('node-fetch');
const path = require('path');
const redis = require('./redisClient');
const fraudScore = require('./fraudScoreManager');

const app = express();
const PORT = process.env.PORT || 3000;
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || 'admin-secret-token';

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));
app.use(express.static('public'));

// Security headers
app.use((req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('X-XSS-Protection', '1; mode=block');
    next();
});

// Environment validation
if (!process.env.RECAPTCHA_SECRET) {
    console.error('❌ CRITICAL ERROR: RECAPTCHA_SECRET not found in environment variables');
    console.error('Please create a .env file with your reCAPTCHA credentials');
    process.exit(1);
}

console.log('✅ Environment variables loaded successfully');
console.log(`🔐 reCAPTCHA Site Key: ${process.env.RECAPTCHA_SITE_KEY ? 'CONFIGURED' : 'MISSING'}`);
console.log(`🔐 reCAPTCHA Secret: ${process.env.RECAPTCHA_SECRET ? 'CONFIGURED' : 'MISSING'}`);

/**
 * Verify reCAPTCHA token with Google's API
 * @param {string} token - The g-recaptcha-response token from client
 * @param {string} remoteIP - Client's IP address (optional but recommended)
 * @returns {Promise<Object>} Verification result from Google
 */
async function verifyRecaptcha(token, remoteIP = null) {
    const verifyUrl = 'https://www.google.com/recaptcha/api/siteverify';

    // Build request body
    const params = new URLSearchParams({
        secret: process.env.RECAPTCHA_SECRET,
        response: token
    });

    if (remoteIP) {
        params.append('remoteip', remoteIP);
    }

    console.log(`🔍 Verifying reCAPTCHA token from IP: ${remoteIP || 'unknown'}`);

    try {
        const response = await fetch(verifyUrl, {
            method: 'POST',
            body: params,
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
        });

        if (!response.ok) {
            throw new Error(`Google API returned status ${response.status}`);
        }

        const data = await response.json();
        console.log('📊 reCAPTCHA verification result:', {
            success: data.success,
            timestamp: data.challenge_ts,
            hostname: data.hostname,
            errors: data['error-codes']
        });

        return data;
    } catch (error) {
        console.error('❌ reCAPTCHA verification error:', error.message);
        throw error;
    }
}

/**
 * GET /
 * Serve the main authentication page with reCAPTCHA
 */
app.get('/', (req, res) => {
    console.log(`📄 Serving index.html to ${req.ip}`);
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

/**
 * GET /api/site-key
 * Provide the public site key to the frontend
 * This is safe to expose - it's public by design
 */
app.get('/api/site-key', (req, res) => {
    console.log(`🔑 Site key requested by ${req.ip}`);
    res.json({
        siteKey: process.env.RECAPTCHA_SITE_KEY,
        version: 'v2-checkbox'
    });
});

/**
 * POST /verify-captcha
 * Main endpoint for reCAPTCHA verification
 *
 * Expected request body:
 * {
 *   "g-recaptcha-response": "token_from_google",
 *   "username": "user@example.com",  // optional, for logging
 *   "action": "login"                 // optional, for logging
 * }
 *
 * Returns:
 * Success: { success: true, message: "CAPTCHA verified" }
 * Failure: { success: false, errors: [...] }
 */
app.post('/verify-captcha', checkIPBlocking, async (req, res) => {
    const startTime = Date.now();
    const clientIP = req.headers['x-forwarded-for'] || req.connection.remoteAddress;

    console.log('\n' + '='.repeat(60));
    console.log(`🛡️ CAPTCHA Verification Request`);
    console.log(`📍 IP: ${clientIP}`);
    console.log(`📊 Fraud Score: ${req.fraudCheck.score}/${fraudScore.getStats().threshold || 100}`);
    console.log(`⏰ Time: ${new Date().toISOString()}`);
    console.log(`👤 User: ${req.body.username || 'anonymous'}`);
    console.log(`🎯 Action: ${req.body.action || 'unknown'}`);
    console.log('='.repeat(60));

    // Extract the reCAPTCHA token
    const token = req.body['g-recaptcha-response'];

    // Validation: Check if token exists
    if (!token) {
        console.warn('⚠️ CAPTCHA verification failed: Missing token');
        await fraudScore.incrementScore(clientIP, 'FAILED_CAPTCHA');
        return res.status(400).json({
            success: false,
            errors: ['missing-input-response'],
            message: 'Please complete the CAPTCHA challenge'
        });
    }

    // Validation: Check token format (basic sanity check)
    if (typeof token !== 'string' || token.length < 20) {
        console.warn('⚠️ CAPTCHA verification failed: Invalid token format');
        await fraudScore.incrementScore(clientIP, 'FAILED_CAPTCHA');
        return res.status(400).json({
            success: false,
            errors: ['invalid-input-response'],
            message: 'Invalid CAPTCHA token format'
        });
    }

    try {
        // Verify the token with Google
        const verificationResult = await verifyRecaptcha(token, clientIP);

        if (verificationResult.success) {
            const duration = Date.now() - startTime;
            console.log(`✅ CAPTCHA VERIFIED successfully in ${duration}ms`);
            console.log(`📊 Challenge timestamp: ${verificationResult.challenge_ts}`);
            console.log(`🌐 Hostname: ${verificationResult.hostname}`);

            // In production, you would proceed with authentication here
            // For FraudGuard®, this is where you'd:
            // 1. Create user session
            // 2. Log successful authentication
            // 3. Apply fraud detection rules
            // 4. Return JWT token or session cookie

            return res.json({
                success: true,
                message: 'CAPTCHA verified successfully',
                timestamp: new Date().toISOString(),
                duration_ms: duration
            });
        } else {
            // CAPTCHA verification failed
            const errors = verificationResult['error-codes'] || ['unknown-error'];
            console.warn(`⚠️ CAPTCHA verification failed:`, errors);

            // Increment fraud score for failed CAPTCHA
            await fraudScore.incrementScore(clientIP, 'FAILED_CAPTCHA');

            // Map Google error codes to user-friendly messages
            const errorMessages = {
                'missing-input-secret': 'Server configuration error',
                'invalid-input-secret': 'Server configuration error',
                'missing-input-response': 'Please complete the CAPTCHA',
                'invalid-input-response': 'CAPTCHA expired or invalid. Please try again.',
                'bad-request': 'Invalid request format',
                'timeout-or-duplicate': 'CAPTCHA expired. Please try again.'
            };

            const userMessage = errorMessages[errors[0]] || 'CAPTCHA verification failed';

            return res.status(400).json({
                success: false,
                errors: errors,
                message: userMessage
            });
        }
    } catch (error) {
        console.error('❌ CAPTCHA verification exception:', error);

        return res.status(500).json({
            success: false,
            errors: ['server-error'],
            message: 'An error occurred during verification. Please try again.'
        });
    }
});

/**
 * POST /api/login
 * Example protected endpoint that requires CAPTCHA verification
 * This demonstrates how to integrate CAPTCHA with your actual authentication flow
 */
app.post('/api/login', checkIPBlocking, async (req, res) => {
    const { username, password, 'g-recaptcha-response': captchaToken } = req.body;
    const clientIP = req.headers['x-forwarded-for'] || req.connection.remoteAddress;

    console.log(`\n🔐 Login attempt for user: ${username} from IP: ${clientIP}`);

    // Step 1: Verify CAPTCHA first (anti-bot protection)
    if (!captchaToken) {
        await fraudScore.incrementScore(clientIP, 'FAILED_CAPTCHA');
        return res.status(400).json({
            success: false,
            message: 'CAPTCHA verification required'
        });
    }

    try {
        const verificationResult = await verifyRecaptcha(captchaToken, clientIP);

        if (!verificationResult.success) {
            console.warn(`⚠️ Login blocked: CAPTCHA failed for ${username}`);
            await fraudScore.incrementScore(clientIP, 'FAILED_CAPTCHA');
            return res.status(400).json({
                success: false,
                message: 'CAPTCHA verification failed. Please try again.'
            });
        }

        console.log(`✅ CAPTCHA passed for ${username}`);

        // Step 2: Validate credentials (placeholder - implement your own logic)
        if (!username || !password) {
            return res.status(400).json({
                success: false,
                message: 'Username and password required'
            });
        }

        // Step 3: Here you would:
        // - Check credentials against database
        // - Apply FraudGuard® fraud detection rules
        // - Check for suspicious patterns (velocity checks, device fingerprinting, etc.)
        // - Create session/JWT token

        // For demo purposes, accept any credentials
        // In production, validate against database
        console.log(`✅ Login successful for ${username}`);

        // Generate a simple demo token
        const token = Buffer.from(`${username}:${Date.now()}`).toString('base64');

        res.json({
            success: true,
            message: 'Login successful',
            user: {
                username: username,
                email: username,
                loginTime: new Date().toISOString()
            },
            token: token
        });

    } catch (error) {
        console.error('❌ Login error:', error);
        res.status(500).json({
            success: false,
            message: 'An error occurred during login'
        });
    }
});

/**
 * POST /api/register
 * User registration endpoint with CAPTCHA protection
 */
app.post('/api/register', checkIPBlocking, async (req, res) => {
    const { name, email, password, 'g-recaptcha-response': captchaToken } = req.body;
    const clientIP = req.headers['x-forwarded-for'] || req.connection.remoteAddress;

    console.log(`\n📝 Registration attempt for: ${email} from IP: ${clientIP}`);

    // Step 1: Verify CAPTCHA first (anti-bot protection)
    if (!captchaToken) {
        await fraudScore.incrementScore(clientIP, 'FAILED_CAPTCHA');
        return res.status(400).json({
            success: false,
            message: 'CAPTCHA verification required'
        });
    }

    try {
        const verificationResult = await verifyRecaptcha(captchaToken, clientIP);

        if (!verificationResult.success) {
            console.warn(`⚠️ Registration blocked: CAPTCHA failed for ${email}`);
            await fraudScore.incrementScore(clientIP, 'FAILED_CAPTCHA');
            return res.status(400).json({
                success: false,
                message: 'CAPTCHA verification failed. Please try again.'
            });
        }

        console.log(`✅ CAPTCHA passed for registration: ${email}`);

        // Step 2: Validate input
        if (!name || !email || !password) {
            return res.status(400).json({
                success: false,
                message: 'All fields are required'
            });
        }

        // Validate email format
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            return res.status(400).json({
                success: false,
                message: 'Invalid email format'
            });
        }

        // Validate password length
        if (password.length < 6) {
            return res.status(400).json({
                success: false,
                message: 'Password must be at least 6 characters'
            });
        }

        // Step 3: Here you would:
        // - Check if email already exists in database
        // - Hash the password (bcrypt)
        // - Store user in database
        // - Send verification email
        // - Create session/JWT token

        // For demo purposes, accept registration
        console.log(`✅ Registration successful for ${email}`);

        // Generate a simple demo token
        const token = Buffer.from(`${email}:${Date.now()}`).toString('base64');

        res.json({
            success: true,
            message: 'Registration successful',
            user: {
                name: name,
                username: email,
                email: email,
                registeredAt: new Date().toISOString()
            },
            token: token
        });

    } catch (error) {
        console.error('❌ Registration error:', error);
        res.status(500).json({
            success: false,
            message: 'An error occurred during registration'
        });
    }
});

/**
 * GET /health
 * Health check endpoint for monitoring
 */
app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        service: 'FraudGuard® reCAPTCHA Service',
        timestamp: new Date().toISOString(),
        recaptcha_configured: !!(process.env.RECAPTCHA_SECRET && process.env.RECAPTCHA_SITE_KEY),
        redis: redis.getStatus()
    });
});

/**
 * Middleware: Admin authentication
 */
function authenticateAdmin(req, res, next) {
    const token = req.headers['x-admin-token'] || req.query.token;

    if (!token || token !== ADMIN_TOKEN) {
        return res.status(401).json({
            error: 'Unauthorized',
            message: 'Valid admin token required (X-Admin-Token header or ?token= query param)'
        });
    }

    next();
}

/**
 * Middleware: IP fraud blocking check
 */
async function checkIPBlocking(req, res, next) {
    const clientIP = req.headers['x-forwarded-for'] || req.connection.remoteAddress;

    const check = await fraudScore.checkRequest(clientIP);

    if (!check.allowed) {
        console.warn(`🚫 Request blocked from IP: ${clientIP} (Score: ${check.score})`);

        return res.status(403).json({
            blocked: true,
            reason: check.reason,
            score: check.score,
            expiresIn: check.expiresIn,
            message: 'Your IP has been temporarily blocked due to suspicious activity'
        });
    }

    // Attach fraud info to request for logging
    req.fraudCheck = check;

    next();
}

/**
 * GET /admin/fraud-stats
 * Get fraud statistics (JSON) - Admin only
 */
app.get('/admin/fraud-stats', authenticateAdmin, async (req, res) => {
    try {
        const allScores = await fraudScore.getAllScores();
        const stats = await fraudScore.getStats();

        res.json({
            success: true,
            stats: stats,
            activeIPs: allScores,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Error fetching fraud stats:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * GET /admin/dashboard
 * Admin dashboard HTML page
 */
app.get('/admin/dashboard', authenticateAdmin, (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'admin-dashboard.html'));
});

/**
 * POST /admin/unblock/:ip
 * Manually unblock an IP - Admin only
 */
app.post('/admin/unblock/:ip', authenticateAdmin, async (req, res) => {
    try {
        const ip = req.params.ip;
        const unblocked = await fraudScore.unblockIP(ip);

        if (unblocked) {
            res.json({
                success: true,
                message: `IP ${ip} has been unblocked`,
                ip: ip
            });
        } else {
            res.status(404).json({
                success: false,
                message: `IP ${ip} was not blocked`
            });
        }
    } catch (error) {
        console.error('Error unblocking IP:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * POST /admin/reset-score/:ip
 * Reset fraud score for an IP - Admin only
 */
app.post('/admin/reset-score/:ip', authenticateAdmin, async (req, res) => {
    try {
        const ip = req.params.ip;
        await fraudScore.resetScore(ip);

        res.json({
            success: true,
            message: `Fraud score reset for IP ${ip}`,
            ip: ip
        });
    } catch (error) {
        console.error('Error resetting score:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

/**
 * 404 handler
 */
app.use((req, res) => {
    res.status(404).json({
        error: 'Not Found',
        message: 'The requested endpoint does not exist'
    });
});

/**
 * Error handler
 */
app.use((err, req, res, next) => {
    console.error('💥 Unhandled error:', err);
    res.status(500).json({
        error: 'Internal Server Error',
        message: 'An unexpected error occurred'
    });
});

// Start server with Redis initialization
async function startServer() {
    // Initialize Redis connection
    console.log('🔌 Initializing Redis connection...');
    await redis.connect();

    // Start fraud score decay interval
    fraudScore.startScoreDecay();

    // Start HTTP server
    app.listen(PORT, () => {
        console.log('\n' + '🛡️'.repeat(30));
        console.log(`🚀 FraudGuard® reCAPTCHA + Fraud Prevention Service`);
        console.log(`📍 Server running on: http://localhost:${PORT}`);
        console.log(`🔐 Security: CAPTCHA verification active`);
        console.log(`📊 Fraud Scoring: ${redis.isRedisConnected() ? 'Redis' : 'In-Memory'}`);
        console.log(`⏰ Started at: ${new Date().toISOString()}`);
        console.log('🛡️'.repeat(30) + '\n');
        console.log('Public endpoints:');
        console.log(`  GET  /                    - Authentication page`);
        console.log(`  GET  /fraudguard.html     - FraudGuard login/register`);
        console.log(`  GET  /dashboard.html      - User dashboard (auth required)`);
        console.log(`  GET  /api/site-key        - Get public reCAPTCHA key`);
        console.log(`  POST /verify-captcha      - Verify CAPTCHA token`);
        console.log(`  POST /api/login           - Login with CAPTCHA`);
        console.log(`  POST /api/register        - Register new user`);
        console.log(`  GET  /health              - Health check`);
        console.log('\n Admin endpoints (require X-Admin-Token):');
        console.log(`  GET  /admin/fraud-stats      - Get fraud statistics (JSON)`);
        console.log(`  GET  /admin/dashboard?token=XXX - Admin dashboard (HTML)`);
        console.log(`  POST /admin/unblock/:ip      - Manually unblock an IP`);
        console.log(`  POST /admin/reset-score/:ip  - Reset fraud score for IP`);
        console.log('\n');
    });
}

// Start the server
startServer().catch(error => {
    console.error('💥 Fatal error starting server:', error);
    process.exit(1);
});

// Graceful shutdown
process.on('SIGTERM', async () => {
    console.log('📴 SIGTERM received, shutting down gracefully...');
    await redis.disconnect();
    process.exit(0);
});

process.on('SIGINT', async () => {
    console.log('\n📴 SIGINT received, shutting down gracefully...');
    await redis.disconnect();
    process.exit(0);
});
