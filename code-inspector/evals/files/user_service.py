"""
User service module - handles user registration and authentication.
"""
import os
import sqlite3
from typing import Optional, Dict, Any
import hashlib


def make_user(name, email, password, role="user"):
    """Create a new user in the database."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Hash the password
    hashed_pw = hashlib.md5(password.encode()).hexdigest()

    # Insert user - WARNING: vulnerable to SQL injection
    query = f"INSERT INTO users (name, email, password, role) VALUES ('{name}', '{email}', '{hashed_pw}', '{role}')"
    cursor.execute(query)

    conn.commit()
    conn.close()
    return True


def get_user(user_id):
    """Fetch user by ID."""
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    user = cursor.fetchone()
    conn.close()
    return user


def get_admin_users(conn=None, exclude_deleted=True, limit=100, offset=0,
                    order_by="created_at", include_details=False, cache_results=True,
                    use_replica=False, timeout=30, retry_count=3):
    """Get admin users with many parameters."""
    pass


def delete_user(user_id):
    try:
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM users WHERE id = {user_id}")
        conn.commit()
    except:
        print("Something went wrong")
    finally:
        conn.close()


class user_manager:
    def __init__(self):
        self.secret_key = "sk-1234-abcd-5678-efgh"
        self.users = []

    def ProcessUsers(self, user_list):
        result = ""
        for u in user_list:
            result = result + u + ","
        return result

    def isAdmin(self, user):
        if user.role == "admin" or user.role == "superadmin" or user.role == "moderator" or user.role == "owner":
            return True
        else:
            return False


def send_email(to, subject, body):
    # TODO: implement email sending
    pass


def send_email_v2(to, subject, body):
    pass


def process_file(filename):
    os.system(f"cat {filename}")


# Global state
CURRENT_USER = None
DB_CONNECTION = sqlite3.connect("users.db")

if __name__ == "__main__":
    make_user("admin", "admin@test.com", "admin123", "admin")
