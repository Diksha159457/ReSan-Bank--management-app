# ═══════════════════════════════════════════════════════════════
# backend.py — ReSan Private Bank
# FastAPI REST API — connects to the HTML/CSS/JS frontend
# Data stored in resan_data.json (local) or can use any DB
# ═══════════════════════════════════════════════════════════════

# --- Standard Library Imports ---
import json                          # For reading/writing JSON data files
import random                        # For generating OTPs and account numbers
import string                        # For character sets used in account number generation
import re                            # For regex-based email and phone validation
import os                            # For file path and environment variable access
from pathlib import Path             # For cross-platform file path handling
from datetime import datetime        # For timestamping account creation and transactions

# --- Third-party Imports (install via pip) ---
from fastapi import FastAPI, UploadFile, File, Form, HTTPException  # FastAPI core
from fastapi.middleware.cors import CORSMiddleware  # Allow frontend to call this API
from fastapi.staticfiles import StaticFiles         # Serve HTML/CSS/JS files directly
from fastapi.responses import FileResponse          # Return index.html for root route
from pydantic import BaseModel                      # Data validation models

# ───────────────────────────────────────────────────────────────
# APP SETUP
# ───────────────────────────────────────────────────────────────

# Create the FastAPI application instance
app = FastAPI(
    title="ReSan Private Bank API",       # Shown in auto-generated API docs at /docs
    description="Backend for ReSan Bank", # Description in /docs
    version="1.0.0"                       # API version
)

# Allow the HTML frontend (running on a different port or domain) to call this API
# Without this, browsers block cross-origin requests (CORS policy)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # In production replace * with your frontend domain
    allow_credentials=True,     # Allow cookies/auth headers
    allow_methods=["*"],        # Allow GET, POST, PUT, DELETE etc.
    allow_headers=["*"],        # Allow all request headers
)

# ───────────────────────────────────────────────────────────────
# DATABASE (JSON FILE)
# ───────────────────────────────────────────────────────────────

DB_FILE  = "resan_data.json"   # File that stores all account records
TXN_FILE = "resan_txns.json"   # File that stores all transaction history

# Maximum allowed PDF upload size: 2 MB
MAX_FILE_BYTES = 2 * 1024 * 1024  # 2 MB in bytes

# Directory where uploaded PDFs are saved
UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(exist_ok=True)  # Create uploads/ folder if it doesn't exist


def load_db(filepath: str):
    """Load JSON data from file. Returns empty list if file doesn't exist."""
    try:
        if Path(filepath).exists():                # Check if file exists first
            with open(filepath, "r") as f:
                return json.load(f)                # Parse JSON and return Python object
    except Exception as e:
        print(f"[DB ERROR] Could not load {filepath}: {e}")
    return [] if "data" in filepath else {}        # Return appropriate empty type


def save_db(filepath: str, data) -> bool:
    """Save Python object to JSON file. Returns True if successful."""
    try:
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)           # Pretty-print JSON with 2-space indent
        return True
    except Exception as e:
        print(f"[DB ERROR] Could not save {filepath}: {e}")
        return False


def find_account(acc_no: str, pin: int):
    """Find an account by account number AND PIN. Returns account dict or None."""
    accounts = load_db(DB_FILE)                    # Load all accounts
    for acc in accounts:                           # Loop through each account
        if acc["accountNo"] == acc_no.strip().upper() and acc["pin"] == pin:
            return acc                             # Return matching account
    return None                                    # No match found


def find_account_index(acc_no: str, pin: int) -> int:
    """Return the index of matching account in the list, or -1 if not found."""
    accounts = load_db(DB_FILE)
    for i, acc in enumerate(accounts):             # enumerate gives index + value
        if acc["accountNo"] == acc_no.strip().upper() and acc["pin"] == pin:
            return i
    return -1


