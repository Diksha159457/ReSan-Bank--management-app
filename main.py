# Import FastAPI class (used to create the backend application)
from fastapi import FastAPI  

# Import CORS middleware (used to allow frontend and backend to communicate)
from fastapi.middleware.cors import CORSMiddleware  

# Import BaseModel (used for request validation)
from pydantic import BaseModel  


# Create FastAPI app instance (this is your main backend app)
app = FastAPI()  


# -------------------- CORS CONFIGURATION --------------------

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,  # Enables communication between frontend & backend

    allow_origins=["https://resan-bank-app.netlify.app"],  
    # 🔥 CHANGE: Only allow your Netlify frontend (more secure than "*")

    allow_credentials=True,  
    # Allows cookies, authentication headers, sessions

    allow_methods=["*"],  
    # Allows all HTTP methods (GET, POST, PUT, DELETE)

    allow_headers=["*"],  
    # Allows all headers (Authorization, Content-Type, etc.)
)


# -------------------- DATA MODEL --------------------

# Define a structure for account data (instead of raw dict)
class Account(BaseModel):  
    name: str       # Account holder name
    balance: float  # Account balance


# -------------------- ROOT ROUTE --------------------

@app.get("/")  
def home():  
    # Runs when base URL is opened
    return {"message": "Backend is working!"}  
    # Returns JSON response


# -------------------- TEST ROUTE --------------------

@app.get("/test")  
def test():  
    # Simple API to check if backend is running
    return {"status": "API working fine"}  


# -------------------- GET ALL ACCOUNTS --------------------

@app.get("/accounts")  
def get_accounts():  
    # Simulated database (dummy data)
    accounts = [
        {"id": 1, "name": "Richa", "balance": 5000},
        {"id": 2, "name": "Amit", "balance": 12000},
    ]
    return {"accounts": accounts}  
    # Returns list of accounts


# -------------------- CREATE ACCOUNT --------------------

@app.post("/accounts")  
def create_account(account: Account):  
    # 🔥 CHANGE: Now using Account model instead of dict
    # FastAPI automatically validates input JSON
    
    return {
        "message": "Account created successfully",
        "data": account
    }  


# -------------------- UPDATE ACCOUNT --------------------

@app.put("/accounts/{account_id}")  
def update_account(account_id: int, account: Account):  
    # account_id comes from URL
    # account data comes from request body (validated)
    
    return {
        "message": f"Account {account_id} updated",
        "updated_data": account
    }  


# -------------------- DELETE ACCOUNT --------------------

@app.delete("/accounts/{account_id}")  
def delete_account(account_id: int):  
    # Deletes account using ID (dummy response)
    
    return {
        "message": f"Account {account_id} deleted successfully"
    }
