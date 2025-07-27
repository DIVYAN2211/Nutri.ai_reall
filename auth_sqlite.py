import streamlit as st
import bcrypt
import sqlite3
import os
from typing import Optional, Dict, Any

# Database file path
DB_PATH = 'nutri_app.db'

def init_database():
    """Initialize SQLite database with users table"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get SQLite database connection"""
    return sqlite3.connect(DB_PATH)

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    """Check if password matches hash"""
    return bcrypt.checkpw(password.encode(), hashed.encode())

def register_user(username: str, email: str, password: str) -> bool:
    """Register a new user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username already exists
        cursor.execute('SELECT username FROM users WHERE username = ?', (username,))
        if cursor.fetchone():
            conn.close()
            return False
        
        # Hash password and insert user
        hashed_password = hash_password(password)
        cursor.execute(
            'INSERT INTO users (username, email, password) VALUES (?, ?, ?)',
            (username, email, hashed_password)
        )
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Registration error: {e}")
        return False

def login_user(username: str, password: str) -> bool:
    """Login user with username and password"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get user by username
        cursor.execute('SELECT password FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result and check_password(password, result[0]):
            return True
        return False
        
    except Exception as e:
        print(f"Login error: {e}")
        return False

def get_user_info(username: str) -> Optional[Dict[str, Any]]:
    """Get user information (excluding password)"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id, username, email, created_at FROM users WHERE username = ?',
            (username,)
        )
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return {
                'id': result[0],
                'username': result[1],
                'email': result[2],
                'created_at': result[3]
            }
        return None
        
    except Exception as e:
        print(f"Get user info error: {e}")
        return None

def update_user_profile(username: str, email: str) -> bool:
    """Update user profile information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE users SET email = ? WHERE username = ?',
            (email, username)
        )
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Update profile error: {e}")
        return False

def delete_user(username: str) -> bool:
    """Delete user account"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Delete user error: {e}")
        return False

# Initialize database when module is imported
init_database() 