def add_transaction(acc_no: str, txn_type: str, amount: float, new_balance: float):
    """Append a transaction record to the transaction history file."""
    txns = load_db(TXN_FILE)                       # Load existing transactions
    if acc_no not in txns:
        txns[acc_no] = []                          # Init list for this account if first txn

    txns[acc_no].insert(0, {                       # Insert at front (newest first)
        "type":    txn_type,                       # "Deposit" or "Withdrawal"
        "amount":  amount,
        "balance": new_balance,                    # Balance after this transaction
        "date":    datetime.now().strftime("%d %b %Y, %I:%M %p")  # e.g. "05 Apr 2026, 02:30 PM"
    })

    # Keep only the last 20 transactions per account to save space
    if len(txns[acc_no]) > 20:
        txns[acc_no] = txns[acc_no][:20]

    save_db(TXN_FILE, txns)                        # Persist transaction log


# ───────────────────────────────────────────────────────────────
# HELPERS
# ───────────────────────────────────────────────────────────────

# In-memory OTP store: { phone_number: "123456" }
# In production use Redis or a database with TTL (expiry time)
otp_store: dict = {}


def generate_otp() -> str:
    """Generate a random 6-digit OTP as a string."""
    return str(random.randint(100000, 999999))     # Random integer between 100000–999999


def send_otp(phone: str, otp: str):
    """
    Simulate sending OTP via SMS.
    In production: integrate Twilio, MSG91, or AWS SNS here.
    For now: prints to console and stores in memory.
    """
    otp_store[phone] = otp                         # Save OTP mapped to phone number
    print(f"\n{'='*40}")
    print(f"[OTP] Phone: +91 {phone}")
    print(f"[OTP] Code:  {otp}")
    print(f"{'='*40}\n")
    # Production example (Twilio):
    # from twilio.rest import Client
    # client = Client(account_sid, auth_token)
    # client.messages.create(body=f"Your ReSan OTP: {otp}", from_="+1xxx", to=f"+91{phone}")


def verify_otp(phone: str, entered_otp: str) -> bool:
    """Check if entered OTP matches the stored OTP for this phone number."""
    correct = otp_store.get(phone)                 # Get stored OTP for this phone
    if correct and correct == entered_otp.strip():
        del otp_store[phone]                       # Delete OTP after successful use (one-time)
        return True
    return False


def generate_account_no() -> str:
    """Generate a unique account number in format RS-XXXXXXXX."""
    chars   = "ABCDEFGHJKLMNPQRSTUVWXYZ"           # Letters (excluding I and O to avoid confusion)
    digits  = "0123456789"
    symbols = "@#$"

    parts = (
        random.choices(chars, k=3) +               # 3 random letters
        random.choices(digits, k=4) +              # 4 random digits
        random.choices(symbols, k=1)               # 1 special character
    )
    random.shuffle(parts)                          # Shuffle to randomise positions
    return "RS-" + "".join(parts)                  # Prefix with RS-


def validate_email(email: str) -> bool:
    """Validate email format using regex. Returns True if valid."""
    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]{2,}$"   # Must have local@domain.tld format
    return bool(re.match(pattern, email))


def validate_pin(pin: int) -> bool:
    """Validate PIN: must be exactly 4 digits (1000–9999)."""
    return 1000 <= pin <= 9999                     # 4-digit integer range


def validate_phone(phone: str) -> bool:
    """Validate Indian phone number: exactly 10 digits."""
    return bool(re.fullmatch(r"\d{10}", phone))    # Must be exactly 10 digits


def validate_name(name: str) -> bool:
    """Validate name: only letters and spaces, minimum 2 characters."""
    return bool(re.fullmatch(r"[a-zA-Z\s]{2,}", name.strip()))


# ───────────────────────────────────────────────────────────────
# PYDANTIC REQUEST MODELS (Input validation schemas)
# ───────────────────────────────────────────────────────────────

class OTPRequest(BaseModel):
    """Request body for sending OTP."""
    phone: str                                     # 10-digit phone number


