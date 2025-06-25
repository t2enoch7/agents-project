import hashlib
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
import json

# Simple token storage (in production, use Redis or database)
tokens = {}

def create_simple_token(email: str, date_of_birth: str) -> str:
    """Create a simple token based on email and date of birth"""
    token_data = f"{email}:{date_of_birth}:{datetime.now().timestamp()}"
    token = hashlib.sha256(token_data.encode()).hexdigest()
    tokens[token] = {
        "email": email,
        "date_of_birth": date_of_birth,
        "created_at": datetime.now(),
        "expires_at": datetime.now() + timedelta(hours=24)
    }
    return token

def verify_token(token: str) -> Optional[dict]:
    """Verify a token and return user data"""
    if token not in tokens:
        return None

    user_data = tokens[token]
    if datetime.now() > user_data["expires_at"]:
        del tokens[token]
        return None

    return user_data

def get_current_user(token: str):
    """Get current user from token"""
    user_data = verify_token(token)
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    return user_data
