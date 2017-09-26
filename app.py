import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import pandas as pd
import shutil

from flask import send_from_directory

import model

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
        file0 = request.files['filez']
        filelist = request.files.getlist('filez')
        
        # if user does not select file, browser also
        # submit a empty part without filename
        if file0.filename == '':
            flash('No selected file')
            return redirect(request.url)

        # if file is not an image, retry
        
        flash('%d file(s) selected'%len(filelist))
        session['filepath'] = []
        for file in filelist:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) 
                file.save(filepath)
                session['filepath'] += [filepath]
                #print url_for('uploaded_file')

        flash('%d file(s) selected'%len(filelist))
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

    #fileurl = session['filepath'][0]
    #print fileurl

    imagefiles = session['filepath']
    fileurl = model.pickbest(imagefiles)

    files = []
    if len(imagefiles) >= 4:
        for tempurl in imagefiles:
            filepart = tempurl.split('/')[1]
            files += ['static/'+filepart]
            shutil.copy2(tempurl,files[-1])
        return render_template('output.html', imagefile=files[3],
                               imagefile1=files[0], imagefile2=files[1], imagefile3=files[2])

    print fileurl[0],type(fileurl[0])
    
    filepart = fileurl.split('/')[1]
    fileout = 'static/'+filepart
    shutil.copy2(fileurl,fileout) #

    url_for_image0 = url_for('static',filename=filepart)
    print url_for_image0

    return render_template('output.html', url0=fileout,
                           imagefile1=fileout, imagefile2=fileout, imagefile3=fileout)



@app.route('/slides')
def showslides():
    return render_template('slides.html')



if __name__ == '__main__':

    #app.run(debug=True, port=5957)
    app.run(debug=True, host='0.0.0.0', port=5000)
