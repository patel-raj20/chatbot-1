"""
Admin User Promotion Script
============================
Promotes an existing user to admin role.

USAGE:
    python backend/promote_admin.py <username>

EXAMPLE:
    python backend/promote_admin.py john_doe

WHY:
    - No UI for admin promotion (by design)
    - Manual role assignment ensures security
    - Simple script for database update

SECURITY:
    - Only run this script with database access
    - Verify username before promotion
    - Consider logging all admin promotions
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User


def promote_to_admin(username: str):
    """
    Promote a user to admin role.
    
    Args:
        username: Username to promote
        
    Returns:
        True if successful, False otherwise
    """
    db: Session = SessionLocal()
    try:
        # Find user by username
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"❌ Error: User '{username}' not found")
            print("\nAvailable users:")
            all_users = db.query(User).all()
            for u in all_users:
                print(f"  - {u.username} (role: {u.role})")
            return False
        
        # Check if already admin
        if user.role == 'ADMIN':
            print(f"ℹ️  User '{username}' is already an admin")
            return True
        
        # Promote to admin
        old_role = user.role
        user.role = 'ADMIN'
        db.commit()
        
        print(f"✅ Success! User '{username}' promoted from '{old_role}' to 'admin'")
        print(f"\nUser details:")
        print(f"  - ID: {user.id}")
        print(f"  - Username: {user.username}")
        print(f"  - Role: {user.role}")
        print(f"  - Created: {user.created_at}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error promoting user: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def list_all_users():
    """List all users and their roles."""
    db: Session = SessionLocal()
    try:
        users = db.query(User).all()
        
        if not users:
            print("No users found in database")
            return
        
        print("\n📋 All Users:")
        print("-" * 60)
        for user in users:
            status = "🔴" if not user.is_active else "🟢"
            role_icon = "👑" if user.role == "ADMIN" else "👤"
            print(f"{status} {role_icon} {user.username:20} | Role: {user.role:10} | ID: {user.id}")
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")
    finally:
        db.close()


def main():
    """Main entry point."""
    print("=" * 60)
    print("         Admin User Promotion Script")
    print("=" * 60)
    
    # Check arguments
    if len(sys.argv) < 2:
        print("\n❌ Error: No username provided")
        print("\nUsage:")
        print("  python backend/promote_admin.py <username>")
        print("\nExamples:")
        print("  python backend/promote_admin.py john_doe")
        print("  python backend/promote_admin.py --list    # List all users")
        
        list_all_users()
        sys.exit(1)
    
    username = sys.argv[1]
    
    # Handle --list flag
    if username == "--list":
        list_all_users()
        sys.exit(0)
    
    # Confirm action
    print(f"\n⚠️  About to promote user '{username}' to admin role")
    print("This will grant full system access.\n")
    
    confirm = input("Continue? (yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("❌ Operation cancelled")
        sys.exit(0)
    
    # Promote user
    success = promote_to_admin(username)
    
    if success:
        print("\n✨ Admin promotion complete!")
        print("\nNext steps:")
        print("  1. User must log out and log back in")
        print("  2. New JWT token will include admin role")
        print("  3. User can now access /admin route")
    else:
        print("\n❌ Admin promotion failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
