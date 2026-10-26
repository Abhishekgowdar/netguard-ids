# 🎯 Option C: Test Data Now + Npcap Later

Complete guide to get your dashboard working immediately, then add real packet capture!

---

## ⚡ Phase 1: Test Data (RIGHT NOW - 2 minutes)

### **Step 1: Make sure frontend is running**

```bash
cd "C:\Users\BWM743\Desktop\Network IDS\frontend"
python server.py
```

Chrome should open automatically to: http://localhost:3000

---

### **Step 2: Generate Test Alerts**

**Option A: Double-click (Easiest)**
- Navigate to: `Network IDS\backend\`
- Double-click: **`GENERATE_TEST_ALERTS.bat`**

**Option B: Command Line**
```bash
cd "C:\Users\BWM743\Desktop\Network IDS\backend"
python generate_test_alerts.py
```

**Expected Output:**
```
============================================================
🧪 NetGuard IDS - Test Alert Generator
============================================================

📂 Initializing database...
✨ Generating 20 test alerts...

🔴 Alert 1: Port Scan (Severity: 8)
   Port scan detected: 150 ports scanned in 45s
🟠 Alert 2: SQL Injection (Severity: 7)
   SQL injection attempt detected in HTTP payload
🟡 Alert 3: Suspicious Port Access (Severity: 6)
   Connection to suspicious port 1337 detected
...

============================================================
✅ Successfully created 20 test alerts!
============================================================

📊 Alert Statistics:

By Severity:
   CRITICAL (9): 3
   HIGH (8): 5
   HIGH (7): 4
   MEDIUM (6): 5
   MEDIUM (5): 3

By Type:
   Port Scan: 5
   SQL Injection: 4
   DDoS Attack: 3
   Brute Force Attack: 3
   Suspicious Port Access: 3
   Anomaly Detected (ML): 2

🌐 Open the dashboard to see these alerts:
   http://localhost:3000
