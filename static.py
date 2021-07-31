from flask import Flask, send_from_directory
import os


app = Flask(__name__)

@app.route('/<path:path>')
@app.route('/')
def send_file(path=''):
    if '' == os.path.basename(path):
        path = path + 'index.html'
    _, ext = os.path.splitext(path)
    if ext == '':
        path += '.html'
    return send_from_directory('baked/norm', path)

app.run(port='8080', debug=True)
