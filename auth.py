import streamlit as st
import bcrypt
import os
from pymongo.collection import Collection

def get_user_collection(db) -> Collection:
    return db['users']

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

def check_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)

def register_user(db, username: str, email: str, password: str) -> bool:
    users = get_user_collection(db)
    if users.find_one({'username': username}):
        return False
    hashed = hash_password(password)
    users.insert_one({'username': username, 'email': email, 'password': hashed})
    return True

def login_user(db, username: str, password: str) -> bool:
    users = get_user_collection(db)
    user = users.find_one({'username': username})
    if not user:
        return False
    return check_password(password, user['password'])

def get_user_info(db, username: str):
    users = get_user_collection(db)
    return users.find_one({'username': username}, {'password': 0}) 