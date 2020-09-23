import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory,flash
from werkzeug.utils import secure_filename
import cv2
import numpy as np
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

UPLOAD_FOLDER ='static/uploads/'
DOWNLOAD_FOLDER = 'static/downloads/'
ALLOWED_EXTENSIONS = {'mkv', 'avi','mp4','wav'}
app = Flask(__name__,  static_url_path="/static")

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file attached in request')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            size = request.form['value']
            size = int(size)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            process_file(os.path.join(app.config['UPLOAD_FOLDER'], filename), filename,size)
            e_mail = request.form['e_mail']
            name = request.form['name']
            data='static/downloads/video.mkv'
            send_mail(e_mail,data,name)
            return render_template("index.html")
    return render_template('index.html')

def process_file(path, filename,size):
    detect_object(path, filename,size)


def detect_object(path,filename,size):
    cap = cv2.VideoCapture(path)
    ret, frame = cap.read()
    FPS= 30
    width = int(frame.shape[1]*int(size)/100)
    height = int(frame.shape[0]*int(size)/100)
    dim = (width,height)
    fourcc = cv2.VideoWriter_fourcc(*'MPEG')
    out = cv2.VideoWriter('static/downloads/video.mkv', fourcc, FPS,(width,height))
    #out = cv2.VideoWriter('/content/drive/My Drive/ISL/58.mkv', fourcc, FPS,(width,height))

    i=0
    ret, image = cap.read()
    while ret:
        ret,image = cap.read()
        if ret:
            res = cv2.resize(image,dim, cv2.INTER_AREA)
        out.write(res)
        

def send_mail(e_ma,fname,name):

    email_user = 'Enter Email'
    email_password = 'Enter Password'
    email_send = e_ma

    subject = 'Compressed Video'

    msg = MIMEMultipart()
    msg['From'] = email_user
    msg['To'] = email_send
    msg['Subject'] = subject

    body = 'Hi '+ name +' Compresseed video from Abhimat Gupta'
    msg.attach(MIMEText(body,'plain'))

    filename= fname
    attachment  =open(filename,'rb')

    part = MIMEBase('application','octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename= "+filename)

    msg.attach(part)
    text = msg.as_string()
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(email_user,email_password)
    server.sendmail(email_user,email_send,text)

if __name__ == '__main__':
    app.run()