```

---

### **Step 3: Check Dashboard**

Go to: http://localhost:3000

**You should see:**
- ✅ Statistics updated (Total: 20, etc.)
- ✅ Alert list populated with colorful alerts
- ✅ Different severity levels (🔴 Critical, 🟠 High, 🟡 Medium)
- ✅ Realistic attack descriptions
- ✅ Source IPs and targets
- ✅ Timestamps

**🎉 Your dashboard is working!**

---

## 🔧 Advanced Test Data Options

### **Generate More Alerts:**
```bash
python generate_test_alerts.py -n 50
```

### **Clear All Alerts and Start Fresh:**
```bash
python generate_test_alerts.py --clear -n 20
```

### **Generate 100 Alerts:**
```bash
python generate_test_alerts.py -n 100
```

---

## 🚀 Phase 2: Install Npcap (LATER - 5 minutes)

When you're ready for **real packet capture**, follow these steps:

### **Step 1: Download Npcap**

1. Go to: **https://npcap.com/#download**
2. Click **"Download Npcap [version]"**
3. Save the installer

---

### **Step 2: Install Npcap**

1. **Run the installer** (double-click downloaded file)
2. Click **"I Agree"** to license
3. **IMPORTANT:** Check these boxes:
   - ✅ **"Install Npcap in WinPcap API-compatible Mode"**
   - ✅ **"Support raw 802.11 traffic"** (optional)
4. Click **"Install"**
5. Wait for installation (1-2 minutes)
6. Click **"Finish"**

---

### **Step 3: Restart Everything**

1. **Close** all PowerShell/Command Prompt windows
2. **Restart** your computer (recommended) OR just restart the terminal
3. **Start backend again:**
   ```bash
   cd "C:\Users\BWM743\Desktop\Network IDS\backend"
   python main.py
   ```

**Expected Output (SUCCESS):**
```
============================================================
🛡️  NetGuard IDS - Network Intrusion Detection System
============================================================
✅ Configuration loaded
✅ Database initialized
✅ SignatureDetector initialized
✅ ML model loaded (or disabled - that's fine!)
✅ NetGuard IDS initialized successfully

🚀 Starting NetGuard IDS...
   Interface: Wi-Fi (or Ethernet)
   Signature Detection: ✅ Enabled
   ML Detection: ❌ Disabled

🔍 Packet capture started         ← THIS IS THE KEY LINE!
```

**No more "winpcap is not available" error!** ✅

---

### **Step 4: Test Real Packet Capture**

With Npcap installed, your IDS will now:

1. **Capture real network traffic** as you browse
2. **Detect real threats** like port scans
3. **Show live alerts** on dashboard

**Test it:**
- Browse some websites
- Watch backend console show: "📦 Packet captured..."
- Check dashboard for real alerts!

---

## 🎯 Quick Reference

### **Commands You'll Use:**

```bash
# Start Frontend
cd "C:\Users\BWM743\Desktop\Network IDS\frontend"
python server.py

# Generate Test Alerts
cd "C:\Users\BWM743\Desktop\Network IDS\backend"
python generate_test_alerts.py -n 20

# Start Backend (after Npcap installed)
cd "C:\Users\BWM743\Desktop\Network IDS\backend"
python main.py

# Or use one-click startup
# Right-click: START_NETGUARD.bat → Run as Administrator
```

---

## 📊 What Alert Types Are Generated?

The test generator creates realistic alerts:

### **1. Port Scan (HIGH/CRITICAL)**
```
Port scan detected: 150 ports scanned in 45s
Source: 203.45.67.89 → Target: 192.168.1.1
```

### **2. DDoS Attack (CRITICAL)**
```
DDoS attack detected: 25000 packets in 10s (2500 pkt/s)
Source: 45.142.212.61 → Target: 192.168.1.1:80
```

### **3. SQL Injection (HIGH)**
```
SQL injection attempt detected in HTTP payload
Source: 185.220.101.34 → Target: 192.168.1.1:80
```

### **4. Brute Force (MEDIUM/HIGH)**
```
Brute force login attempts detected: 250 failed attempts
Source: 94.102.49.173 → Target: 192.168.1.1:22
```

### **5. Suspicious Port Access (MEDIUM)**
```
Connection to suspicious port 1337 detected
Source: 192.168.1.100 → Target: 192.168.1.1:1337
```

### **6. ML Anomaly (MEDIUM/HIGH)**
```
ML model detected unusual network behavior (anomaly score: -0.852)
Source: 10.0.0.55 → Target: 192.168.1.1:443
```

---

## 🎨 Dashboard Preview

**What you'll see:**

```
┌─────────────────────────────────────────────────┐
│  🛡️ NetGuard IDS         [●] System Online    │
├─────────────────────────────────────────────────┤
│                                                 │
│  Total: 20  Today: 20  Hour: 5  Critical: 3   │
│                                                 │
│  🛡️ Recent Threats              [Refresh]      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  🔴 DDoS Attack                    [CRITICAL]  │
│      DDoS: 25000 packets in 10s (2500 pkt/s)  │
│      📍 45.142.212.61 → 192.168.1.1:80        │
│      ⏰ 2 hours ago  ✓ Confidence: 92%        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  🟠 Port Scan                          [HIGH]  │
│      Port scan detected: 150 ports in 45s     │
│      📍 203.45.67.89 → 192.168.1.1            │
│      ⏰ 5 hours ago  ✓ Confidence: 95%        │
└─────────────────────────────────────────────────┘
```

---

## ✅ Success Checklist

### **Phase 1 Complete When:**
- ✅ Frontend opens in Chrome automatically
- ✅ Dashboard shows "System Online"
- ✅ Test alerts generated (20+)
- ✅ Alerts visible on dashboard with colors
- ✅ Statistics cards showing correct numbers
- ✅ You can click refresh and see updates

### **Phase 2 Complete When:**
- ✅ Npcap installed
- ✅ Backend shows "🔍 Packet capture started"
- ✅ No "winpcap" errors
- ✅ Packets being captured as you browse
- ✅ Real alerts appearing in dashboard

---

## 🆘 Troubleshooting

### **Dashboard shows 0 alerts:**
```bash
# Regenerate alerts
cd backend
python generate_test_alerts.py -n 20
```

### **Want to start fresh:**
```bash
# Clear all alerts and generate new ones
python generate_test_alerts.py --clear -n 20
```

### **Npcap installation fails:**
- Make sure you're running installer as Administrator
- Uninstall any old WinPcap first
- Reboot after installation

### **Backend still shows winpcap error after Npcap:**
- Restart computer
- Or close all terminals and reopen as Administrator

---

## 🎉 Summary

**What You Have Now:**
✅ Working dashboard with auto-open Chrome  
✅ Test alert generator for immediate testing  
✅ Realistic fake data to explore features  
✅ Clear path to add real packet capture later  

**Next Steps:**
1. **NOW:** Generate test alerts and explore dashboard
2. **LATER:** Install Npcap for real packet capture
3. **ENJOY:** Professional IDS on your GitHub!

---

**🚀 Start by running:**
```bash
cd "C:\Users\BWM743\Desktop\Network IDS\backend"
python generate_test_alerts.py
```

Then refresh your dashboard and see the magic! ✨
