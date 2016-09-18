import os
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug import secure_filename
import indicoio
from PIL import Image
import numpy as np
import operator
from config import indico_api_key, db_connection_string
from flask_sqlalchemy import SQLAlchemy
import hashlib
from shutil import copyfile


UPLOAD_FOLDER = 'static/images/uploads'
TMP_FOLDER = 'tmp'
ALLOWED_EXTENSIONS = set(['jpg','jpeg', 'png'])
indicoio.config.api_key = indico_api_key



app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['TMP_FOLDER'] = TMP_FOLDER
app.config['SQLALCHEMY_DATABASE_URI'] = db_connection_string
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(TMP_FOLDER):
    os.makedirs(TMP_FOLDER)
db = SQLAlchemy(app)

class images_table(db.Model):
    __tablename__ = 'images_table'

    hash_id = db.Column(db.String(), primary_key=True)
    url = db.Column(db.String())
    emotion_angry = db.Column(db.Numeric())
    emotion_sad = db.Column(db.Numeric())
    emotion_happy = db.Column(db.Numeric())
    emotion_fear = db.Column(db.Numeric())
    emotion_neutral = db.Column(db.Numeric())
    emotion_surprise = db.Column(db.Numeric())

    def __init__(self, hash_id, url, emotion_angry, emotion_sad, emotion_happy, emotion_fear, emotion_neutral, emotion_surprise):
        self.url = url
        self.hash_id = hash_id
        self.emotion_angry = emotion_angry
        self.emotion_sad = emotion_sad
        self.emotion_happy = emotion_happy
        self.emotion_fear = emotion_fear
        self.emotion_neutral = emotion_neutral
        self.emotion_surprise = emotion_surprise

    def __repr__(self):
        return '<id {}>'.format(self.hash_id)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['TMP_FOLDER'], filename))
            image = Image.open(os.path.join(app.config['TMP_FOLDER'], filename))
            hash_object = hashlib.sha256(image.tobytes()).hexdigest()
            ext = filename.split(".")[-1]
            hash_name = "{}.{}".format(hash_object,ext)
            if images_table.query.filter(images_table.hash_id == hash_object).count() == 0:
                # Save Image
                copyfile(os.path.join(app.config['TMP_FOLDER'], filename), os.path.join("/home/htn/symmetrical-snuffle", app.config['UPLOAD_FOLDER'], hash_name))
                # print os.path.join(app.config['TMP_FOLDER'], filename)
                # print os.path.join("/home/htn/symmetrical-snuffle", app.config['UPLOAD_FOLDER'], hash_name)
                # file.save(os.path.join(app.config['UPLOAD_FOLDER'], hash_name))
                # Get rating
                pixel_array = np.array(image)
                results = indicoio.fer(pixel_array, detect=False)
                #Save in DB
                image_query = images_table(hash_id = hash_object, 
                    url = hash_name,
                    emotion_angry = results["Angry"],
                    emotion_sad = results["Sad"],
                    emotion_happy = results["Happy"],
                    emotion_fear = results["Fear"],
                    emotion_surprise = results["Surprise"],
                    emotion_neutral = results["Neutral"])
                db.session.add(image_query)
                db.session.commit()
            
            os.remove(os.path.join(app.config['TMP_FOLDER'], filename))
            return redirect(url_for('pic', pic_name=hash_object))
    return render_template('index.html',title='Welcome')

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    return d

@app.route('/pic/<pic_name>')
def pic(pic_name):
    # pic_url = url_for('static',filename='images/uploads/{}'.format(pic_name))
    image_query = images_table.query.filter(images_table.hash_id == pic_name).first()
    # image = Image.open("static/images/uploads/{}".format(pic_name))
    # pixel_array = np.array(image)
    # results = indicoio.fer(pixel_array, detect=False) 
    
    pic_url = url_for('static',filename='images/uploads/{}'.format(image_query.url))
    results = {'emotion_angry': image_query.emotion_angry,
        'emotion_sad': image_query.emotion_sad,
        'emotion_happy': image_query.emotion_happy,
        'emotion_fear': image_query.emotion_fear,
        'emotion_surprise': image_query.emotion_surprise,
        'emotion_neutral': image_query.emotion_neutral}
    emotion_results = max(results.iteritems(), key=operator.itemgetter(1))[0]
    emotion_results = (emotion_results, results[emotion_results])
    more_details_link = url_for('details', pic_name = pic_name)
    return render_template("picture.html", title= "Results", image_src = pic_url, emotion = emotion_results[0].split('_')[1], more_details_link = more_details_link)

@app.route('/details/<pic_name>')
def details(pic_name):
    image_query = images_table.query.filter(images_table.hash_id == pic_name).first()
    # pic_url = url_for('static',filename='images/uploads/{}'.format(pic_name))
    # image = Image.open("static/images/uploads/{}".format(pic_name))
    # pixel_array = np.array(image)
    # results = indicoio.fer(pixel_array, detect=False)
    pic_url = url_for('static',filename='images/uploads/{}'.format(image_query.url))
    results = {'emotion_angry': image_query.emotion_angry,
        'emotion_sad': image_query.emotion_sad,
        'emotion_happy': image_query.emotion_happy,
        'emotion_fear': image_query.emotion_fear,
        'emotion_surprise': image_query.emotion_surprise,
        'emotion_neutral': image_query.emotion_neutral}
    emotion_results = max(results.iteritems(), key=operator.itemgetter(1))[0]
    emotion_results = (emotion_results, results[emotion_results])
    return render_template("picture_more_details.html", 
        title= "Results", 
        image_src = pic_url, 
        emotion_result = emotion_results[0].split('_')[1],
        emotion_angry = results["emotion_angry"],
        emotion_sad = results["emotion_sad"],
        emotion_happy = results["emotion_happy"],
        emotion_fear = results["emotion_fear"],
        emotion_surprise = results["emotion_surprise"],
        emotion_neutral = results["emotion_neutral"])

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)