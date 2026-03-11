// helper to fetch stats and update cards
async function loadStats() {
    try {
        const resp = await fetch("http://localhost:5001/stats");
        const data = await resp.json();
        document.getElementById("totalCount").textContent = data.total_transactions;
        document.getElementById("lowCount").textContent = data.safe_transactions - data.fraud_transactions;
        document.getElementById("mediumCount").textContent = 0; // we don't track separately
        document.getElementById("highCount").textContent = data.fraud_transactions;
    } catch (err) {
        console.error("Failed to load stats", err);
    }
}

// draw charts given formatted transactions
let pieChart, barChart, lineChart;
function updateCharts(formatted) {
    const total = formatted.length;
    const high = formatted.filter(t => t.risk_level === "HIGH").length;
    const low = total - high;
    const levelCounts = {
        LOW: low,
        MEDIUM: formatted.filter(t=>t.risk_level==="MEDIUM").length,
        HIGH: high
    };
    // pie
    const pieCtx = document.getElementById('pieChart').getContext('2d');
    if (pieChart) pieChart.destroy();
    pieChart = new Chart(pieCtx, {
        type: 'pie',
        data: {
            labels: ['Safe', 'Fraud'],
            datasets: [{
                data: [low, high],
                backgroundColor: ['#00e676', '#ff5252']
            }]
        }
    });
    // bar
    const barCtx = document.getElementById('barChart').getContext('2d');
    if (barChart) barChart.destroy();
    barChart = new Chart(barCtx, {
        type: 'bar',
        data: {
            labels: ['LOW','MEDIUM','HIGH'],
            datasets: [{
                label: 'Risk Levels',
                data: [levelCounts.LOW, levelCounts.MEDIUM, levelCounts.HIGH],
                backgroundColor: ['#00e676','#ffca28','#ff5252']
            }]
        }
    });
    // line: transactions over time
    const times = formatted.map(t=>new Date(t.timestamp));
    times.sort((a,b)=>a-b);
    const lineCtx = document.getElementById('lineChart').getContext('2d');
    if (lineChart) lineChart.destroy();
    lineChart = new Chart(lineCtx, {
        type: 'line',
        data: {
            labels: times.map(d=>d.toLocaleString()),
            datasets: [{
                label: 'Transactions',
                data: times.map((_,i)=>i+1),
                borderColor: '#00ffc6',
                fill: false
            }]
        }
    });
}

// Load and display transactions
function loadTransactions() {
    fetch("http://localhost:5001/transactions")
        .then(response => response.json())
        .then(data => {
            const transactions = data.transactions || [];
            
            const formatted = transactions.map(t => {
                return {
                    timestamp: t.timestamp,
                    upi_number: t.user_id,
                    trans_amount: t.transaction_amount,
                    risk_level: t.risk_level,
                    fraud_risk_score: t.fraud_risk_score,
                    source: t.device_used || t.payment_method || "N/A"
                };
            });

            const lowCount = formatted.filter(t => t.risk_level === "LOW").length;
            const mediumCount = formatted.filter(t => t.risk_level === "MEDIUM").length;
            const highCount = formatted.filter(t => t.risk_level === "HIGH").length;
            
            // Update stats
            document.getElementById("totalCount").textContent = formatted.length;
            document.getElementById("lowCount").textContent = lowCount;
            document.getElementById("mediumCount").textContent = mediumCount;
            document.getElementById("highCount").textContent = highCount;

            updateCharts(formatted);
            
            // Display transactions
            const listContainer = document.getElementById("transactionList");
            const transactionsToDisplay = formatted;
            
            if (transactionsToDisplay.length === 0) {
                listContainer.innerHTML = `
                    <div class="empty-state">
                        <p>📭 No transactions recorded yet</p>
                    </div>
                `;
                return;
            }
            
            const sorted = transactionsToDisplay.sort((a, b) => {
                return new Date(b.timestamp) - new Date(a.timestamp);
            });
            
            listContainer.innerHTML = "";
            sorted.forEach((tx, index) => {
                const riskClass = tx.risk_level.toLowerCase();
                const html = `
                    <div class="transaction-item">
                        <div class="tx-field">
                            <div class="tx-label">Timestamp</div>
                            <div>${tx.timestamp}</div>
                        </div>
                        <div class="tx-field">
                            <div class="tx-label">User ID</div>
                            <div>${tx.upi_number}</div>
                        </div>
                        <div class="tx-field">
                            <div class="tx-label">Amount</div>
                            <div>₹${tx.trans_amount}</div>
                        </div>
                        <div class="tx-field">
                            <div class="tx-label">Risk Level</div>
                            <div class="risk-field">
                                <div class="risk-indicator ${riskClass}"></div>
                                <div class="risk-badge ${riskClass}">${tx.risk_level}</div>
                            </div>
                        </div>
                        <div class="tx-field">
                            <div class="tx-label">Risk Score</div>
                            <div>${tx.fraud_risk_score}%</div>
                        </div>
                        <div class="tx-field">
                            <div class="tx-label">Source</div>
                            <div>${tx.source}</div>
                        </div>
                    </div>
                `;
                listContainer.innerHTML += html;
            });
            
            loadLoginHistory();
        })
        .catch(err => {
            console.error("Error loading transactions:", err);
            document.getElementById("transactionList").innerHTML = `
                <div class="empty-state">
                    <p>❌ Error loading transactions</p>
                    <p style="font-size: 0.9rem;">${err.message}</p>
                </div>
            `;
        });
}

// Load transactions and stats initially
loadTransactions();
loadStats();

// Refresh every 3 seconds
setInterval(() => {
    loadTransactions();
    loadStats();
}, 3000);

// simulation button
const simBtn = document.getElementById('simulateBtn');
if (simBtn) {
    simBtn.addEventListener('click', async () => {
        simBtn.disabled = true;
        simBtn.textContent = 'Simulating...';
        try {
            await fetch('http://localhost:5001/simulate', { method: 'POST' });
        } catch (err) {
            console.error('Simulation error', err);
        }
        simBtn.disabled = false;
        simBtn.textContent = 'Run Simulation';
    });
}

// load login history separately
async function loadLoginHistory() {
    try {
        const resp = await fetch("http://localhost:5001/logins");
        const data = await resp.json();
        const list = document.getElementById("loginHistoryList");
        if (!list) return;
        if (!data.logins || data.logins.length === 0) {
            list.innerHTML = `<div class="empty-state"><p>📭 No logins</p></div>`;
            return;
        }
        list.innerHTML = '';
        data.logins.forEach(l => {
            const html = `
                <div class="transaction-item">
                    <div class="tx-field">
                        <div class="tx-label">User</div>
                        <div>${l.username}</div>
                    </div>
                    <div class="tx-field">
                        <div class="tx-label">Time</div>
                        <div>${l.login_time}</div>
                    </div>
                </div>`;
            list.innerHTML += html;
        });
    } catch (err) {
        console.error("Error loading login history", err);
    }
}
