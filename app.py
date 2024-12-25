from flask import Flask, render_template, send_file, session, flash, request, redirect, url_for
from flask_pymongo import PyMongo
from config import Config
from bcrypt import hashpw, gensalt, checkpw
import os,re
from dotenv import load_dotenv
import base64
from flask import Flask, request, jsonify
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message 
from datetime import datetime
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import cv2
from bson.objectid import ObjectId


load_dotenv()

app = Flask(__name__)
# mail config 
# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'finalyearprojectnitpy@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'vfkf hmle lint ixja'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = ('NITPY AI Attendance', 'contact.vasanml@gmail.com')  # Default sender info

# Initialize Flask-Mail
mail = Mail(app)

app.config['UPLOAD_FOLDER'] = './uploads'
app.config['OUTPUT_FOLDER'] = './outputs'

# Create folders if not exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)


# app.config.from_object(Config)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config['SECRET_KEY']=os.getenv("SECRET_KEY")
# app.config["MONGO_URI"] = os.getenv('MONGO_URI')
mongo = PyMongo(app)
client = MongoClient(app.config["MONGO_URI"])
db = client["Attendence"]

collection = db["Attendence_data"]

# Load the YOLO models
face_detection_model = YOLO(r"ai_models/yolov8m-face.pt")  # Face detection model
trained_model = YOLO(r"ai_models/best_2.pt")  # Custom trained model for roll numbers

attendance_records = []  # To store attendance details dynamically

