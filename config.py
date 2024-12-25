import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MONGO_URI = os.getenv('MONGO_URI')  # Set your MongoDB URI in environment variables
    # SECRET_KEY = os.getenv('SECRET_KEY')  # Use a secure random key for session management
    SECRET_KEY="MVP@123"
    MONGO_URI="mongodb+srv://Vasan_R:6DV1CN0ukOF83RcP@cluster0.wcrsf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    
    
    # mongodb+srv://Vasan_R:<db_password>@cluster0.wcrsf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
