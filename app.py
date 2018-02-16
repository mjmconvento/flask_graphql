#! usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, url_for
from flask_graphql import GraphQLView
from database import db_session
from flask_cors import CORS, cross_origin
from schema import schema

# sample
import cgi
import os
from werkzeug.utils import secure_filename
UPLOAD_FOLDER = '/var/www/flask_graphql/uploads'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'js'])


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True, context={'session': db_session}))

# sample routes
@app.route('/')
def index():
    return "Go to /graphql"

@app.route('/user/<username>')
def user(username):
    return "Hello, %s" % username

@app.route('/post/<int:post_id>')
def post(post_id):
    return "Post id: %s" % post_id  

@app.route('/request_method', methods=['GET', 'POST'])
def request_method():
    if request.method == 'POST':
        return 'you are using POST'
    else:
        return 'you are using GET'

@app.route('/template/<name>')
def template(name):
    return render_template("profile.html", name=name)


@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'GET':
        return render_template("upload_file.html")
    else:
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return filename

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
