from flask import session, redirect, url_for

def login_required(func):
    def wrapper(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('auth.student_login_page'))  # Redirect to login if not authenticated
        return func(*args, **kwargs)
    return wrapper
