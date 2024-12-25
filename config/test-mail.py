from flask import Flask
from flask_mail import Mail, Message

app = Flask(__name__)

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your SMTP server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'finalyearprojectnitpy@gmail.com'  # Replace with your email address
app.config['MAIL_PASSWORD'] = 'vfkf hmle lint ixja'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = ('NITPY AI Attendence', 'contact.vasanml@gmail.com')  # Default sender info

# Initialize Flask-Mail
mail = Mail(app)

@app.route('/')
def index():
    try:
        # Create a message
        msg = Message(
            subject='Test Email',  # Email subject
            recipients=['contact.vasan04@gmail.com','vassan11052004@gmail.com','bhamidimanjari@gmail.com,','POSAHEMANTH@gmail.com,'],  # Replace with recipient's email address
            body='Hello! This is a test email sent from Flask-Mail.'  # Email body
        )

        # Send the email
        mail.send(msg)
        return 'Email sent successfully!'
    except Exception as e:
        return f'Failed to send email: {str(e)}'

# print(send_email())

if __name__ == '__main__':
    app.run(debug=True)
