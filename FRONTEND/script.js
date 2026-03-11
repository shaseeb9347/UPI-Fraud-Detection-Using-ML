// Initialize on page load
document.addEventListener("DOMContentLoaded", function() {
    console.log("Page loaded");
    showSection('home');
});

function showSection(section) {
    console.log("Showing section:", section);
    const sections = document.querySelectorAll(".page-section");
    sections.forEach(sec => sec.classList.add("hidden"));
    
    if (section === "home") {
        const homeSection = document.getElementById("homeSection");
        if (homeSection) homeSection.classList.remove("hidden");
    } else if (section === "check") {
        const checkSection = document.getElementById("checkSection");
        if (checkSection) checkSection.classList.remove("hidden");
    } else if (section === "dashboard") {
        window.location.href = "dashboard.html";
        return;
    }
    
    window.scrollTo(0, 0);
}

// perform login and update history
async function doLogin() {
    const username = document.getElementById("loginUsername")?.value?.trim();
    if (!username) {
        alert("Please enter a username");
        return;
    }
    try {
        const resp = await fetch("http://localhost:5001/login", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({ username })
        });
        if (!resp.ok) throw new Error(`status ${resp.status}`);
        await loadLoginHistory();
        alert("Logged in successfully");
    } catch (err) {
        console.error("Login error", err);
        alert("Login failed");
    }
}

async function loadLoginHistory() {
    try {
        const resp = await fetch("http://localhost:5001/logins");
        const data = await resp.json();
        const list = document.getElementById("loginList");
        if (!list) return;
        if (!data.logins || data.logins.length === 0) {
            list.innerHTML = `<div class="empty-state"><p>📭 No login records</p></div>`;
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

async function checkFraud() {
    console.log("🔵 checkFraud() called");
    
    try {
        // Get form values
        const user_id = document.getElementById("user_id")?.value?.trim();
        const amount = document.getElementById("amount")?.value?.trim();
        const device = document.getElementById("device")?.value?.trim();
        const location = document.getElementById("location")?.value?.trim();
        const transaction_type = document.getElementById("transaction_type")?.value?.trim();
        const payment_method = document.getElementById("payment_method")?.value?.trim();
        
        console.log("Form values:", { user_id, amount, device, location, payment_method });
        
        // Validation
        if (!user_id) { alert("User ID required"); return; }
        if (!amount) { alert("Amount required"); return; }
        if (!device) { alert("Device required"); return; }
        if (!location) { alert("Location required"); return; }
        if (!transaction_type) { alert("Transaction type required"); return; }
        if (!payment_method) { alert("Payment method required"); return; }
        
        console.log("✅ Validation passed");
        
        // Show loading
        const resultDiv = document.getElementById("result");
        const alertEl = document.getElementById("alertMsg");
        
        if (resultDiv) {
            resultDiv.classList.remove("hidden");
            resultDiv.style.display = "block";
        }
        if (alertEl) alertEl.textContent = "⏳ Processing...";
        
        console.log("Making request to backend...");
        
        const payload = {
            User_ID: user_id,
            Transaction_Amount: parseFloat(amount),
            Device: device,
            Location: location,
            Transaction_Type: transaction_type,
            // include current hour as time
            Time_of_Transaction: new Date().getHours(),
            Payment_Method: payment_method
        };
        
        console.log("Payload:", payload);
        
        const response = await fetch("http://localhost:5001/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        
        console.log("Response status:", response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error("Error response:", errorText);
            if (alertEl) alertEl.textContent = `❌ Error: ${response.status}`;
            return;
        }
        
        const result = await response.json();
        console.log("✅ Result:", result);
        
        // Update UI
        const scoreEl = document.getElementById("riskScore");
        const levelEl = document.getElementById("riskLevel");
        const badgeEl = document.getElementById("riskBadge");
        const riskBar = document.getElementById("riskBar");
        const reasonList = document.getElementById("reasonList");
        
        if (scoreEl) scoreEl.textContent = Math.round(result.fraud_risk_score);
        if (levelEl) levelEl.textContent = result.risk_level;
        if (riskBar) riskBar.style.width = Math.round(result.fraud_risk_score) + "%";
        if (alertEl) alertEl.textContent = "✅ Analysis complete";
        
        // populate reasoning
        if (reasonList) {
            reasonList.innerHTML = "";
            (result.reasons || []).forEach(r => {
                const li = document.createElement("li");
                li.textContent = r;
                reasonList.appendChild(li);
            });
        }
        
        // Set badge color
        if (badgeEl) {
            badgeEl.className = "risk-badge";
            if (result.risk_level === "LOW") {
                badgeEl.classList.add("badge-low");
                badgeEl.textContent = "🟢 LOW RISK";
            } else if (result.risk_level === "MEDIUM") {
                badgeEl.classList.add("badge-medium");
                badgeEl.textContent = "🟡 MEDIUM RISK";
            } else {
                badgeEl.classList.add("badge-high");
                badgeEl.textContent = "🔴 HIGH RISK";
            }
        }
        
        // Show popup for high risk
        if (result.risk_level === "HIGH") {
            const popup = document.getElementById("fraudPopup");
            if (popup) {
                popup.classList.remove("hidden");
                setTimeout(() => popup.classList.add("hidden"), 3000);
            }
        }
        
        console.log("✅ UI updated successfully");
        
    } catch (error) {
        console.error("❌ Fatal error:", error);
        const alertEl = document.getElementById("alertMsg");
        if (alertEl) alertEl.textContent = `❌ Error: ${error.message}`;
    }
}
