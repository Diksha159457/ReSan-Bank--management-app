# ═══════════════════════════════════════════════════════════════
# main.py — ReSan Private Bank Backend
# This file is the entire backend brain of the bank app.
# It handles accounts, login, deposits, withdrawals and more.
# ═══════════════════════════════════════════════════════════════

from fastapi import FastAPI, HTTPException
# FastAPI  → creates our backend web server (the bank's backend engine)
# HTTPException → used to send error messages to frontend (like "wrong PIN")

from fastapi.middleware.cors import CORSMiddleware
# CORSMiddleware → allows our Netlify frontend to talk to this Render backend
# Without this, the browser would block all requests from frontend to backend

from pydantic import BaseModel
# BaseModel → used to define the shape/structure of data we receive from frontend
# Example: when frontend sends account number + PIN, pydantic validates it automatically

from typing import Optional
# Optional → means a field is not required (can be None/empty)
# Used for fields like guardian_name which only minor accounts need

import random
# random → used to generate random OTP numbers and account numbers
# Example: random.choices picks random digits for OTP like "482951"

import string
# string → gives us character sets like string.digits = "0123456789"
# Used when generating account numbers like RSN1234

from datetime import datetime
# datetime → gives us current date and time
# Used to record when transactions happen and when accounts are created

# ─── APP SETUP ────────────────────────────────────────────────

app = FastAPI()
# Creates the main FastAPI application object
# This is the core of our bank backend — all routes are attached to this

app.add_middleware(
    CORSMiddleware,                    # Adds CORS protection layer to the app
    allow_origins=["https://resan-bank-app.netlify.app"],
    # Only allows requests from our Netlify frontend URL
    # If this doesn't match your Netlify URL exactly, all buttons will fail
    allow_credentials=True,            # Allows cookies and auth headers to be sent
    allow_methods=["*"],               # Allows GET, POST, PUT, DELETE — all HTTP methods
    allow_headers=["*"],               # Allows all headers like Content-Type, Authorization
)

# ─── IN-MEMORY DATABASE ───────────────────────────────────────

accounts_db = {}
# This is our bank's database — stored in memory as a Python dictionary
# Key = account number (e.g. "RSN1234"), Value = full account details
# ⚠️ WARNING: This resets every time Render restarts (free tier goes to sleep)
# For permanent storage, you would use PostgreSQL or MongoDB later

otp_store = {}
# Temporary storage for OTPs (One Time Passwords)
# Key = phone number, Value = 6-digit OTP string
# OTP is deleted after it is used successfully

# ─── HELPER FUNCTIONS ─────────────────────────────────────────

def generate_acc_no():
    # This function creates a unique account number for every new customer
    while True:
        # Keep trying until we get an account number that doesn't already exist
        acc = "RSN" + "".join(random.choices(string.digits, k=4))
        # "RSN" is the bank prefix, followed by 4 random digits
        # Example output: "RSN4821", "RSN0037", "RSN9914"
        if acc not in accounts_db:
            # Only return this number if it's not already taken by another account
            return acc

def generate_otp():
    # Creates a random 6-digit OTP for login and signup verification
    return "".join(random.choices(string.digits, k=6))
    # Picks 6 random digits and joins them into a string
    # Example output: "482951", "003847", "719204"

def get_account(acc_no: str, pin: int):
    # This is a reusable security check used by deposit, withdraw, login etc.
    # It checks if the account exists AND if the PIN is correct
    acc = accounts_db.get(acc_no.upper())
    # .upper() converts account number to uppercase so "rsn1234" = "RSN1234"
    # .get() returns None if the account doesn't exist (doesn't crash)
    if not acc:
        # If account number is not found in our database
        raise HTTPException(status_code=404, detail="Account not found.")
        # Sends a 404 error back to frontend with the message "Account not found."
    if acc["pin"] != pin:
        # If the PIN entered doesn't match the stored PIN
        raise HTTPException(status_code=401, detail="Incorrect PIN.")
        # Sends a 401 error (unauthorized) back to frontend
    return acc
    # If both checks pass, return the full account data to be used by the caller

