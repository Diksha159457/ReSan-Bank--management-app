# Import necessary modules for the FastAPI backend
from fastapi import FastAPI, HTTPException, UploadFile, File, Form  # FastAPI for building the API, HTTPException for errors, UploadFile/File/Form for file handling
from fastapi.middleware.cors import CORSMiddleware  # To handle Cross-Origin Resource Sharing for frontend-backend communication
from fastapi.staticfiles import StaticFiles  # To serve static files like CSS, JS from frontend directory
from fastapi.responses import FileResponse  # To serve the main HTML file
from pydantic import BaseModel  # For defining request/response models with validation
import json  # For reading/writing JSON data to resan_data.json file
import os  # For file system operations like creating directories
from datetime import datetime  # For handling dates and times in transactions
import random  # For generating random account numbers and OTPs
import string  # For string operations in generating account numbers
from twilio.rest import Client  # Twilio client for sending SMS

# Initialize in-memory databases (will be loaded from/saved to JSON file)
accounts_db = {}  # Dictionary to store all bank accounts data
transactions_db = {}  # Dictionary to store transaction history for each account
otp_store = {}  # Temporary store for OTPs during verification process

# Twilio configuration (set these as environment variables for security)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")  # Your Twilio Account SID
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")    # Your Twilio Auth Token
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER", "")  # Your Twilio phone number (e.g., +1234567890)
ENABLE_SMS = bool(TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_PHONE_NUMBER)  # Only enable if all credentials are set

# Initialize Twilio client if credentials are available
twilio_client = None
if ENABLE_SMS:
    try:
        twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        print("✓ Twilio SMS enabled")
        print("  Note: Free trial can only send to verified numbers.")
        print("  Upgrade your Twilio account to send to ANY number worldwide!")
        print("  Visit: https://console.twilio.com/us1/billing/manage-billing/billing-overview")
    except Exception as e:
        print(f"✗ Twilio initialization failed: {e}")
        ENABLE_SMS = False
else:
    print("✗ Twilio SMS disabled (set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER environment variables to enable)")
    print("  Running in DEV MODE - OTP will be shown in console and API responses")

# Load existing data from JSON file if it exists
try:
    with open("resan_data.json", "r") as f:  # Open the data file for reading
        data = json.load(f)  # Parse JSON data
        if isinstance(data, dict):  # Check if data is a dictionary
            accounts_db = data.get("accounts", {})  # Load accounts data
            transactions_db = data.get("transactions", {})  # Load transactions data
        else:
            # If data is not a dict (e.g., empty list), initialize empty
            accounts_db = {}
            transactions_db = {}
except FileNotFoundError:  # If file doesn't exist, continue with empty databases
    pass

# Function to save current data to JSON file
def save_data():
    with open("resan_data.json", "w") as f:  # Open file for writing
        json.dump({"accounts": accounts_db, "transactions": transactions_db}, f, indent=2)  # Save data with pretty formatting

# Create FastAPI application instance
app = FastAPI()  # Main application object

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,  # Enable CORS
    allow_origins=["*"],  # Allow all origins (in production, specify frontend URL)
    allow_credentials=True,  # Allow cookies/credentials
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Mount static files directory for serving frontend assets
app.mount("/static", StaticFiles(directory="frontend"), name="static")  # Serve CSS, JS, images from frontend/
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")  # Serve frontend files at /frontend/

# Route to serve the main HTML page
@app.get("/")  # GET request to root URL
async def serve_index():
    return FileResponse("frontend/index.html")  # Return the main HTML file

# Pydantic models for request validation
class CreateAccountRequest(BaseModel):  # Model for account creation request
    name: str  # User's full name
    age: int  # User's age
    email: str  # User's email
    phone: str  # User's phone number
    pin: int  # 4-digit PIN
    otp: str  # OTP for verification
    guardian_name: str = None  # Guardian name (for minors)
    guardian_age: int = None  # Guardian age
    guardian_relation: str = None  # Relationship to guardian
    guardian_phone: str = None  # Guardian phone
    guardian_email: str = None  # Guardian email

class LoginOTPRequest(BaseModel):  # Model for login OTP request
    acc_no: str  # Account number
    pin: int  # PIN

