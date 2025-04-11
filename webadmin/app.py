from flask import Flask, render_template, request, redirect, url_for, flash, session
import subprocess
import logging
import pexpect
from functools import wraps
import pam

app = Flask(__name__)
app.secret_key = 'cadet-secret'

# Simulated admin credentials (replace with a secure method in production)

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

pam_auth = pam.pam()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('You need to log in to access this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        logging.debug("User already logged in. Redirecting to dashboard.")
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        logging.debug(f"Attempting to authenticate user: {username}")
        if pam_auth.authenticate(username, password):
            logging.debug(f"Authentication successful for user: {username}")
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            logging.debug(f"Authentication failed for user: {username}")
            flash('Invalid credentials.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    users = subprocess.getoutput("sudo pdbedit -L").splitlines()
    return render_template('index.html', users=users)

@app.route('/add', methods=['POST'])
@login_required
def add_user():
    username = request.form.get('username')
    password = request.form.get('password')
    if username and password:
        try:
            # Check if the Linux user exists
            user_check = subprocess.run(["id", username], capture_output=True, text=True)
            if user_check.returncode != 0:
                # Create the Linux user if it does not exist
                logging.debug(f"User {username} does not exist. Creating Linux user.")
                create_user = subprocess.run(["sudo", "useradd", "-m", username], capture_output=True, text=True)
                if create_user.returncode != 0:
                    flash(f"Failed to create Linux user {username}: {create_user.stderr}", 'danger')
                    return redirect(url_for('index'))

            # Add the user as an SMB user
            command = f"sudo smbpasswd -a {username}"
            logging.debug(f"Executing command: {command}")
            child = pexpect.spawn(command)
            child.expect('New SMB password:')
            child.sendline(password)
            child.expect('Retype new SMB password:')
            child.sendline(password)
            child.expect(pexpect.EOF)
            output = child.before.decode('utf-8')
            logging.debug(f"Command output: {output}")
            if 'Failed to add entry' in output:
                flash(f'Failed to add user {username}: {output}', 'danger')
            else:
                flash(f'User {username} added successfully!', 'success')
        except Exception as e:
            logging.error(f"Exception occurred while adding user: {str(e)}")
            flash(f'Error: {str(e)}', 'danger')
    else:
        flash('Invalid username or password.', 'danger')
    return redirect(url_for('index'))

@app.route('/delete/<username>')
@login_required
def delete_user(username):
    try:
        process = subprocess.run(["sudo", "smbpasswd", "-x", username], capture_output=True, text=True)
        if process.returncode == 0:
            flash(f'User {username} deleted.', 'warning')
        else:
            flash(f'Failed to delete user {username}: {process.stderr}', 'danger')
    except Exception as e:
        flash(f'Error: {str(e)}', 'danger')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)