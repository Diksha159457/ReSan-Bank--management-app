# 🔧 Troubleshooting Guide - ReSan Bank

## Issue 1: OTP Not Coming to Phone Number

### Why This Happens

By default, the app runs in **DEV MODE** where OTP is shown in the console, not sent via SMS.

### Solution: Enable Real SMS

**Step 1: Create Twilio Account**
1. Go to https://www.twilio.com/try-twilio
2. Sign up (free $15 credit)
3. Verify your email and phone

**Step 2: Get Credentials**
1. Go to https://console.twilio.com/
2. Copy your **Account SID** (starts with AC...)
3. Copy your **Auth Token** (click to reveal)

**Step 3: Get Phone Number**
1. In Twilio Console: **Phone Numbers** → **Manage** → **Buy a number**
2. Choose your country
3. Select a number with SMS capability
4. Click **Buy**
5. Copy your new phone number (format: +1234567890)

**Step 4: Create .env File**

```bash
# In your terminal, run:
cd ~/path/to/bank\ magement\ project
cp config/.env.example config/.env
nano config/.env
```

**Step 5: Add Your Credentials**

Edit `config/.env` and replace with YOUR actual credentials:

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx1234
TWILIO_AUTH_TOKEN=your_actual_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

**Step 6: Restart Server**

```bash
# Stop the server (Ctrl+C)
# Start again:
./scripts/start.sh
```

You should see:
```
✓ Twilio SMS enabled
```

**Step 7: Upgrade Twilio Account (Important!)**

⚠️ **Free trial limitation**: Can only send to verified numbers

To send to ANY number:
1. Go to https://console.twilio.com/us1/billing/manage-billing/billing-overview
2. Add a payment method (credit card)
3. Upgrade your account
4. Now you can send to any phone number worldwide!

**Cost**: ~$0.0075 per SMS (less than 1 cent per OTP)

---

## Issue 2: Profile Not Being Saved

### Possible Causes

1. **Server not running** - Data only saves when server is active
2. **File permissions** - `resan_data.json` not writable
3. **Browser cache** - Old data cached in browser
4. **Not logged in** - Must be logged in to see profile

### Solutions

**Solution 1: Check Server is Running**

```bash
# Check if server is running:
ps aux | grep "python.*main.py"

# If not running, start it:
./scripts/start.sh
```

**Solution 2: Check Data File**

```bash
# Check if data file exists and is writable:
ls -la resan_data.json

# View current data:
cat resan_data.json

# If file doesn't exist or is corrupted, recreate:
echo '{"accounts":{},"transactions":{}}' > resan_data.json
```

**Solution 3: Clear Browser Cache**

1. Open browser
2. Press **Cmd+Shift+R** (Mac) or **Ctrl+Shift+R** (Windows)
3. Or try **Incognito/Private mode**

**Solution 4: Check Console for Errors**

1. Open browser
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Look for red error messages
5. Share the error message for help

**Solution 5: Test Account Creation**

```bash
# Test creating an account via API:
curl -X POST http://localhost:8000/api/otp/send \
  -H "Content-Type: application/json" \
  -d '{"phone":"9876543210"}'

# You should see:
# {"message":"OTP sent successfully","dev_otp":"123456","note":"SMS disabled - using dev mode"}

# Use the OTP to create account:
curl -X POST http://localhost:8000/api/account/create \
  -H "Content-Type: application/json" \
  -d '{
    "name":"Test User",
    "age":25,
    "email":"test@example.com",
    "phone":"9876543210",
    "pin":1234,
    "otp":"123456"
  }'

# Check if account was saved:
cat resan_data.json
```

---

## Quick Diagnostic Commands

**Check if server is running:**
```bash
curl http://localhost:8000/api/stats
```

**Check data file:**
```bash
cat resan_data.json | python3 -m json.tool
```

**Check environment variables:**
```bash
cat config/.env
```

**View server logs:**
```bash
# Server logs show in the terminal where you ran ./scripts/start.sh
# Look for:
# ✓ Twilio SMS enabled  (good)
# ✗ Twilio SMS disabled (need to configure)
```

---

## Common Error Messages

### "Invalid or expired OTP"
- **Cause**: OTP was already used or doesn't match
- **Fix**: Request a new OTP

### "Account not found"
- **Cause**: Account number doesn't exist
- **Fix**: Check account number spelling (e.g., RSN1234)

### "Incorrect PIN"
- **Cause**: Wrong PIN entered
- **Fix**: Enter correct 4-digit PIN

### "Insufficient balance"
- **Cause**: Trying to withdraw more than available
- **Fix**: Check balance first, withdraw less

### "SMS disabled - using dev mode"
- **Cause**: Twilio not configured
- **Fix**: Follow "Enable Real SMS" steps above

---

## Testing Checklist

- [ ] Server is running (`./scripts/start.sh`)
- [ ] Can access http://localhost:8000
- [ ] Can see homepage
- [ ] Can click "Sign Up"
- [ ] Can fill form
- [ ] Can request OTP
- [ ] OTP appears in console (dev mode) or phone (SMS mode)
- [ ] Can create account
- [ ] Account number is shown
- [ ] Can login with account number and PIN
- [ ] Can see dashboard
- [ ] Balance shows correctly
- [ ] Can make deposit
- [ ] Balance updates
- [ ] Can refresh page and still logged in
- [ ] Data persists after server restart

---

## Still Having Issues?

1. **Check server logs** - Look for error messages in terminal
2. **Check browser console** - Press F12, look for errors
3. **Check data file** - `cat resan_data.json`
4. **Restart everything**:
   ```bash
   # Stop server (Ctrl+C)
   # Clear data (optional):
   echo '{"accounts":{},"transactions":{}}' > resan_data.json
   # Restart:
   ./scripts/start.sh
   ```

5. **Test with curl** - Use the API directly to isolate issues

---

## Contact & Support

- **Documentation**: docs/DOCUMENTATION.md
- **API Docs**: http://localhost:8000/docs
- **Twilio Docs**: https://www.twilio.com/docs/sms

---

**Last Updated**: April 29, 2026
