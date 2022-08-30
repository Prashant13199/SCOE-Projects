from flask import Flask , render_template , request , redirect, url_for , session , flash , jsonify
from flask_mysqldb import MySQL , MySQLdb
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


app = Flask(__name__,template_folder='template')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'prashant13'
app.config['MYSQL_DB'] = 'flaskdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


@app.route('/',methods=["GET","POST"])
def slogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE email=%s",(email,))
        user = curl.fetchone()
        curl.close()

        if user:
            if (password == user["password"]):
                session['name'] = user['name']
                session['branch'] = user['branch']
                session['email'] = user['email']
                session['year'] = user['year']
                session['prn'] = user['prn']
                return redirect(url_for("sdashboard"))
            else:
                error =  "Password and email not match"
                return render_template("home.html" , value = error)
                
        else:
            error = "User not found"
            return render_template("home.html" , value = error)
    else:
        return render_template("home.html")



@app.route('/slist' , methods=["GET","POST"])    
def slist():
    curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl.execute("select * from users")
    data = curl.fetchall()
    return render_template("slist.html", value=data)

@app.route('/sdelete/<int:id>' , methods=["GET" , "POST"])
def sdelete(id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("DELETE FROM users WHERE id=%s",[id])
    mysql.connection.commit()
    flash( "User Deleted...")
    return redirect(url_for("slist"))



@app.route('/tlist' , methods=["GET","POST"])    
def tlist():
    curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl.execute("select * from teacher")
    data = curl.fetchall()
    return render_template("tlist.html", value=data)

@app.route('/tdelete/<int:id>' , methods=["GET" , "POST"])
def tdelete(id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM teacher WHERE id=%s",[id])
    mysql.connection.commit()
    flash("Teacher Deleted...")
    return redirect(url_for("tlist"))

    

@app.route('/tlogin',methods=["GET","POST"])
def tlogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM teacher WHERE email=%s",[email])
        user = curl.fetchone()
        curl.close()

        if  user:
            if (password == user["password"]):
                session['name'] = user['name']
                session['email'] = user['email']
                session['subject'] = user['subject']
                return render_template("tdashboard.html")
            else:
                error =  "Password and email not match"
                return render_template("tlogin.html" , value = error)
                
        else:
            error =  "User not found"
            return render_template("tlogin.html" , value = error)
    else:
        return render_template("tlogin.html")
    
    



@app.route('/alogin',methods=["GET","POST"])
def alogin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM admin WHERE email=%s",[email])
        user = curl.fetchone()
        curl.close()

        if user:
            if (password == user["password"]):
                session['name'] = user['name']
                session['email'] = user['email']
                return redirect(url_for("adashboard"))
            else:
                error = "Password and email not match"
                return render_template("alogin.html", value = error)
        else:
            error = "User not found"
            return render_template("alogin.html", value = error)
    else:
        return render_template("alogin.html")




@app.route('/logout', methods=["GET", "POST"])
def logout():
    session.clear()
    return render_template("home.html")



@app.route('/sregister', methods=["GET", "POST"])
def sregister():
    if request.method == 'GET':
        return render_template("sregister.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        prn = request.form['prn']
        year = request.form['year']
        branch = request.form['branch']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s or prn=%s",(email,prn))
        user = cur.fetchone()

        if user:
            error = ("User exist")
            return render_template("sregister.html" , value = error)
        else:
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users (name, email, password , prn , year , branch) VALUES (%s,%s,%s,%s,%s,%s)",(name,email,password,prn,year,branch))
            mysql.connection.commit()
            flash("User Created...")
            return redirect(url_for('sregister'))




@app.route('/tregister', methods=["GET", "POST"])
def tregister():
    if request.method == 'GET':
        return render_template("tregister.html")
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        teacherid = request.form['teacherid']
        subject = request.form['subject']
        branch = request.form['branch']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM teacher WHERE email=%s",[email])
        user = cur.fetchone()

        if user:
            error = ("Teacher exist")
            return render_template("tregister.html" , value = error)
        else:
            cur.execute("INSERT INTO teacher (name, email, password , teacherid , subject , branch) VALUES (%s,%s,%s,%s,%s,%s)",(name,email,password,teacherid,subject,branch))
            mysql.connection.commit()
            flash("Teacher Created")
            return redirect(url_for('tregister'))




@app.route('/supdate', methods=["GET", "POST"])
def supdate():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        prn = request.form['prn']
        year = request.form['year']
        branch = request.form['branch']

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE prn=%s",[prn])
        user = curl.fetchone()
        curl.close()

        if len(user) > 0:
            if (prn, user["prn"] == user["prn"]):
                cur = mysql.connection.cursor()
                cur.execute("UPDATE users set email=%s,password=%s,year=%s,branch=%s where prn=%s",(email,password,year,branch,prn))
                mysql.connection.commit()
                flash("Student Data Updated...")
                return redirect(url_for('supdate'))
            else:
                flash( "Error : prn not found")
        else:
            flash( "Error user not found")
    else:
        return render_template("supdate.html")



@app.route('/supdate2/<int:id>')
def supdate2(id):
    curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl.execute("SELECT * FROM users WHERE id=%s",[id])
    data = curl.fetchone()
    return render_template("supdate2.html",value = data)
    
    
    


@app.route('/tupdate', methods=["GET", "POST"])
def tupdate():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        teacherid = request.form['teacherid']
        subject = request.form['subject']
        branch = request.form['branch']

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM teacher WHERE teacherid=%s",[teacherid])
        user = curl.fetchone()
        curl.close()

        if len(user) > 0:
            if (teacherid, user["teacherid"] == user["teacherid"]):
                cur = mysql.connection.cursor()
                cur.execute("UPDATE teacher set email=%s,password=%s,subject=%s,branch=%s where teacherid=%s",(email,password,subject,branch,teacherid))
                mysql.connection.commit()
                flash("Teacher Data Updated")
                return redirect(url_for('tupdate'))
            else:
                flash( "Error : prn not found")
        else:
            flash( "Error user not found")
    else:
        return render_template("tupdate.html")
    

@app.route('/tupdate2/<int:id>')
def tupdate2(id):
    curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl.execute("SELECT * FROM teacher WHERE id=%s",[id])
    data = curl.fetchone()
    return render_template("tupdate2.html",value = data)



@app.route('/schangepassword', methods=["GET", "POST"])
def schangepassword():
    if request.method == 'POST':
        prn = request.form['prn']
        password = request.form['password']
        newpassword = request.form['newpassword']

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM users WHERE prn=%s and password=%s",[prn,password])
        user = curl.fetchone()
        curl.close()
        if (prn, user["prn"] == user["prn"]):
            if (password, user["password"] == user["password"]):
                cur = mysql.connection.cursor()
                cur.execute("UPDATE users set password=%s where prn=%s",(newpassword,prn))
                mysql.connection.commit()
                flash("Password changed")
                return redirect(url_for('schangepassword'))
            else:
                flash("Incorrect Password")
        else:
            flash( "Incorrect PRN")
    else:
        return render_template("schangepassword.html")





@app.route('/tchangepassword', methods=["GET", "POST"])    
def tchangepassword():
    if request.method == 'POST':
        teacherid = request.form['teacherid']
        password = request.form['password']
        newpassword = request.form['newpassword']

        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("SELECT * FROM teacher WHERE teacherid=%s and password=%s",[teacherid,password])
        user = curl.fetchone()
        curl.close()
        if (teacherid, user["teacherid"] == user["teacherid"]):
            if (password, user["password"] == user["password"]):
                cur = mysql.connection.cursor()
                cur.execute("UPDATE teacher set password=%s where teacherid=%s",(newpassword,teacherid))
                mysql.connection.commit()
                flash("Password Changed")
                return redirect(url_for('tchangepassword'))
            else:
                flash( "Incorrect Password")
        else:
            flash("Incorrect PRN")
    else:
        return render_template("tchangepassword.html")
    
        

@app.route('/sdashboard', methods=["GET", "POST"])
def sdashboard():
    flash("Success! Signed In...")
    return render_template("sdashboard.html")




@app.route('/tdashboard', methods=["GET", "POST"])
def tdashboard():
    flash("Success! Signed In...")
    return render_template("tdashboard.html")




@app.route('/adashboard', methods=["GET", "POST"])
def adashboard():
    flash("Success! Signed In...")
    return render_template("adashboard.html")




@app.route('/forgotpassword', methods=["GET", "POST"])
def forgotpassword():
    return render_template("forgotpassword.html")




@app.route('/forgotpassword1', methods=["GET", "POST"])
def forgotpassword1():
    return render_template("forgotpassword1.html")




@app.route('/tupload', methods=["GET", "POST"])
def tupload():
    if request.method == 'POST':
        file = request.files['file']
        book = pd.read_csv(file)
        subject = request.form['subject']
        unit = request.form['unit']
        branch = request.form['branch3']
        for row in range(len(book)):
            rows = (book.iloc[row][0],book.iloc[row][1],book.iloc[row][2],book.iloc[row][3],book.iloc[row][4],book.iloc[row][5],book.iloc[row][6],subject,unit,branch)
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO question(question,option1,option2,option3,option4,correctoption,marks,subject,unit,branch) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",rows)
            mysql.connection.commit()
        flash( "File Uploaded...")
        return redirect(url_for('tupload'))
    else:
        return render_template("qupload.html")

@app.route('/branchch', methods=['POST'])
def branchch():
    if request.method=='POST':
        id=request.form['branch1']
        branch2=str(id)
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("select subject from subjects where branch=%s",[branch2])
        data = curl.fetchall()
        data1=[]
        for i in range(len(data)):
            data1.append(data[i]["subject"])
        #return str(data1)
        return jsonify(data1)



@app.route('/queslist' , methods=["GET","POST"])    
def queslist():
    subject = session['subject']
    curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl.execute("select * from question where subject=%s",[subject])
    data = curl.fetchall()
    
    return render_template("queslist.html", value=data)




@app.route('/update', methods=['POST'])
def update():
    if request.method=='POST':
        id=request.form['id']
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("select * from question where id=%s",[id])
        data = curl.fetchone()
        return jsonify(data)

@app.route('/mock',methods= ["POST","GET"])
def mock():
    if request.method == 'GET':
        branch = session['branch']
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("select distinct subject from question where branch = %s",[branch])
        data = curl.fetchall()
        curl.close()
        data1 = len(data)
        return render_template("mock.html" , value = data , len = data1)
        


@app.route('/mock2',methods= ["POST","GET"])
def mock2():
    if request.method=="POST":
        leng=20
        sub = request.form['sub']
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("select * from question where subject=%s order by rand() limit %s",(sub,leng))
        data = curl.fetchall()

        i=1
        for item in data:
            item.update({'srno':i})
            i=i+1
            if i>len(data):
                break
        curl.close()

        return render_template("exam.html", value=data , length=leng)



@app.route('/result', methods=['POST'])
def result():
    data=request.json
    leng=len(data)-1
    option=[]
    marks=0
    year = session['year']
    prn = session['prn']
    subject = data[-1][1]
    for i in range(0,leng):
        option.append(data[i][0])
        if int(option[i])==int(data[i][1]):
            marks=marks+1
    result=int((marks/leng)*100)
    for i in range(0,leng):
        curl1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl1.execute("insert into result(id,selected,correct) values (%s,%s,%s)",(data[i][2],data[i][0],data[i][1]))
        mysql.connection.commit()
    curl1.close()
    curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl.execute("insert into final_result(prn,year,subject,marks) values (%s,%s,%s,%s)",(prn,year,subject,result))
    mysql.connection.commit()
    curl.close()
    return jsonify({'marks':result , 'urll': url_for('displayresult',name=result)})



@app.route('/displayresult/<string:name>', methods=['GET','POST'])
def displayresult(name):
    curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl.execute("select * from result")
    data = curl.fetchall()
    curl.close()

    curl1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl1.execute("select * from question where id in(select id from result)")
    data1 = curl1.fetchall()
    lengt=len(data1)
    curl1.close()

    curl2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl2.execute("delete from result")
    curl2.close()
    mysql.connection.commit()


    return render_template("result_ques.html",value=data1,value1=data,length=lengt,result=name)


@app.route('/exam2',methods= ["POST","GET"])
def ques():
    if request.method=="GET":
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("select * from question order by rand() limit 6")
        data = curl.fetchall()
        i=1
        for item in data:
            item.update({'srno':i})
            i=i+1
            if i>len(data):
                break
        curl.close()
        data1=(data[0]["correctoption"],data[1]["correctoption"],data[2]["correctoption"],data[3]["correctoption"],data[4]["correctoption"],data[5]["correctoption"])
        curl1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl1.execute("INSERT into op(opt1,opt2,opt3,opt4,opt5,opt6) VALUES (%s,%s,%s,%s,%s,%s)",data1)
        mysql.connection.commit()
        return render_template("exam.html", value=data)
    else:
        option=[]
        marks=0
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("select * from op")
        data2 = curl.fetchone()
        for i in range(0,6):
            option.append(request.form['optradio'+str(i+1)])
            if option[i]==data2['opt'+str(i+1)]:
                marks=marks+1
        result=(marks/6)*100
        curl1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl1.execute("delete from op")
        mysql.connection.commit()
        return "YOU GOT "+str(result)+"%"





@app.route('/practice', methods=["GET","POST"])
def practice():
    if request.method == 'GET': 
        branch = session['branch']
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("select distinct subject from question where branch = %s",[branch])
        data = curl.fetchall()
        curl.close()
        data1 = len(data)
        return render_template("practice.html" , value = data , len = data1)
        



@app.route('/practice2', methods=["GET","POST"])
def practice2():
    unit_sub = request.form['unit']
    unit_sub1 = (unit_sub[0],unit_sub[2:])
    sql = "select * from question where unit=%s and subject=%s order by rand()"
    curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl.execute(sql,unit_sub1)
    data = curl.fetchall()
    data1 = len(data)
    curl.close()
    curl1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    mysql.connection.commit()
    curl1.close()
    return render_template("practice2.html", value=data , length = data1)



@app.route('/testseries' , methods=["GET","POST"])
def testseries():
    if request.method=="GET":
        branch = session['branch']
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("select distinct subject from question where branch = %s",[branch])
        data = curl.fetchall()
        curl.close()
        data1 = len(data)
        return render_template("testseries.html" , value = data , len = data1)



@app.route('/testseries2',methods=["GET","POST"])
def testseries2():
    if request.method=="POST":
        number = int(request.form['number'])
        leng=number
        sub = request.form['sub']
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("select * from question where subject=%s order by rand() limit %s",(sub,leng))
        data = curl.fetchall()

        i=1
        for item in data:
            item.update({'srno':i})
            i=i+1
            if i>len(data):
                break
        curl.close()

        return render_template("exam.html", value=data , length=leng)



@app.route('/ranalysis',methods=["GET","POST"])
def reanalysis():
    return render_template("ranalysis.html")




import os
FOLDER= os.path.join('static','p_photo')
app.config['UPLOAD_FOLDER']=FOLDER
i=0

@app.route('/ryear',methods=["GET","POST"])
def ryear():
    if request.method == "GET":
        return render_template("ryear.html")
    else:
        yearwise = request.form['ryear']
        #subject=request.form['sub']
        #return str(subject)
        #return str(yearwise)
        i=1
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("select * from final_result where year=%s",[yearwise])
        data = curl.fetchall()
        curl.close()
        if data:
            dataf = pd.DataFrame.from_dict(data)
            arr = np.array(dataf['marks'])
            final=[]
            final.append(arr[(arr>='0')&(arr<'20')].size)
            final.append(arr[(arr>='20')&(arr<'40')].size)
            final.append(arr[(arr>='40')&(arr<'60')].size)
            final.append(arr[(arr>='60')&(arr<'80')].size)
            final.append(arr[(arr>='40')&(arr<'60')].size)
            final.append(arr[arr=='100'].size)
            #return str(final)
            plt.figure(1)
            plt.subplot(121)
            #plt.figure(figsize=(20,11))
            plt.bar(['0','20','40','60','80','100'] ,final)
            plt.xlabel('Marks')
            plt.ylabel('No of Students')
            plt.title('Result Analysis '+str(yearwise))
            plt.subplot(122)
            plt.pie(final,labels=['0','20','40','60','80','100'],shadow=True)
            #return str(dataf)
            #plt.legend()
            #file_name='static/bar.png'
            file_name=os.path.join(app.config['UPLOAD_FOLDER'],str(yearwise)+'_graph.png')
            app.config["CACHE_TYPE"] = "null"
            plt.savefig(file_name)
            plt.close()
            i=i+1
            return render_template('graph.html',file_name = file_name)
        else:
            error = "No Data Found"
            return render_template('graph.html',value = error)
            
        



@app.route('/rsubject',methods=["GET","POST"])
def rsubject():
    if request.method == "GET":
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("select distinct subject from question")
        data = curl.fetchall()
        curl.close()
        data1 = len(data)
        return render_template("rsubject.html" , value = data , len = data1)
    else:
        subject=request.form['sub']
        #return str(subject)
        i=1
        curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        curl.execute("select * from final_result where subject=%s",[subject])
        data = curl.fetchall()
        curl.close()
        if data:
            dataf = pd.DataFrame.from_dict(data)
            arr = np.array(dataf['marks'])
            final=[]
            final.append(arr[arr=='0'].size)
            final.append(arr[arr=='20'].size)
            final.append(arr[arr=='40'].size)
            final.append(arr[arr=='60'].size)
            final.append(arr[arr=='80'].size)
            final.append(arr[arr=='100'].size)
            #return str(final)
            plt.figure(1)
            plt.subplot(121)
            #plt.figure(figsize=(20,11))
            plt.bar(['0','20','40','60','80','100'] ,final)
            plt.xlabel('Marks')
            plt.ylabel('No of Students')
            plt.title('Result Analysis' +str(subject))
            plt.subplot(122)
            plt.pie(final,labels=['0','20','40','60','80','100'],shadow=True)
            #return str(dataf)
            #plt.legend()
            #file_name='static/bar.png'
            file_name=os.path.join(app.config['UPLOAD_FOLDER'],str(subject)+'_graph.png')
            app.config["CACHE_TYPE"] = "null"
            plt.savefig(file_name)
            plt.close()
            i=i+1
            return render_template('graph.html',file_name = file_name)
        else:
            error = "No Data Found"
            return render_template('graph.html',value = error)
            
        


@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response
        


@app.route('/aqupload', methods=["GET", "POST"])
def aqupload():
    if request.method == 'POST':
        file = request.files['file']
        book = pd.read_csv(file)
        subject = request.form['subject']
        unit = request.form['unit']
        branch = request.form['branch3']
        for row in range(len(book)):
            rows = (book.iloc[row][0],book.iloc[row][1],book.iloc[row][2],book.iloc[row][3],book.iloc[row][4],book.iloc[row][5],book.iloc[row][6],subject,unit,branch)
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO question(question,option1,option2,option3,option4,correctoption,marks,subject,unit,branch) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",rows)
            mysql.connection.commit()
        flash( "File Uploaded...")
        return redirect(url_for('tupload'))
    else:
        return render_template("aqupload.html")

@app.route('/asupload', methods=["GET", "POST"])
def asupload():
    if request.method == 'POST':
        file = request.files['file']
        book = pd.read_csv(file)
        for row in range(len(book)):
            rows = (book.iloc[row][0],book.iloc[row][1],book.iloc[row][2],book.iloc[row][3],book.iloc[row][4],book.iloc[row][5])
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO users(name,email,password,prn,year,branch) VALUES (%s,%s,%s,%s,%s,%s)",rows)
            mysql.connection.commit()
        flash( "File Uploaded...")
        return redirect(url_for('asupload'))
    else:
        return render_template("asupload.html")


@app.route('/atupload', methods=["GET", "POST"])
def atupload():
    if request.method == 'POST':
        file = request.files['file']
        book = pd.read_csv(file)
        for row in range(len(book)):
            rows = (book.iloc[row][0],book.iloc[row][1],book.iloc[row][2],book.iloc[row][3],book.iloc[row][4],book.iloc[row][5])
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO teacher(name,email,password,teacherid,subject,branch) VALUES (%s,%s,%s,%s,%s,%s)",rows)
            mysql.connection.commit()
        flash( "File Uploaded...")
        return redirect(url_for('atupload'))
    else:
        return render_template("atupload.html")

@app.route('/aqlist' , methods=["GET","POST"])    
def aqlist():
    curl = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    curl.execute("select * from question")
    data = curl.fetchall()
    
    return render_template("aqlist.html", value=data)

 

if __name__ == '__main__':
    app.secret_key = "^A%DJAJU^JJ123"
    app.run(debug=True)
    #app.run(host='192.168.31.252', debug=True, port=3134)