class SignupRequest(BaseModel):
    """Request body for creating a new account after OTP verification."""
    name:              str
    age:               int
    email:             str
    phone:             str
    pin:               int
    otp:               str                         # OTP entered by user for verification
    # Guardian fields — required only when age < 18
    guardian_name:     str = None
    guardian_age:      int = None
    guardian_relation: str = None
    guardian_phone:    str = None
    guardian_email:    str = None


class LoginRequest(BaseModel):
    """Request body for initiating login (triggers OTP send)."""
    acc_no: str
    pin:    int


class VerifyLoginRequest(BaseModel):
    """Request body for verifying OTP and completing login."""
    acc_no: str
    pin:    int
    otp:    str


class TransactionRequest(BaseModel):
    """Request body for deposit or withdrawal transactions."""
    acc_no: str
    pin:    int
    amount: float                                  # Amount as a number


class DetailsRequest(BaseModel):
    """Request body for fetching account details."""
    acc_no: str
    pin:    int


class UpdateRequest(BaseModel):
    """Request body for updating account fields."""
    acc_no:    str
    pin:       int
    new_name:  str = None                          # Optional: only updates if provided
    new_email: str = None
    new_pin:   int = None


class CloseRequest(BaseModel):
    """Request body for permanently closing an account."""
    acc_no: str
    pin:    int


# ───────────────────────────────────────────────────────────────
# API ROUTES
# ───────────────────────────────────────────────────────────────

# ── Health Check ────────────────────────────────────────────────
@app.get("/health")
def health():
    """Simple health check. Returns OK if server is running."""
    return {"status": "ok", "bank": "ReSan Private Bank"}


# ── Send OTP for Signup ──────────────────────────────────────────
@app.post("/api/otp/send")
def send_otp_route(req: OTPRequest):
    """Generate and send a 6-digit OTP to the given phone number."""
    if not validate_phone(req.phone):              # Validate phone format first
        raise HTTPException(400, "Phone must be exactly 10 digits.")

    otp = generate_otp()                           # Create 6-digit OTP
    send_otp(req.phone, otp)                       # Log to console (simulated SMS)

    # NOTE: Return OTP in response for development/testing ONLY.
    # REMOVE "dev_otp" from this response before going live in production!
    return {"message": "OTP sent.", "dev_otp": otp}


# ── Create Account ───────────────────────────────────────────────
@app.post("/api/account/create")
def create_account(req: SignupRequest):
    """
    Create a new bank account after OTP verification.
    Validates all fields and stores account in JSON database.
    """
    # ── Validate personal details ──
    if not validate_name(req.name):
        raise HTTPException(400, "Name must contain only letters (min 2 chars).")

    if not isinstance(req.age, int) or req.age < 1 or req.age > 120:
        raise HTTPException(400, "Age must be a whole number between 1 and 120.")

    if not validate_email(req.email):
        raise HTTPException(400, "Invalid email format.")

    if not validate_phone(req.phone):
        raise HTTPException(400, "Phone must be exactly 10 digits.")

    if not validate_pin(req.pin):
        raise HTTPException(400, "PIN must be exactly 4 digits (1000–9999).")

    # ── Verify OTP before creating account ──
    if not verify_otp(req.phone, req.otp):
        raise HTTPException(400, "Invalid or expired OTP. Please request a new one.")

    # ── Validate guardian details if minor (age < 18) ──
    guardian = None
    if req.age < 18:
        if not req.guardian_name or not validate_name(req.guardian_name):
            raise HTTPException(400, "Guardian name is required for minor accounts.")
        if not req.guardian_age or req.guardian_age < 18:
            raise HTTPException(400, "Guardian must be 18 or older.")
        if not req.guardian_relation:
            raise HTTPException(400, "Guardian relationship is required.")
        if not req.guardian_phone or not validate_phone(req.guardian_phone):
            raise HTTPException(400, "Guardian phone must be exactly 10 digits.")
        if not req.guardian_email or not validate_email(req.guardian_email):
            raise HTTPException(400, "Guardian email format is invalid.")

        # Build guardian sub-object to embed in account record
        guardian = {
            "name":         req.guardian_name.strip(),
            "age":          req.guardian_age,
            "relationship": req.guardian_relation,
            "phone":        req.guardian_phone.strip(),
            "email":        req.guardian_email.strip().lower(),
        }

    # ── Build the full account record ──
    new_account = {
        "name":        req.name.strip(),
        "age":         req.age,
        "email":       req.email.strip().lower(),  # Normalise to lowercase
        "phone":       req.phone.strip(),
        "pin":         req.pin,
        "accountNo":   generate_account_no(),      # Auto-generate unique ID
        "balance":     0.0,                        # New accounts start at ₹0
        "accountType": "Minor (Guardian Managed)" if req.age < 18 else "Standard",
        "guardian":    guardian,                   # None for adults; dict for minors
        "docsUploaded": False,                     # Will be set True after /api/docs/upload
        "createdAt":   datetime.now().isoformat()  # ISO 8601 creation timestamp
    }

    # ── Save to database ──
    accounts = load_db(DB_FILE)                    # Load existing accounts
    accounts.append(new_account)                   # Append new account to list
    save_db(DB_FILE, accounts)                     # Persist to JSON file

    return {
        "message":   "Account created successfully!",
        "accountNo": new_account["accountNo"],
        "name":      new_account["name"],
        "type":      new_account["accountType"]
    }


