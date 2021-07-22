# An application using to serve files if the password for each file is correct

from flask import Flask, render_template, request, send_from_directory, abort, redirect, url_for
import os, json, bcrypt, secrets, hashlib

# Initialize the Flask application
app = Flask(__name__)
# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'

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
        file_name = request.form['file_name']
        # check if the file exists
        if os.path.isdir(app.config['UPLOAD_FOLDER'] + file_name):
            #check if the password is correct from the json file
            with open(os.path.join(app.config['UPLOAD_FOLDER'], file_name, 'data.json')) as json_file:
                data = json.load(json_file)
                #check if the password is correct
                if bcrypt.checkpw(request.form['password'].encode('utf-8'), data['password']):
                    #send the file to the client
                    return send_from_directory(app.config['UPLOAD_FOLDER'] + file_name, file_name, as_attachment=True)
                else:
                    abort(403)
        else:
            abort(404)
    else:
        abort(405)


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
            if os.path.isdir(app.config['UPLOAD_FOLDER'] + file.filename):
                abort(409)
            else:
                os.mkdir(app.config['UPLOAD_FOLDER'] + file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename, file.filename))
                with open(os.path.join(app.config['UPLOAD_FOLDER'], file.filename, "data.json"), 'w') as dataJson:
                    json.dump({"password":bcrypt.hashpw(request.form['password'], bcrypt.gensalt(12)), "fileName":file.filename, "browserAuth":secrets.token_urlsafe(1024)}, dataJson)

                return redirect(url_for('upload'))
        else:
            abort(400)
    else:
        abort(405)

# Download a file from a link 
@app.route("/download/<file_name>/<hash>/<password>")
def download_link(file_name, hash, password):
    #check if the file exists
    if os.path.isdir(app.config['UPLOAD_FOLDER'] + file_name):
        #check if the password is correct from the json file
        with open(os.path.join(app.config['UPLOAD_FOLDER'], file_name, 'data.json')) as json_file:
            data = json.load(json_file)
            #check if the password is correct
            print(password == data['browserAuth'])
            # Hash the file
            with open(os.path.join(app.config['UPLOAD_FOLDER'], file_name, file_name), 'rb') as file:
                bytes = file.read()
                fileHash = hashlib.sha256(bytes).hexdigest()

            print(fileHash)
            print(hash)
            if password == data['browserAuth'] and hash == fileHash:
                return send_from_directory(app.config['UPLOAD_FOLDER'] + file_name, file_name, as_attachment=True)
            else:
                abort(403)
    else:
        abort(404)

# Generate a file download link
@app.route("/generate", methods=['GET', 'POST'])
def generate():
    if request.method == 'GET':
        return render_template('generate.html')
    elif request.method == 'POST':
        # Get the name of the file to be uploaded
        file_name = request.form['file_name']
        # Check if the password is correct from the json file
        with open(os.path.join(app.config['UPLOAD_FOLDER'], file_name, 'data.json')) as json_file:
            data = json.load(json_file)
            #check if the password is correct
            if bcrypt.checkpw(request.form['password'].encode('utf-8'), data['password']):
                # Hash the file
                with open(os.path.join(app.config['UPLOAD_FOLDER'], file_name, file_name), 'rb') as file:
                    bytes = file.read()
                    fileHash = hashlib.sha256(bytes).hexdigest()
                # Generate a link to the file
                link = "http://127.0.0.1:5000/download/" + file_name + "/" + fileHash + "/" + data['browserAuth']
                return render_template('generate.html', link=link)