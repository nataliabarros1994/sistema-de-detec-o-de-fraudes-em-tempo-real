/**
 * FraudGuard® Dashboard Router
 * SPA Navigation System with Dynamic Content Loading
 */

class DashboardRouter {
    constructor() {
        this.currentSection = 'overview';
        this.contentContainer = document.getElementById('mainContent');
        this.init();
    }

    init() {
        // Set up navigation event listeners
        this.setupNavigation();

        // Handle browser back/forward
        window.addEventListener('hashchange', () => this.handleRouteChange());

        // Load initial route
        this.handleRouteChange();
    }

    setupNavigation() {
        document.querySelectorAll('.sidebar-menu a:not([href^="http"])').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const hash = link.getAttribute('href');
                window.location.hash = hash;

                // Update active state
                document.querySelectorAll('.sidebar-menu a').forEach(a => a.classList.remove('active'));
                link.classList.add('active');
            });
        });
    }

    handleRouteChange() {
        const hash = window.location.hash.slice(1) || 'overview';
        this.loadSection(hash);
    }

    async loadSection(section) {
        this.showLoading();

        try {
            const content = this.getContent(section);
            await this.animateTransition(content);
            this.currentSection = section;
            this.updateTitle(section);

            // Initialize section-specific features
            this.initSectionFeatures(section);

        } catch (error) {
            console.error('Error loading section:', error);
            showToast('Error loading section', 'error');
        } finally {
            this.hideLoading();
        }
    }

    async animateTransition(newContent) {
        // Fade out
        this.contentContainer.style.opacity = '0';
        await this.delay(200);

        // Update content
        this.contentContainer.innerHTML = newContent;

        // Fade in
        this.contentContainer.style.opacity = '1';
        await this.delay(200);
    }

    getContent(section) {
        const sections = {
            overview: this.getOverviewContent(),
            analytics: this.getAnalyticsContent(),
            'ai-detection': this.getAIDetectionContent(),
            'risk-analysis': this.getRiskAnalysisContent(),
            alerts: this.getAlertsContent(),
            reports: this.getReportsContent(),
            settings: this.getSettingsContent()
        };

        return sections[section] || sections.overview;
    }

    getOverviewContent() {
        return `
            <!-- Stats Grid -->
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon primary">
                        <i class="fas fa-shield-check"></i>
                    </div>
                    <div class="stat-label">Protection Rate</div>
                    <div class="stat-value" id="protectionRate">99.8%</div>
                    <div class="stat-change positive">
                        <i class="fas fa-arrow-up"></i>
                        <span>2.1% from last week</span>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon success">
                        <i class="fas fa-check-circle"></i>
                    </div>
                    <div class="stat-label">Transactions Analyzed</div>
                    <div class="stat-value" id="transactionsCount">0</div>
                    <div class="stat-change positive">
                        <i class="fas fa-arrow-up"></i>
                        <span>18% increase</span>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon danger">
                        <i class="fas fa-ban"></i>
                    </div>
                    <div class="stat-label">Frauds Blocked</div>
                    <div class="stat-value" id="fraudsBlocked">0</div>
                    <div class="stat-change negative">
                        <i class="fas fa-arrow-down"></i>
                        <span>12% decrease</span>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon warning">
                        <i class="fas fa-exclamation-circle"></i>
                    </div>
                    <div class="stat-label">High Risk IPs</div>
                    <div class="stat-value" id="highRiskIPs">0</div>
                    <div class="stat-change positive">
                        <i class="fas fa-arrow-down"></i>
                        <span>5 less than yesterday</span>
                    </div>
                </div>

                <div class="stat-card">
                    <div class="stat-icon info">
                        <i class="fas fa-clock"></i>
                    </div>
                    <div class="stat-label">Avg Response Time</div>
                    <div class="stat-value">&lt;50ms</div>
                    <div class="stat-change positive">
                        <i class="fas fa-check"></i>
                        <span>Excellent performance</span>
                    </div>
                </div>
            </div>

            <!-- Charts Row -->
            <div class="row mb-4">
                <div class="col-md-8">
                    <div class="chart-card">
                        <h3><i class="fas fa-chart-area me-2"></i>Fraud Detection Trends (Last 7 Days)</h3>
                        <div class="chart-container">
                            <canvas id="trendsChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="chart-card">
                        <h3><i class="fas fa-chart-pie me-2"></i>Risk Distribution</h3>
                        <div class="chart-container">
                            <canvas id="riskChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Alerts and Activity Row -->
            <div class="row">
                <div class="col-md-8">
                    <div class="alerts-container">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h3 style="margin: 0;"><i class="fas fa-bell me-2"></i>Recent Alerts</h3>
                            <button class="btn-custom btn-outline-custom btn-sm" onclick="clearAlerts()">
                                <i class="fas fa-check me-1"></i>Mark All Read
                            </button>
                        </div>

                        <div id="alertsList">
                            <div class="alert-item critical">
                                <div class="alert-icon critical">
                                    <i class="fas fa-exclamation-triangle"></i>
                                </div>
                                <div class="alert-content">
                                    <div class="alert-title">Critical: Multiple Failed Login Attempts</div>
                                    <div class="alert-message">IP 192.168.1.100 attempted 5 failed logins in 2 minutes</div>
                                    <div class="alert-time">2 minutes ago</div>
                                    <div class="alert-actions">
                                        <button class="btn btn-sm btn-danger">Block IP</button>
                                        <button class="btn btn-sm btn-outline-secondary">View Details</button>
                                    </div>
                                </div>
                            </div>

                            <div class="alert-item warning">
                                <div class="alert-icon warning">
                                    <i class="fas fa-shield-alt"></i>
                                </div>
                                <div class="alert-content">
                                    <div class="alert-title">Warning: Unusual Pattern Detected</div>
                                    <div class="alert-message">Transaction velocity exceeded threshold for user ID 12345</div>
                                    <div class="alert-time">15 minutes ago</div>
                                    <div class="alert-actions">
                                        <button class="btn btn-sm btn-warning">Investigate</button>
                                        <button class="btn btn-sm btn-outline-secondary">Dismiss</button>
                                    </div>
                                </div>
                            </div>

                            <div class="alert-item info">
                                <div class="alert-icon info">
                                    <i class="fas fa-info-circle"></i>
                                </div>
                                <div class="alert-content">
                                    <div class="alert-title">Info: System Health Check</div>
                                    <div class="alert-message">All fraud detection models updated successfully</div>
                                    <div class="alert-time">1 hour ago</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="col-md-4">
                    <div class="chart-card">
                        <h3 style="margin-bottom: 1rem;"><i class="fas fa-history me-2"></i>Recent Activity</h3>
                        <ul class="activity-list">
                            <li class="activity-item">
                                <div class="activity-dot danger"></div>
                                <div class="activity-content">
                                    <div class="activity-title">IP Blocked</div>
                                    <div class="activity-time">2 minutes ago</div>
                                </div>
                            </li>
                            <li class="activity-item">
                                <div class="activity-dot success"></div>
                                <div class="activity-content">
                                    <div class="activity-title">Transaction Approved</div>
                                    <div class="activity-time">5 minutes ago</div>
                                </div>
                            </li>
                            <li class="activity-item">
                                <div class="activity-dot info"></div>
                                <div class="activity-content">
                                    <div class="activity-title">New User Registered</div>
                                    <div class="activity-time">12 minutes ago</div>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    getAnalyticsContent() {
        return `
            <div class="section-header mb-4">
                <h2><i class="fas fa-chart-line me-2"></i>Advanced Analytics</h2>
                <p>Detailed analysis and visualizations of fraud detection patterns</p>
            </div>

            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="chart-card">
                        <h3><i class="fas fa-chart-bar me-2"></i>Monthly Fraud Statistics</h3>
                        <div class="chart-container" style="height: 400px;">
                            <canvas id="monthlyChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="chart-card">
                        <h3><i class="fas fa-globe me-2"></i>Geographic Distribution</h3>
                        <div class="chart-container">
                            <canvas id="geoChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-card">
                        <h3><i class="fas fa-clock me-2"></i>Hourly Patterns</h3>
                        <div class="chart-container">
                            <canvas id="hourlyChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-12">
                    <div class="chart-card">
                        <h3><i class="fas fa-table me-2"></i>Top Blocked IPs</h3>
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>IP Address</th>
                                        <th>Country</th>
                                        <th>Attempts</th>
                                        <th>Last Seen</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>192.168.1.100</td>
                                        <td>🇺🇸 United States</td>
                                        <td><span class="badge bg-danger">47</span></td>
                                        <td>2 minutes ago</td>
                                        <td><button class="btn btn-sm btn-outline-primary">Details</button></td>
                                    </tr>
                                    <tr>
                                        <td>10.0.0.50</td>
                                        <td>🇧🇷 Brazil</td>
                                        <td><span class="badge bg-warning">23</span></td>
                                        <td>15 minutes ago</td>
                                        <td><button class="btn btn-sm btn-outline-primary">Details</button></td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getAIDetectionContent() {
        return `
            <div class="section-header mb-4">
                <h2><i class="fas fa-brain me-2"></i>AI Detection Models</h2>
                <p>Machine Learning models for real-time fraud detection</p>
            </div>

            <div class="row mb-4">
                <div class="col-md-4">
                    <div class="stat-card">
                        <div class="stat-icon primary">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="stat-label">Active Models</div>
                        <div class="stat-value">5</div>
                        <div class="stat-change positive">
                            <i class="fas fa-check"></i>
                            <span>All operational</span>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card">
                        <div class="stat-icon success">
                            <i class="fas fa-bullseye"></i>
                        </div>
                        <div class="stat-label">Model Accuracy</div>
                        <div class="stat-value">97.5%</div>
                        <div class="stat-change positive">
                            <i class="fas fa-arrow-up"></i>
                            <span>1.2% improvement</span>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="stat-card">
                        <div class="stat-icon info">
                            <i class="fas fa-sync-alt"></i>
                        </div>
                        <div class="stat-label">Last Training</div>
                        <div class="stat-value">2h ago</div>
                        <div class="stat-change positive">
                            <i class="fas fa-check"></i>
                            <span>Successful</span>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="chart-card">
                        <h3><i class="fas fa-project-diagram me-2"></i>Model Performance</h3>
                        <div class="alert alert-info">
                            <i class="fas fa-info-circle me-2"></i>
                            <strong>Current Model:</strong> Random Forest Classifier v3.2 |
                            <strong>Training Data:</strong> 1.2M transactions |
                            <strong>Precision:</strong> 96.8% |
                            <strong>Recall:</strong> 94.2%
                        </div>
                        <div class="chart-container" style="height: 300px;">
                            <canvas id="modelPerformanceChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-6">
                    <div class="chart-card">
                        <h3><i class="fas fa-layer-group me-2"></i>Feature Importance</h3>
                        <div class="chart-container">
                            <canvas id="featureChart"></canvas>
                        </div>
                    </div>
                </div>
                <div class="col-md-6">
                    <div class="chart-card">
                        <h3><i class="fas fa-cogs me-2"></i>Model Configuration</h3>
                        <div class="list-group">
                            <div class="list-group-item">
                                <strong>Algorithm:</strong> Random Forest
                                <span class="badge bg-success float-end">Active</span>
                            </div>
                            <div class="list-group-item">
                                <strong>Features:</strong> 47 behavioral patterns
                            </div>
                            <div class="list-group-item">
                                <strong>Update Frequency:</strong> Every 6 hours
                            </div>
                            <div class="list-group-item">
                                <strong>Threshold:</strong> 0.75 probability
                            </div>
                        </div>
                        <button class="btn btn-primary mt-3 w-100">
                            <i class="fas fa-sync-alt me-2"></i>Retrain Model
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    getRiskAnalysisContent() {
        return `
            <div class="section-header mb-4">
                <h2><i class="fas fa-exclamation-triangle me-2"></i>Risk Analysis</h2>
                <p>Comprehensive risk assessment and scoring system</p>
            </div>

            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="chart-card">
                        <h3><i class="fas fa-sliders-h me-2"></i>Risk Score Configuration</h3>
                        <div class="row">
                            <div class="col-md-6">
                                <label class="form-label">Auto-Block Threshold</label>
                                <input type="range" class="form-range" min="50" max="150" value="100" id="thresholdSlider">
                                <div class="d-flex justify-content-between">
                                    <small>Low (50)</small>
                                    <strong id="thresholdValue">100</strong>
                                    <small>High (150)</small>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <label class="form-label">Block Duration (minutes)</label>
                                <input type="range" class="form-range" min="5" max="60" value="15" id="durationSlider">
                                <div class="d-flex justify-content-between">
                                    <small>5 min</small>
                                    <strong id="durationValue">15</strong>
                                    <small>60 min</small>
                                </div>
                            </div>
                        </div>
                        <button class="btn btn-success mt-3">
                            <i class="fas fa-save me-2"></i>Save Configuration
                        </button>
                    </div>
                </div>
            </div>

            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="chart-card">
                        <h3><i class="fas fa-chart-line me-2"></i>Risk Score Distribution</h3>
                        <div class="chart-container" style="height: 350px;">
                            <canvas id="riskDistributionChart"></canvas>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-12">
                    <div class="chart-card">
                        <h3><i class="fas fa-list me-2"></i>Current High-Risk Transactions</h3>
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Transaction ID</th>
                                        <th>User</th>
                                        <th>Risk Score</th>
                                        <th>Reason</th>
                                        <th>Time</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td>#TX-10234</td>
                                        <td>user@example.com</td>
                                        <td><span class="badge bg-danger">92</span></td>
                                        <td>Velocity exceeded</td>
                                        <td>2 min ago</td>
                                        <td>
                                            <button class="btn btn-sm btn-danger">Block</button>
                                            <button class="btn btn-sm btn-success">Approve</button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getAlertsContent() {
        return `
            <div class="section-header mb-4">
                <h2><i class="fas fa-bell me-2"></i>Alert Center</h2>
                <p>Manage and configure system alerts and notifications</p>
            </div>

            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="chart-card">
                        <div class="d-flex justify-content-between align-items-center mb-3">
                            <h3 style="margin: 0;"><i class="fas fa-filter me-2"></i>Alert Filters</h3>
                            <div class="btn-group">
                                <button class="btn btn-sm btn-outline-danger">Critical</button>
                                <button class="btn btn-sm btn-outline-warning">Warning</button>
                                <button class="btn btn-sm btn-outline-info active">All</button>
                            </div>
                        </div>

                        <div class="alert-item critical">
                            <div class="alert-icon critical">
                                <i class="fas fa-exclamation-triangle"></i>
                            </div>
                            <div class="alert-content">
                                <div class="alert-title">Critical: Brute Force Attack Detected</div>
                                <div class="alert-message">Multiple IPs (192.168.1.x) performing coordinated login attempts</div>
                                <div class="alert-time">Just now</div>
                                <div class="alert-actions">
                                    <button class="btn btn-sm btn-danger">Block Range</button>
                                    <button class="btn btn-sm btn-outline-secondary">Details</button>
                                    <button class="btn btn-sm btn-outline-secondary">Dismiss</button>
                                </div>
                            </div>
                        </div>

                        <div class="alert-item warning">
                            <div class="alert-icon warning">
                                <i class="fas fa-shield-alt"></i>
                            </div>
                            <div class="alert-content">
                                <div class="alert-title">Warning: High Transaction Volume</div>
                                <div class="alert-message">User ID 45678 has made 15 transactions in 10 minutes</div>
                                <div class="alert-time">5 minutes ago</div>
                                <div class="alert-actions">
                                    <button class="btn btn-sm btn-warning">Investigate</button>
                                    <button class="btn btn-sm btn-outline-secondary">Dismiss</button>
                                </div>
                            </div>
                        </div>

                        <div class="alert-item info">
                            <div class="alert-icon info">
                                <i class="fas fa-info-circle"></i>
                            </div>
                            <div class="alert-content">
                                <div class="alert-title">Info: Scheduled Maintenance</div>
                                <div class="alert-message">System will undergo maintenance tonight at 2 AM UTC</div>
                                <div class="alert-time">1 hour ago</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-12">
                    <div class="chart-card">
                        <h3><i class="fas fa-cog me-2"></i>Alert Settings</h3>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="emailAlerts" checked>
                            <label class="form-check-label" for="emailAlerts">
                                <strong>Email Notifications</strong> - Receive alerts via email
                            </label>
                        </div>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="smsAlerts">
                            <label class="form-check-label" for="smsAlerts">
                                <strong>SMS Notifications</strong> - Receive critical alerts via SMS
                            </label>
                        </div>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="slackAlerts" checked>
                            <label class="form-check-label" for="slackAlerts">
                                <strong>Slack Integration</strong> - Post alerts to Slack channel
                            </label>
                        </div>
                        <button class="btn btn-success">
                            <i class="fas fa-save me-2"></i>Save Preferences
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    getReportsContent() {
        return `
            <div class="section-header mb-4">
                <h2><i class="fas fa-file-alt me-2"></i>Reports & Export</h2>
                <p>Generate and download detailed fraud detection reports</p>
            </div>

            <div class="row mb-4">
                <div class="col-md-12">
                    <div class="chart-card">
                        <h3><i class="fas fa-file-download me-2"></i>Generate New Report</h3>
                        <div class="row">
                            <div class="col-md-4">
                                <label class="form-label">Report Type</label>
                                <select class="form-select">
                                    <option>Daily Summary</option>
                                    <option>Weekly Analysis</option>
                                    <option>Monthly Report</option>
                                    <option>Custom Range</option>
                                </select>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">Format</label>
                                <select class="form-select">
                                    <option>PDF</option>
                                    <option>Excel (XLSX)</option>
                                    <option>CSV</option>
                                    <option>JSON</option>
                                </select>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">&nbsp;</label>
                                <button class="btn btn-primary w-100">
                                    <i class="fas fa-file-export me-2"></i>Generate Report
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-12">
                    <div class="chart-card">
                        <h3><i class="fas fa-history me-2"></i>Recent Reports</h3>
                        <div class="table-responsive">
                            <table class="table table-hover">
                                <thead>
                                    <tr>
                                        <th>Report Name</th>
                                        <th>Type</th>
                                        <th>Generated</th>
                                        <th>Size</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr>
                                        <td><i class="fas fa-file-pdf text-danger me-2"></i>Fraud Report - Jan 2025</td>
                                        <td>Monthly</td>
                                        <td>2 hours ago</td>
                                        <td>2.4 MB</td>
                                        <td>
                                            <button class="btn btn-sm btn-outline-primary">
                                                <i class="fas fa-download"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td><i class="fas fa-file-excel text-success me-2"></i>Transaction Log - Week 3</td>
                                        <td>Weekly</td>
                                        <td>1 day ago</td>
                                        <td>1.8 MB</td>
                                        <td>
                                            <button class="btn btn-sm btn-outline-primary">
                                                <i class="fas fa-download"></i>
                                            </button>
                                            <button class="btn btn-sm btn-outline-danger">
                                                <i class="fas fa-trash"></i>
                                            </button>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    getSettingsContent() {
        return `
            <div class="section-header mb-4">
                <h2><i class="fas fa-cog me-2"></i>System Settings</h2>
                <p>Configure FraudGuard® detection parameters</p>
            </div>

            <div class="row mb-4">
                <div class="col-md-6">
                    <div class="chart-card">
                        <h3><i class="fas fa-shield-alt me-2"></i>Detection Settings</h3>
                        <div class="mb-3">
                            <label class="form-label">Auto-Block Threshold</label>
                            <input type="number" class="form-control" value="100">
                            <small class="form-text text-muted">Points required for automatic IP blocking</small>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Block Duration (seconds)</label>
                            <input type="number" class="form-control" value="900">
                            <small class="form-text text-muted">How long IPs remain blocked (900 = 15 min)</small>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Score Decay Interval (seconds)</label>
                            <input type="number" class="form-control" value="3600">
                            <small class="form-text text-muted">Time between score decreases (3600 = 1 hour)</small>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Score Decay Amount</label>
                            <input type="number" class="form-control" value="10">
                            <small class="form-text text-muted">Points to decrease per decay interval</small>
                        </div>
                    </div>
                </div>

                <div class="col-md-6">
                    <div class="chart-card">
                        <h3><i class="fas fa-bell me-2"></i>Notification Settings</h3>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="setting1" checked>
                            <label class="form-check-label" for="setting1">
                                Enable Email Notifications
                            </label>
                        </div>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="setting2" checked>
                            <label class="form-check-label" for="setting2">
                                Enable Real-time Alerts
                            </label>
                        </div>
                        <div class="form-check form-switch mb-3">
                            <input class="form-check-input" type="checkbox" id="setting3">
                            <label class="form-check-label" for="setting3">
                                Enable SMS Alerts (Critical Only)
                            </label>
                        </div>
                        <div class="mb-3 mt-4">
                            <label class="form-label">Admin Email</label>
                            <input type="email" class="form-control" value="admin@fraudguard.com">
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Alert Webhook URL</label>
                            <input type="url" class="form-control" placeholder="https://hooks.slack.com/...">
                        </div>
                    </div>
                </div>
            </div>

            <div class="row">
                <div class="col-md-12">
                    <div class="chart-card">
                        <h3><i class="fas fa-database me-2"></i>Redis Configuration</h3>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Redis URL</label>
                                    <input type="text" class="form-control" value="redis://localhost:6379" readonly>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Connection Status</label>
                                    <div class="form-control" style="background: #d4edda;">
                                        <i class="fas fa-check-circle text-success me-2"></i>Connected
                                    </div>
                                </div>
                            </div>
                        </div>
                        <button class="btn btn-success me-2">
                            <i class="fas fa-save me-2"></i>Save All Settings
                        </button>
                        <button class="btn btn-outline-secondary">
                            <i class="fas fa-undo me-2"></i>Reset to Defaults
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    initSectionFeatures(section) {
        switch(section) {
            case 'overview':
                this.initOverview();
                break;
            case 'analytics':
                this.initAnalytics();
                break;
            case 'ai-detection':
                this.initAIDetection();
                break;
            case 'risk-analysis':
                this.initRiskAnalysis();
                break;
            case 'settings':
                this.initSettings();
                break;
        }
    }

    initOverview() {
        // Initialize charts
        if (typeof Chart !== 'undefined') {
            setTimeout(() => {
                const trendsCanvas = document.getElementById('trendsChart');
                const riskCanvas = document.getElementById('riskChart');

                if (trendsCanvas) {
                    const trendsCtx = trendsCanvas.getContext('2d');
                    new Chart(trendsCtx, {
                        type: 'line',
                        data: {
                            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                            datasets: [{
                                label: 'Frauds Detected',
                                data: [12, 19, 8, 15, 23, 18, 23],
                                borderColor: '#fc8181',
                                backgroundColor: 'rgba(252, 129, 129, 0.1)',
                                tension: 0.4,
                                fill: true
                            }, {
                                label: 'Transactions',
                                data: [150, 180, 165, 190, 210, 195, 220],
                                borderColor: '#667eea',
                                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                                tension: 0.4,
                                fill: true
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false
                        }
                    });
                }

                if (riskCanvas) {
                    const riskCtx = riskCanvas.getContext('2d');
                    new Chart(riskCtx, {
                        type: 'doughnut',
                        data: {
                            labels: ['Low Risk', 'Medium Risk', 'High Risk'],
                            datasets: [{
                                data: [65, 25, 10],
                                backgroundColor: ['#48bb78', '#f6ad55', '#fc8181']
                            }]
                        },
                        options: {
                            responsive: true,
                            maintainAspectRatio: false
                        }
                    });
                }
            }, 100);
        }

        // Animate counters
        this.animateCounters();
    }

    initAnalytics() {
        // Initialize analytics charts
        showToast('Analytics data loaded', 'success');
    }

    initAIDetection() {
        showToast('AI detection models loaded', 'success');
    }

    initRiskAnalysis() {
        // Initialize sliders
        const thresholdSlider = document.getElementById('thresholdSlider');
        const durationSlider = document.getElementById('durationSlider');

        if (thresholdSlider) {
            thresholdSlider.addEventListener('input', (e) => {
                document.getElementById('thresholdValue').textContent = e.target.value;
            });
        }

        if (durationSlider) {
            durationSlider.addEventListener('input', (e) => {
                document.getElementById('durationValue').textContent = e.target.value;
            });
        }
    }

    initSettings() {
        showToast('Settings loaded', 'info');
    }

    animateCounters() {
        const counters = [
            { id: 'transactionsCount', target: 1247 },
            { id: 'fraudsBlocked', target: 23 },
            { id: 'highRiskIPs', target: 7 }
        ];

        counters.forEach(({ id, target }) => {
            const element = document.getElementById(id);
            if (!element) return;

            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {
                current += increment;
                if (current >= target) {
                    element.textContent = target.toLocaleString();
                    clearInterval(timer);
                } else {
                    element.textContent = Math.floor(current).toLocaleString();
                }
            }, 20);
        });
    }

    updateTitle(section) {
        const titles = {
            'overview': 'Dashboard',
            'analytics': 'Analytics',
            'ai-detection': 'AI Detection',
            'risk-analysis': 'Risk Analysis',
            'alerts': 'Alerts',
            'reports': 'Reports',
            'settings': 'Settings'
        };

        const titleElement = document.querySelector('.top-bar h1');
        if (titleElement) {
            titleElement.textContent = titles[section] || 'Dashboard';
        }
    }

    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.classList.add('active');
    }

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.classList.remove('active');
    }

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Initialize router when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.dashboardRouter = new DashboardRouter();
    });
} else {
    window.dashboardRouter = new DashboardRouter();
}
