#imports
import os
import PIL
from PIL import Image
import traceback
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, session, Blueprint,send_file,safe_join,jsonify, Response
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap
import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
import telegram
import time
from models import Image1
import shutil
import math
import ifcfg
import json
import shutil
from pyngrok import ngrok
from zipfile import ZipFile
import datetime
from datetime import date
import pyAesCrypt

password = "please-use-a-long-and-random-password"

# time.sleep(30)

#telegram init
print("Telegram Intitialization")
bot = telegram.Bot(token="1634378361:AAGJR3zwC5Svx9Df9M2PIJD6x_Ncy6lXytQ")
chat_id = 1409170051

#getting local IP
print("Getting Local IP")
hosts = []
for name, interface in ifcfg.interfaces().items():
    if (interface['inet4']):
        hosts.append(interface['inet4'])
host = ', '.join(hosts[1])
print(host)

#ngrok init
print("Starting Ngrok Tunnel")
ngrok.set_auth_token("1gxfsxxcnGRfsSgCcdszOCHbZ20_44SUz5KgQz13jBb6a8G9D")
http_tunnel = ngrok.connect(5555)
tunnels = ngrok.get_tunnels()[0]
tunnels = str(tunnels)
ng = tunnels[13:44]
print(ng)
bot.sendMessage(text = 'Welcome To My Storage\n\nNgrokTunnel: {}\n\nLocalhost: "{}:5555"'.format(ng,host), chat_id=chat_id)
print("Link sent")

#auth for firebase    
authconfig = {
    "apiKey": "AIzaSyDbpGOYeQiO-zSNzFIhV1ARBg-IWYmSKLE",
    "authDomain": "mystorage-c0037.firebaseapp.com",
    "projectId": "mystorage-c0037",
    "databaseURL" : "",
    "storageBucket": "mystorage-c0037.appspot.com",
    "messagingSenderId": "609857072687",
    "appId": "1:609857072687:web:2ad53d5f42399a34e3a0da",
    "measurementId": "G-HZE332F31E"
}

