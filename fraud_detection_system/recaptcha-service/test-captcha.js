/**
 * FraudGuard® reCAPTCHA Service - Test Script
 *
 * This script tests various CAPTCHA verification scenarios
 * Run: node test-captcha.js
 */

const fetch = require('node-fetch');

const BASE_URL = 'http://localhost:3000';

// ANSI color codes for terminal output
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  red: '\x1b[31m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m'
};

function log(color, message) {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

function logTest(name) {
  console.log(`\n${colors.cyan}${'='.repeat(60)}${colors.reset}`);
  console.log(`${colors.blue}📝 Test: ${name}${colors.reset}`);
  console.log(`${colors.cyan}${'='.repeat(60)}${colors.reset}`);
}

async function testHealthCheck() {
  logTest('Health Check');

  try {
    const response = await fetch(`${BASE_URL}/health`);
    const data = await response.json();

    if (response.status === 200 && data.status === 'healthy') {
      log('green', '✅ PASS: Service is healthy');
      console.log(JSON.stringify(data, null, 2));
    } else {
      log('red', '❌ FAIL: Service is not healthy');
      console.log(JSON.stringify(data, null, 2));
    }
  } catch (error) {
    log('red', `❌ FAIL: Cannot connect to server - ${error.message}`);
    log('yellow', '💡 Make sure the server is running: npm start');
    process.exit(1);
  }
}

async function testMissingToken() {
  logTest('Missing CAPTCHA Token');

  try {
    const response = await fetch(`${BASE_URL}/verify-captcha`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });

    const data = await response.json();

    if (response.status === 400 && data.errors.includes('missing-input-response')) {
      log('green', '✅ PASS: Correctly rejected missing token');
      console.log(JSON.stringify(data, null, 2));
    } else {
      log('red', '❌ FAIL: Should reject missing token with 400');
      console.log(JSON.stringify(data, null, 2));
    }
  } catch (error) {
    log('red', `❌ FAIL: ${error.message}`);
  }
}

async function testInvalidToken() {
  logTest('Invalid CAPTCHA Token');

  try {
    const response = await fetch(`${BASE_URL}/verify-captcha`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        'g-recaptcha-response': 'invalid_token_12345',
        'username': 'test@example.com',
        'action': 'test'
      })
    });

    const data = await response.json();

    if (response.status === 400 && !data.success) {
      log('green', '✅ PASS: Correctly rejected invalid token');
      console.log(JSON.stringify(data, null, 2));
    } else {
      log('red', '❌ FAIL: Should reject invalid token');
      console.log(JSON.stringify(data, null, 2));
    }
  } catch (error) {
    log('red', `❌ FAIL: ${error.message}`);
  }
}

async function testShortToken() {
  logTest('Short/Malformed Token');

  try {
    const response = await fetch(`${BASE_URL}/verify-captcha`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        'g-recaptcha-response': 'abc'
      })
    });

    const data = await response.json();

    if (response.status === 400 && data.errors.includes('invalid-input-response')) {
      log('green', '✅ PASS: Correctly rejected malformed token');
      console.log(JSON.stringify(data, null, 2));
    } else {
      log('red', '❌ FAIL: Should reject malformed token');
      console.log(JSON.stringify(data, null, 2));
    }
  } catch (error) {
    log('red', `❌ FAIL: ${error.message}`);
  }
}

async function testSiteKeyEndpoint() {
  logTest('Site Key Retrieval');

  try {
    const response = await fetch(`${BASE_URL}/api/site-key`);
    const data = await response.json();

    if (response.status === 200 && data.siteKey && data.version) {
      log('green', '✅ PASS: Site key endpoint working');
      console.log(JSON.stringify(data, null, 2));
    } else {
      log('red', '❌ FAIL: Site key endpoint failed');
      console.log(JSON.stringify(data, null, 2));
    }
  } catch (error) {
    log('red', `❌ FAIL: ${error.message}`);
  }
}

