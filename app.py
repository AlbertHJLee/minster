import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import pandas as pd
import shutil

from flask import send_from_directory
import imghdr

import model

length = 4
verbose = 0

UPLOAD_FOLDER = 'uploads'
allowed_extensions = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#sess = Session()
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
#sess.init_app(app)




def allowed_ext(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def allowed_file(file):
    return imghdr.what(file).lower() in allowed_extensions

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        
        # Check if POST request has the file part
        if 'filez' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file0 = request.files['filez']
        filelist = request.files.getlist('filez')
        
        # If user does not select file, retry
        if file0.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # Check every file to see if it's a valid format
        # If all files aren't images, retry
        
        flash('%d file(s) selected'%len(filelist))
        session['filepath'] = []
        for file in filelist:
            if file and allowed_ext(file.filename) and allowed_file(file):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) 
                file.save(filepath)
                session['filepath'] += [filepath]

        if len(session['filepath']) is 0:
            flash('No valid file')
            return redirect(request.url)

        flash('%d file(s) selected'%len(filelist))
        return redirect(url_for('uploaded_file'))

    return render_template('index.html')





@app.route('/output')
def uploaded_file():

    #fileurl = session['filepath'][0]
    #print fileurl

    imagefiles = session['filepath']
    besturls,prob = model.pickbest(imagefiles)

    files = []
    fileurls = []
    if len(imagefiles) >= 4:
        
        for tempurl in besturls:
            filepart = tempurl.split('/')[1]
            files += ['static/'+filepart]
	    fileurls += [url_for('static', filename=filepart)]
            shutil.copy2(tempurl,files[-1])
            
        if verbose > 2:
            print ''
            print prob, fileurls
            
        return render_template('output.html', imagefile=fileurls[3], prob0=prob[3],
                               imagefile1=fileurls[2], imagefile2=fileurls[1], imagefile3=fileurls[0],
                               prob1=prob[2], prob2=prob[1], prob3=prob[0])

    if verbose > 2:
        print besturls[0],type(besturls[0])

    if len(imagefiles) > 0:
        filepart = besturls.split('/')[1]
        fileout = 'static/'+filepart
        shutil.copy2(besturls,fileout)

        return render_template('output.html', imagefile=fileout, prob0=prob,
                               imagefile1=fileout, imagefile2=fileout, imagefile3=fileout,
                               prob1=prob, prob2=prob, prob3=prob)

    else:
        flash('No valid file')
        return render_template('index.html')




    
@app.route('/slides')
def showslides():
    return render_template('slides.html')



if __name__ == '__main__':

    app.run(debug=True, host="0.0.0.0", port=8000)

