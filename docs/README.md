# 🏦 ReSan Private Bank

A full-stack bank management system with theme support and real SMS OTP.

## ⚡ Quick Start

**macOS/Linux:**
```bash
./start.sh
```

**Windows:**
```bash
start.bat
```

Open http://localhost:8000 🎉

## 📚 Complete Documentation

**See [DOCUMENTATION.md](DOCUMENTATION.md) for:**
- Installation guide
- Theme system (Light/Dark/Auto)
- SMS OTP setup (send to any number worldwide)
- Usage guide
- Deployment instructions
- API reference
- Troubleshooting
- FAQ

## ✨ Features

- ✅ Account creation with KYC documents
- ✅ Deposits & withdrawals
- ✅ Transaction history
- ✅ Real SMS OTP (Twilio) - works with any phone number
- ✅ Light/Dark/Auto themes
- ✅ Minor account support with guardian
- ✅ Responsive design
- ✅ Production-ready

## 🎨 Theme System

Three beautiful themes with toggle buttons in sidebar:
- **☀ Light Mode** - Clean white interface
- **☾ Dark Mode** - Luxury navy-black (default)
- **⚙ Auto Mode** - Matches system preference

## 📱 SMS OTP

- **Dev Mode** (default): OTP shown in console - no setup needed
- **SMS Mode**: Real SMS to any number worldwide via Twilio
  - Free $15 credit (~2000 messages)
  - Upgrade account to send to any number
  - See [DOCUMENTATION.md](DOCUMENTATION.md#-sms-otp-setup) for setup

## 🚀 Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **SMS**: Twilio API
- **Storage**: JSON (upgradeable to database)

## 📦 Project Structure

```
resan-bank/
├── main.py              # FastAPI backend
├── frontend/            # HTML, CSS, JS
├── DOCUMENTATION.md     # Complete guide
├── start.sh / .bat      # Quick start scripts
└── .env.example         # Config template
```

## 🌐 Deploy

Works on Railway, Render, Heroku, and any Python hosting platform.

See [DOCUMENTATION.md](DOCUMENTATION.md#-deployment) for detailed instructions.

## 🔧 Git Commands

### Quick Setup
```bash
# Interactive setup (recommended)
./git-setup.sh

# Or manual setup
git init
git add .
git commit -m "Initial commit: ReSan Bank v2.0.0"
git remote add origin https://github.com/YOUR_USERNAME/resan-bank.git
git push -u origin main
```

### Daily Workflow
```bash
git add .
git commit -m "Your changes"
git push
```

**See [GIT_COMMANDS.md](GIT_COMMANDS.md) for complete Git guide**



---
📁 NEW ORGANIZED STRUCTURE:

resan-bank/
│
├── 📂 Core Files (Root)
│   ├── main.py                     ✅ Backend (FastAPI)
│   ├── requirements.txt            ✅ Python dependencies
│   ├── resan_data.json            ✅ Database (auto-created)
│   ├── Procfile                   ✅ Deployment config
│   ├── runtime.txt                ✅ Python version
│   ├── .gitignore                 ✅ Git ignore rules
│   ├── README.md                  ✅ Main README
│   └── PROJECT_STRUCTURE.md       ✅ Structure documentation
│
├── 📂 frontend/                    ✅ Frontend files
│   ├── index.html                 ✅ HTML with theme system
│   ├── style.css                  ✅ Styles (3 themes)
│   └── app.js                     ✅ JavaScript logic
│
├── 📂 docs/                        ✅ Documentation
│   ├── README.md                  ✅ Quick overview
│   ├── DOCUMENTATION.md           ✅ Complete guide
│   ├── PROJECT_SUMMARY.md         ✅ Delivery summary
├── 📂 config/                      ✅ Configuration
│   ├── .env.example               ✅ Environment template
│   ├── Procfile                   ✅ Deployment config
│   ├── runtime.txt                ✅ Python version
│   └── _redirects                 ✅ Netlify redirects
│
├── 📂 scripts/                     ✅ Utility scripts
│   ├── start.sh                   ✅ Quick start (macOS/Linux)
│   ├── start.bat                  ✅ Quick start (Windows)
│   ├── git-setup.sh               ✅ Git setup helper
│   └── verify.sh                  ✅ Project verification
│
└── 📂 uploads/                     ✅ Uploaded documents
    └── .gitkeep                   ✅ Keep folder in git

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━



1. ✅ Created organized folder structure:
   - docs/ for all documentation
   - config/ for configuration files
   - scripts/ for utility scripts
   - frontend/ for HTML, CSS, JS
   - uploads/ for uploaded files

2. ✅ Moved files to appropriate folders:
   - All .md files → docs/
   - .env.example, Procfile, runtime.txt → config/
   - start.sh, start.bat, verify.sh, git-setup.sh → scripts/
   - Kept deployment files in root (Procfile, runtime.txt)

3. ✅ Updated all scripts:
   - start.sh - navigates to project root
   - start.bat - navigates to project root
   - git-setup.sh - works from scripts folder
   - verify.sh - checks new structure

4. ✅ Updated documentation:
   - README.md - reflects new structure
   - PROJECT_STRUCTURE.md - complete structure guide
   - All docs reference new paths

5. ✅ Updated .gitignore:
   - Includes config/.env
   - Better organized
   - More comprehensive

## 📄 License

MIT License - Free to use for learning or production!
**Built with ❤️ using FastAPI, Twilio, and modern web technologies**
