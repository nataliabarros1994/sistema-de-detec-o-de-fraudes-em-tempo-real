/**
 * FraudGuard® - Fraud Scoring Test Script
 *
 * This script simulates fraud events and tests the fraud scoring system
 * Run: node test-fraud-scoring.js
 */

const fetch = require('node-fetch');

const BASE_URL = 'http://localhost:3000';
const ADMIN_TOKEN = process.env.ADMIN_TOKEN || 'admin-secret-token';

// Colors for terminal output
const colors = {
    reset: '\x1b[0m',
    green: '\x1b[32m',
    red: '\x1b[31m',
    yellow: '\x1b[33m',
    blue: '\x1b[34m',
    cyan: '\x1b[36m',
    magenta: '\x1b[35m'
};

function log(color, message) {
    console.log(`${colors[color]}${message}${colors.reset}`);
}

function logTest(name) {
    console.log(`\n${colors.cyan}${'='.repeat(70)}${colors.reset}`);
    console.log(`${colors.blue}🧪 Test: ${name}${colors.reset}`);
    console.log(`${colors.cyan}${'='.repeat(70)}${colors.reset}`);
}

// Simulated delay
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Test 1: Simulate failed CAPTCHA attempts (should increase fraud score)
 */
async function testFailedCAPTCHA() {
    logTest('Failed CAPTCHA Attempts');

    const testIP = '192.168.1.100';

    log('cyan', `Testing IP: ${testIP}`);
    log('cyan', 'Simulating 3 failed CAPTCHA attempts...\n');

    for (let i = 1; i <= 3; i++) {
        try {
            const response = await fetch(`${BASE_URL}/verify-captcha`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Forwarded-For': testIP
                },
                body: JSON.stringify({
                    'g-recaptcha-response': 'invalid_token_test',
                    'username': 'test@example.com',
                    'action': 'test'
                })
            });

            const data = await response.json();

            if (!data.success) {
                log('yellow', `  Attempt ${i}/3: CAPTCHA failed (expected)`);
                log('cyan', `  → Fraud score should have increased by ~25 points`);
            }

            await delay(500);
        } catch (error) {
            log('red', `  Error on attempt ${i}: ${error.message}`);
        }
    }

    log('green', '\n✅ Test complete. Checking fraud score...');

    // Check fraud stats
    await delay(1000);
    await checkIPScore(testIP);
}

/**
 * Test 2: Test IP blocking (score exceeds threshold)
 */
async function testIPBlocking() {
    logTest('IP Blocking Test');

    const testIP = '10.0.0.50';

    log('cyan', `Testing IP: ${testIP}`);
    log('cyan', 'Simulating 5 failed CAPTCHA attempts (should trigger block)...\n');

    for (let i = 1; i <= 5; i++) {
        try {
            const response = await fetch(`${BASE_URL}/verify-captcha`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Forwarded-For': testIP
                },
                body: JSON.stringify({
                    'g-recaptcha-response': '', // Empty token
                    'action': 'test'
                })
            });

            const data = await response.json();

            if (data.blocked) {
                log('yellow', `  Attempt ${i}/5: IP BLOCKED (threshold exceeded)`);
                break;
            } else {
                log('yellow', `  Attempt ${i}/5: CAPTCHA failed`);
            }

            await delay(500);
        } catch (error) {
            log('red', `  Error: ${error.message}`);
        }
    }

    log('green', '\n✅ Block test complete. Checking IP status...');
    await delay(1000);
    await checkIPScore(testIP);
}

/**
 * Test 3: Check admin dashboard endpoint
 */
