from flask import Blueprint, render_template
from controllers import signup_user, login_user

auth = Blueprint('auth', __name__)

# Render the student login page
@auth.route('/studentlogin', methods=['GET'])
def student_login_page():
    return render_template('studentlogin.html')

# Handle student login
@auth.route('/api/auth/login', methods=['POST'])
def login():
    return login_user()

# Render the student signup page
@auth.route('/studentsignup', methods=['GET'])
def student_signup_page():
    return render_template('studentsignup.html')

# Handle student signup
@auth.route('/api/auth/signup', methods=['POST'])
def signup():
    return signup_user()

# Student dashboard (after login)
@auth.route('/studentpage', methods=['GET'])
def student_dashboard():
    return render_template('studentpage.html')
