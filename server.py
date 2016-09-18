import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug import secure_filename
import indicoio
from PIL import Image
import numpy as np
import operator
from config import indico_api_key
from config import db_connection_string
# from flask.ext.sqlalchemy import SQLAlchemy


UPLOAD_FOLDER = 'static/images/uploads'
ALLOWED_EXTENSIONS = set(['jpg','jpeg', 'png'])
indicoio.config.api_key = indico_api_key

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('pic', pic_name=filename))
    return render_template('index.html',title='Welcome')

@app.route('/pic/<pic_name>')
def pic(pic_name):
    pic_url = url_for('static',filename='images/uploads/{}'.format(pic_name))
    image = Image.open("static/images/uploads/{}".format(pic_name))
    pixel_array = np.array(image)
    results = indicoio.fer(pixel_array, detect=False)
    emotion_results = max(results.iteritems(), key=operator.itemgetter(1))[0]
    emotion_results = (emotion_results, results[emotion_results])
    return render_template("picture.html", title= "Results", image_src = pic_url, emotion = emotion_results[0])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)