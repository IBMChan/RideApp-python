#to register and authenticate and register a new user. 
from typing import Dict, Optional
from models.user import Rider, Driver, UserRole, AbstractUser
from utils.db import users_col


class AuthService:
    def __init__(self):
        pass
#creating new user, assigning user id with user details
    def get_next_user_id(self) -> str:
        users = list(users_col.find())
        max_id = 0
        for u in users:
            uid = u.get("user_id", "")
            if isinstance(uid, int):
                max_id = max(max_id, uid)
            elif isinstance(uid, str) and uid and uid[0].upper() == 'U' and uid[1:].isdigit():
                max_id = max(max_id, int(uid[1:]))
        return f"U{max_id+1:03d}"

    def load_users(self) -> Dict[str, AbstractUser]:
        users: Dict[str, AbstractUser] = {}
        for u in users_col.find():
            role = UserRole(u["role"])
            if role == UserRole.RIDER:
                user = Rider(u["user_id"], u["full_name"], u["email"], u["phone"], u["password"], role)
            else:
                user = Driver(u["user_id"], u["full_name"], u["email"], u["phone"], u["password"], u.get("license_number", ""))
            users[u["email"]] = user
        return users

    def save_user(self, user: AbstractUser):
        doc = {
            "user_id": user.user_id,
            "full_name": user.name,
            "email": user.email,
            "phone": user.phone,
            "password": user.password,
            "role": user.role.value,
            "created_at": getattr(user, "created_at", None)
        }
        if hasattr(user, "license_number"):
            doc["license_number"] = user.license_number
        users_col.update_one({"email": user.email}, {"$set": doc}, upsert=True)

    
    def register_user(self, user: AbstractUser):
        if users_col.find_one({"email": user.email}):
            print("User already exists.")
        else:
            self.save_user(user)
            print(f"Registered {user}")

    def login(self, email: str, password: str) -> Optional[AbstractUser]:
        u = users_col.find_one({"email": email})
        if u and u["password"] == password:
            role = UserRole(u["role"])
            if role == UserRole.RIDER:
                user = Rider(u["user_id"], u["full_name"], u["email"], u["phone"], u["password"], role)
            else:
                user = Driver(u["user_id"], u["full_name"], u["email"], u["phone"], u["password"], u.get("license_number", ""))
            print(f"Welcome back, {user.name}.")
            return user
        print("Invalid credentials.")
        return None

    def update_password(self, email: str, new_password: str) -> bool:
        result = users_col.update_one({"email": email}, {"$set": {"password": new_password}})
        if result.matched_count == 0:
            print("No user found with this email.")
            return False
        print(f"Password updated successfully for {email}")
        return True

    def get_users(self) -> Dict[str, dict]:
        return {u["email"]: u for u in users_col.find()}
