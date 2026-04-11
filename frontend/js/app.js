const API_BASE = 'http://127.0.0.1:5000/api';
let chartInstance = null;

const FEATURES = [
    "MonsoonIntensity", "TopographyDrainage", "RiverManagement", "Deforestation",
    "Urbanization", "ClimateChange", "DamsQuality", "Siltation", "AgriculturalPractices",
    "Encroachments", "IneffectiveDisasterPreparedness", "DrainageSystems",
    "CoastalVulnerability", "Landslides", "Watersheds", "DeterioratingInfrastructure",
    "PopulationScore", "WetlandLoss", "InadequatePlanning", "PoliticalFactors"
];

document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    generateFeatureInputs();
    
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('predict-form').addEventListener('submit', handlePredict);
});

function switchTab(tab) {
    document.getElementById('tab-login').classList.remove('active');
    document.getElementById('tab-register').classList.remove('active');
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('register-form').style.display = 'none';
    
    if (tab === 'login') {
        document.getElementById('tab-login').classList.add('active');
        document.getElementById('login-form').style.display = 'block';
    } else {
        document.getElementById('tab-register').classList.add('active');
        document.getElementById('register-form').style.display = 'block';
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const user = document.getElementById('login-user').value;
    const pass = document.getElementById('login-pass').value;
    const msg = document.getElementById('login-msg');
    
    try {
        const res = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: user, password: pass})
        });
        const data = await res.json();
        
        if (res.ok) {
            sessionStorage.setItem('token', data.token);
            sessionStorage.setItem('role', data.role);
            sessionStorage.setItem('username', data.username);
            checkAuth();
        } else {
            msg.className = 'msg error';
            msg.textContent = data.message;
        }
    } catch (err) {
        msg.className = 'msg error';
        msg.textContent = 'Connection failed.';
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const user = document.getElementById('reg-user').value;
    const pass = document.getElementById('reg-pass').value;
    const role = document.getElementById('reg-role').value;
    const msg = document.getElementById('reg-msg');
    
    try {
        const res = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({username: user, password: pass, role: role})
        });
        const data = await res.json();
        
        if (res.ok) {
            msg.className = 'msg success';
            msg.textContent = 'Account created! Please login.';
            setTimeout(() => switchTab('login'), 1500);
        } else {
            msg.className = 'msg error';
            msg.textContent = data.message;
        }
    } catch (err) {
        msg.className = 'msg error';
        msg.textContent = 'Connection failed.';
    }
}

function generateFeatureInputs() {
    const container = document.getElementById('feature-inputs');

    const featureDescriptions = {
        MonsoonIntensity: "Rainfall level",
        TopographyDrainage: "Land drainage capacity",
        RiverManagement: "River maintenance quality",
        Deforestation: "Forest loss level",
        Urbanization: "Urban development level",
        ClimateChange: "Climate impact severity",
        DamsQuality: "Dam condition",
        Siltation: "Sediment buildup in rivers",
        AgriculturalPractices: "Farming impact",
        Encroachments: "Construction in flood areas",
        IneffectiveDisasterPreparedness: "Lack of planning",
        DrainageSystems: "Drainage efficiency",
        CoastalVulnerability: "Coastal flood risk",
        Landslides: "Landslide risk",
        Watersheds: "Water basin effect",
        DeterioratingInfrastructure: "Infrastructure condition",
        PopulationScore: "Population density",
        WetlandLoss: "Loss of wetlands",
        InadequatePlanning: "Poor planning",
        PoliticalFactors: "Governance quality"
    };

    FEATURES.forEach(feature => {
        const wrapper = document.createElement('div');

        const label = document.createElement('label');
        label.textContent = featureDescriptions[feature] || feature;

        const input = document.createElement('input');
        input.type = 'number';
        input.min = '0';
        input.max = '10';
        input.step = '1';
        input.id = `feat_${feature}`;
        input.required = true;

        wrapper.appendChild(label);
        wrapper.appendChild(input);
        container.appendChild(wrapper);
    });
}