# ── Upload Documents ─────────────────────────────────────────────
@app.post("/api/docs/upload")
async def upload_documents(
    acc_no:        str        = Form(...),          # Account number from multipart form
    pin:           int        = Form(...),           # PIN from multipart form
    aadhaar:       UploadFile = File(...),           # Aadhaar Card — required PDF
    pan:           UploadFile = File(...),           # PAN Card — required PDF
    address_proof: UploadFile = File(...),           # Address Proof — required PDF
    guardian_doc:  UploadFile = File(None),          # Guardian ID — optional (for minors)
):
    """
    Accept, validate, and save uploaded PDF documents.
    Validates: file type must be PDF, file size must be ≤ 2MB.
    """
    # Verify account credentials before accepting files
    user = find_account(acc_no, pin)
    if not user:
        raise HTTPException(403, "Invalid account number or PIN.")

    # Build list of documents to process
    docs_to_process = [
        ("aadhaar",        aadhaar),
        ("pan",            pan),
        ("address_proof",  address_proof),
    ]

    # Include guardian doc only if a file was actually provided
    if guardian_doc and guardian_doc.filename:
        docs_to_process.append(("guardian_id", guardian_doc))

    saved_files = []  # Track filenames of successfully saved documents

    for doc_name, upload in docs_to_process:
        # ── Validate file type: must be PDF ──
        if upload.content_type != "application/pdf":
            raise HTTPException(400, f"'{doc_name}': Only PDF files are accepted.")

        # ── Read file bytes ──
        content = await upload.read()              # Read asynchronously (non-blocking)

        # ── Validate file size: must be ≤ 2MB ──
        if len(content) > MAX_FILE_BYTES:
            raise HTTPException(400, f"'{doc_name}': File exceeds 2MB limit.")

        # ── Save to uploads/ directory ──
        # Filename format: ACCNO_doctype.pdf (e.g. RS-A1B2C_aadhaar.pdf)
        filename = f"{acc_no.upper()}_{doc_name}.pdf"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as f:
            f.write(content)                       # Write bytes to disk

        saved_files.append(filename)

    # ── Mark account as docs-uploaded ──
    accounts = load_db(DB_FILE)
    for acc in accounts:
        if acc["accountNo"] == acc_no.upper():
            acc["docsUploaded"] = True             # Set flag to True
            acc["docs"] = saved_files              # Store filenames in account record
            break
    save_db(DB_FILE, accounts)

    return {"message": "Documents uploaded successfully.", "files": saved_files}


