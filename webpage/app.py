import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
import pandas as pd

from flask import send_from_directory
#from flask import Session


length = 4

UPLOAD_FOLDER = 'uploads'
allowed_extensions = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#sess = Session()
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
#sess.init_app(app)




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'filez' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['filez']
        filelist = request.files.getlist('filez')
        print filelist
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            session['filepath'] = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print url_for('uploaded_file')

            return redirect(url_for('uploaded_file'))
            #return redirect(url_for('uploaded_file',
            #                        filename=filename))

    return render_template('index.html')


"""

@app.route('/uploads') #/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

"""

@app.route('/output')
def uploaded_file():
    """
    if True:
        if 'filez' not in request.files:
            return redirect(request.url)
        file = request.files['filez']
        filelist = request.files.getlist('filez')
        print filelist
        
        filename = secure_filename(file.filename)

    fileurl = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    print fileurl
    """

    fileurl = session['filepath']
    print fileurl
    
    return render_template('output.html', imagefile=fileurl)




if __name__ == '__main__':

    app.run(debug=True, port=5957)
