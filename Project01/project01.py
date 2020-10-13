from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
	return '<div><div><h1>Project01 - Advanced Web Technologies</h1><p><h2>Hello Napier!!!</h2></p></div></div>'