class VerifyOTPRequest(BaseModel):  # Model for OTP verification
    acc_no: str  # Account number
    pin: int  # PIN
    otp: str  # OTP code

class DepositRequest(BaseModel):  # Model for deposit request
    acc_no: str  # Account number
    pin: int  # PIN
    amount: int  # Amount to deposit

class WithdrawRequest(BaseModel):  # Model for withdrawal request
    acc_no: str  # Account number
    pin: int  # PIN
    amount: int  # Amount to withdraw

class DetailsRequest(BaseModel):  # Model for account details request
    acc_no: str  # Account number
    pin: int  # PIN

class UpdateRequest(BaseModel):  # Model for account update request
    acc_no: str  # Account number
    pin: int  # Current PIN
    new_name: str = None  # New name (optional)
    new_email: str = None  # New email (optional)
    new_pin: int = None  # New PIN (optional)

class CloseRequest(BaseModel):  # Model for account closure request
    acc_no: str  # Account number
    pin: int  # PIN

class SendOTPRequest(BaseModel):  # Model for sending OTP
    phone: str  # Phone number to send OTP to

# API Endpoints

# Endpoint to create a new bank account
@app.post("/api/account/create")  # POST request to create account
async def create_account(req: CreateAccountRequest):
    if req.otp not in otp_store or otp_store[req.otp] != req.phone:  # Verify OTP is valid and matches phone
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")  # Raise error if invalid
    del otp_store[req.otp]  # Remove used OTP
    acc_no = "RSN" + "".join(random.choices(string.digits, k=4))  # Generate unique account number
    while acc_no in accounts_db:  # Ensure uniqueness
        acc_no = "RSN" + "".join(random.choices(string.digits, k=4))
    account = {  # Create account data structure
        "accountNo": acc_no,
        "name": req.name,
        "age": req.age,
        "email": req.email,
        "phone": req.phone,
        "pin": req.pin,
        "balance": 0,  # Start with zero balance
        "accountType": "Minor Account" if req.age < 18 else "Savings Account",  # Determine account type
        "createdAt": datetime.now().isoformat(),  # Timestamp
        "docsUploaded": False,  # Documents not uploaded yet
        "guardian": None if req.age >= 18 else {  # Guardian info for minors
            "name": req.guardian_name,
            "age": req.guardian_age,
            "relationship": req.guardian_relation,
            "phone": req.guardian_phone,
            "email": req.guardian_email,
        }
    }
    accounts_db[acc_no] = account  # Store account
    transactions_db[acc_no] = []  # Initialize empty transaction list
    save_data()  # Save to file
    return {"accountNo": acc_no}  # Return account number

# Endpoint to request OTP for login
@app.post("/api/login/otp")  # POST request for login OTP
async def login_otp(req: LoginOTPRequest):
    if req.acc_no not in accounts_db:  # Check if account exists
        raise HTTPException(status_code=404, detail="Account not found.")
    if accounts_db[req.acc_no]["pin"] != req.pin:  # Verify PIN
        raise HTTPException(status_code=401, detail="Incorrect PIN.")
    
    otp = "".join(random.choices(string.digits, k=6))  # Generate 6-digit OTP
    phone = accounts_db[req.acc_no]["phone"]
    otp_store[otp] = phone  # Store OTP with phone
    
    # Send SMS if Twilio is enabled
    sms_sent = False
    if ENABLE_SMS and twilio_client:
        try:
            # Format phone number for international format
            phone_formatted = phone if phone.startswith("+") else "+91" + phone
            
            # Send SMS via Twilio
            message = twilio_client.messages.create(
                body=f"Your ReSan Bank login OTP is: {otp}. Valid for 5 minutes.",
                from_=TWILIO_PHONE_NUMBER,
                to=phone_formatted
            )
            sms_sent = True
            print(f"✓ Login OTP sent to {phone_formatted}: {message.sid}")
        except Exception as e:
            print(f"✗ SMS failed: {e}")
    
    # Return response
    response = {"message": "OTP sent successfully"}
    if not sms_sent:
        response["dev_otp"] = otp
        response["note"] = "SMS disabled - using dev mode"
    
    return response

