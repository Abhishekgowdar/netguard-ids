# Screenshots

Add your dashboard screenshots here:

## Required Screenshots:

1. **dashboard-empty.png** - Dashboard before starting detection (clean state)
2. **dashboard-active.png** - Dashboard with active threat detection (140+ alerts)

## How to Take Screenshots:

### Screenshot 1: Empty Dashboard
1. Stop the backend if running
2. Open dashboard: http://localhost:3000
3. Take full-page screenshot (F11 for fullscreen mode, then screenshot)
4. Save as: `dashboard-empty.png`

### Screenshot 2: Active Dashboard
1. Start backend: `python backend/run_api.py`
2. Generate alerts: `python backend/generate_test_alerts.py` (run 7 times for 140 alerts)
3. Refresh dashboard: http://localhost:3000
4. Take full-page screenshot showing:
   - Total alerts: 140
   - Color-coded threat cards
   - Statistics at top
   - Recent threats list
5. Save as: `dashboard-active.png`

## Tips for Great Screenshots:

- Use **F11** for fullscreen mode (removes browser UI)
- Capture **full page** including header and footer
- Ensure **dark theme** is visible
- Show **multiple alert cards** in the list
- Make sure **statistics** are clearly visible
- Use **high resolution** (1920x1080 or higher)

---

Once you have both screenshots, replace the placeholder text in README.md with actual image references.
