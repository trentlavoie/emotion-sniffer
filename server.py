import os
from flask import Flask, request, redirect, url_for, send_from_directory
from werkzeug import secure_filename
import indicoio
from PIL import Image
import numpy as np
import operator
from config import indico_api_key

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
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <p>%s</p>
    """ % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER'],))

@app.route('/pic/<pic_name>')
def pic(pic_name):
    pic_url = url_for('static',filename='images/uploads/{}'.format(pic_name))
    image = Image.open("static/images/uploads/{}".format(pic_name))
    pixel_array = np.array(image)
    results = indicoio.fer(pixel_array, detect=False)
    emotion_results = max(results.iteritems(), key=operator.itemgetter(1))[0]
    emotion_results = (emotion_results, results[emotion_results])
    return """
    <!doctype html>
    <title>Image Details</title>
    <h1>Image Details</h1>
    <img src='{}' style='max-width:500px; max-height:400px; image-orientation: from-image;'>
    <p>{}</p>
    <br>
    <p>{}</p>
    </html>
    """.format(pic_url, emotion_results[0], results)

# @app.route('/uploads/<pic_name>')
# def uploads(pic_name):
#     return send_from_directory('uploads', pic_name)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)