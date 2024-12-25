import pandas as pd
from pymongo import MongoClient
from bcrypt import hashpw, gensalt
import base64

# MongoDB Configuration
MONGO_URI = "your_mongodb_atlas_connection_string"  # Replace with your MongoDB Atlas connection string
DATABASE_NAME = "Attendance"
COLLECTION_NAME = "Students"

def hash_password_to_base64(password):
    """
    Hash the password using bcrypt and convert it to Base64 format.
    """
    hashed_password = hashpw(password.encode('utf-8'), gensalt())
    base64_password = base64.b64encode(hashed_password).decode('utf-8')
    return f"Binary.createFromBase64('{base64_password}', 0)"

def upload_data_to_mongodb(excel_file):
    # Step 1: Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # Step 2: Read Excel File
    data = pd.read_excel(excel_file)

    # Step 3: Iterate through rows and upload data
    for _, row in data.iterrows():
        document = {
            "username": row["Roll No"],  # Roll number as username
            "student_name": row["Student Name"],  # Student name
            "email": row["Email"],  # Email address
            "password": hash_password_to_base64(row["Password"])  # Hashed password in Base64
        }
        collection.insert_one(document)
        print(f"Inserted: {document}")

    print("Data upload completed successfully.")

if __name__ == "__main__":
    # Path to the Excel file
    excel_file_path = "path_to_your_excel_file.xlsx"  # Update with your Excel file path
    upload_data_to_mongodb(excel_file_path)
