from __future__ import annotations

import json
import random
import string
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "resan_data.json"
FRONTEND_DIR = BASE_DIR / "frontend"
UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(exist_ok=True)

app = FastAPI(title="ReSan Private Bank", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

accounts_db: dict[str, dict[str, Any]] = {}
otp_store: dict[str, str] = {}


def load_accounts() -> None:
    if not DATA_FILE.exists():
        DATA_FILE.write_text("[]", encoding="utf-8")
        return
    try:
        raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        DATA_FILE.write_text("[]", encoding="utf-8")
        return

    # Support both list and legacy dict format
    if isinstance(raw, dict):
        raw = list(raw.get("accounts", {}).values())
    if not isinstance(raw, list):
        return

    for record in raw:
        if not isinstance(record, dict):
            continue
        acc_no = str(record.get("accountNo", "")).strip().upper()
        if not acc_no:
            continue
        accounts_db[acc_no] = {
            "accountNo": acc_no,
            "name": record.get("name", "Unknown User"),
            "age": int(record.get("age", 18) or 18),
            "email": record.get("email", ""),
            "phone": str(record.get("phone", "")),
            "pin": int(record.get("pin", 0) or 0),
            "balance": float(record.get("balance", 0) or 0),
            "accountType": record.get("accountType")
            or ("Minor Account" if int(record.get("age", 18) or 18) < 18 else "Savings Account"),
            "docsUploaded": bool(record.get("docsUploaded", False)),
            "createdAt": record.get("createdAt") or datetime.now().isoformat(),
            "transactions": record.get("transactions", []) or [],
            "guardian": record.get("guardian"),
        }


def save_accounts() -> None:
    payload = list(accounts_db.values())
    DATA_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def generate_acc_no() -> str:
    alphabet = string.ascii_uppercase + string.digits
    while True:
        acc = "RS-" + "".join(random.choices(alphabet, k=8))
        if acc not in accounts_db:
            return acc


def generate_otp() -> str:
    return "".join(random.choices(string.digits, k=6))


def get_account(acc_no: str, pin: int) -> dict[str, Any]:
    acc = accounts_db.get(acc_no.upper())
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found.")
    if acc["pin"] != pin:
        raise HTTPException(status_code=401, detail="Incorrect PIN.")
    return acc


def append_transaction(acc: dict[str, Any], tx_type: str, amount: float) -> None:
    acc.setdefault("transactions", []).insert(
        0,
        {
            "type": tx_type,
            "amount": amount,
            "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
            "balance": acc["balance"],
        },
    )
    # Keep last 50 transactions
    acc["transactions"] = acc["transactions"][:50]


def validate_email(value: str) -> str:
    email = value.strip()
    if "@" not in email or "." not in email.split("@")[-1]:
        raise ValueError("Enter a valid email address.")
    return email


# ── Pydantic models ──────────────────────────────────────────────────────────

class OTPRequest(BaseModel):
    phone: str


class LoginOTPRequest(BaseModel):
    acc_no: str
    pin: int


class LoginVerifyRequest(BaseModel):
    acc_no: str
    pin: int
    otp: str


class SignupRequest(BaseModel):
    name: str
    age: int
    email: str
    phone: str
    pin: int
    otp: str
    guardian_name: Optional[str] = None
    guardian_age: Optional[int] = None
    guardian_relation: Optional[str] = None
    guardian_phone: Optional[str] = None
    guardian_email: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        digits = "".join(ch for ch in value if ch.isdigit())
        if len(digits) != 10:
            raise ValueError("Phone number must be 10 digits.")
        return digits

    @field_validator("pin")
    @classmethod
    def validate_pin(cls, value: int) -> int:
        if value < 1000 or value > 9999:
            raise ValueError("PIN must be 4 digits.")
        return value

    @field_validator("email")
    @classmethod
    def validate_signup_email(cls, value: str) -> str:
        return validate_email(value)


class AccountDetailsRequest(BaseModel):
    acc_no: str
    pin: int


class DepositRequest(BaseModel):
    acc_no: str
    pin: int
    amount: float


class WithdrawRequest(BaseModel):
    acc_no: str
    pin: int
    amount: float


class TransferRequest(BaseModel):
    from_acc: str
    pin: int
    to_acc: str
    amount: float


class UpdateRequest(BaseModel):
    acc_no: str
    pin: int
    new_name: Optional[str] = None
    new_email: Optional[str] = None
    new_pin: Optional[int] = None

    @field_validator("new_email")
    @classmethod
    def validate_update_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        return validate_email(value)


class CloseRequest(BaseModel):
    acc_no: str
    pin: int


# ── API Endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": "2.0.0"}


@app.post("/api/otp/send")
def send_otp(req: OTPRequest) -> dict[str, str]:
    otp = generate_otp()
    otp_store[req.phone] = otp
    # In production: integrate SMS gateway here
    return {"message": f"OTP sent to {req.phone}", "dev_otp": otp}


@app.post("/api/account/create")
def create_account(req: SignupRequest) -> dict[str, str]:
    saved_otp = otp_store.get(req.phone)
    if not saved_otp or saved_otp != req.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")

    if req.age < 18:
        guardian_fields = [req.guardian_name, req.guardian_age, req.guardian_relation, req.guardian_phone]
        if any(v in (None, "") for v in guardian_fields):
            raise HTTPException(status_code=400, detail="Guardian details are required for minor accounts.")

    acc_no = generate_acc_no()
    accounts_db[acc_no] = {
        "accountNo": acc_no,
        "name": req.name.strip(),
        "age": req.age,
        "email": str(req.email),
        "phone": req.phone,
        "pin": req.pin,
        "balance": 0.0,
        "accountType": "Minor Account" if req.age < 18 else "Savings Account",
        "docsUploaded": False,
        "createdAt": datetime.now().isoformat(),
        "transactions": [],
        "guardian": {
            "name": req.guardian_name,
            "age": req.guardian_age,
            "relationship": req.guardian_relation,
            "phone": req.guardian_phone,
            "email": str(req.guardian_email) if req.guardian_email else None,
        } if req.age < 18 else None,
    }
    save_accounts()
    otp_store.pop(req.phone, None)
    return {"message": "Account created successfully!", "accountNo": acc_no, "name": req.name}


@app.post("/api/login/otp")
def login_send_otp(req: LoginOTPRequest) -> dict[str, str]:
    acc = get_account(req.acc_no, req.pin)
    phone = acc.get("phone")
    if not phone:
        raise HTTPException(status_code=400, detail="No phone number on file.")
    otp = generate_otp()
    otp_store[phone] = otp
    return {"message": "OTP sent to registered phone.", "dev_otp": otp}


@app.post("/api/login/verify")
def login_verify_otp(req: LoginVerifyRequest) -> dict[str, Any]:
    acc = get_account(req.acc_no, req.pin)
    phone = acc.get("phone")
    if not phone:
        raise HTTPException(status_code=400, detail="Cannot verify OTP — no phone stored.")
    saved_otp = otp_store.get(phone)
    if not saved_otp or saved_otp != req.otp:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP.")
    otp_store.pop(phone, None)
    return {
        "message": "Login successful!",
        "accountNo": acc["accountNo"],
        "name": acc["name"],
        "balance": acc["balance"],
        "accountType": acc["accountType"],
    }


@app.post("/api/account/details")
def account_details(req: AccountDetailsRequest) -> dict[str, Any]:
    acc = get_account(req.acc_no, req.pin)
    return {k: v for k, v in acc.items() if k != "pin"}


@app.post("/api/deposit")
def deposit(req: DepositRequest) -> dict[str, Any]:
    acc = get_account(req.acc_no, req.pin)
    if req.amount < 1:
        raise HTTPException(status_code=400, detail="Minimum deposit is ₹1.")
    if req.amount > 1_000_000:
        raise HTTPException(status_code=400, detail="Single deposit limit is ₹10,00,000.")
    acc["balance"] += req.amount
    append_transaction(acc, "Credit", req.amount)
    save_accounts()
    return {"message": f"₹{req.amount:,.2f} deposited successfully!", "new_balance": acc["balance"]}


@app.post("/api/withdraw")
def withdraw(req: WithdrawRequest) -> dict[str, Any]:
    acc = get_account(req.acc_no, req.pin)
    if req.amount < 1:
        raise HTTPException(status_code=400, detail="Minimum withdrawal is ₹1.")
    if req.amount > acc["balance"]:
        raise HTTPException(status_code=400, detail=f"Insufficient balance. Available: ₹{acc['balance']:,.2f}")
    acc["balance"] -= req.amount
    append_transaction(acc, "Debit", req.amount)
    save_accounts()
    return {"message": f"₹{req.amount:,.2f} withdrawn successfully!", "new_balance": acc["balance"]}


@app.post("/api/transfer")
def transfer(req: TransferRequest) -> dict[str, Any]:
    from_acc = get_account(req.from_acc, req.pin)
    to_acc = accounts_db.get(req.to_acc.upper())
    if not to_acc:
        raise HTTPException(status_code=404, detail="Destination account not found.")
    if req.from_acc.upper() == req.to_acc.upper():
        raise HTTPException(status_code=400, detail="Cannot transfer to the same account.")
    if req.amount < 1:
        raise HTTPException(status_code=400, detail="Minimum transfer is ₹1.")
    if req.amount > from_acc["balance"]:
        raise HTTPException(status_code=400, detail=f"Insufficient balance. Available: ₹{from_acc['balance']:,.2f}")
    from_acc["balance"] -= req.amount
    to_acc["balance"] += req.amount
    append_transaction(from_acc, "Transfer Out", req.amount)
    append_transaction(to_acc, "Transfer In", req.amount)
    save_accounts()
    return {
        "message": f"₹{req.amount:,.2f} transferred to {to_acc['name']} successfully!",
        "new_balance": from_acc["balance"],
    }


@app.get("/api/transactions/{acc_no}")
def get_transactions(acc_no: str, pin: int) -> dict[str, Any]:
    acc = get_account(acc_no, pin)
    return {"transactions": acc.get("transactions", []), "balance": acc["balance"]}


@app.put("/api/account/update")
def update_account(req: UpdateRequest) -> dict[str, str]:
    acc = get_account(req.acc_no, req.pin)
    if req.new_name:
        acc["name"] = req.new_name.strip()
    if req.new_email:
        acc["email"] = str(req.new_email)
    if req.new_pin:
        if req.new_pin < 1000 or req.new_pin > 9999:
            raise HTTPException(status_code=400, detail="New PIN must be 4 digits.")
        acc["pin"] = req.new_pin
    save_accounts()
    return {"message": "Account updated successfully!"}


@app.delete("/api/account/close")
def close_account(req: CloseRequest) -> dict[str, str]:
    get_account(req.acc_no, req.pin)
    del accounts_db[req.acc_no.upper()]
    save_accounts()
    return {"message": f"Account {req.acc_no.upper()} closed successfully."}


@app.post("/api/docs/upload")
async def upload_docs(
    acc_no: str = Form(...),
    pin: int = Form(...),
    aadhaar: UploadFile = File(...),
    pan: UploadFile = File(...),
    address_proof: UploadFile = File(...),
    guardian_doc: Optional[UploadFile] = File(None),
) -> dict[str, str]:
    acc = get_account(acc_no, pin)
    required_files = [aadhaar, pan, address_proof]
    for f in required_files:
        if f.content_type and f.content_type != "application/pdf":
            raise HTTPException(status_code=400, detail=f"{f.filename} must be a PDF.")
        content = await f.read()
        if len(content) > 2 * 1024 * 1024:
            raise HTTPException(status_code=400, detail=f"{f.filename} exceeds 2MB limit.")
        dest = UPLOADS_DIR / f"{acc_no}_{f.filename}"
        dest.write_bytes(content)
    acc["docsUploaded"] = True
    save_accounts()
    return {"message": "Documents uploaded and verified successfully!"}


@app.get("/api/stats")
def get_stats() -> dict[str, Any]:
    total = len(accounts_db)
    total_bal = sum(float(a.get("balance", 0)) for a in accounts_db.values())
    savings = sum(1 for a in accounts_db.values() if a.get("accountType") == "Savings Account")
    minor = sum(1 for a in accounts_db.values() if a.get("accountType") == "Minor Account")
    return {
        "total_accounts": total,
        "total_balance": total_bal,
        "savings_accounts": savings,
        "minor_accounts": minor,
    }


load_accounts()
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
