from fastapi import APIRouter, HTTPException, Depends
from jose import JWTError, jwt
from passlib.context import CryptContext
import logging
import os

# Router for authentication
router = APIRouter()

log_file = "app.log"
if not os.path.exists(log_file):
    with open(log_file, "w") as file:
        pass  # Create an empty log file
# Configure logging
logging.basicConfig(
    filename=log_file,  # Log file name
    level=logging.INFO,  # Log level (INFO, DEBUG, WARNING, etc.)
    format="%(asctime)s - %(levelname)s - %(message)s"  # Add missing parenthesis here
)

# Password hashing utility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Hash the password
hashed_password = pwd_context.hash("password123")
print(hashed_password)
logging.info("This is a test log message.")
logging.info(f"Hashed password: {hashed_password}")

# Sample user data (replace with a proper database in production)
fake_users_db = {
    "user1": {"username": "user1", "hashed_password": "$2b$12$r.iooHd4/1Af5.eaV4tWL.RX3J/CFWqy76tVxEZmWt0aDSCaAGTNq"},
}

SECRET_KEY = "mysecretkey"  # Replace with a secure key
ALGORITHM = "HS256"

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def authenticate_user(username: str, password: str):
    user = fake_users_db.get(username)
    if not user or not verify_password(password, user["hashed_password"]):
        return False
    return user

@router.post("/login")
def login(username: str, password: str):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    token = jwt.encode({"sub": username}, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