#firebase init
firebase = pyrebase.initialize_app(authconfig)
auth1 = firebase.auth()
cred = credentials.Certificate("mystorage-c0037-firebase-adminsdk-pvjg7-d0254d5da8.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
storage = firebase.storage()

print("Starting Flask App")

#init flask app
app = Flask(__name__, static_folder="static")
app.config['SECRET_KEY'] = 'siyadevelopers27'
app.config['MAX_CONTENT_LENGTH'] = 100000 * 1024 * 1024

gallery = Blueprint('gallery', __name__, template_folder='templates', static_folder='static')
ALLOWED_EXTENSIONS_IMAGE = ['png', 'jpg', 'jpeg', 'gif', 'ico', 'icon']
ALLOWED_EXTENSIONS_VIDEO = ['mp4', 'mov', 'mkv', 'avi', 'mpeg']
ALLOWED_EXTENSIONS_FILE = ['txt', 'rar', 'zip', '7zip', 'doc', 'docx', 'mp3', 'mp4', 'mov', 'mkv', 'avi', 'pdf', 'xlsx', 'ppt', 'pptx', 'png', 'jpg', 'jpeg', 'gif', 'ico', 'icon', 'png', 'bmp', 'py', 'html', 'pages','numbers','key','pem','aes']
app.register_blueprint(gallery, url_prefix='/gallery')

bootstrap = Bootstrap(app)

######################### Routes ##########################

#signin
@app.route('/')
@app.route('/signin', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        collection = db.collection('users')
        doc = collection.document(email).get()
        data = doc.to_dict()
        try:
            usr = data['email']
            if usr == email:
                try:
                    auth1.sign_in_with_email_and_password(email, password)
                    session['name'] = data['name']
                    session['email'] = data['email']
                    session['phone'] = data['phone']
                    session['userid'] = data['userid']
                    session['status'] = 'Active'
                    path ="/"
                    stat = shutil.disk_usage(path)
                    free = math.floor(stat.free/1024/1024/1024)
                    session['free'] = free
                    session['GALLERY_ROOT_DIR'] = 'data/{}/images/'.format(session['userid'])
                    session['THUMBNAIL_FOLDER_T'] = 'data/{}/images/thumbnail/'.format(session['userid'])
                    session['FILE_ROOT_DIR'] = 'data/{}/files/'.format(session['userid'])
                    session['BIN_ROOT_DIR'] = 'data/{}/bin/'.format(session['userid'])
                    session['ENCRYPTED'] = 'data/{}/encrypted/'.format(session['userid'])
                    return redirect(url_for('show_file'))
                except:
                    return render_template("signin.html",error="a",message="Wrong Password")
        except:
            return render_template("signin.html",error="a", message="User not found")
    else:
        return render_template("signin.html")

#register
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'GET':
        return render_template("signup.html")
    else:
        name = request.form['name']
        email = request.form['email']
        email = email.lower()
        password = request.form['password']
        phone = request.form['phone']
        collection = db.collection('users')
        try:
            auth1.create_user_with_email_and_password(email, password)
            userid = name[0:4].lower()+phone[6:]
            print("User Registered")
            collection.document(email).set({"name": name, "email": email, "phone": phone,"userid": userid})
            print('Making Directories')
            os.mkdir("data/{}".format(userid))
            os.mkdir("data/{}/files".format(userid))
            os.mkdir("data/{}/images".format(userid))
            os.mkdir("data/{}/bin".format(userid))
            os.mkdir("data/{}/encrypted".format(userid))
            os.mkdir("data/{}/images/thumbnail".format(userid))
            return render_template('signin.html',success="a", message="User Registered Successfully")
        except:
            return render_template("signup.html",error="a", message='User already registered')

#forgotpassword
@app.route('/forgotpassword', methods=["GET", "POST"])
def forgotpassword():
    if request.method == "GET":
        return render_template("forgotpassword.html")
    else:
        email = request.form['email']
        try:
            auth1.send_password_reset_email(email)
            return render_template('forgotpassword.html',success="a",message="Reset Link Sent")
        except:
            return render_template("forgotpassword.html",error="a",message="Unable to send link")

def page_not_found(e):
    return render_template('404.html'), 404

#logout
@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("signin.html")

#l404
@app.route('/404', methods=["GET", "POST"])
def er():
    return render_template("404.html")

#user
@app.route('/user', methods=['GET', 'POST'])
def user():
    try:
        if session['status'] == 'Active':
            if request.method == 'GET':
                collection = db.collection('users')
                doc = collection.document(session["email"]).get()
                data = doc.to_dict()
                return render_template('user.html',name=data['name'],email=data['email'],phone=data['phone'],userid=data['userid'])
            else:
                name = request.form['name']
                phone = request.form['phone']
                try:
                    db.collection('users').document(session['email']).update(
                        {'name': name,'phone': phone})
                    collection = db.collection('users')
                    doc = collection.document(session["email"]).get()
                    data = doc.to_dict()
                    session['name'] = name
                    return render_template('user.html', success='a',message="Details Updated",name=data['name'],email=data['email'],phone=data['phone'],userid=data['userid'])
                except:
                    return render_template('user.html',error="a",message="Not able to update details",name=data['name'],email=data['email'],phone=data['phone'],userid=data['userid'])
    except:
        return redirect(url_for('logout'))

#change password
@app.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    try:
        auth1.send_password_reset_email(session['email'])
        return render_template('user.html',success="a",message="Reset Link Sent")
    except:
        return render_template("user.html",error="a",message="Unable to send link")



#uploadImage
@app.route('/uploadimage', methods=['POST'])
def uploadimage():
    try:
        if request.method == 'POST':
            print("sdvsd")
            if 'files[]' not in request.files:
                return redirect(request.url)
            files = request.files.getlist('files[]')
            for file in files:
                if file and allowed_image(file.filename):
                    filename = secure_filename(file.filename)
                    filename = gen_file_name2(filename)
                    file.save(os.path.join(session['GALLERY_ROOT_DIR'], filename))
                    image_thumbnail(filename)
            return jsonify({'message':'Uploaded'})
    except:
        return jsonify({'message':'Not able upload'})

#showImage
@app.route('/image')
def index():
    try:
        if session['status']== 'Active':
            return redirect(url_for('show_gallery'))
        else:
            return redirect(url_for('logout'))
    except:
        return redirect(url_for('logout'))

#getting files from filepaths
@app.route('/cdn/<path:filename>')
def custom_static(filename):
    path = filename.split('/')
    filename = path[-1]
    path = '/'.join(path[:-1])
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ALLOWED_EXTENSIONS_VIDEO:
        return send_from_directory(path, filename)
    return send_from_directory(session['THUMBNAIL_FOLDER_T'], filename)

#showImage
@app.route('/show_gallery', methods=['GET', 'POST'])
def show_gallery():
    try:
        if session['status']== 'Active':
            year = []
            images = Image1.all(session['THUMBNAIL_FOLDER_T'])
            for i in images:
                if i.date not in year:
                    year.append(i.date)
            year.sort(reverse=True)
            return render_template('image.html', images=images,year = year)
        else:
            return redirect(url_for('logout'))
    except:
        return redirect(url_for('logout'))

#creating thumbnails
def image_thumbnail(image):
    try:
        base_width = 180
        img = Image.open(os.path.join(session['GALLERY_ROOT_DIR'], image))
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
        img.save(os.path.join(session['THUMBNAIL_FOLDER_T'], image))
        return True
    except:
        print (traceback.format_exc())
        return False        

#deleting images
@app.route('/deleteimages', methods=['GET', 'POST'])
def deleteimages():
    try:
        information = request.data
        data = json.loads(information)
        for i in data:
            source = os.path.join(session['GALLERY_ROOT_DIR'],i)
            os.utime(source)
            destination = os.path.join(session['BIN_ROOT_DIR'],i)
            os.remove(os.path.join(session['THUMBNAIL_FOLDER_T'],i))
            shutil.move(source, destination)
        return jsonify({'message':'Moved to Bin'})
    except:
        return jsonify({'message':'Not able to delete'})

#zipping images for download
def zip(data):
    with ZipFile('Images.zip','w') as zip: 
        for file0 in data:
            file1 = os.path.join(session['GALLERY_ROOT_DIR'],file0)
            os.chdir(file1[:14]) 
            zip.write(file1[14:])
            os.chdir("../../")
    source = os.path.join(os.getcwd(),'Images.zip')
    destination = os.path.join(session['GALLERY_ROOT_DIR'],'Images.zip')
    shutil.move(source, destination)
    return 

#download images
@app.route('/downloadimages',methods=["GET", "POST"])
def downloadimages():
    information = request.data
    data = json.loads(information)
    zip(data)
    return jsonify({'message':'Images.zip created, staring download','urll': url_for('downimg')})

#download zipped images
@app.route('/downimg' , methods=["GET" , "POST"])
def downimg():
    return send_from_directory(session['GALLERY_ROOT_DIR'], "Images.zip", as_attachment=True)

def allowed_image(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_IMAGE

def gen_file_name2(filename):
    i = 1
    while os.path.exists(os.path.join(session['GALLERY_ROOT_DIR'], filename)):
        name, extension = os.path.splitext(filename)
        filename = '%s_%s%s' % (name, str(i), extension)
        i += 1
    return filename

@app.route('/shareimages', methods=['GET', 'POST'])
def shareimages():
    try:
        information = request.data
        data = json.loads(information)
        date1 = date.today().strftime("%m/%d/%y")
        for i in data:
            db.collection("shared").document(i).set({
                    "filename": i,"path":session['GALLERY_ROOT_DIR'],"sharedBy": session["name"],"date":date1
                })
        return jsonify({'message':'Shared'})
    except:
        return jsonify({'message':'Unable to share'})



#Files
@app.route('/uploadfile/<path:subpath>', methods=['POST'])
def uploadfile(subpath):
    try:
        if request.method == 'POST':
            if 'files[]' not in request.files:
                return redirect(request.url)
            files = request.files.getlist('files[]')
            encryptFile = request.form.getlist('encrypt')
            for file in files:
                if file and allowed_file1(file.filename):
                    filename = secure_filename(file.filename)
                    filename = gen_file_name1(filename)
                    file.save(os.path.join(subpath, filename))
                    if(encryptFile):
                        pyAesCrypt.encryptFile(os.path.join(subpath, filename), os.path.join(subpath, filename+".aes"), password)
                        os.remove(os.path.join(subpath, filename))
            return jsonify({'message':'Uploaded'})
    except:
        return jsonify({'message':'Not able to upload'})

@app.route('/newfiledir', methods=['GET', 'POST'])
def newfiledir():
    information = request.data
    data = json.loads(information)
    path = data[1]
    name = data[0]
    i=1
    while os.path.exists(os.path.join(path, name)):
        name = '%s_%s' % (name, str(i))
        i += 1
    os.mkdir(os.path.join(path, name))
    return jsonify({'message':'Folder Created'})

@app.route('/file')
def file1():
    if session['status']== 'Active':
        return redirect(url_for('show_file'))
    else:
        return redirect(url_for('logout'))

@app.route('/show_file', methods=['GET', 'POST'])
def show_file():
    try:
        if session['status']== 'Active':
            try:
                shutil.rmtree(session['ENCRYPTED'])
                os.mkdir("data/{}/encrypted".format(session['userid']))
            except:
                pass
            files = Image1.all(session['FILE_ROOT_DIR'])
            path1 = session['FILE_ROOT_DIR'].split('/')
            path1 = path1[2:-1]
            print(path1)
            return render_template('file.html', files=files, path=session['FILE_ROOT_DIR'],path1=path1)
        else:
            return redirect(url_for('logout'))
    except:
        return redirect(url_for('logout'))

@app.route('/renamefile', methods=['GET', 'POST'])
def renamefile():
    information = request.data
    data = json.loads(information)
    newname = data[1]
    path = data[0].split('/')
    filename = path[-1]
    path = '/'.join(path[:-1])
    i=1
    while os.path.exists(os.path.join(session['FILE_ROOT_DIR'], newname)):
        name,ext = os.path.splitext(newname)
        newname = '%s_%s%s' % (name, str(i),ext)
    old1=os.path.join(path,filename)
    new1=os.path.join(path,newname)
    os.rename(old1, new1)
    message = "Renamed as {}".format(newname)
    return jsonify({'message': message})

@app.route('/deletefiles', methods=['GET', 'POST'])
def deletefiles():
    try:
        information = request.data
        data = json.loads(information)
        for i in data:
            path = i.split('/')
            filename = path[-1]
            path = '/'.join(path[:-1])
            source = os.path.join(path,filename)
            os.utime(source)
            destination = os.path.join(session['BIN_ROOT_DIR'],filename)
            shutil.move(source, destination)
        return jsonify({'message':'Moved to Bin'})
    except:
        return jsonify({'message':'Unable to delete'})

@app.route('/sharefiles', methods=['GET', 'POST'])
def sharefiles():
    try:
        information = request.data
        data = json.loads(information)
        for i in data:
            path = i.split('/')
            filename = path[-1]
            date1 = date.today().strftime("%m/%d/%y")
            path = '/'.join(path[:-1])
            db.collection("shared").document(filename).set({
                "filename": filename,"path":path,"sharedBy": session["name"],"date":date1
            })
        return jsonify({'message':'Shared'})
    except:
        return jsonify({'message':'Not able to share folder'})

@app.route('/showfile/<path:subpath>' , methods=["GET" , "POST"])
def showfile(subpath):
    try:
        if session['status']== 'Active':
            path = subpath.split('/')
            filename = path[-1]
            path = '/'.join(path[:-1])
            name, ext = os.path.splitext(filename)
            print(name,ext)
            if not ext:
                files = Image1.all(subpath)
                path1 = subpath.split('/')
                path1 = path1[2:]
                return render_template('file.html', files=files, path = subpath, path1=path1)
            ext = filename.rsplit('.', 1)[1].lower()
            if ext in ALLOWED_EXTENSIONS_VIDEO:
                return render_template('playvideo.html',path=subpath,name=filename)
            if ext == 'aes':
                pyAesCrypt.decryptFile(os.path.join(path,filename), os.path.join(path,filename[:-4]), password)
                filename = filename[:-4]
                source = os.path.join(path,filename)
                destination = os.path.join(session['ENCRYPTED'],filename)
                shutil.move(source, destination)
                return send_from_directory(session['ENCRYPTED'], filename)
            return send_from_directory(path, filename)
        else:
            return redirect(url_for('logout'))
    except:
        return redirect(url_for('logout'))

@app.route('/showfile1/<path:name>/<path:path>')
def showfile1(path, name):
    if session['status']== 'Active':
        path = path.split('/')
        subpath = []
        for i in path:
            if(i==name):
                subpath.append(i)
                break
            subpath.append(i)
        path1 = '/'.join(subpath)
        files = Image1.all(path1)
        path2 = path1.split('/')
        path2 = path2[2:]
        return render_template('file.html', files=files,path=path1,path1=path2)


def allowed_file1(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_FILE

def gen_file_name1(filename):
    i = 1
    while os.path.exists(os.path.join(session['FILE_ROOT_DIR'], filename)):
        name, extension = os.path.splitext(filename)
        filename = '%s_%s%s' % (name, str(i), extension)
        i += 1

    return filename

def zipfile(names,path):
    with ZipFile('Files.zip','w') as zip: 
        for file0 in names:
            file1 = os.path.join(path,file0) 
            zip.write(file1)
    source = os.path.join(os.getcwd(),'Files.zip')
    destination = os.path.join(session['FILE_ROOT_DIR'],'Files.zip')
    shutil.move(source, destination)
    return 

@app.route('/downloadfiles',methods=["GET", "POST"])
def downloadfiles():
    names = []
    information = request.data
    data = json.loads(information)
    for i in data:
        path = i.split('/')
        filename = path[-1]
        path = '/'.join(path[:-1])
        print(filename)
        names.append(filename)
    print(names,path)
    zipfile(names,path)
    return jsonify({'message':'Files.zip created, staring download','urll': url_for('downfile')})

@app.route('/downfile' , methods=["GET" , "POST"])
def downfile():
    return send_from_directory(session['FILE_ROOT_DIR'], "Files.zip", as_attachment=True)

@app.route('/downloadfile/<path:name1>/<path:subpath>' , methods=["GET" , "POST"])
def downloadfile(name1,subpath):
    path = subpath.split('/')
    filename = path[-1]
    name, extension = os.path.splitext(filename)
    print(name, extension)
    path = '/'.join(path[:-1])
    if not extension:
        file_paths = get_all_file_paths(subpath)
        with ZipFile('Files.zip','w') as zip:
            for file in file_paths:
                os.chdir(file[:20])
                zip.write(file[20:])
                os.chdir("../../../")
        source = os.path.join(os.getcwd(),'Files.zip')
        destination = os.path.join(session['FILE_ROOT_DIR'],'Files.zip')
        shutil.move(source, destination)
        print('All files zipped successfully!')
        return send_from_directory(session['FILE_ROOT_DIR'], "Files.zip", as_attachment=True)
    if extension == '.aes':
        pyAesCrypt.decryptFile(os.path.join(path,filename), os.path.join(path,filename[:-4]), password)
        filename = filename[:-4]
        source = os.path.join(path,filename)
        destination = os.path.join(session['ENCRYPTED'],filename)
        shutil.move(source, destination)
        return send_from_directory(session['ENCRYPTED'], filename, as_attachment=True)
    return send_from_directory(path, filename, as_attachment=True)

def get_all_file_paths(directory):
    file_paths = []
    for root, directories, files in os.walk(directory):
        print(directories)
        for filename in files:
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)
    return file_paths     


#Shared
@app.route('/shared')
def shared():
    try:
        if session['status']== 'Active':
            return redirect(url_for('show_shared'))
        else:
            return redirect(url_for('logout'))
    except:
        return redirect(url_for('logout'))

@app.route('/show_shared', methods=['GET', 'POST'])
def show_shared():
    try:
        if session['status']== 'Active':
            lst = []
            docs = db.collection('shared').stream()
            for doc in docs:
                dic = {}
                link = doc.to_dict()
                dic['filename'] = link['filename']
                dic['sharedBy'] = link['sharedBy']
                dic['path'] = link['path']
                dic['date'] = link['date']
                lst.append(dic)
            return render_template('shared.html', lst=lst)
    except:
        return redirect(url_for('logout'))

@app.route('/showshared/<filename>/<path:subpath>', methods=['GET', 'POST'])
def showshared(filename,subpath):
    try:
        if session['status']== 'Active':
            path = os.path.join(subpath,filename)
            name, ext = os.path.splitext(filename)
            print(name,ext)
            if not ext:
                return redirect(url_for('show_shared'))
            ext = filename.rsplit('.', 1)[1].lower()
            if ext in ALLOWED_EXTENSIONS_VIDEO:
                return render_template('playvideo.html',path=path,name=filename)
            return send_from_directory(subpath, filename)
    except:
        return redirect(url_for('logout'))

@app.route('/downloadshared/<filename>/<path:path>' , methods=["GET" , "POST"])
def downloadshared(filename,path):
    name,ext = os.path.splitext(filename)
    print(name,ext)
    subpath = os.path.join(path,filename)
    if not ext:
        file_paths = get_all_file_paths(subpath)
        with ZipFile('Files.zip','w') as zip:
            for file in file_paths:
                os.chdir(file[:20])
                zip.write(file[20:])
                os.chdir("../../../")
        source = os.path.join(os.getcwd(),'Files.zip')
        destination = os.path.join(session['FILE_ROOT_DIR'],'Files.zip')
        shutil.move(source, destination)
        return send_from_directory(session['FILE_ROOT_DIR'], "Files.zip", as_attachment=True)
    return send_from_directory(path, filename, as_attachment=True)

@app.route('/deleteshared',methods=['GET', 'POST'])
def deleteshared():
        information = request.data
        data = json.loads(information)
        filename = data[0]
        db.collection('shared').document(filename).delete()
        return jsonify({'message':'Deleted'})



#Bin
@app.route('/bin')
def bin():
    try:
        if session['status']== 'Active':
            return redirect(url_for('show_bin'))
        else:
            return redirect(url_for('logout'))
    except:
        return redirect(url_for('logout'))

@app.route('/show_bin', methods=['GET', 'POST'])
def show_bin():
    try:
        if session['status']== 'Active':
            file1 = Image1.all(session['BIN_ROOT_DIR'])
            for i in file1:
                old_time = datetime.datetime.strptime(i.date, '%x')
                current_time = datetime.datetime.now().strftime("%x")
                current_time1 = datetime.datetime.strptime(current_time, '%x')
                diff = current_time1 - old_time
                if diff.days > 30:
                    os.remove(os.path.join(session['BIN_ROOT_DIR'],i.path))
                    print("Deleted")
            images = Image1.all(session['BIN_ROOT_DIR'])
            return render_template('bin.html', images=images)
        else:
            return redirect(url_for('logout'))
    except:
        return redirect(url_for('logout'))

@app.route('/deletebins', methods=['GET', 'POST'])
def deletebins():
    try:
        information = request.data
        data = json.loads(information)
        for i in data:
            name1, extension = os.path.splitext(i)
            print(name1,extension)
            if not extension:
                shutil.rmtree(os.path.join(session['BIN_ROOT_DIR'],i))
            else:
                os.remove(os.path.join(session['BIN_ROOT_DIR'],i))
        return jsonify({'message':'Deleted','urll': url_for('show_bin')})
    except:
        return jsonify({'message':'Unable to Delete'})

@app.route('/restoremultiple', methods=['GET', 'POST'])
def restoremultiple():
    if session['status']== 'Active':
        information = request.data
        data = json.loads(information)
        for i in data:
            name1, extension = os.path.splitext(i)
            print(name1,extension)
            ext = extension.replace('.','')
            source = os.path.join(session['BIN_ROOT_DIR'],i)
            if ext in ALLOWED_EXTENSIONS_IMAGE:
                j = 1
                while os.path.exists(os.path.join(session['GALLERY_ROOT_DIR'], i)):
                    name, extension = os.path.splitext(i)
                    i = '%s_%s%s' % (name, str(i), extension)
                    j += 1
                destination = os.path.join(session['GALLERY_ROOT_DIR'],i)
                shutil.move(source, destination)
                image_thumbnail(i)
            elif ext in ALLOWED_EXTENSIONS_FILE or not ext:
                j = 1
                while os.path.exists(os.path.join(session['FILE_ROOT_DIR'], i)):
                    name, extension = os.path.splitext(i)
                    i = '%s_%s%s' % (name, str(i), extension)
                    j += 1
                destination = os.path.join(session['FILE_ROOT_DIR'],i)
                shutil.move(source, destination)
        return jsonify({'message':'Restored'})
        
    else:
        return redirect(url_for('logout'))

# upload firebase
@app.route('/firebase', methods=["GET", "POST"])
def firebase():
    print("In firebase")
    if session['status'] == 'Active':
        if request.method == 'GET':
            lst = []
            collection = db.collection('folders')
            docs = collection.document(session["userid"]).collection(session['userid']).stream()
            for doc in docs:
                dic = {}
                filename = doc.id
                print(filename)
                folder = ('{}/{}').format(session['userid'], filename)
                url = storage.child(folder).get_url(None)
                dic['filename'] = filename
                dic['url'] = url
                lst.append(dic)
                print(lst)
            return render_template('firebase.html',lst=lst)
        else:
            file1 = request.files['file']
            filename = file1.filename
            try:
                folder = ('{}/{}').format(session['userid'], filename)
                storage.child(folder).put(file1)
                collection = db.collection('folders')
                collection.document(session["userid"]).collection(
                    session["userid"]).document(filename).set({"filename": filename})
                return render_template('firebase.html', success='a', message='Uploaded')
            except:
                return render_template('firebase.html', error='a',message='Not able to Upload')
    else:
        return redirect(url_for('logout'))

#delete firebase
@app.route('/deletefirebase/<filename>', methods=["GET", "POST"])
def deletetest(filename):
    try:
        db.collection('folders').document(session["userid"]).collection(
                    session["userid"]).document(filename).delete()
        folder = ('{}/{}').format(session['userid'], filename)
        storage.delete(folder)
        return render_template("firebase.html",success="a", message='Deleted')
    except:
        return render_template('firebase.html',error='a', message='Not able to delete')


#####END#####