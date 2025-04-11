from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'cadet-secret'

# Simulated user store (replace with actual Samba commands)
users = []

@app.route('/')
def index():
    return render_template('index.html', users=users)

@app.route('/add', methods=['POST'])
def add_user():
    username = request.form.get('username')
    if username and username not in users:
        users.append(username)
        flash(f'User {username} added successfully!', 'success')
    else:
        flash('Invalid or duplicate username.', 'danger')
    return redirect(url_for('index'))

@app.route('/delete/<username>')
def delete_user(username):
    if username in users:
        users.remove(username)
        flash(f'User {username} deleted.', 'warning')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)