async function testLoginWithoutCaptcha() {
  logTest('Login Without CAPTCHA');

  try {
    const response = await fetch(`${BASE_URL}/api/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: 'test@example.com',
        password: 'password123'
      })
    });

    const data = await response.json();

    if (response.status === 400 && !data.success) {
      log('green', '✅ PASS: Login correctly requires CAPTCHA');
      console.log(JSON.stringify(data, null, 2));
    } else {
      log('red', '❌ FAIL: Login should require CAPTCHA');
      console.log(JSON.stringify(data, null, 2));
    }
  } catch (error) {
    log('red', `❌ FAIL: ${error.message}`);
  }
}

async function testRootEndpoint() {
  logTest('Root Endpoint (HTML Page)');

  try {
    const response = await fetch(`${BASE_URL}/`);
    const html = await response.text();

    if (response.status === 200 && html.includes('FraudGuard') && html.includes('recaptcha')) {
      log('green', '✅ PASS: HTML page served correctly');
      log('cyan', `📄 Page length: ${html.length} bytes`);
      log('cyan', '🔍 Contains "FraudGuard": Yes');
      log('cyan', '🔍 Contains "recaptcha": Yes');
    } else {
      log('red', '❌ FAIL: HTML page not served correctly');
    }
  } catch (error) {
    log('red', `❌ FAIL: ${error.message}`);
  }
}

async function testNotFoundEndpoint() {
  logTest('404 Not Found');

  try {
    const response = await fetch(`${BASE_URL}/nonexistent-endpoint`);
    const data = await response.json();

    if (response.status === 404) {
      log('green', '✅ PASS: 404 handled correctly');
      console.log(JSON.stringify(data, null, 2));
    } else {
      log('red', '❌ FAIL: Should return 404');
      console.log(JSON.stringify(data, null, 2));
    }
  } catch (error) {
    log('red', `❌ FAIL: ${error.message}`);
  }
}

// Main test runner
async function runAllTests() {
  console.log('\n');
  log('blue', '🛡️'.repeat(30));
  log('blue', '🚀 FraudGuard® reCAPTCHA Service - Test Suite');
  log('blue', '🛡️'.repeat(30));
  console.log('\n');

  const tests = [
    testHealthCheck,
    testSiteKeyEndpoint,
    testRootEndpoint,
    testMissingToken,
    testInvalidToken,
    testShortToken,
    testLoginWithoutCaptcha,
    testNotFoundEndpoint
  ];

  let passed = 0;
  let failed = 0;

  for (const test of tests) {
    try {
      await test();
      passed++;
    } catch (error) {
      log('red', `❌ Test failed: ${error.message}`);
      failed++;
    }
    await new Promise(resolve => setTimeout(resolve, 500)); // Delay between tests
  }

  // Summary
  console.log('\n');
  log('cyan', '='.repeat(60));
  log('blue', '📊 Test Summary');
  log('cyan', '='.repeat(60));
  log('green', `✅ Passed: ${passed}`);
  log('red', `❌ Failed: ${failed}`);
  log('cyan', `📝 Total: ${passed + failed}`);
  log('cyan', '='.repeat(60));
  console.log('\n');

  // Manual test instructions
  log('yellow', '📌 Manual Test Required:');
  log('yellow', '   To test with a REAL valid CAPTCHA token:');
  log('yellow', '   1. Open http://localhost:3000 in a browser');
  log('yellow', '   2. Open DevTools → Network tab');
  log('yellow', '   3. Fill the form and complete CAPTCHA');
  log('yellow', '   4. Click "Sign In Securely"');
  log('yellow', '   5. Check the Network request for "g-recaptcha-response"');
  log('yellow', '   6. Verify the response shows success: true');
  console.log('\n');

  process.exit(failed > 0 ? 1 : 0);
}

// Run tests
runAllTests().catch(error => {
  log('red', `💥 Fatal error: ${error.message}`);
  process.exit(1);
});