# ─── PYDANTIC MODELS (Request Structures) ─────────────────────
# These classes define what data we EXPECT to receive from the frontend
# Pydantic automatically validates types and raises errors if data is wrong

class OTPRequest(BaseModel):
    phone: str
    # Used when frontend asks backend to send an OTP
    # Expects: { "phone": "9876543210" }

class LoginOTPRequest(BaseModel):
    acc_no: str                        # Account number entered by user on login page
    pin: int                           # 4-digit PIN entered by user on login page

class LoginVerifyRequest(BaseModel):
    acc_no: str                        # Account number (same as login step 1)
    pin: int                           # PIN (same as login step 1)
    otp: str                           # 6-digit OTP the user received and entered

class SignupRequest(BaseModel):
    name: str                          # Full name of the new account holder
    age: int                           # Age — determines if Minor or Savings account
    email: str                         # Email address of the account holder
    phone: str                         # Phone number — also used to send OTP
    pin: int                           # 4-digit PIN chosen by user for future logins
    otp: str                           # OTP entered by user to verify phone number
    guardian_name: Optional[str] = None      # Guardian's name (only for age < 18)
    guardian_age: Optional[int] = None       # Guardian's age (must be 18+)
    guardian_relation: Optional[str] = None  # Relationship: Father, Mother, etc.
    guardian_phone: Optional[str] = None     # Guardian's phone number
    guardian_email: Optional[str] = None     # Guardian's email address

class AccountDetailsRequest(BaseModel):
    acc_no: str                        # Account number to look up
    pin: int                           # PIN to verify the user owns this account

class DepositRequest(BaseModel):
    acc_no: str                        # Account number to deposit money into
    pin: int                           # PIN to verify identity before depositing
    amount: int                        # Amount in rupees to deposit (must be ≥ 1)

class WithdrawRequest(BaseModel):
    acc_no: str                        # Account number to withdraw money from
    pin: int                           # PIN to verify identity before withdrawing
    amount: int                        # Amount in rupees to withdraw

class UpdateRequest(BaseModel):
    acc_no: str                        # Account number of the account to update
    pin: int                           # Current PIN to verify identity
    new_name: Optional[str] = None     # New name to update (leave None to skip)
    new_email: Optional[str] = None    # New email to update (leave None to skip)
    new_pin: Optional[int] = None      # New PIN to set (leave None to keep old PIN)

class CloseRequest(BaseModel):
    acc_no: str                        # Account number to permanently close
    pin: int                           # PIN to confirm the user owns this account

# ─── ROOT ─────────────────────────────────────────────────────

@app.get("/")
# This is the home route — runs when someone opens the backend URL directly
def home():
    return {"message": "ReSan Bank Backend is working!"}
    # Returns a simple JSON message to confirm the backend is alive and running

# ─── OTP: SEND (for signup) ───────────────────────────────────

@app.post("/api/otp/send")
# Called by frontend during signup Step 3 to send OTP to user's phone
def send_otp(req: OTPRequest):
    otp = generate_otp()
    # Generate a fresh 6-digit OTP for this user
    otp_store[req.phone] = otp
    # Save the OTP in memory, linked to this phone number
    # When user enters OTP later, we compare against this saved value
    # In production: send SMS via Twilio / Fast2SMS here
    return {
        "message": f"OTP sent to {req.phone}",  # Confirmation message to frontend
        "dev_otp": otp                           # ⚠️ Only for development! Remove in production
    }

# ─── ACCOUNT: CREATE (signup) ─────────────────────────────────