# Endpoint to verify login OTP
@app.post("/api/login/verify")  # POST request to verify OTP
async def verify_login(req: VerifyOTPRequest):
    if req.otp not in otp_store or otp_store[req.otp] != accounts_db[req.acc_no]["phone"]:  # Verify OTP
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    del otp_store[req.otp]  # Remove used OTP
    return {  # Return account info
        "accountNo": req.acc_no,
        "name": accounts_db[req.acc_no]["name"]
    }

# Endpoint to deposit money
@app.post("/api/deposit")  # POST request for deposit
async def deposit(req: DepositRequest):
    if req.acc_no not in accounts_db:  # Check account exists
        raise HTTPException(status_code=404, detail="Account not found.")
    if accounts_db[req.acc_no]["pin"] != req.pin:  # Verify PIN
        raise HTTPException(status_code=401, detail="Incorrect PIN.")
    if req.amount > 100000:  # Check deposit limit
        raise HTTPException(status_code=400, detail="Deposit limit is ₹1,00,000.")
    accounts_db[req.acc_no]["balance"] += req.amount  # Add to balance
    transactions_db[req.acc_no].append({  # Record transaction
        "type": "Deposit",
        "amount": req.amount,
        "date": datetime.now().strftime("%d %b %Y, %I:%M %p")  # Formatted date
    })
    save_data()  # Save data
    return {"message": f"₹{req.amount:,} deposited successfully!"}  # Success message

# Endpoint to withdraw money
@app.post("/api/withdraw")  # POST request for withdrawal
async def withdraw(req: WithdrawRequest):
    if req.acc_no not in accounts_db:  # Check account exists
        raise HTTPException(status_code=404, detail="Account not found.")
    if accounts_db[req.acc_no]["pin"] != req.pin:  # Verify PIN
        raise HTTPException(status_code=401, detail="Incorrect PIN.")
    if accounts_db[req.acc_no]["balance"] < req.amount:  # Check sufficient balance
        raise HTTPException(status_code=400, detail="Insufficient balance.")
    accounts_db[req.acc_no]["balance"] -= req.amount  # Deduct from balance
    transactions_db[req.acc_no].append({  # Record transaction
        "type": "Withdrawal",
        "amount": req.amount,
        "date": datetime.now().strftime("%d %b %Y, %I:%M %p")
    })
    save_data()  # Save data
    return {"message": f"₹{req.amount:,} withdrawn successfully!"}  # Success message

# Endpoint to get account details
@app.post("/api/account/details")  # POST request for account details
async def account_details(req: DetailsRequest):
    if req.acc_no not in accounts_db:  # Check account exists
        raise HTTPException(status_code=404, detail="Account not found.")
    if accounts_db[req.acc_no]["pin"] != req.pin:  # Verify PIN
        raise HTTPException(status_code=401, detail="Incorrect PIN.")
    account = accounts_db[req.acc_no]  # Get account data
    return {  # Return detailed account info
        "accountNo": account["accountNo"],
        "name": account["name"],
        "age": account["age"],
        "email": account["email"],
        "phone": account["phone"],
        "balance": account["balance"],
        "accountType": account["accountType"],
        "createdAt": account["createdAt"],
        "docsUploaded": account["docsUploaded"],
        "guardian": account["guardian"],
        "transactions": transactions_db[req.acc_no][-20:]  # Last 20 transactions
    }

# Endpoint to update account information
@app.put("/api/account/update")  # PUT request for account update
async def update_account(req: UpdateRequest):
    if req.acc_no not in accounts_db:  # Check account exists
        raise HTTPException(status_code=404, detail="Account not found.")
    if accounts_db[req.acc_no]["pin"] != req.pin:  # Verify PIN
        raise HTTPException(status_code=401, detail="Incorrect PIN.")
    if req.new_name:  # Update name if provided
        accounts_db[req.acc_no]["name"] = req.new_name
    if req.new_email:  # Update email if provided
        accounts_db[req.acc_no]["email"] = req.new_email
    if req.new_pin:  # Update PIN if provided
        accounts_db[req.acc_no]["pin"] = req.new_pin
    save_data()  # Save changes
    return {"message": "Account updated successfully!"}  # Success message

