# 🏦 ReSan Private Bank

A full-stack bank management system with theme support and real SMS OTP.

## ⚡ Quick Start

**macOS/Linux:**
```bash
./scripts/start.sh
```

**Windows:**
```bash
scripts\start.bat
```

Open http://localhost:8000 🎉

## 📁 Project Structure

```
resan-bank/
├── 📂 Core Files
│   ├── main.py                 # Backend (FastAPI)
│   ├── requirements.txt        # Python dependencies
│   └── resan_data.json         # Database (auto-created)
│
├── 📂 frontend/                # Frontend files
│   ├── index.html             # Main HTML with theme system
│   ├── style.css              # Styles (Light/Dark/Auto themes)
│   └── app.js                 # Frontend JavaScript
│
├── 📂 docs/                    # Documentation
│   ├── README.md              # This file
│   ├── DOCUMENTATION.md       # Complete guide
│   ├── PROJECT_SUMMARY.md     # Delivery summary
│   ├── GIT_COMMANDS.md        # Git guide
│   └── GIT_QUICK_REFERENCE.txt # Quick Git reference
│
├── 📂 config/                  # Configuration files
│   ├── .env.example           # Environment variables template
│   ├── Procfile               # Deployment config
│   ├── runtime.txt            # Python version
│   └── _redirects             # Netlify redirects
│
├── 📂 scripts/                 # Utility scripts
│   ├── start.sh               # Quick start (macOS/Linux)
│   ├── start.bat              # Quick start (Windows)
│   ├── git-setup.sh           # Git setup helper
│   └── verify.sh              # Project verification
│
├── 📂 uploads/                 # Uploaded documents (auto-created)
│
└── .gitignore                 # Git ignore rules
```

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
  - See [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md#-sms-otp-setup) for setup

## 🚀 Tech Stack

- **Backend**: FastAPI, Python 3.8+
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **SMS**: Twilio API
- **Storage**: JSON (upgradeable to database)

## 📚 Documentation

**Complete Guide**: [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md)

Includes:
- Installation guide
- Theme system (Light/Dark/Auto)
- SMS OTP setup (send to any number worldwide)
- Usage guide
- Deployment instructions
- API reference
- Troubleshooting
- FAQ

## 🔧 Git Commands

**Quick Setup:**
```bash
./scripts/git-setup.sh  # Interactive (recommended)
```

**Manual:**
```bash
git init
git add .
git commit -m "Initial commit: ReSan Bank v2.0.0"
git remote add origin https://github.com/YOUR_USERNAME/resan-bank.git
git push -u origin main
```

**See [docs/GIT_COMMANDS.md](docs/GIT_COMMANDS.md) for complete guide**

## 🌐 Deploy

Works on Railway, Render, Heroku, and any Python hosting platform.

See [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md#-deployment) for detailed instructions.

## 📄 License

MIT License - Free to use for learning or production!

---

**Built with ❤️ using FastAPI, Twilio, and modern web technologies**
