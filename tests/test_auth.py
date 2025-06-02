"""
Tests for authentication endpoints.
"""
import pytest
from fastapi import status
import os
import sys

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_register_user(client):
    """Test user registration endpoint"""
    user_data = {
        "username": "newuser",
        "email": "new@example.com",
        "password": "password123",
        "role": "user"
    }
    response = client.post("/api/auth/register", json=user_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "password" not in data

def test_login_user(client, test_user):
    """Test user login endpoint"""
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    response = client.post("/api/auth/token", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_invalid_login(client):
    """Test login with invalid credentials"""
    login_data = {
        "username": "wronguser",
        "password": "wrongpass"
    }
    response = client.post("/api/auth/token", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, test_user):
    """Test getting current user details"""
    # First login to get token
    login_data = {
        "username": "testuser",
        "password": "testpass123"
    }
    login_response = client.post("/api/auth/token", data=login_data)
    token = login_response.json()["access_token"]
    
    # Use token to get user details
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
