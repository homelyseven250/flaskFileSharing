# An application using to serve files if the password for each file is correct

from flask import Flask, render_template, request, send_from_directory, abort, redirect, url_for
import os
import hashlib

# Initialize the Flask application
app = Flask(__name__)
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

# Index page
@app.route('/')
def index():
    return redirect(url_for('download'))

# Download page
@app.route('/download', methods=['GET', 'POST'])
def download():
    # A form which will ask for the name of the file to be downloaded if it is a get request
    if request.method == 'GET':
        return render_template('download.html')
    # If the request was a post request, find the file in the upload directory by hash and send it to the client
    elif request.method == 'POST':
                # Get the name of the file to be downloaded
        file_hash = request.form['file_hash']
        # Loop through the files in the upload directory and find the file with the matching hash
        for file in os.listdir(app.config['UPLOAD_FOLDER']):
                        # If the file has the hash, send it to the client
            if file_hash == hashlib.sha256(open(app.config['UPLOAD_FOLDER'] + file, 'rb').read()).hexdigest():
                return send_from_directory(app.config['UPLOAD_FOLDER'], file, as_attachment=True)
        # If the file was not found, return an error message
        abort(418)

# Upload page
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    # A form which will ask for the name of the file to be uploaded if it is a get request
    if request.method == 'GET':
        return render_template('upload.html')
    # If the request was a post request, find the file in the upload directory and save it to the upload directory
    elif request.method == 'POST':
                # Get the name of the file to be uploaded

        file = request.files['file']
        if file:
            if os.path.isfile(app.config['UPLOAD_FOLDER'] + file.filename):
                abort(409)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            return hashlib.sha256(open(app.config['UPLOAD_FOLDER'] + file.filename, 'rb').read()).hexdigest() + '''
            <a href="download"> Go to the download page!</a>'''
    abort(418)