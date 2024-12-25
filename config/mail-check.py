from flask import Flask, render_template, request
from flask_mail import Mail, Message
from pymongo import MongoClient

app = Flask(__name__)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Update with your email provider's SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'finalyearprojectnitpy@gmail.com'  # Replace with your email address
app.config['MAIL_PASSWORD'] = 'Smart@420'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@gmail.com'  # Replace with the sender's email address

mail = Mail(app)

# MongoDB Configuration
MONGO_URI = "your_mongodb_atlas_connection_string"  # Replace with your MongoDB Atlas connection string
DATABASE_NAME = "Attendance"
COLLECTION_NAME = "Students"

# Flask Route to Send Emails
@app.route('/send-emails', methods=['GET'])
def send_emails():
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        # Retrieve all student email addresses
        students = collection.find({}, {"email": 1, "_id": 0})  # Retrieve only the 'email' field
        email_list = [student['email'] for student in students]

        # Send emails
        for email in email_list:
            msg = Message(
                subject="Attendance Notification",
                recipients=[email],  # Recipient email address
                body="Dear Student,\n\nThis is a notification regarding your attendance.\n\nBest regards,\nAdmin"
            )
            mail.send(msg)
            print(f"Email sent to: {email}")

        return "Emails sent successfully to all students!", 200

    except Exception as e:
        print(f"Error: {e}")
        return "An error occurred while sending emails.", 500

if __name__ == '__main__':
    app.run(debug=True)
