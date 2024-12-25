from flask import request, jsonify, redirect, url_for, session
from models import User

# Handle student signup
def signup_user():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "student")  # Default role is student

    # Check if the user already exists
    if User.find_by_email(email):
        return jsonify({"message": "User already exists"}), 409

    # Create a new user and save to MongoDB
    new_user = User(email=email, password=password, role=role)
    new_user.save()

    return jsonify({"message": "Signup successful"}), 201

# Handle student login
def login_user():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    # Find the user by email
    user = User.find_by_email(email)
    if not user or not User.check_password(user["password"], password):
        return jsonify({"message": "Invalid credentials"}), 401

    # If credentials are correct, store user in session
    session['email'] = email
    session['role'] = user["role"]
    return jsonify({"message": "Login successful"}), 200