# Endpoint to close/delete account
@app.delete("/api/account/close")  # DELETE request for account closure
async def close_account(req: CloseRequest):
    if req.acc_no not in accounts_db:  # Check account exists
        raise HTTPException(status_code=404, detail="Account not found.")
    if accounts_db[req.acc_no]["pin"] != req.pin:  # Verify PIN
        raise HTTPException(status_code=401, detail="Incorrect PIN.")
    del accounts_db[req.acc_no]  # Remove account
    del transactions_db[req.acc_no]  # Remove transactions
    save_data()  # Save changes
    return {"message": f"Account {req.acc_no} closed successfully."}  # Success message

# Endpoint to send OTP
@app.post("/api/otp/send")  # POST request to send OTP
async def send_otp(req: SendOTPRequest):
    otp = "".join(random.choices(string.digits, k=6))  # Generate 6-digit OTP
    otp_store[otp] = req.phone  # Store OTP with phone number
    
    # Send SMS if Twilio is enabled
    sms_sent = False
    if ENABLE_SMS and twilio_client:
        try:
            # Format phone number for international format (add +91 for India if not present)
            phone = req.phone
            if not phone.startswith("+"):
                phone = "+91" + phone  # Assuming Indian numbers
            
            # Send SMS via Twilio
            message = twilio_client.messages.create(
                body=f"Your ReSan Bank OTP is: {otp}. Valid for 5 minutes. Do not share this code.",
                from_=TWILIO_PHONE_NUMBER,
                to=phone
            )
            sms_sent = True
            print(f"✓ SMS sent to {phone}: {message.sid}")
        except Exception as e:
            print(f"✗ SMS failed: {e}")
            # Continue anyway - OTP is still valid for dev mode
    
    # Return response
    response = {"message": "OTP sent successfully"}
    if not sms_sent:
        # In development mode or if SMS fails, return OTP in response
        response["dev_otp"] = otp
        response["note"] = "SMS disabled - using dev mode"
    
    return response

# Endpoint to upload documents
@app.post("/api/docs/upload")  # POST request for document upload
async def upload_docs(
    acc_no: str = Form(...),  # Account number from form
    pin: int = Form(...),  # PIN from form
    aadhaar: UploadFile = File(...),  # Aadhaar PDF
    pan: UploadFile = File(...),  # PAN PDF
    address_proof: UploadFile = File(...),  # Address proof PDF
    guardian_doc: UploadFile = File(None)  # Guardian doc (optional)
):
    if acc_no not in accounts_db:  # Check account exists
        raise HTTPException(status_code=404, detail="Account not found.")
    if accounts_db[acc_no]["pin"] != pin:  # Verify PIN
        raise HTTPException(status_code=401, detail="Incorrect PIN.")
    os.makedirs("uploads", exist_ok=True)  # Create uploads directory if needed
    for file, name in [(aadhaar, "aadhaar"), (pan, "pan"), (address_proof, "address_proof")] + ([(guardian_doc, "guardian_doc")] if guardian_doc else []):  # Loop through files
        if file:  # If file exists
            with open(f"uploads/{acc_no}_{name}.pdf", "wb") as f:  # Open file for writing
                f.write(await file.read())  # Write file content
    accounts_db[acc_no]["docsUploaded"] = True  # Mark docs as uploaded
    save_data()  # Save data
    return {"message": "Documents uploaded successfully!"}  # Success message

# Endpoint to get transaction history
@app.get("/api/transactions/{acc_no}")  # GET request for transactions
async def get_transactions(acc_no: str):
    if acc_no not in transactions_db:  # Check if transactions exist
        return []  # Return empty list
    return transactions_db[acc_no][-20:]  # Return last 20 transactions

# Endpoint to get bank statistics
@app.get("/api/stats")  # GET request for stats
async def get_stats():
    total_accounts = len(accounts_db)  # Count total accounts
    total_balance = sum(acc["balance"] for acc in accounts_db.values())  # Sum all balances
    return {"total_accounts": total_accounts, "total_balance": total_balance}  # Return stats

# Run the server if this file is executed directly
if __name__ == "__main__":
    import uvicorn  # Import uvicorn for running the server
    uvicorn.run(app, host="0.0.0.0", port=8000)  # Start server on all interfaces, port 8000