@app.post("/api/account/create")
# Called by frontend after user enters OTP in signup Step 3
def create_account(req: SignupRequest):
    saved_otp = otp_store.get(req.phone)
    # Look up the OTP we stored for this phone number
    if not saved_otp or saved_otp != req.otp:
        # If no OTP exists for this phone, or user entered wrong OTP
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")

    acc_type = "Minor Account" if req.age < 18 else "Savings Account"
    # Automatically assign account type based on age
    # Age < 18 → Minor Account (needs guardian details)
    # Age ≥ 18 → Regular Savings Account

    acc_no = generate_acc_no()
    # Generate a unique account number like RSN4821 for this new customer

    accounts_db[acc_no] = {
        # Store all account information in our in-memory database
        "accountNo":    acc_no,              # The unique account number e.g. RSN4821
        "name":         req.name,            # Customer's full name
        "age":          req.age,             # Customer's age
        "email":        req.email,           # Customer's email address
        "phone":        req.phone,           # Customer's phone number
        "pin":          req.pin,             # 4-digit PIN for future logins
        "balance":      0.0,                 # Starting balance is always ₹0
        "accountType":  acc_type,            # "Savings Account" or "Minor Account"
        "docsUploaded": False,               # Documents not uploaded yet at this point
        "createdAt":    datetime.now().isoformat(),
        # Records exact date and time when account was created
        "transactions": [],
        # Empty list — will be filled as deposits/withdrawals happen
        "guardian": {
            # Guardian details — only stored if customer is under 18
            "name":         req.guardian_name,
            "age":          req.guardian_age,
            "relationship": req.guardian_relation,
            "phone":        req.guardian_phone,
            "email":        req.guardian_email,
        } if req.age < 18 else None
        # If age ≥ 18, guardian is set to None (not needed)
    }

    del otp_store[req.phone]
    # Delete the used OTP from memory so it can't be reused again

    return {
        "message":   "Account created successfully!",  # Success message to frontend
        "accountNo": acc_no,                           # Send account number to frontend
        "name":      req.name,                         # Send name back for welcome message
    }

# ─── LOGIN: SEND OTP ──────────────────────────────────────────

@app.post("/api/login/otp")
# Called when user clicks "Login" button — verifies credentials then sends OTP
def login_send_otp(req: LoginOTPRequest):
    acc = get_account(req.acc_no, req.pin)
    # First verify account exists and PIN is correct before sending OTP
    # This prevents sending OTPs to random phone numbers
    otp = generate_otp()
    # Generate fresh OTP for this login attempt
    otp_store[acc["phone"]] = otp
    # Store OTP against the account's registered phone number
    return {
        "message": "OTP sent to registered phone.",  # Confirmation to frontend
        "dev_otp": otp                               # ⚠️ Dev only — remove in production
    }

# ─── LOGIN: VERIFY OTP ────────────────────────────────────────

@app.post("/api/login/verify")
# Called when user enters the OTP on the login OTP screen
def login_verify_otp(req: LoginVerifyRequest):
    acc = get_account(req.acc_no, req.pin)
    # Re-verify account + PIN (security double check)
    saved_otp = otp_store.get(acc["phone"])
    # Retrieve the OTP we stored for this account's phone number
    if not saved_otp or saved_otp != req.otp:
        # If OTP doesn't exist or doesn't match what user entered
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    del otp_store[acc["phone"]]
    # Delete OTP after successful use — prevents replay attacks
    return {
        "message":   "Login successful!",    # Success message to frontend
        "accountNo": acc["accountNo"],        # Send account number for session storage
        "name":      acc["name"],             # Send name for welcome message
    }

# ─── ACCOUNT: DETAILS ─────────────────────────────────────────

@app.post("/api/account/details")
# Called by dashboard and "View Details" page to fetch full account info
def account_details(req: AccountDetailsRequest):
    acc = get_account(req.acc_no, req.pin)
    # Verify PIN before showing any sensitive account details
    return acc
    # Return entire account object — frontend picks what to display

# ─── DEPOSIT ──────────────────────────────────────────────────

@app.post("/api/deposit")
# Called when user clicks "Deposit" button and submits the deposit form
def deposit(req: DepositRequest):
    acc = get_account(req.acc_no, req.pin)
    # Verify account and PIN before touching any money
    if req.amount < 1:
        # Reject deposits of zero or negative amounts
        raise HTTPException(status_code=400, detail="Minimum deposit is ₹1.")
    acc["balance"] += req.amount
    # Add the deposit amount to current balance
    acc["transactions"].append({
        # Record this transaction in the account's history
        "type":   "Deposit",                                      # Type of transaction
        "amount": req.amount,                                     # How much was deposited
        "date":   datetime.now().strftime("%d %b %Y, %I:%M %p")  # e.g. "25 Apr 2025, 03:45 PM"
    })
    return {
        "message":     f"₹{req.amount} deposited successfully!",  # Success message
        "new_balance": acc["balance"]                             # Updated balance
    }