async function handlePredict(e) {
    e.preventDefault();
    const token = sessionStorage.getItem('token');
    const msg = document.getElementById('predict-msg');
    
    const featuresDict = {};
    FEATURES.forEach(feature => {
        let val = document.getElementById(`feat_${feature}`).value;
        featuresDict[feature] = parseFloat(val) || 0;
    });
    
    try {
        const res = await fetch(`${API_BASE}/predict/evaluate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({features: featuresDict})
        });
        const data = await res.json();
        
        if (res.ok) {
            msg.textContent = '';
            displayResults(data);
        } else {
            msg.className = 'msg error';
            msg.textContent = data.message;
            if(res.status === 401 || res.status === 403) {
                setTimeout(logout, 2000);
            }
        }
    } catch (err) {
        msg.className = 'msg error';
        msg.textContent = 'Prediction failed. Is model trained or server running?';
    }
}

function displayResults(data) {
    const riskIndicator = document.getElementById('risk-level-display');
    const probNum = document.getElementById('prob-num');
    
    riskIndicator.textContent = data.risk_level;
    probNum.textContent = (data.probability * 100).toFixed(2) + '%';
    
    if (data.risk_level === 'Low') {
        riskIndicator.style.color = 'var(--risk-low)';
    } else if (data.risk_level === 'Medium') {
        riskIndicator.style.color = 'var(--risk-med)';
    } else {
        riskIndicator.style.color = 'var(--risk-high)';
    }
    
    if(data.feature_importance) {
        renderChart(data.feature_importance);
    }
}

function renderChart(importanceData) {
    const ctx = document.getElementById('importanceChart').getContext('2d');
    
    // Sort and get top 5 features
    const sortedFeatures = Object.entries(importanceData)
        .sort((a,b) => b[1] - a[1])
        .slice(0, 5);
        
    const labels = sortedFeatures.map(item => item[0].replace(/([A-Z])/g, ' $1').trim());
    const data = sortedFeatures.map(item => item[1]);
    
    if (chartInstance) {
        chartInstance.destroy();
    }
    
    chartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(139, 92, 246, 0.8)',
                    'rgba(236, 72, 153, 0.8)',
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(245, 158, 11, 0.8)'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#1e293b' }
                },
                title: {
                    display: true,
                    text: 'Top 5 Contributing Factors',
                    color: '#0f172a'
                }
            }
        }
    });
}

function checkAuth() {
    const token = sessionStorage.getItem('token');
    const role = sessionStorage.getItem('role');
    const user = sessionStorage.getItem('username');
    
    if (token) {
        document.getElementById('auth-section').style.display = 'none';
        document.getElementById('dashboard-section').style.display = 'block';
        if (role === 'Admin') {
            document.getElementById('logs-section').style.display = 'block';
        } else {
            document.getElementById('logs-section').style.display = 'none';
        }
        document.getElementById('user-badge').innerHTML = 
            `<span class="user-badge">${role}</span> <strong>${user}</strong>`;
            
        // Pre-fill dummy data for quick testing if empty
        if(document.getElementById('feat_MonsoonIntensity').value === "") {
             FEATURES.forEach(feature => {
                 document.getElementById(`feat_${feature}`).value = Math.floor(Math.random() * 10);
             });
        }
    } else {
        document.getElementById('auth-section').style.display = 'block';
        document.getElementById('dashboard-section').style.display = 'none';
        
        // Reset everything
        document.getElementById('login-msg').textContent = '';
        document.getElementById('reg-msg').textContent = '';
        if(chartInstance) chartInstance.destroy();
        document.getElementById('risk-level-display').textContent = '--';
        document.getElementById('risk-level-display').style.color = '#fff';
        document.getElementById('prob-num').textContent = '0.00';
    }
}

function logout() {
    sessionStorage.clear();
    checkAuth();
}

async function viewLogs() {
    const token = sessionStorage.getItem('token');

    const res = await fetch(`${API_BASE}/predict/logs`, {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`
        }
    });

    const data = await res.json();

    const container = document.getElementById('logs-container');
    container.innerHTML = '';

    data.forEach(log => {
        const div = document.createElement('div');
        div.innerHTML = `
            <p><b>Action:</b> ${log.action}</p>
            <p><b>User:</b> ${log.user_id}</p>
            <p><b>Time:</b> ${log.timestamp}</p>
            <hr>
        `;
        container.appendChild(div);
    });
}