async function testAdminDashboard() {
    logTest('Admin Dashboard Endpoint');

    try {
        log('cyan', 'Fetching fraud statistics from admin endpoint...\n');

        const response = await fetch(`${BASE_URL}/admin/fraud-stats`, {
            headers: {
                'X-Admin-Token': ADMIN_TOKEN
            }
        });

        if (!response.ok) {
            if (response.status === 401) {
                log('red', '❌ FAIL: Admin token invalid or missing');
                log('yellow', '💡 Set ADMIN_TOKEN environment variable or update server .env');
                return;
            }
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (data.success) {
            log('green', '✅ Admin endpoint accessible\n');

            // Display stats
            log('blue', '📊 Current Statistics:');
            console.log(`  Total IPs: ${data.stats.totalIPs}`);
            console.log(`  Active IPs: ${data.stats.activeCount}`);
            console.log(`  Blocked IPs: ${data.stats.blockedCount}`);
            console.log(`  High Risk IPs: ${data.stats.highRiskCount}`);
            console.log(`  Average Score: ${data.stats.averageScore}`);
            console.log(`  Block Threshold: ${data.stats.threshold}`);
            console.log(`  Redis Status: ${data.stats.redisStatus.mode}`);

            if (data.activeIPs.length > 0) {
                log('blue', '\n📋 Top 5 IPs by Score:');
                data.activeIPs.slice(0, 5).forEach((ip, index) => {
                    const status = ip.blocked ? '🚫 BLOCKED' : '✅ Active';
                    console.log(`  ${index + 1}. ${ip.ip}: ${ip.score} points (${status})`);
                });
            }
        }
    } catch (error) {
        log('red', `❌ FAIL: ${error.message}`);
    }
}

/**
 * Test 4: Test manual unblock
 */
async function testManualUnblock() {
    logTest('Manual IP Unblock');

    const testIP = '10.0.0.50'; // Previously blocked IP

    try {
        log('cyan', `Attempting to unblock IP: ${testIP}\n`);

        const response = await fetch(`${BASE_URL}/admin/unblock/${testIP}`, {
            method: 'POST',
            headers: {
                'X-Admin-Token': ADMIN_TOKEN
            }
        });

        const data = await response.json();

        if (data.success) {
            log('green', `✅ IP ${testIP} has been unblocked`);
        } else {
            log('yellow', `⚠️ ${data.message}`);
        }

        await delay(500);
        await checkIPScore(testIP);
    } catch (error) {
        log('red', `❌ Error: ${error.message}`);
    }
}

/**
 * Test 5: Test score reset
 */
async function testScoreReset() {
    logTest('Score Reset');

    const testIP = '192.168.1.100';

    try {
        log('cyan', `Resetting fraud score for IP: ${testIP}\n`);

        const response = await fetch(`${BASE_URL}/admin/reset-score/${testIP}`, {
            method: 'POST',
            headers: {
                'X-Admin-Token': ADMIN_TOKEN
            }
        });

        const data = await response.json();

        if (data.success) {
            log('green', `✅ Fraud score reset for IP ${testIP}`);
        } else {
            log('red', `❌ ${data.message}`);
        }

        await delay(500);
        await checkIPScore(testIP);
    } catch (error) {
        log('red', `❌ Error: ${error.message}`);
    }
}

/**
 * Helper: Check fraud score for an IP
 */
async function checkIPScore(ip) {
    try {
        const response = await fetch(`${BASE_URL}/admin/fraud-stats`, {
            headers: {
                'X-Admin-Token': ADMIN_TOKEN
            }
        });

        if (!response.ok) {
            log('red', '❌ Cannot fetch IP score (admin endpoint not accessible)');
            return;
        }

        const data = await response.json();
        const ipData = data.activeIPs.find(item => item.ip === ip);

        if (ipData) {
            log('blue', `\n📊 IP Status for ${ip}:`);
            console.log(`  Fraud Score: ${ipData.score}`);
            console.log(`  Status: ${ipData.blocked ? '🚫 BLOCKED' : '✅ Active'}`);

            if (ipData.blocked && ipData.blockDetails) {
                console.log(`  Block Reason: ${ipData.blockDetails.reason}`);
                console.log(`  Expires In: ${ipData.blockDetails.expiresIn}`);
            }
        } else {
            log('yellow', `⚠️ No fraud score data found for IP ${ip}`);
        }
    } catch (error) {
        log('red', `❌ Error checking score: ${error.message}`);
    }
}

/**
 * Main test runner
 */
async function runAllTests() {
    console.log('\n');
    log('magenta', '🛡️'.repeat(35));
    log('magenta', '🚀 FraudGuard® Fraud Scoring Test Suite');
    log('magenta', '🛡️'.repeat(35));
    console.log('\n');

    // Check if server is running
    try {
        const response = await fetch(`${BASE_URL}/health`);
        if (!response.ok) {
            throw new Error('Server not healthy');
        }
        log('green', '✅ Server is running and healthy\n');
    } catch (error) {
        log('red', '❌ Cannot connect to server');
        log('yellow', '💡 Make sure the server is running: npm start');
        process.exit(1);
    }

    const tests = [
        { name: 'Failed CAPTCHA', fn: testFailedCAPTCHA },
        { name: 'IP Blocking', fn: testIPBlocking },
        { name: 'Admin Dashboard', fn: testAdminDashboard },
        { name: 'Manual Unblock', fn: testManualUnblock },
        { name: 'Score Reset', fn: testScoreReset }
    ];

    for (const test of tests) {
        try {
            await test.fn();
            await delay(2000); // Wait between tests
        } catch (error) {
            log('red', `❌ Test "${test.name}" failed: ${error.message}`);
        }
    }

    // Final summary
    console.log('\n');
    log('cyan', '='.repeat(70));
    log('blue', '📊 Test Summary');
    log('cyan', '='.repeat(70));
    log('green', `✅ All fraud scoring tests completed`);
    log('yellow', '\n💡 To view the admin dashboard, visit:');
    log('cyan', `   http://localhost:3000/admin/dashboard?token=${ADMIN_TOKEN}`);
    console.log('\n');

    process.exit(0);
}

// Run tests
runAllTests().catch(error => {
    log('red', `💥 Fatal error: ${error.message}`);
    process.exit(1);
});
