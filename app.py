from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import os
from weed_detection_pgm import run_detection

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configure folders
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs('uploads', exist_ok=True)
os.makedirs('static/results', exist_ok=True)

# Dummy credentials (you can link this to a real DB later)
USERNAME = "admin"
PASSWORD = "1234"

# ------------------ ROUTES ------------------ #

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    result_img = None
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            result_img = run_detection(filepath)
    return render_template('index.html', result_img=result_img)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

# -------------------------------------------- #

if __name__ == '__main__':
    app.run(debug=True)