def predict_and_label_faces_in_image(image_path, output_path):
    """
    Detect faces and recognize roll numbers. Annotate the image with results.
    Returns a list of detected roll numbers along with their confidence scores.
    """
    detected_roll_numbers = {}  # To store unique roll numbers and their confidence scores
    image = cv2.imread(image_path)
    
    # Step 1: Detect faces in the input image
    face_results = face_detection_model(image)
    for face_result in face_results:
        for box in face_result.boxes.xyxy:  # Iterate over each detected face
            x1, y1, x2, y2 = map(int, box)
            face = image[y1:y2, x1:x2]  # Crop the face
            
            # Step 2: Predict roll numbers using the trained model
            results = trained_model(face)
            for result in results:
                for class_id_tensor in result.boxes.cls:  # Iterate over detected classes
                    class_id = int(class_id_tensor.item())
                    if class_id in result.names:
                        roll_number = result.names[class_id]  # Extract roll number
                        confidence_score = result.boxes.conf[0].item()  # Get confidence score
                        
                        # Store roll number and confidence score if not already stored
                        if roll_number not in detected_roll_numbers:
                            tempx=confidence_score
                            temp=int(tempx*100)
                            # temp=int(temp)
                            confidence_score=temp
                            detected_roll_numbers[roll_number] = confidence_score
                        
                        # Annotate the image
                        for box in result.boxes.xyxy:
                            fx1, fy1, fx2, fy2 = map(int, box)
                            abs_x1, abs_y1, abs_x2, abs_y2 = x1 + fx1, y1 + fy1, x1 + fx2, y1 + fy2
                            cv2.rectangle(image, (abs_x1, abs_y1), (abs_x2, abs_y2), (0, 255, 0), 2)
                            cv2.putText(image, roll_number, (abs_x1, abs_y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Step 3: Save the annotated image
    cv2.imwrite(output_path, image)
    
    # Convert the dictionary to a list of tuples
    return [{"roll_number": roll} for roll, score in detected_roll_numbers.items()]


@app.route('/take-attendance', methods=['GET', 'POST'])
def take_attendance():
    if request.method == 'POST':
        attendance_records.clear()
        file = request.files['file']
        if file:
            # Save the uploaded image
            filename = secure_filename(file.filename)
            input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(input_path)
            
            # Generate output path and timestamp
            output_path = os.path.join(app.config['OUTPUT_FOLDER'], f"output_{filename}")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Process the image and extract roll numbers
            detected_roll_numbers = predict_and_label_faces_in_image(input_path, output_path)
            
            # Update attendance records with detected roll numbers and their confidence scores
            for entry in detected_roll_numbers:
               
                attendance_records.append({
                        "roll_number": entry["roll_number"], 
                        "timestamp": timestamp, 
                        # "confidence_score": entry["confidence_score"]
                    })
                
            attendance_records.sort(key=lambda record: datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S'), reverse=True)

            return render_template('take-attendance.html', output_image=None, records=attendance_records)
    return render_template('take-attendance.html', output_image=None, records=attendance_records)

@app.route("/add-to-database", methods=["POST"])
def add_to_database():
    try:
        data = request.json
        if not data:
            return jsonify({"message": "No data provided"}), 400

        collection.insert_one(data)
        return jsonify({"message": "Data successfully added to the database!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    """
    Allow users to download the processed image.
    """
    return send_file(os.path.join(app.config['OUTPUT_FOLDER'], filename), as_attachment=True)
# students_collection = db["Students"]

# Password validation function
def is_strong_password(password):
    # Check password length
    if len(password) < 6:
        return False
    # Check for uppercase, lowercase, digit, and special character
    if not re.search(r'[A-Z]', password):  # At least one uppercase letter
        return False
    if not re.search(r'[a-z]', password):  # At least one lowercase letter
        return False
    if not re.search(r'[0-9]', password):  # At least one digit
        return False
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):  # At least one special character
        return False
    return True
# mongo.db.Students.insert_one(student_data)

# print("MongoDB initialized:", mongo.db.Students.find({}))
all_students = mongo.db.Students.find()
# for student in all_students:
    # print(student)
@app.route('/')
def home():
    return render_template('index.html')

import base64

@app.route('/studentlogin', methods=['GET', 'POST'])
def login_student():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if mongo.db is None:
            print("MongoDB is not initialized")
            return "MongoDB connection error", 500
        
        # Fetch user from the database
        user = mongo.db.Students.find_one({'username': username})
        
        if user:
            # Extract the stored password and decode from the specified format
            stored_password_db_format = user.get('password', '')
            
            # Parse the base64 part of the stored password
            base64_password = stored_password_db_format.split("'")[1]
            stored_password = base64.b64decode(base64_password)
            
            # Verify the provided password
            if checkpw(password.encode('utf-8'), stored_password):
                session['user'] = username
                return redirect(url_for('dashboard_student'))
        
        flash('Invalid credentials. Please try again.')
        
    return render_template('studentlogin.html')



@app.route('/studentsignup', methods=['GET', 'POST'])
def signup_student():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('signup_student'))
        
        if not is_strong_password(password):
            flash('Password must be at least 6 characters long, contain uppercase and lowercase letters, at least one digit, and one special character.')
            return redirect(url_for('signup_student'))
        
        # Hash the password using bcrypt and encode in base64
        hashed_password = hashpw(password.encode('utf-8'), gensalt())
        base64_password = base64.b64encode(hashed_password).decode('utf-8')
        db_password_format = f"Binary.createFromBase64('{base64_password}', 0)"

        # Check if MongoDB is correctly initialized
        if mongo.db is None:
            raise Exception("MongoDB connection not initialized. Check MONGO_URI configuration.")
        
        # Insert user into MongoDB
        mongo.db.Students.insert_one({
            'username': username,
            'password': db_password_format
        })
        flash('Signup successful! Please login.')
        return redirect(url_for('login_student'))
    
    return render_template('studentsignup.html')



@app.route('/dashboard_student')
def dashboard_student():
    if 'user' in session:
        username = session['user']
        return render_template('dashboard_student.html', username=username)
    return redirect(url_for('login_student'))

@app.route('/student-settings')
def student_settings():
    return render_template('students-settings.html')

@app.route('/update_user_settings', methods=['POST'])
def update_user_settings():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    phone = data.get("phone")
    current_password = data.get("currentPassword")
    new_password = data.get("newPassword")
    images = data.get("images")  # Base64-encoded image list

    # Fetch the user document
    student = mongo.db.Students.find_one({"username": username})

    if not student or "password" not in student:
        return jsonify({"message": "User not found."}), 400

    # Decode the stored password, if in bytes
    try:
        stored_password = student["password"].decode("utf-8")
    except AttributeError:
        stored_password = student["password"]

    # Password validation if currentPassword is provided
    if current_password:
        if ":" in stored_password:  # Checking hash format
            if not check_password_hash(stored_password, current_password):
                return jsonify({"message": "Current password is incorrect"}), 400
        else:
            return jsonify({"message": "Invalid password format in the database"}), 500

    # Prepare update data
    update_data = {"email": email, "phone": phone}
    if new_password:
        update_data["password"] = generate_password_hash(new_password)

    # Store images if provided
    if images:  # Ensure all 12 images are present
        try:
            # Decode images from base64 and store in database
            update_data["images"] = [base64.b64decode(img) for img in images]
        except Exception as e:
            print(f"Error decoding images: {e}")
            return jsonify({"message": "Failed to process images."}), 500
    else:
        return jsonify({"message": "Please upload all 12 images."}), 400

    # Perform the update
    mongo.db.Students.update_one({"username": username}, {"$set": update_data})
    print("***"*3)
    print(len(update_data['images']))

    return jsonify({"message": "Settings updated successfully."})

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('You have been logged out.')
    return redirect(url_for('home'))


@app.route('/facultysignup', methods=['GET', 'POST'])
def signup_faculty():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('signup_faculty'))
        
        if not is_strong_password(password):
            flash('Password must be at least 6 characters long, contain uppercase and lowercase letters, at least one digit, and one special character.')
            return redirect(url_for('signup_faculty'))
        
        hashed_password = hashpw(password.encode('utf-8'), gensalt())
        print(f'hashed_password:{hashed_password}')

        # Check if mongo.db is correctly initialized
        if  mongo.db is None:
            raise Exception("MongoDB connection not initialized. Check MONGO_URI configuration.")
        
        # Insert user into MongoDB
        mongo.db.Faculty.insert_one({'username': username, 'password': hashed_password})
        flash('Signup successful! Please login.')
        return redirect(url_for('login_faculty'))
    
    return render_template('/faculty/facultysignup.html')

@app.route('/facultylogin', methods=['GET', 'POST'])
def login_faculty():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if mongo.db is None:
            print("MongoDB is not initialized")
            return "MongoDB connection error", 500
        
        user = mongo.db.Faculty.find_one({'username': username})
        
        if user and checkpw(password.encode('utf-8'), user['password']):
            session['user'] = username
            return redirect(url_for('dashboard_faculty'))
        
        flash('Invalid credentials. Please try again.')
        
    return render_template('/faculty/facultylogin.html')

@app.route('/faculty-settings')
def faculty_settings():
    if 'user' in session:
        username = session['user']
    return render_template('/faculty/faculty-settings.html',username=username)

@app.route('/mail-service', methods=['GET', 'POST'])
def mail_service():
    print('hello')
    try:
        # Fetch Attendance data
        # attendance_data = mongo.db.Attendance_data.find({})
        attendance_col = db['Attendence_data']
        print(attendance_col)
        attendance_data = list(attendance_col.find({}))
        # 
        print("Attendance Records:", (attendance_data))
        print('hi')
        for i in attendance_data:
            print("***"*3)
            print(i)
            
        # Prepare a list to store attendance details along with student info
        detailed_attendance = []

        # Loop through each attendance record
        for record in attendance_data:
            subject = record.get('subject', 'N/A')
            date = record.get('date', 'N/A')
            

            present_students = record.get('present_students', [])

            # For each student in the present_students list, fetch name and email
            student_info = []
            for roll_number in present_students:
                # Fetch student details from the Students collection
                student = mongo.db['Students'].find_one({'username': roll_number})

                if student:
                    # Add student details to the list (name, email)
                    student_name = student.get('student_name', 'N/A')
                    student_email = student.get('email', 'N/A')
                else:
                    # In case student is not found
                    student_name = 'N/A'
                    student_email = 'N/A'

                student_info.append({
                    'roll_number': roll_number,
                    'name': student_name,
                    'email': student_email
                })
            print(student_info)
            # Add the attendance record with student details
            detailed_attendance.append({
                'subject': subject,
                'date': date,
                'students': student_info
            })
            
            if request.method == 'POST':
                email_addresses = request.form.getlist('email_addresses')
                subject = request.form.get('subject')
                date = request.form.get('date')
                time = request.form.get('time')
                send_email(email_addresses,subject,date,time)  # Call the function to send email
                flash("Email sent successfully!", 'success')  # Flash success message
                return redirect(url_for('mail_service'))  # Redirect to the same page to display the message

        # return render_template('mail-service.html', attendance_data=detailed_attendance)

        return render_template('/faculty/mail-service.html', attendance_data=detailed_attendance)
    
    except Exception as e:
        print("Error Fetching Data xxx :", e)
        return "Error fetching attendance data."

def send_email(recipients,subject,date,time):
    body = f"You have been marked present for  today's  {subject} class ({date}) ."

    try:
        msg = Message(
            subject="Your Todays's Attendance Records",  # Subject of the email
            recipients=recipients,  # List of recipient emails
            body=body
        )
        mail.send(msg)  # Send the email
        print(f"Email sent to {', '.join(recipients)}")
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


@app.route('/dashboard_faculty')
def dashboard_faculty():
    
    if 'user' in session:
        username = session['user']
        return render_template('/faculty/facultypage.html',username=username)
    return redirect(url_for('login_faculty'))

@app.route('/update_faculty_settings', methods=['POST'])
def update_faculty_settings():
    data = request.get_json()
    faculty_id = data.get("facultyId")
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    department = data.get("department")
    current_password = data.get("currentPassword")
    new_password = data.get("newPassword")
    subjects = data.get("subjects", [])  # List of subjects
    
    # Fetch the faculty document
    faculty = mongo.db.Faculty.find_one({"username": faculty_id})

    if not faculty:
        return jsonify({"message": "Faculty member not found."}), 400

    # Decode the stored password if in bytes
    try:
        stored_password = faculty["password"].decode("utf-8")
    except AttributeError:
        stored_password = faculty["password"]

    # Password validation if currentPassword is provided
    if current_password:
        if ":" in stored_password:  # Checking hash format
            if not check_password_hash(stored_password, current_password):
                return jsonify({"message": "Current password is incorrect"}), 400
        else:
            return jsonify({"message": "Invalid password format in the database"}), 500

    # Prepare update data
    update_data = {
        "username": name,
        "email": email,
        "phone": phone,
        "department": department,
        "subjects": subjects
    }
    
    # Update the password if new_password is provided
    if new_password:
        update_data["password"] = generate_password_hash(new_password)

    # Perform the update
    try:
        mongo.db.Faculty.update_one({"username": faculty_id}, {"$set": update_data})
        return jsonify({"message": "Faculty settings updated successfully."})
    except Exception as e:
        print(f"Error updating faculty settings: {e}")
        return jsonify({"message": "Failed to update settings."}), 500

if __name__ == '__main__':
    app.run(debug=True, host="127.0.0.1" , port=5001)
    