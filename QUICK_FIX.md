# 🚀 Quick Fix Guide - ReSan Bank

## Problem 1: OTP Not Coming to Phone

### Current Status: ❌ SMS Disabled (Dev Mode)

Your app is running in **development mode** where OTP shows in the console, not sent to your phone.

### Quick Fix (2 Options):

#### Option A: Use Dev Mode (No Setup Required) ✅ EASIEST

1. **Start the server:**
   ```bash
   ./scripts/start.sh
   ```

2. **Keep the terminal window visible**

3. **Create an account in the browser**

4. **Look at the terminal** - You'll see:
   ```
   OTP: 123456
   ```

5. **Copy the OTP from terminal** and paste it in the browser

**This works immediately - no configuration needed!**

---

#### Option B: Enable Real SMS (Requires Twilio Setup) 📱

**Quick Setup (5 minutes):**

1. **Run the setup script:**
   ```bash
   ./scripts/setup-sms.sh
   ```

2. **Follow the prompts** - You'll need:
   - Twilio Account SID (from https://console.twilio.com/)
   - Twilio Auth Token
   - Twilio Phone Number

3. **Restart the server:**
   ```bash
   ./scripts/start.sh
   ```

4. **You should see:**
   ```
   ✓ Twilio SMS enabled
   ```

5. **⚠️ IMPORTANT**: Free trial can only send to verified numbers
   - To send to ANY number, upgrade your Twilio account
   - Visit: https://console.twilio.com/us1/billing/manage-billing/billing-overview
   - Add payment method (credit card)
   - Cost: ~$0.0075 per SMS (less than 1 cent)

---

## Problem 2: Profile Not Being Saved

### Possible Causes & Fixes:

#### Fix 1: Server Must Be Running ⚠️

**Check if server is running:**
```bash
ps aux | grep "python.*main.py" | grep -v grep
```

**If nothing shows, start the server:**
```bash
./scripts/start.sh
```

**You should see:**
```
🚀 Starting ReSan Bank...
🌐 App will be available at: http://localhost:8000
```

**Keep this terminal window open!** If you close it, the server stops and data won't save.

---

#### Fix 2: Check Data File Permissions

```bash
# Check if file exists and is writable:
ls -la resan_data.json

# If it shows "Permission denied" or doesn't exist:
echo '{"accounts":{},"transactions":{}}' > resan_data.json
chmod 644 resan_data.json
```

---

#### Fix 3: Clear Browser Cache

1. Open your browser
2. Press **Cmd+Shift+R** (Mac) or **Ctrl+Shift+R** (Windows/Linux)
3. This forces a fresh reload

Or try **Incognito/Private mode**:
- Chrome: Cmd+Shift+N (Mac) or Ctrl+Shift+N (Windows)
- Safari: Cmd+Shift+N
- Firefox: Cmd+Shift+P (Mac) or Ctrl+Shift+P (Windows)

---

#### Fix 4: Test Account Creation

**Step-by-step test:**

1. **Start server** (if not running):
   ```bash
   ./scripts/start.sh
   ```

2. **Open browser**: http://localhost:8000

3. **Click "Sign Up"**

4. **Fill the form:**
   - Name: Test User
   - Age: 25
   - Email: test@example.com
   - Phone: 9876543210
   - PIN: 1234

5. **Click "Send OTP & Continue"**

6. **Check terminal** - You should see:
   ```
   OTP: 123456
   ```

7. **Enter the OTP** from terminal

8. **Click "Verify & Create Account"**

9. **You should see**: "Account created successfully! Your account number is RSN1234"

10. **Check if saved**:
    ```bash
    cat resan_data.json
    ```
    
    You should see your account data!

---

#### Fix 5: Check Browser Console for Errors

1. Open browser
2. Press **F12** (or Cmd+Option+I on Mac)
3. Click **Console** tab
4. Look for red error messages
5. Common errors:

   **"Failed to fetch"**
   - Server is not running
   - Fix: Start server with `./scripts/start.sh`

   **"Network error"**
   - Wrong URL
   - Fix: Make sure you're on http://localhost:8000

   **"CORS error"**
   - Server configuration issue
   - Fix: Restart server

---

## Complete Test Procedure

**Follow these steps in order:**

### Step 1: Start Fresh

```bash
# Stop any running servers (Ctrl+C in terminal)

# Clear old data (optional):
echo '{"accounts":{},"transactions":{}}' > resan_data.json

# Start server:
./scripts/start.sh
```

### Step 2: Verify Server is Running

```bash
# In a NEW terminal window:
curl http://localhost:8000/api/stats

# You should see:
# {"total_accounts":0,"total_balance":0}
```

### Step 3: Test in Browser

1. Open: http://localhost:8000
2. Click "Sign Up"
3. Fill form with test data
4. Request OTP
5. Check terminal for OTP
6. Enter OTP
7. Create account
8. Note your account number (e.g., RSN1234)

### Step 4: Verify Data Saved

```bash
cat resan_data.json
```

You should see your account!

### Step 5: Test Login

1. Click "Login" in sidebar
2. Enter your account number
3. Enter your PIN (1234)
4. Request OTP
5. Check terminal for OTP
6. Enter OTP
7. You should see your dashboard!

---

## Still Not Working?

### Debug Checklist:

- [ ] Server is running (`./scripts/start.sh`)
- [ ] Terminal window is open and showing logs
- [ ] Browser is on http://localhost:8000 (not https)
- [ ] No errors in browser console (F12)
- [ ] No errors in terminal
- [ ] `resan_data.json` file exists
- [ ] File has write permissions
- [ ] Tried clearing browser cache
- [ ] Tried incognito mode

### Get More Help:

1. **Check server logs** - Look at terminal where server is running
2. **Check browser console** - Press F12, look for errors
3. **Check data file**:
   ```bash
   cat resan_data.json | python3 -m json.tool
   ```
4. **View API docs**: http://localhost:8000/docs
5. **Read full guide**: TROUBLESHOOTING_GUIDE.md

---

## Quick Commands Reference

```bash
# Start server:
./scripts/start.sh

# Check if server is running:
curl http://localhost:8000/api/stats

# View data:
cat resan_data.json

# Clear data:
echo '{"accounts":{},"transactions":{}}' > resan_data.json

# Setup SMS:
./scripts/setup-sms.sh

# Verify project:
./scripts/verify.sh
```

---

## Summary

**For OTP Issue:**
- Use Dev Mode (OTP in terminal) - No setup needed ✅
- OR setup Twilio for real SMS 📱

**For Profile Not Saving:**
- Make sure server is running ⚠️
- Check data file permissions
- Clear browser cache
- Test step-by-step

**Most Common Issue:**
- Server not running! Always run `./scripts/start.sh` first!

---

**Need more help?** See TROUBLESHOOTING_GUIDE.md for detailed solutions.

**Last Updated**: April 29, 2026