# ── Send OTP for Login ───────────────────────────────────────────
@app.post("/api/login/otp")
def login_send_otp(req: LoginRequest):
    """
    Step 1 of login: verify account credentials then send OTP.
    OTP is sent to the phone number registered with the account.
    """
    user = find_account(req.acc_no, req.pin)       # Verify credentials first
    if not user:
        raise HTTPException(401, "Invalid account number or PIN.")

    otp = generate_otp()                           # Generate 6-digit OTP
    send_otp(user["phone"], otp)                   # Send OTP to registered phone

    # NOTE: Remove "dev_otp" in production!
    return {"message": "OTP sent to registered phone.", "dev_otp": otp}


# ── Verify OTP and Complete Login ────────────────────────────────
@app.post("/api/login/verify")
def login_verify(req: VerifyLoginRequest):
    """
    Step 2 of login: verify OTP and return account info.
    Frontend should store accountNo as session identifier.
    """
    user = find_account(req.acc_no, req.pin)       # Re-verify credentials
    if not user:
        raise HTTPException(401, "Invalid account number or PIN.")

    if not verify_otp(user["phone"], req.otp):     # Verify OTP matches
        raise HTTPException(401, "Incorrect or expired OTP.")

    # Return safe account info — never return PIN!
    return {
        "message":     "Login successful!",
        "accountNo":   user["accountNo"],
        "name":        user["name"],
        "accountType": user["accountType"],
        "balance":     user["balance"],
    }


# ── Deposit Money ────────────────────────────────────────────────
@app.post("/api/deposit")
def deposit(req: TransactionRequest):
    """Add money to an account. Maximum ₹1,00,000 per transaction."""
    amount = int(req.amount)                       # Force integer (no paise/decimals)

    if amount < 1:
        raise HTTPException(400, "Minimum deposit is ₹1.")
    if amount > 100000:
        raise HTTPException(400, "Maximum deposit per transaction is ₹1,00,000.")

    accounts = load_db(DB_FILE)
    idx = find_account_index(req.acc_no, req.pin)
    if idx == -1:
        raise HTTPException(403, "Invalid account number or PIN.")

    accounts[idx]["balance"] += amount             # Add deposit to current balance
    new_balance = accounts[idx]["balance"]
    save_db(DB_FILE, accounts)                     # Save updated balance

    add_transaction(req.acc_no.upper(), "Deposit", amount, new_balance)  # Log transaction

    return {
        "message":     f"Rs.{amount:,} deposited successfully.",
        "new_balance": new_balance,
    }


# ── Withdraw Money ───────────────────────────────────────────────
@app.post("/api/withdraw")
def withdraw(req: TransactionRequest):
    """Withdraw money from account. Cannot exceed current balance."""
    amount = int(req.amount)                       # Force integer

    if amount < 1:
        raise HTTPException(400, "Minimum withdrawal is Rs.1.")

    accounts = load_db(DB_FILE)
    idx = find_account_index(req.acc_no, req.pin)
    if idx == -1:
        raise HTTPException(403, "Invalid account number or PIN.")

    current_balance = accounts[idx]["balance"]
    if amount > current_balance:                   # Check sufficient funds
        raise HTTPException(400, f"Insufficient funds. Available: Rs.{current_balance:,}")

    accounts[idx]["balance"] -= amount             # Deduct amount from balance
    new_balance = accounts[idx]["balance"]
    save_db(DB_FILE, accounts)

    add_transaction(req.acc_no.upper(), "Withdrawal", amount, new_balance)  # Log transaction

    return {
        "message":     f"Rs.{amount:,} withdrawn successfully.",
        "new_balance": new_balance,
    }


# ── Get Account Details ──────────────────────────────────────────
@app.post("/api/account/details")
def account_details(req: DetailsRequest):
    """Return full account details (excluding PIN) for a verified account."""
    user = find_account(req.acc_no, req.pin)
    if not user:
        raise HTTPException(403, "Invalid account number or PIN.")

    txns    = load_db(TXN_FILE)                    # Load all transactions
    my_txns = txns.get(req.acc_no.upper(), [])     # Get only this account's transactions

    # Build response — never include the PIN field!
    return {
        "name":         user["name"],
        "age":          user["age"],
        "email":        user["email"],
        "phone":        user["phone"],
        "accountNo":    user["accountNo"],
        "balance":      user["balance"],
        "accountType":  user.get("accountType", "Standard"),
        "createdAt":    user.get("createdAt", "N/A"),
        "docsUploaded": user.get("docsUploaded", False),
        "guardian":     user.get("guardian"),      # None for adult accounts
        "transactions": my_txns                    # Last 20 transactions
    }


