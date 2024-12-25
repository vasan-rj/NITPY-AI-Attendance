from werkzeug.security import generate_password_hash, check_password_hash
from config import mongo

class User:
    def __init__(self, email, password, role="student"):
        self.email = email
        self.password = generate_password_hash(password)
        self.role = role
    
    # Save the user to MongoDB
    def save(self):
        user = {
            "email": self.email,
            "password": self.password,
            "role": self.role
        }
        return mongo.db.users.insert_one(user)
    
    # Find user by email
    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({"email": email})
    
    # Check password
    @staticmethod
    def check_password(stored_password, input_password):
        return check_password_hash(stored_password, input_password)
