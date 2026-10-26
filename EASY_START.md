# 🚀 Easy Start Guide - NetGuard IDS

## ✨ NEW: One-Click Startup!

I've created automated startup scripts for you!

---

## 🎯 **Method 1: One-Click Start (EASIEST!)**

### **Start Everything at Once:**

1. Right-click **`START_NETGUARD.bat`** in the project folder
2. Select **"Run as Administrator"**
3. Done! ✅

**What happens:**
- ✅ Backend starts (packet capture + API)
- ✅ Frontend starts (minimized in background)
- ✅ Chrome opens automatically with dashboard
- ✅ Everything configured and ready!

---

## 🎯 **Method 2: Frontend Only (Testing)**

### **Just start the dashboard:**

**Option A: Double-click**
- Double-click **`frontend/start_frontend.bat`**
- Chrome opens automatically

**Option B: Command line**
```bash
cd "C:\Users\BWM743\Desktop\Network IDS\frontend"
python server.py
```
- Chrome opens automatically after 1.5 seconds
- Server runs in the current window

---

## 🎯 **Method 3: Manual Start (Full Control)**

### **Terminal 1 - Backend (Run as Admin):**
```bash
cd "C:\Users\BWM743\Desktop\Network IDS\backend"
python main.py
```

### **Terminal 2 - Frontend:**
```bash
cd "C:\Users\BWM743\Desktop\Network IDS\frontend"
python server.py
```
- Chrome opens automatically

---

## 🎛️ **Customization**

### **Disable Auto-Open Browser:**

Edit `frontend/server.py`, change line:
```python
AUTO_OPEN_BROWSER = False  # Set to False to disable
```

### **Change Port:**

Edit `frontend/server.py`, change:
```python
PORT = 3000  # Change to any port you want
```

---

## ⏹️ **How to Stop**

### **If using START_NETGUARD.bat:**
1. Go to "NetGuard Backend" window
2. Press **Ctrl + C**
3. Close both terminal windows

### **If using individual commands:**
- Press **Ctrl + C** in each terminal window

---

## 🌐 **Access URLs**

- **Dashboard:** http://localhost:3000
- **API:** http://localhost:8000/api
- **API Docs:** http://localhost:8000/docs

---

## ✅ **What Works Now**

### **Updated server.py features:**
✅ Auto-opens Chrome browser  
✅ Tries Chrome first, falls back to default browser  
✅ Runs server in background when using .bat files  
✅ 1.5 second delay to ensure server is ready  
✅ Can be disabled with `AUTO_OPEN_BROWSER = False`  

### **Batch Files Created:**
✅ `START_NETGUARD.bat` - Start everything at once  
✅ `frontend/start_frontend.bat` - Start frontend only  

---

## 🎯 **Quick Test**

**Want to test right now?**

1. **Right-click** `START_NETGUARD.bat`
2. **Select** "Run as Administrator"
3. **Wait** 5 seconds
4. **Chrome opens** with dashboard! 🎉

---

## 🐛 **Troubleshooting**

### **Chrome doesn't open:**
- Check if Chrome is installed in standard location
- Or manually open: http://localhost:3000

### **"Not running as Administrator" error:**
- Right-click the .bat file
- Select "Run as Administrator"

### **Port 3000 already in use:**
- Edit `server.py` and change `PORT = 3000` to another port
- Update the URL in your browser accordingly

---

## 📝 **Summary**

### **Before (Manual):**
```
1. Open PowerShell as Admin
2. cd to backend folder
3. Run python main.py
4. Open another PowerShell
5. cd to frontend folder  
6. Run python server.py
7. Open browser manually
8. Type URL manually
```

### **Now (Automatic):**
```
1. Right-click START_NETGUARD.bat
2. Run as Administrator
✅ Done! Everything opens automatically!
```

---

**🎉 Enjoy your automated NetGuard IDS startup!**
