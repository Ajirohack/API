"""
Create an admin user for the API.
"""
import sys
import os
import logging
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy.orm import Session
from database.connection import get_db_session
from services.user_service import UserService
from models import UserCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Create admin user if it doesn't exist"""
    logger.info("Checking for admin user...")
    
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@space.api")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")  # Change in production!
    
    db = next(get_db_session())
    user_service = UserService(db)
    
    # Check if admin exists
    existing_user = user_service.get_user_by_email(admin_email)
    if existing_user:
        logger.info(f"Admin user {admin_email} already exists")
        return
    
    # Create admin user
    admin_user = UserCreate(
        email=admin_email,
        username="admin",
        password=admin_password,
        is_admin=True
    )
    
    created_user = user_service.create_user(admin_user)
    logger.info(f"Created admin user: {created_user.email}")

if __name__ == "__main__":
    main()
