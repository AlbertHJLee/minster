import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import pandas as pd

from flask import send_from_directory



length = 4

UPLOAD_FOLDER = './uploads'
allowed_extensions = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
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
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file multiple="">
         <input type=submit value=Upload>
    </form>
    '''




@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)




@app.route('/')
def main():
    return render_template('index.html', length=length,
                           dataframe='<table border="1"> <thead> <tr> <th>lol</th> <th>yea</th> </tr> </thead>'+
                                     '<tbody> <tr> <th>20</th> <th>10</th> </tr> </tbody> </table>')


if __name__ == '__main__':
    app.run(debug=True, port=5957)
