# 🏦 ReSan Private Bank - Complete Documentation

**Version 2.0.0** | Production Ready ✅

---

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Features](#-features)
3. [Installation](#-installation)
4. [Theme System](#-theme-system)
5. [SMS OTP Setup](#-sms-otp-setup)
6. [Usage Guide](#-usage-guide)
7. [Deployment](#-deployment)
8. [Testing](#-testing)
9. [Troubleshooting](#-troubleshooting)
10. [API Reference](#-api-reference)
11. [Project Structure](#-project-structure)
12. [Security](#-security)
13. [FAQ](#-faq)

---

## ⚡ Quick Start

### Fastest Way (One Command)

**macOS/Linux:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

Open http://localhost:8000 - Done! 🎉

### Manual Start

```bash
# 1. Create virtual environment
python3 -m venv .venv

# 2. Activate it
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python main.py
```

Open http://localhost:8000 in your browser!

---

## 🚀 Features

### Core Banking Features
- ✅ **Account Creation** - Register with name, age, email, PIN, auto-generated account number
- ✅ **Deposits & Withdrawals** - Secure money transfers with balance validation
- ✅ **Transaction History** - View last 20 transactions per account
- ✅ **OTP Verification** - Real SMS OTP via Twilio (with dev mode fallback)
- ✅ **Minor Accounts** - Guardian-managed accounts for users under 18
- ✅ **Document Upload** - Upload PDF documents (Aadhaar, PAN, Address Proof)

### Additional Features
- ✅ **Theme Support** - Light, Dark, and Auto (system) themes
- ✅ **Responsive Design** - Works on desktop, tablet, and mobile
- ✅ **Real-time Updates** - Dynamic UI updates without page refreshes
- ✅ **Data Persistence** - JSON-based storage (easily upgradeable to database)
- ✅ **SMS Integration** - Real OTP delivery to any phone number worldwide

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Git (optional, for cloning)

### Step-by-Step Setup

1. **Clone or Download the Project**
   ```bash
   git clone https://github.com/yourusername/resan-bank.git
   cd resan-bank
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv .venv
   ```

3. **Activate Virtual Environment**
   ```bash
   # macOS/Linux:
   source .venv/bin/activate
   
   # Windows:
   .venv\Scripts\activate
   ```

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the Application**
   ```bash
   python main.py
   ```

6. **Open in Browser**
   - Navigate to: http://localhost:8000
   - API docs: http://localhost:8000/docs

---

## 🎨 Theme System

### Available Themes

The app includes three beautiful themes:

1. **☀ Light Mode**
   - Clean white interface
   - Dark text on light background
   - Perfect for daytime use
   - Reduced eye strain in bright environments

2. **☾ Dark Mode** (Default)
   - Luxury navy-black background
   - Soft blue-white text
   - Perfect for nighttime use
   - Reduced eye strain in low light

3. **⚙ Auto Mode**
   - Automatically matches your system preference
   - Switches when you change OS theme
   - Best of both worlds

### How to Use Themes

1. Open the app in your browser
2. Look at the **bottom-left sidebar**
3. You'll see three theme buttons: **☀ ⚙ ☾**
4. Click any button to switch themes
5. Your choice is saved automatically in browser localStorage

### Theme Features

- ✅ Smooth transitions between themes
- ✅ Persistent preference (survives page refresh)
- ✅ Real-time system theme detection
- ✅ All UI elements adapt (cards, modals, inputs, toasts)
- ✅ Accessible color contrast in both themes
- ✅ No page reload required

### Technical Details

Themes are applied via CSS custom properties (variables):

```css
/* Dark theme */
:root[data-theme="dark"] {
  --bg: #0b0b18;
  --text: #ccd6f6;
}

/* Light theme */
:root[data-theme="light"] {
  --bg: #f8f9fa;
  --text: #1a1a2e;
}
```

JavaScript manages theme switching:
```javascript
function setTheme(theme) {
  localStorage.setItem("resan_theme", theme);
  document.documentElement.setAttribute("data-theme", theme);
}
```

---

## 📱 SMS OTP Setup

### Default Behavior (Dev Mode)

By default, the app works in **development mode**:
- ✅ OTP codes are generated
- ✅ OTP shown in console output
- ✅ OTP included in API response
- ✅ Perfect for testing without SMS costs
- ✅ No configuration needed

### Enable Real SMS (Twilio)

To send real SMS to **any phone number worldwide**:

#### Step 1: Get Twilio Account

1. Sign up at https://www.twilio.com/try-twilio
2. Verify your email and phone number
3. You'll get **$15 free credit** (~2000 SMS messages)

#### Step 2: Get Credentials

1. Go to [Twilio Console](https://console.twilio.com/)
2. Copy these values from the dashboard:
   - **Account SID** (starts with AC...)
   - **Auth Token** (click to reveal)

#### Step 3: Get a Phone Number

1. In Twilio Console: **Phone Numbers** → **Manage** → **Buy a number**
2. Choose your country (e.g., United States, India, UK)
3. Select a number with **SMS** capability
4. Click **Buy** (uses your free credit)
5. Copy your new phone number (format: +1234567890)

#### Step 4: Configure the App

1. **Copy the example file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file:**
   ```bash
   nano .env  # or use any text editor
   ```

3. **Add your credentials:**
   ```
   TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_PHONE_NUMBER=+1234567890
   ```

4. **Save and close the file**

#### Step 5: Restart the Server

```bash
python main.py
```

You should see:
```
✓ Twilio SMS enabled
```

#### Step 6: Upgrade to Send to Any Number

**Free Trial Limitation**: Can only send to verified numbers

**To send to ANY number:**

1. Go to [Twilio Billing](https://console.twilio.com/us1/billing/manage-billing/billing-overview)
2. Add a payment method (credit card)
3. Upgrade your account
4. Now you can send to **any phone number worldwide**!

**Cost**: ~$0.0075 per SMS (less than 1 cent per OTP)

### Phone Number Formats

The app automatically formats phone numbers:

**India:**
- Input: `9876543210` → Sends to: `+919876543210`
- Input: `+919876543210` → Sends to: `+919876543210`

**USA/Canada:**
- Input: `5551234567` → Sends to: `+15551234567`

**Other Countries:**
Modify `main.py` to change the default country code:
```python
# Find this line in main.py:
phone = "+91" + phone  # India

# Change to your country:
phone = "+1" + phone   # USA/Canada
phone = "+44" + phone  # UK
phone = "+61" + phone  # Australia
```

### Monitoring SMS Delivery

View SMS status in Twilio Console:
1. Go to [Monitor → Logs → SMS](https://console.twilio.com/us1/monitor/logs/sms)
2. See all sent messages
3. Check delivery status
4. View error messages if any

### SMS Troubleshooting

**"SMS disabled - using dev mode"**
- Cause: Environment variables not set
- Fix: Check `.env` file exists and has correct values, restart server

**"Twilio initialization failed"**
- Cause: Invalid credentials
- Fix: Double-check Account SID and Auth Token in `.env`

**"Unable to create record"**
- Cause: Phone number not verified (free trial) or invalid format
- Fix: Upgrade account or verify number in Twilio Console

**SMS not received**
- Check phone number is correct
- Verify phone has signal
- Check Twilio Console logs for delivery status
- Some carriers may delay SMS by a few minutes

---

## 📖 Usage Guide

### Creating an Account

1. **Click "Sign Up"** button in sidebar
2. **Step 1: Personal Information**
   - Enter full name (letters only)
   - Enter age (1-120)
   - If under 18, guardian section appears automatically
   - Enter email (valid format required)
   - Enter phone number (10 digits for India)
   - Choose 4-digit PIN

3. **Step 2: Upload Documents**
   - Upload Aadhaar Card PDF (max 2MB)
   - Upload PAN Card PDF (max 2MB)
   - Upload Address Proof PDF (max 2MB)
   - For minors: Upload Guardian ID PDF

4. **Step 3: OTP Verification**
   - OTP sent to your phone (or shown in console)
   - Enter 6-digit OTP
   - Click "Verify & Create Account"

5. **Success!**
   - Account created with unique account number
   - Automatically logged in
   - Redirected to Dashboard

### Logging In

1. **Click "Login"** button
2. Enter account number (e.g., RSN1234)
3. Enter 4-digit PIN
4. Click "Send OTP & Login"
5. OTP sent to registered phone
6. Enter 6-digit OTP
7. Click "Verify & Login"
8. Redirected to Dashboard

### Making a Deposit

1. Go to **"Deposit"** page from sidebar
2. Enter account number
3. Enter 4-digit PIN
4. Enter amount (₹1 to ₹1,00,000)
5. Click "Deposit Now"
6. Success! Balance updated

### Making a Withdrawal

1. Go to **"Withdraw"** page
2. Enter account number
3. Enter 4-digit PIN
4. Enter amount (must not exceed balance)
5. Click "Withdraw"
6. Success! Balance updated

### Viewing Account Details

1. Go to **"My Details"** page
2. Enter account number and PIN
3. Click "View Details"
4. See complete account information:
   - Balance
   - Personal details
   - Account type
   - Guardian info (if minor)
   - Document upload status
   - Member since date

### Updating Account

1. Go to **"Update"** page
2. Enter account number and current PIN
3. Fill fields you want to update:
   - New name (optional)
   - New email (optional)
   - New PIN (optional)
4. Leave blank to keep existing value
5. Click "Save Changes"

### Closing Account

⚠️ **Warning**: This action is permanent and cannot be undone!

1. Go to **"Close Acct"** page
2. Enter account number and PIN
3. **Tick the confirmation checkbox**
4. Click "Close My Account"
5. Account permanently deleted
6. If logged in, automatically logged out

### Viewing Dashboard

The Dashboard shows:
- **Balance Card**: Current balance in large display
- **Account Stats**: Name, age, email, account type
- **Recent Transactions**: Last 20 transactions
  - Green (+) for deposits
  - Red (−) for withdrawals
  - Date and time for each

---

## 🌐 Deployment

### Railway (Recommended)

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/resan-bank.git
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Go to [Railway.app](https://railway.app/)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python and deploys!

3. **Add Environment Variables** (for SMS)
   - Go to your project → Variables
   - Add:
     - `TWILIO_ACCOUNT_SID`
     - `TWILIO_AUTH_TOKEN`
     - `TWILIO_PHONE_NUMBER`

4. **Done!** Your app is live at: `https://your-app.railway.app`

### Render

1. **Create Web Service**
   - Go to [Render.com](https://render.com/)
   - Click "New" → "Web Service"
   - Connect your GitHub repository

2. **Configure**
   - Name: `resan-bank`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`

3. **Add Environment Variables**
   - Go to Environment tab
   - Add Twilio credentials (optional)

4. **Deploy!** Your app is live at: `https://resan-bank.onrender.com`

### Heroku

1. **Install Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # Windows
   # Download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Login and Create App**
   ```bash
   heroku login
   heroku create resan-bank
   ```

3. **Set Environment Variables**
   ```bash
   heroku config:set TWILIO_ACCOUNT_SID=your_sid
   heroku config:set TWILIO_AUTH_TOKEN=your_token
   heroku config:set TWILIO_PHONE_NUMBER=your_number
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

5. **Open App**
   ```bash
   heroku open
   ```

### Environment Variables for Production

Always set these in your hosting platform (not in code):

```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

---

## 🧪 Testing

### Manual Testing Checklist

#### Theme System
- [ ] Click ☀ button → Light theme activates
- [ ] Click ☾ button → Dark theme activates
- [ ] Click ⚙ button → Auto theme activates
- [ ] Refresh page → Theme persists
- [ ] Change system theme (in Auto mode) → App theme changes

#### Account Creation
- [ ] Create adult account (age ≥ 18)
- [ ] Create minor account (age < 18) → Guardian fields appear
- [ ] Upload 3 PDFs → All accepted
- [ ] Try uploading non-PDF → Error shown
- [ ] Try uploading >2MB file → Error shown
- [ ] Enter OTP → Account created successfully

#### Login
- [ ] Login with correct credentials → Success
- [ ] Login with wrong PIN → Error shown
- [ ] Login with non-existent account → Error shown
- [ ] Enter wrong OTP → Error shown
- [ ] Enter correct OTP → Logged in successfully

#### Transactions
- [ ] Deposit ₹5000 → Balance increases
- [ ] Withdraw ₹2000 → Balance decreases
- [ ] Try withdrawing more than balance → Error shown
- [ ] Try depositing >₹1,00,000 → Error shown
- [ ] Check Dashboard → Transactions appear

#### Account Management
- [ ] View account details → All info displayed
- [ ] Update name → Name changes
- [ ] Update email → Email changes
- [ ] Update PIN → New PIN works
- [ ] Close account → Account deleted

#### Mobile Responsiveness
- [ ] Open on mobile → Sidebar hidden
- [ ] Click hamburger (☰) → Sidebar opens
- [ ] Click outside sidebar → Sidebar closes
- [ ] All forms work on mobile
- [ ] Theme buttons work on mobile

#### SMS (if enabled)
- [ ] Create account → SMS received
- [ ] Login → SMS received
- [ ] OTP works when entered
- [ ] Check Twilio logs → SMS delivered

### Automated Testing

Run Python syntax check:
```bash
python -m py_compile main.py
```

Check for common issues:
```bash
# Check if all dependencies are installed
pip list | grep -E "fastapi|uvicorn|twilio|pydantic"

# Check if data file is valid JSON
python -c "import json; json.load(open('resan_data.json'))"
```

---

## 🐛 Troubleshooting

### Common Issues

#### Port Already in Use

**Error**: `Address already in use`

**Solution**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
python main.py --port 8001
```

#### Module Not Found

**Error**: `ModuleNotFoundError: No module named 'fastapi'`

**Solution**:
```bash
# Make sure virtual environment is activated
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

#### Theme Not Working

**Symptoms**: Theme doesn't change or persists incorrectly

**Solutions**:
1. Clear browser cache (Ctrl+Shift+R or Cmd+Shift+R)
2. Check browser console (F12) for JavaScript errors
3. Ensure JavaScript is enabled in browser
4. Try in incognito/private mode

#### SMS Not Sending

**Symptoms**: "SMS disabled - using dev mode" message

**Solutions**:
1. Check `.env` file exists in project root
2. Verify credentials are correct (no extra spaces)
3. Restart server after changing `.env`
4. Check console for specific error messages

#### Data Lost After Restart

**Symptoms**: Accounts disappear after server restart

**Solutions**:
1. Check if `resan_data.json` exists
2. Verify file has correct format:
   ```json
   {
     "accounts": {},
     "transactions": {}
   }
   ```
3. Check file permissions (must be writable)
4. Look for errors in console during save operations

#### Upload Fails

**Symptoms**: Document upload doesn't work

**Solutions**:
1. Check `uploads/` directory exists
2. Verify file is PDF format
3. Ensure file is under 2MB
4. Check browser console for errors

### Getting Help

1. **Check Console Logs**: Most issues show helpful error messages
2. **Check Browser Console**: Press F12 to see frontend errors
3. **Check API Docs**: http://localhost:8000/docs for API testing
4. **Review This Documentation**: Search for your specific issue

---

## 📡 API Reference

### Base URL

- **Local**: `http://localhost:8000`
- **Production**: `https://your-app.railway.app`

### Authentication

All endpoints use PIN-based authentication. No JWT tokens required.

### Endpoints

#### Create Account
```http
POST /api/account/create
Content-Type: application/json

{
  "name": "John Doe",
  "age": 25,
  "email": "john@example.com",
  "phone": "9876543210",
  "pin": 1234,
  "otp": "123456"
}

Response: { "accountNo": "RSN1234" }
```

#### Login (Request OTP)
```http
POST /api/login/otp
Content-Type: application/json

{
  "acc_no": "RSN1234",
  "pin": 1234
}

Response: { "dev_otp": "123456" } // or { "message": "OTP sent" }
```

#### Login (Verify OTP)
```http
POST /api/login/verify
Content-Type: application/json

{
  "acc_no": "RSN1234",
  "pin": 1234,
  "otp": "123456"
}

Response: { "accountNo": "RSN1234", "name": "John Doe" }
```

#### Deposit
```http
POST /api/deposit
Content-Type: application/json

{
  "acc_no": "RSN1234",
  "pin": 1234,
  "amount": 5000
}

Response: { "message": "₹5,000 deposited successfully!" }
```

#### Withdraw
```http
POST /api/withdraw
Content-Type: application/json

{
  "acc_no": "RSN1234",
  "pin": 1234,
  "amount": 2000
}

Response: { "message": "₹2,000 withdrawn successfully!" }
```

#### Get Account Details
```http
POST /api/account/details
Content-Type: application/json

{
  "acc_no": "RSN1234",
  "pin": 1234
}

Response: {
  "accountNo": "RSN1234",
  "name": "John Doe",
  "age": 25,
  "email": "john@example.com",
  "phone": "9876543210",
  "balance": 5000,
  "accountType": "Savings Account",
  "transactions": [...]
}
```

#### Update Account
```http
PUT /api/account/update
Content-Type: application/json

{
  "acc_no": "RSN1234",
  "pin": 1234,
  "new_name": "John Smith",
  "new_email": "johnsmith@example.com",
  "new_pin": 5678
}

Response: { "message": "Account updated successfully!" }
```

#### Close Account
```http
DELETE /api/account/close
Content-Type: application/json

{
  "acc_no": "RSN1234",
  "pin": 1234
}

Response: { "message": "Account RSN1234 closed successfully." }
```

#### Send OTP
```http
POST /api/otp/send
Content-Type: application/json

{
  "phone": "9876543210"
}

Response: { "dev_otp": "123456" } // or { "message": "OTP sent" }
```

#### Upload Documents
```http
POST /api/docs/upload
Content-Type: multipart/form-data

Form Data:
- acc_no: RSN1234
- pin: 1234
- aadhaar: [PDF file]
- pan: [PDF file]
- address_proof: [PDF file]
- guardian_doc: [PDF file] (optional, for minors)

Response: { "message": "Documents uploaded successfully!" }
```

#### Get Statistics
```http
GET /api/stats

Response: {
  "total_accounts": 10,
  "total_balance": 125000
}
```

### Interactive API Documentation

Visit http://localhost:8000/docs for:
- Interactive API testing
- Request/response examples
- Schema documentation
- Try-it-out functionality

---

## 📁 Project Structure

```
resan-bank/
├── main.py                 # FastAPI backend application
├── requirements.txt        # Python dependencies
├── runtime.txt            # Python version for deployment
├── Procfile               # Deployment configuration (Heroku/Railway)
├── .env.example           # Environment variables template
├── .env                   # Your credentials (create this, not in git)
├── .gitignore             # Git ignore rules
├── resan_data.json        # Database (auto-created)
├── DOCUMENTATION.md       # This file
├── start.sh               # Quick start script (macOS/Linux)
├── start.bat              # Quick start script (Windows)
├── _redirects             # Netlify redirects config
├── frontend/
│   ├── index.html         # Main HTML page
│   ├── style.css          # Styles with theme support
│   └── app.js             # Frontend JavaScript
└── uploads/               # Uploaded documents (auto-created)
```

### Key Files Explained

**main.py**
- FastAPI backend application
- All API endpoints
- Business logic
- Twilio SMS integration
- Data persistence

**frontend/index.html**
- Single-page application
- All UI components
- Theme toggle buttons
- Forms and modals

**frontend/style.css**
- Theme system CSS
- Light/Dark/Auto themes
- Responsive design
- Animations

**frontend/app.js**
- Frontend logic
- API calls
- Theme management
- Form validation
- OTP handling

**resan_data.json**
- JSON database
- Stores accounts and transactions
- Auto-created on first run
- Persists across restarts

**.env**
- Environment variables
- Twilio credentials
- Not in git (create from .env.example)

---

## 🔒 Security

### Best Practices

#### For Development
- ✅ `.env` is in `.gitignore` - never commit it
- ✅ Dev mode OTP shown in console - intentional for testing
- ✅ Use strong PINs even in development
- ✅ Test with dummy data, not real information

#### For Production
1. **Environment Variables**: Use platform's environment variable system
2. **HTTPS**: Always use HTTPS (Railway/Render provide this automatically)
3. **Secrets**: Never commit `.env` or credentials to git
4. **Rotate Tokens**: If Twilio tokens are exposed, regenerate them immediately
5. **Rate Limiting**: Consider adding rate limiting for API endpoints
6. **Database**: Replace JSON file with PostgreSQL/MongoDB for production
7. **Input Validation**: All inputs are validated on both frontend and backend
8. **PIN Security**: PINs are validated but not encrypted (add encryption for production)

### Security Features

- ✅ OTP verification for sensitive operations
- ✅ PIN-based authentication
- ✅ Input validation and sanitization
- ✅ File type and size validation
- ✅ CORS configuration
- ✅ Error messages don't leak sensitive info

### Recommendations for Production

1. **Add Password Hashing**: Use bcrypt for PIN storage
2. **Add JWT Tokens**: For session management
3. **Add Rate Limiting**: Prevent brute force attacks
4. **Add CSRF Protection**: For form submissions
5. **Add Database**: PostgreSQL or MongoDB instead of JSON
6. **Add Logging**: Track all transactions and access
7. **Add Backup**: Regular database backups
8. **Add Monitoring**: Track errors and performance

---

## ❓ FAQ

### General Questions

**Q: Is this production-ready?**
A: Yes! The app is fully functional and can be deployed. For high-traffic production, consider adding a database and additional security features.

**Q: Can I use this for a real bank?**
A: This is a demonstration project. For a real bank, you'd need additional features like encryption, compliance, auditing, and regulatory approval.

**Q: What database does it use?**
A: Currently uses JSON file storage. Easy to upgrade to PostgreSQL, MongoDB, or any database.

**Q: Does it cost money to run?**
A: The app itself is free. Twilio SMS costs ~$0.0075 per message. Hosting platforms have free tiers (Railway, Render).

### Theme Questions

**Q: Can I add custom themes?**
A: Yes! Edit `frontend/style.css` and add new theme variables under `:root[data-theme="your-theme"]`.

**Q: Why isn't my theme saving?**
A: Check if browser localStorage is enabled. Try in incognito mode to test.

**Q: Can I set a default theme?**
A: Yes! In `frontend/app.js`, change the default in `initTheme()` function.

### SMS Questions

**Q: Can I send OTP to any number?**
A: Yes! After upgrading your Twilio account (adding payment method), you can send to any number worldwide.

**Q: How much does SMS cost?**
A: ~$0.0075 per SMS (less than 1 cent). Twilio gives $15 free credit (~2000 messages).

**Q: Can I use a different SMS provider?**
A: Yes! Replace Twilio code in `main.py` with your preferred provider (e.g., AWS SNS, MessageBird).

**Q: Does it work without SMS?**
A: Yes! Dev mode works perfectly without Twilio. OTP shows in console.

### Technical Questions

**Q: What Python version is required?**
A: Python 3.8 or higher. Tested on 3.8, 3.9, 3.10, 3.11, 3.12.

**Q: Can I use this with React/Vue/Angular?**
A: Yes! The backend is a REST API. Replace the frontend with any framework.

**Q: How do I add more features?**
A: Edit `main.py` for backend, `frontend/` files for frontend. All code is well-commented.

**Q: Can I deploy to AWS/Azure/GCP?**
A: Yes! Works on any platform that supports Python. Use the Procfile for configuration.

### Troubleshooting Questions

**Q: Why is port 8000 already in use?**
A: Another process is using it. Kill it with `lsof -i :8000` then `kill -9 <PID>`.

**Q: Why aren't my changes showing?**
A: Clear browser cache (Ctrl+Shift+R) or try incognito mode.

**Q: Why is SMS not working?**
A: Check `.env` file exists, has correct credentials, and server was restarted.

**Q: Where is my data stored?**
A: In `resan_data.json` file in the project root directory.

---

## 📞 Support

### Resources

- **API Documentation**: http://localhost:8000/docs
- **Twilio Docs**: https://www.twilio.com/docs/sms
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Python Docs**: https://docs.python.org/3/

### Getting Help

1. Check this documentation first
2. Check console logs for error messages
3. Check browser console (F12) for frontend errors
4. Review the code comments (extensively documented)
5. Test in API docs (http://localhost:8000/docs)

---

## 📝 License

MIT License - Feel free to use this project for learning or production!

---

## 🎉 Conclusion

You now have a fully functional bank management system with:
- ✅ Beautiful theme system (Light/Dark/Auto)
- ✅ Real SMS OTP to any number worldwide
- ✅ Complete banking features
- ✅ Production-ready deployment
- ✅ Comprehensive documentation

**Next Steps:**
1. Run the app: `./start.sh` or `start.bat`
2. Create your first account
3. Try different themes
4. (Optional) Set up Twilio for SMS
5. Deploy to production!

**Built with ❤️ using FastAPI, Twilio, and modern web technologies**

---

*Last Updated: 2024 | Version 2.0.0*
