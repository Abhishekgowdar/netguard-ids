# 🚀 Quick Start Guide - NetGuard IDS

## Prerequisites

Before you begin, make sure you have:
- ✅ Python 3.8 or higher installed
- ✅ Node.js 16 or higher installed  
- ✅ Administrator/Root privileges (for packet capture)

## Step 1: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 2: Install Frontend Dependencies

```bash
cd frontend
npm install
```

## Step 3: (Optional) Train ML Model

If you want to use ML-based detection, download and train the model:

```bash
# Download NSL-KDD dataset
python ml-training/scripts/download_dataset.py

# Train the model (takes 5-10 minutes)
python ml-training/scripts/train_model.py
```

**Note:** A pre-trained model will be included, so this step is optional.

## Step 4: Run the Application

### Option A: Run Everything Together (Recommended)

**Terminal 1 - Backend (Packet Capture + API):**
```bash
cd backend
python main.py
```

**Terminal 2 - Frontend Dashboard:**
```bash
cd frontend
npm run dev
```

### Option B: Run API Separately

If you want to test the dashboard without capturing packets:

**Terminal 1 - API Only:**
```bash
cd backend
python run_api.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## Step 5: Access the Dashboard

Open your browser and navigate to:
```
http://localhost:3000
```

You should see the NetGuard IDS dashboard!

## 🎯 What to Expect

### When Running Full IDS (main.py):
- Backend captures network packets in real-time
- Detects suspicious activity using:
  - Signature-based rules (port scans, DDoS, SQL injection)
  - ML anomaly detection
- Alerts appear in real-time on the dashboard
- Data is stored in SQLite database

### Dashboard Features:
- **Statistics Cards**: Total alerts, today's alerts, last hour, critical threats
- **Alert List**: Recent threats with severity levels
- **Auto-refresh**: Updates every 5 seconds

## ⚠️ Important Notes

### Running as Administrator (Windows):
```powershell
# Right-click Command Prompt or PowerShell → "Run as Administrator"
cd "C:\Users\BWM743\Desktop\Network IDS\backend"
python main.py
```

### Running as Root (Linux/Mac):
```bash
sudo python backend/main.py
```

### Firewall Permissions:
You may need to allow Python through your firewall when prompted.

## 🧪 Testing the System

### Generate Test Traffic:

**1. Port Scan Simulation:**
```bash
# Install nmap (if not installed)
# Windows: Download from nmap.org
# Linux: sudo apt install nmap
# Mac: brew install nmap

# Run a port scan
nmap -p 1-100 localhost
```

**2. High Traffic Simulation:**
```bash
# Use curl in a loop
for i in {1..1000}; do curl http://localhost:8000/api/health; done
```

**3. SQL Injection Test (in browser):**
```
http://localhost:8000/api/alerts?id=' OR '1'='1
```

These actions should trigger alerts that appear on the dashboard!

## 🐛 Troubleshooting

### Backend won't start - "Permission Denied"
- **Solution**: Run as Administrator/root
- Packet capture requires elevated privileges

### Frontend shows "System Offline"
- **Check**: Is the backend running?
- **Check**: Backend should be on http://localhost:8000
- **Test**: Visit http://localhost:8000/api/health in browser

### No alerts appearing
- **Check**: Is packet capture active? Look for "🔍 Packet capture started" in backend logs
- **Check**: Is your network interface correct? The system auto-detects, but you can specify one:
  ```python
  # In backend/config.py
  NETWORK_INTERFACE = "eth0"  # or "Wi-Fi", "en0", etc.
  ```

### ML detection not working
- **Check**: Is the model trained? Look for `ml-training/models/isolation_forest.pkl`
- **Solution**: Run `python ml-training/scripts/train_model.py`

### "Module not found" errors
- **Solution**: Make sure you're in the correct directory and dependencies are installed
  ```bash
  cd backend
  pip install -r requirements.txt
  ```

## 📊 Expected Performance

- **Packet Processing**: ~1,000-10,000 packets/second (depends on CPU)
- **Detection Latency**: <100ms per packet
- **Memory Usage**: ~200-500MB
- **CPU Usage**: ~15-30%

## 🎓 Next Steps

1. ✅ Explore the codebase
2. ✅ Customize detection rules in `backend/detection/signature_rules.py`
3. ✅ Add new attack patterns
4. ✅ Improve the ML model with more training data
5. ✅ Add email/Slack notifications for critical alerts
6. ✅ Deploy to a server for real network monitoring

## 📧 Need Help?

Check the main README.md for detailed documentation or open an issue on GitHub.

---

**🛡️ Happy Threat Hunting!**
