from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/studentpage')
def studentpage():
    return render_template('studentpage.html')

@app.route('/facultypage')
def facultypage():
    return render_template('facultypage.html')

if __name__ == '__main__':
    app.run(debug=True)