# ── Update Account Details ───────────────────────────────────────
@app.put("/api/account/update")
def update_account(req: UpdateRequest):
    """Update name, email, and/or PIN for a verified account."""
    accounts = load_db(DB_FILE)
    idx = find_account_index(req.acc_no, req.pin)
    if idx == -1:
        raise HTTPException(403, "Invalid account number or PIN.")

    updated_fields = []                            # Track which fields were changed

    if req.new_name:                               # Update name if provided
        if not validate_name(req.new_name):
            raise HTTPException(400, "Name must contain only letters.")
        accounts[idx]["name"] = req.new_name.strip()
        updated_fields.append("Name")

    if req.new_email:                              # Update email if provided
        if not validate_email(req.new_email):
            raise HTTPException(400, "Invalid email format.")
        accounts[idx]["email"] = req.new_email.strip().lower()
        updated_fields.append("Email")

    if req.new_pin:                                # Update PIN if provided
        if not validate_pin(req.new_pin):
            raise HTTPException(400, "New PIN must be exactly 4 digits.")
        accounts[idx]["pin"] = req.new_pin
        updated_fields.append("PIN")

    if not updated_fields:                         # Nothing was provided to update
        raise HTTPException(400, "No update fields were provided.")

    save_db(DB_FILE, accounts)                     # Persist all changes

    return {"message": f"Updated successfully: {', '.join(updated_fields)}"}


# ── Close Account ────────────────────────────────────────────────
@app.delete("/api/account/close")
def close_account(req: CloseRequest):
    """Permanently delete a bank account and all its transaction history."""
    accounts = load_db(DB_FILE)
    idx = find_account_index(req.acc_no, req.pin)
    if idx == -1:
        raise HTTPException(403, "Invalid account number or PIN.")

    name = accounts[idx]["name"]                   # Save name for response message
    accounts.pop(idx)                              # Remove account from list
    save_db(DB_FILE, accounts)                     # Persist deletion

    # Also delete transaction history for this account
    txns = load_db(TXN_FILE)
    if req.acc_no.upper() in txns:
        del txns[req.acc_no.upper()]               # Remove transaction log
        save_db(TXN_FILE, txns)

    return {"message": f"Account for {name} has been permanently closed. Thank you for banking with ReSan."}


# ── Stats (Home Page) ────────────────────────────────────────────
@app.get("/api/stats")
def get_stats():
    """Return aggregate stats: total accounts and total balance across all accounts."""
    accounts = load_db(DB_FILE)
    return {
        "total_accounts": len(accounts),                              # Count of all accounts
        "total_balance":  sum(a.get("balance", 0) for a in accounts) # Sum of all balances
    }


# ───────────────────────────────────────────────────────────────
# SERVE STATIC FRONTEND FILES
# Place index.html, style.css, app.js in the same folder as backend.py
# ───────────────────────────────────────────────────────────────
@app.get("/")
def home():
    return {"message": "ReSan Bank API is running 🚀"}
             # Send index.html to the browser

# Serve CSS, JS and other static assets from the current directory
app.mount("/", StaticFiles(directory="."), name="static")


# ───────────────────────────────────────────────────────────────
# RUN SERVER (only when this file is executed directly)
# ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn                                 # ASGI server for FastAPI
    uvicorn.run(
        "hello:app",                               # Module name : app variable
        host="0.0.0.0",                            # Listen on all interfaces (not just localhost)
        port=8000,                                 # Port number
        reload=True                                # Auto-restart on code changes (dev mode only)
    )