# ─── WITHDRAW ─────────────────────────────────────────────────

@app.post("/api/withdraw")
# Called when user clicks "Withdraw" button and submits the withdrawal form
def withdraw(req: WithdrawRequest):
    acc = get_account(req.acc_no, req.pin)
    # Verify account and PIN before allowing any withdrawal
    if req.amount < 1:
        # Reject withdrawals of zero or negative amounts
        raise HTTPException(status_code=400, detail="Minimum withdrawal is ₹1.")
    if req.amount > acc["balance"]:
        # Reject if user is trying to withdraw more than they have
        raise HTTPException(status_code=400, detail="Insufficient balance.")
    acc["balance"] -= req.amount
    # Deduct the withdrawal amount from current balance
    acc["transactions"].append({
        # Record this transaction in the account's history
        "type":   "Withdrawal",                                   # Type of transaction
        "amount": req.amount,                                     # How much was withdrawn
        "date":   datetime.now().strftime("%d %b %Y, %I:%M %p")  # Timestamp
    })
    return {
        "message":     f"₹{req.amount} withdrawn successfully!",  # Success message
        "new_balance": acc["balance"]                             # Updated balance
    }

# ─── ACCOUNT: UPDATE ──────────────────────────────────────────

@app.put("/api/account/update")
# Called when user submits the "Update Account" form
def update_account(req: UpdateRequest):
    acc = get_account(req.acc_no, req.pin)
    # Verify PIN before allowing any changes to account
    if req.new_name:
        acc["name"] = req.new_name
        # Update name only if a new name was provided
    if req.new_email:
        acc["email"] = req.new_email
        # Update email only if a new email was provided
    if req.new_pin:
        acc["pin"] = req.new_pin
        # Update PIN only if a new PIN was provided
    return {"message": "Account updated successfully!"}
    # Confirm update to frontend

# ─── ACCOUNT: CLOSE ───────────────────────────────────────────

@app.delete("/api/account/close")
# Called when user confirms they want to permanently close their account
def close_account(req: CloseRequest):
    acc = get_account(req.acc_no, req.pin)
    # Verify PIN before permanently deleting anything
    del accounts_db[req.acc_no.upper()]
    # Permanently remove account from database — this cannot be undone
    return {"message": f"Account {req.acc_no} closed successfully."}
    # Confirm deletion to frontend

# ─── DOCS: UPLOAD ─────────────────────────────────────────────

from fastapi import UploadFile, File, Form
# UploadFile → handles file uploads (PDFs)
# File → marks a parameter as a file upload field
# Form → marks a parameter as a form text field (not JSON)

@app.post("/api/docs/upload")
# Called after account creation to upload Aadhaar, PAN and Address Proof PDFs
async def upload_docs(
    acc_no: str = Form(...),               # Account number sent as form field
    pin: int = Form(...),                  # PIN sent as form field for verification
    aadhaar: UploadFile = File(...),       # Aadhaar PDF uploaded by user (required)
    pan: UploadFile = File(...),           # PAN Card PDF uploaded by user (required)
    address_proof: UploadFile = File(...), # Address proof PDF uploaded by user (required)
    guardian_doc: Optional[UploadFile] = File(None),
    # Guardian ID PDF — only required for minor accounts, optional otherwise
):
    acc = get_account(acc_no, pin)
    # Verify account exists and PIN is correct before accepting documents
    acc["docsUploaded"] = True
    # Mark documents as uploaded in the account record
    # In production: save files to cloud storage like AWS S3 or Cloudinary
    # For now we just acknowledge receipt without storing the actual files
    return {"message": "Documents uploaded successfully!"}

# ─── STATS ────────────────────────────────────────────────────

@app.get("/api/stats")
# Called by the home page to show live bank statistics
def get_stats():
    total_accounts = len(accounts_db)
    # Count how many accounts currently exist in the database
    total_balance = sum(a["balance"] for a in accounts_db.values())
    # Add up all account balances across every account in the bank
    return {
        "total_accounts": total_accounts,  # Shown on home page as "Total Accounts"
        "total_balance":  total_balance    # Shown on home page as "Total Deposits"
    }