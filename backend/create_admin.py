"""
Create Admin User Script
=========================
Script to manually create the first admin user account.

WHY: Need at least one admin to access admin panel
WHERE: Run manually from command line
HOW: Creates user with admin role directly in database

USAGE:
    python backend/create_admin.py
    
    The script will prompt for:
    - Email address
    - Username  
    - Password
    
    Creates user with role='admin' and is_active=True
"""

import sys
import os
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from getpass import getpass

from app.database import SessionLocal, engine, Base
from app.models import User, UserRole
from app.core.security import hash_password
from app.core.logger import get_logger

logger = get_logger(__name__)


def create_admin_user():
    """
    Interactive script to create an admin user.
    
    FLOW:
        1. Prompt for email, username, password
        2. Check if user  already exists
        3. Create user with role='admin'
        4. Save to database
        5. Confirm creation
    """
    print("\n" + "="*60)
    print("CREATE ADMIN USER")
    print("="*60 + "\n")
    
    # Ensure database tables exist
    Base.metadata.create_all(bind=engine)
    
    # Get user input
    email = input("Enter admin email: ").strip()
    username = input("Enter admin username: ").strip()
    password = getpass("Enter admin password: ").strip()
    confirm_password = getpass("Confirm password: ").strip()
    
    # Validate input
    if not email or not username or not password:
        print("\n❌ Error: All fields are required!")
        return
    
    if password != confirm_password:
        print("\n❌ Error: Passwords do not match!")
        return
    
    if len(password) < 6:
        print("\n❌ Error: Password must be at least 6 characters!")
        return
    
    # Create database session
    db: Session = SessionLocal()
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            print(f"\n❌ Error: User with email '{email}' or username '{username}' already exists!")
            if existing_user.role == UserRole.ADMIN:
                print(f"   This user is already an admin.")
            else:
                print(f"\n   To promote existing user '{existing_user.username}' to admin:")
                print(f"   UPDATE users SET role='admin' WHERE email='{existing_user.email}';")
            return
        
        # Create admin user
        print("\n⏳ Creating admin user...")
        
        admin_user = User(
            email=email,
            username=username,
            hashed_password=hash_password(password),
            role=UserRole.ADMIN,  # Set as admin
            is_active=True
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"\n✅ Admin user created successfully!")
        print(f"\n" + "-"*60)
        print(f"ID:       {admin_user.id}")
        print(f"Email:    {admin_user.email}")
        print(f"Username: {admin_user.username}")
        print(f"Role:     {admin_user.role.value}")
        print(f"Active:   {admin_user.is_active}")
        print(f"Created:  {admin_user.created_at}")
        print("-"*60)
        
        print(f"\n✨ You can now login with:")
        print(f"   Email:    {admin_user.email}")
        print(f"   Password: [the password you entered]")
        print(f"\n   Admin panel will be accessible at: http://localhost:3000/admin")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error creating admin user: {e}")
        logger.error(f"Failed to create admin user: {e}")
    finally:
        db.close()


def list_users():
    """
    List all existing users.
    
    Useful to see current users in database.
    """
    print("\n" + "="*60)
    print("CURRENT USERS")
    print("="*60 + "\n")
    
    db: Session = SessionLocal()
    
    try:
        users = db.query(User).order_by(User.created_at.desc()).all()
        
        if not users:
            print("No users found in database.\n")
            return
        
        print(f"{'Email':<30} {'Username':<20} {'Role':<10} {'Active':<10}")
        print("-" * 70)
        
        for user in users:
            active_str = "✓" if user.is_active else "✗"
            print(f"{user.email:<30} {user.username:<20} {user.role.value:<10} {active_str:<10}")
        
        print()
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")
    finally:
        db.close()


def promote_user_to_admin():
    """
    Promote an existing user to admin role.
    
    FLOW:
        1. List all users 
        2. Prompt for email
        3. Update role to admin
        4. Confirm update
    """
    print("\n" + "="*60)
    print("PROMOTE USER TO ADMIN")
    print("="*60 + "\n")
    
    db: Session = SessionLocal()
    
    try:
        # Show existing users
        users = db.query(User).all()
        
        if not users:
            print("No users found in database.")
            print("Create a user first using the registration page.\n")
            return
        
        print("Existing users:")
        print(f"{'Email':<35} {'Username':<20} {'Current Role':<10}")
        print("-" * 65)
        for user in users:
            print(f"{user.email:<35} {user.username:<20} {user.role.value:<10}")
        print()
        
        # Get email to promote
        email = input("Enter email of user to promote to admin: ").strip()
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"\n❌ Error: User with email '{email}' not found!")
            return
        
        if user.role == UserRole.ADMIN:
            print(f"\n⚠️  User '{user.username}' is already an admin!")
            return
        
        # Confirm promotion
        confirm = input(f"\nPromote '{user.username}' ({user.email}) to admin? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("\n❌ Cancelled.")
            return
        
        # Update role
        old_role = user.role
        user.role = UserRole.ADMIN
        db.commit()
        
        print(f"\n✅ User '{user.username}' promoted from {old_role.value} to admin!")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error promoting user: {e}")
    finally:
        db.close()


def main():
    """
    Main menu for admin user management.
    """
    while True:
        print("\n" + "="*60)
        print("ADMIN USER MANAGEMENT")
        print("="*60)
        print("\n1. Create new admin user")
        print("2. List all users")
        print("3. Promote existing user to admin")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == '1':
            create_admin_user()
        elif choice == '2':
            list_users()
        elif choice == '3':
            promote_user_to_admin()
        elif choice == '4':
            print("\nGoodbye!\n")
            break
        else:
            print("\n❌ Invalid option. Please choose 1-4.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Cancelled by user.\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
        logger.error(f"Script error: {e}")
