# Bank Management System

A full-stack web application for managing bank accounts, built with FastAPI backend and a modern HTML/CSS/JS frontend. Features a luxury dark-gold aesthetic with glassmorphism design.

## 📋 About

This is a private banking system that allows users to create accounts, deposit/withdraw money, view transaction history, and upload documents. The app simulates real banking operations with OTP verification for security.

## 🚀 Features

### Core Banking Features
- **Account Creation**: Register new accounts with name, age, email, PIN, and auto-generated account number
- **Deposits & Withdrawals**: Secure money transfers with balance validation
- **Transaction History**: View last 20 transactions per account
- **OTP Verification**: Phone-based OTP for enhanced security (simulated SMS)

### Additional Features
- **File Uploads**: Upload PDF documents (up to 2MB) for account verification
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Dynamic UI updates without page refreshes
- **Data Persistence**: Stores data in JSON files (easily replaceable with a database)

## 🛠 Tech Stack

### Backend (Python)
- **FastAPI**: High-performance web framework for building REST APIs
  - Used for: API endpoints, request validation, CORS handling, static file serving
- **Pydantic**: Data validation and serialization
  - Used for: Request/response models, automatic validation
- **Uvicorn**: ASGI server for running FastAPI
  - Used for: Production-ready server with auto-reload in development

### Frontend
- **HTML5**: Page structure and semantic markup
  - Used for: Layout, forms, navigation
- **CSS3**: Styling with custom properties and animations
  - Used for: Luxury dark theme, glassmorphism effects, responsive design
- **JavaScript (ES6+)**: Client-side interactivity
  - Used for: Page navigation, API calls, form handling, dynamic content updates

### Data & Tools
- **JSON**: Data storage format
  - Used for: Account data and transaction logs
- **Git**: Version control
  - Used for: Code versioning and collaboration

## 📦 Installation

### Prerequisites
- Python 3.12+
- Git

### Local Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/bank-management-app.git
   cd bank-management-app
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python hello.py
   ```

5. **Open in browser**:
   - Navigate to `http://localhost:8000`
   - API docs available at `http://localhost:8000/docs`

## 🎯 Usage

### Web Interface
- Use the sidebar to navigate between pages
- Create an account on the registration page
- Use your account number and PIN for deposits/withdrawals
- View transaction history in the dashboard

### API Endpoints
- `GET /` - Serve the main HTML page
- `POST /api/create-account` - Create new account
- `POST /api/deposit` - Deposit money
- `POST /api/withdraw` - Withdraw money
- `GET /api/transactions/{account_no}` - Get transaction history
- `POST /api/send-otp` - Send OTP to phone
- `POST /api/verify-otp` - Verify OTP code

## 🚀 Deployment

### Railway (Recommended)
1. Push code to GitHub
2. Connect Railway to your GitHub repo
3. Deploy automatically - Railway detects Python and runs `python hello.py`

### Render
1. Create a Web Service on Render
2. Connect your GitHub repo
3. Set start command: `python hello.py`

### Heroku
1. Add a `Procfile` with: `web: python hello.py`
2. Push to GitHub
3. Connect Heroku to your repo and deploy

## 📁 Project Structure

```
bank-management-app/
├── hello.py              # FastAPI backend application
├── requirements.txt      # Python dependencies
├── pageoverview.html     # Main HTML page
├── style.css            # CSS stylesheets
├── app.js               # Frontend JavaScript
├── resan_data.json      # Account data storage
├── resan_txns.json      # Transaction history
├── uploads/             # Uploaded files directory
└── .gitignore           # Git ignore rules
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔧 Future Enhancements

- Database integration (PostgreSQL/MongoDB)
- User authentication with JWT
- Email notifications
- Multi-currency support
- Admin dashboard
- Mobile app companion

---

Built with ❤️ using FastAPI and modern web technologies.