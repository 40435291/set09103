from flask import Flask, render_template, flash, redirect, request, url_for, session, logging, g
from data import Notes
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt 
from functools import wraps

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# MySQL (Connection)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'pw'
app.config['MYSQL_DB'] = 'flasknote'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# MySQL (Initialisation)
mysql = MySQL(app)

Notes = Notes()

# Index
@app.route('/')
def index():
    return render_template('index.html')

# Notes
@app.route('/notes')
def notes():
    return render_template('notes.html', notes = Notes)

# Note
@app.route('/note/<string:id>/')
def note(id):
    return render_template('note.html', id=id)

# Help
@app.route('/help')
def help():
    return render_template('help.html')

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        email = form.email.data
        password = sha256_crypt.hash(str(form.password.data))

        # Create Cursor
        cur = mysql.connection.cursor()
        
        # Database query
        cur.execute("INSERT INTO users(name, username, email,password) VALUES(%s, %s, %s, %s)", (name, username, email, password))
        
        # Commit to Database
        mysql.connection.commit()
        
        # Close DB connection
        cur.close()

        flash('You have successfully registered.', 'success')

        return redirect(url_for('index'))
    return render_template('register.html', form=form)

# Login functionality
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Capture Form Data
        username = request.form['username']
        password_entered = request.form['password']

        # Create Cursor
        cur = mysql.connection.cursor()

        # Select user (by username)
        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:
            # Retrieve stored details (1st match from "result")
            data = cur.fetchone()
            password = data['password']
            name = data['name']


            # Password comparison
            if sha256_crypt.verify(password_entered, password):
                # Session started (password validation passed)
                session['logged_in'] = True
                session['username'] = username
                session['name'] = name

                flash('Login successful', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = "Password Invalid. Please re-enter."
                return render_template('login.html', error=error)

            # Close DB connection
            cur.close()
        
        else:
            error = "Incorrect Username. Please try again."
            return render_template('login.html', error = error)
    return render_template('login.html')

# Check if user is logged in
def is_logged_in(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Please login to access the Dashboard', 'danger')
            return redirect(url_for('login', next=request.url))
    return decorated_function    

# Logout functionality
@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You have successfully logged out', 'success')
    return redirect(url_for('login'))

# Dashboard
@app.route('/dashboard')
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

# Add Note
@app.route('/add_note', methods=['GET', 'POST'])
@is_logged_in
def add_note():
    form = NoteForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        description = form.description.data

        # Create Cursor
        cur = mysql.connection.cursor()
        
        # Database query
        cur.execute("INSERT INTO notes(title, description, author) VALUES(%s, %s, %s)", (title, description, session['name']))
        
        # Commit to Database
        mysql.connection.commit()
        
        # Close DB connection
        cur.close()

        flash('Note added.', 'success')

        return redirect(url_for('dashboard'))
    return render_template('add_note.html', form=form)


# Register Form
class RegisterForm(Form):
    name = StringField('Name:', [validators.Length(min=1, max=50)])    
    username = StringField('Username:', [validators.Length(min=4, max=25)]) 
    email = StringField('Email:', [validators.Length(min=6, max=50)])
    password = PasswordField('Password:', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='The Passwords entered do not match')
    ])
    confirm = PasswordField('Repeat Password:')

# Notes Form
class NoteForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])    
    description = TextAreaField('Description', [validators.Length(min=25)]) 

    

if __name__ == '__main__':
    app.run(debug=True)
# Debug Mode: On = (debug=True)