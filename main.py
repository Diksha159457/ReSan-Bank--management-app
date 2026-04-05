# Import FastAPI class (used to create the backend application)
from fastapi import FastAPI  

# Import CORS middleware (used to allow frontend and backend to communicate)
from fastapi.middleware.cors import CORSMiddleware  


# Create FastAPI app instance (this is your main backend app)
app = FastAPI()  


# -------------------- CORS CONFIGURATION --------------------

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,  # Enables CORS handling

    allow_origins=["*"],  
    # Allows requests from ANY frontend (Netlify, localhost, etc.)
    # "*" = no restriction (good for testing, restrict later for security)

    allow_credentials=True,  
    # Allows cookies, authentication headers, login sessions

    allow_methods=["*"],  
    # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)

    allow_headers=["*"],  
    # Allows all types of headers (Authorization, Content-Type, etc.)
)


# -------------------- ROOT ROUTE --------------------

# Define a GET API at the root URL "/"
@app.get("/")  
def home():  
    # This function runs when user opens base URL
    return {"message": "Backend is working!"}  
    # Returns JSON response


# -------------------- TEST ROUTE --------------------

# Define another GET API for testing
@app.get("/test")  
def test():  
    # This endpoint is useful to check if API is running
    return {"status": "API working fine"}  


# -------------------- SAMPLE DATA ROUTE --------------------

# Example: return some dummy bank data
@app.get("/accounts")  
def get_accounts():  
    # Simulated data (you can replace with database later)
    accounts = [
        {"id": 1, "name": "Richa", "balance": 5000},
        {"id": 2, "name": "Amit", "balance": 12000},
    ]
    return {"accounts": accounts}  


# -------------------- CREATE DATA ROUTE --------------------

# Example: POST API to add account
@app.post("/accounts")  
def create_account(account: dict):  
    # Accepts JSON data from frontend
    # Example input: {"name": "Riya", "balance": 3000}
    
    return {
        "message": "Account created successfully",
        "data": account
    }  


# -------------------- UPDATE DATA ROUTE --------------------

# Example: update account using PUT
@app.put("/accounts/{account_id}")  
def update_account(account_id: int, account: dict):  
    # account_id comes from URL
    # account data comes from request body
    
    return {
        "message": f"Account {account_id} updated",
        "updated_data": account
    }  


# -------------------- DELETE DATA ROUTE --------------------

# Example: delete account
@app.delete("/accounts/{account_id}")  
def delete_account(account_id: int):  
    # Deletes account using ID
    
    return {
        "message": f"Account {account_id} deleted successfully"
    }  
