from flask import Flask, render_template, flash, redirect, request, url_for, session, logging
from data import Notes
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt  

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/notes')
def notes():
    return render_template('notes.html', notes = Notes)

@app.route('/note/<string:id>/')
def note(id):
    return render_template('note.html', id=id)

@app.route('/help')
def help():
    return render_template('help.html')

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

        flash('You have successfully registered. Please log in.', 'success')

        return redirect(url_for('index'))
    return render_template('register.html', form=form)

class RegisterForm(Form):
    name = StringField('Name:', [validators.Length(min=1, max=50)])    
    username = StringField('Username:', [validators.Length(min=4, max=25)]) 
    email = StringField('Email:', [validators.Length(min=6, max=50)])
    password = PasswordField('Password:', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='The Passwords entered do not match')
    ])
    confirm = PasswordField('Repeat Password:')

if __name__ == '__main__':
    app.run(debug=True)
# Debug Mode: On = (debug=True)