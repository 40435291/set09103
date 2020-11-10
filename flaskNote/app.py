from flask import Flask, render_template
from data import Notes 

app = Flask(__name__)

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


if __name__ == '__main__':
    app.run(debug=True)
# Debug Mode: On = (debug=True)