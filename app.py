from flask import Flask, render_template
from flask import request, jsonify, redirect, url_for
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)

# mongo db setup
app.config["MONGO_URI"] = "mongodb+srv://finalyearprojectnitpy:qGjMQJHiLViCMjH0@cluster0.24xm4.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.json['email']
        password = request.json['password']
        user = mongo.db.users.find_one({'email': email})

        if user and check_password_hash(user['password'], password):
            return jsonify({'message': 'Login successful!'}), 200
        else:
            return jsonify({'message': 'Invalid credentials'}), 401
    return 'Login Page'
    # return render_template('login.html')


# Route for the signup page
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    email = data['email']
    password = data['password']

    # Check if the user already exists
    if mongo.db.users.find_one({'email': email}):
        return jsonify({'message': 'User already exists'}), 409

    # Insert the new user into the database
    hash_password = generate_password_hash(password)
    mongo.db.users.insert_one({'email': email, 'password': hash_password})
    return jsonify({'message': 'User registered successfully!'}), 201


@app.route('/studentpage')
def studentpage():
    return render_template('studentpage.html')

@app.route('/facultypage')
def facultypage():
    return render_template('facultypage.html')

if __name__ == '__main__':
    app.run(debug=True)
