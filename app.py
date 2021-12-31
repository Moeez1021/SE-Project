from logging import NullHandler
from flask import Flask
from flask import render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import re
from datetime import timedelta

app = Flask(__name__)

app.secret_key = "project"
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "12345"
app.config["MYSQL_DB"] = "project"

mysql = MySQL(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST':
        userdetails = request.form
        name = userdetails['name']
        email = userdetails['email']
        password = userdetails['password']
        c_password = userdetails['cpassword']
        semesid = userdetails['semesid']
        if c_password == password:
            cur = mysql.connection.cursor()
            cur.execute(
                'SELECT * FROM students WHERE name = %s OR email = % s', (name, email))
            account = cur.fetchall()
            if account:
                msg = 'Account already exists !'
                return redirect('/login')
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address !'
            elif not re.match(r'[A-Za-z]+', name):
                msg = 'name must contain only characters!'
            elif not name or not email or not password:
                msg = 'Please fill out the form !'
            else:
                cur.execute(
                    'INSERT INTO students VALUES (NULL, % s, % s, % s, % s)', (name, email, password, semesid))
                mysql.connection.commit()
                cur.close()
                msg = 'You have successfully registered !'
                return redirect('/adminstds')
    # elif request.method == 'POST':
    #     msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route("/login", methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        userDetails = request.form
        email1 = userDetails['email']
        password1 = userDetails['password']
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM students WHERE email = % s AND password = % s', (email1, password1))
        account = cur.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['name'] = account[1]
            session['email'] = account[2]
            session['semesid'] = account[4]
            msg = 'Logged in successfully !'
            return redirect(url_for('dashboard'))
        cur = mysql.connection.cursor()
        cur.execute(
            'SELECT * FROM admin WHERE email = % s AND password = % s', (email1, password1))
        account = cur.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['name'] = account[1]
            session['email'] = account[2]
            msg = 'Logged in successfully !'
            return redirect(url_for('admindashboard'))
        else:
            msg = 'Incorrect name / password !'
    return render_template("login.html", msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('name', None)
    return redirect(url_for('login'))

# @app.before_request
# def sessions():
#     session.permanent = True
#     app.permanent_session_lifetime = timedelta(seconds=10)

def GPA_cal(grades):
    QP = 0
    credit_hrs = 0
    for i in grades:
        QP = QP + (i[0] * i[1])
        credit_hrs = credit_hrs + i[0]
    gpa = QP/credit_hrs
    GPA = ("{:.2f}".format(round(gpa, 2)))
    return GPA

@app.route('/dashboard')
def dashboard():
    if session['loggedin'] == True:
        C_courses = []
        stdid = session['id']
        name = session['name']
        cur_semes = session['semesid']
        cur = mysql.connection.cursor()
        # if cur_semes > 1:
        #     pre_semes = cur_semes - 1
        #     cur.execute('SELECT credit_hours,grade_point FROM results WHERE stdid=%s AND semesid=%s',(stdid,str(pre_semes)))
        #     grades = cur.fetchall()
        #     gpa = GPA_cal(grades)
        #     TQP = 0
        #     Tcredit_hrs = 0
        #     for i in range(1,cur_semes):
        #         cur.execute('SELECT credit_hours,grade_point FROM results WHERE stdid=%s AND semesid=%s',(stdid,str(i)))
        #         all_grades = cur.fetchall()
        #         for i in all_grades:
        #             TQP = TQP + (i[0] * i[1])
        #             Tcredit_hrs = Tcredit_hrs + i[0]
        #     cgpa = TQP/Tcredit_hrs
        #     CGPA = ("{:.3f}".format(round(cgpa, 3)))
        # else:
        #     gpa = None
        #     CGPA = None
        # cur.execute('SELECT * FROM semesters WHERE id = %s', str(cur_semes))
        # account = cur.fetchall()
        # for i in account:
        #     C_courses.append(i[2])
        cur.execute('SELECT * FROM announcements ORDER BY id DESC')
        acc = cur.fetchone()
        return render_template("dashboard.html", s=cur_semes, name=name, len=len(C_courses), courses=C_courses, an=acc)
    return redirect('/login')

# , GPA=gpa, CGPA=CGPA
@app.route('/announcement')
def announcement():
    if session['loggedin'] == True:
        name = session['name']
        announcements = []
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM announcements ORDER BY id DESC')
        account = cur.fetchall()
        for i in account:
            announcements.append(i)
        return render_template("announcement.html", name=name, an=announcements, len=len(announcements))

@app.route('/courses')
def courses():
    if session['loggedin'] == True:
        C_courses = []
        name = session['name']
        cur_semes = session['semesid']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM semesters WHERE id = %s', str(cur_semes))
        account = cur.fetchall()
        for i in account:
            C_courses.append(i[2])
        return render_template("courses.html", s=cur_semes, name=name, len=len(C_courses), courses=C_courses)

@app.route('/courses1')
def courses1():
    if session['loggedin'] == True:
        C_courses = []
        name = session['name']
        cur_semes = session['semesid']
        for s in range(1,cur_semes+1):
            cur = mysql.connection.cursor()
            cur.execute('SELECT * FROM semesters WHERE id = %s', str(s))
            account = cur.fetchall()
            for i in account:
                C_courses.append(i[2])
        return render_template("courses1.html", s=cur_semes, name=name, len=len(C_courses), courses=C_courses)

@app.route('/profile')
def profile():
    name = session['name']
    em = session['email']
    return render_template("profile.html", name=name, email=em)


@app.route('/admindashboard')
def admindashboard():
    if session['loggedin'] == True:
        name = session['name']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM announcements ORDER BY id DESC')
        acc = cur.fetchone()
        return render_template("admindashboard.html", name=name, an=acc)


@app.route('/adminannouncement', methods=['GET', 'POST'])
def adminannouncement():
    if request.method == 'POST':
        userdetails = request.form
        text = userdetails['texts']
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO announcements (id, texts) VALUES (%s, %s)', (None, text))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('adminannouncement'))
    if session['loggedin'] == True:
        name = session['name']
        announcements = []
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM announcements ORDER BY id DESC')
        account = cur.fetchall()
        for i in account:
            announcements.append(i)
        return render_template("adminannouncement.html", name=name, an=announcements, len=len(announcements))

@app.route('/adminstds')
def admindstds():
    if session['loggedin'] == True:
        name = session['name']
        students = []
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM students ORDER BY semesid')
        stds = cur.fetchall()
        for i in stds:
            students.append(i)
        return render_template("adminstds.html", name=name, len=len(students),students=students)

@app.route('/adminresults')
def admindresults():
    if session['loggedin'] == True:
        name = session['name']
        students = []
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM students ORDER BY semesid')
        stds = cur.fetchall()
        for i in stds:
            students.append(i)
        return render_template("adminresults.html", name=name, len=len(students),students=students)

@app.route("/addresults", methods=['GET', 'POST'])
def addresults():
    if request.method == 'POST':
        userdetails = request.form
        stdid = userdetails['stdid']
        semesid = userdetails['semesid']
        course_code = userdetails['course_code']
        credit_hours = userdetails['credit_hours']
        grade_point = userdetails['grade_point']
        cur = mysql.connection.cursor()
        cur.execute('SELECT * from students WHERE id=%s',(stdid))
        std = cur.fetchone()
        cur.execute('SELECT id,course_code,credit_hours from semesters WHERE id=%s AND course_code=%s AND credit_hours=%s',(semesid,course_code,credit_hours))
        semes = cur.fetchone()
        # print(stdid,semesid,semes[0],semes[1],semes[2])
        # print(std[0],std[4],semesid,course_code,credit_hours)
        # if str(stdid) == str(std[0]) and str(semesid) == str(std[4]):
            # if str(semes[0]) == str(semesid) and str(semes[1]) == str(course_code) and str(semes[2]) == str(credit_hours):
        if std and semes:
            print("DONE")
            cur.execute('INSERT INTO results VALUES (% s, % s, % s, % s, % s)', (stdid, semesid, course_code, credit_hours, grade_point))
            mysql.connection.commit()
            cur.close()
            return redirect('/adminresults')
        else:
            return redirect('/addresults')
    return render_template("addresults.html")
    
    
    
    
    
# @app.route('/posts', methods=['GET', 'POST'])
# def posts():
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT * FROM posts ORDER BY postid DESC;")
#     postDetails = cur.fetchall()
#     return render_template('post.html', postDetails=postDetails)


# @app.route('/createpost', methods=['GET', 'POST'])
# def createpost():
#     if request.method == 'POST':
#         userDetails = request.form
#         name = userDetails['name']
#         title = userDetails['title']
#         text = userDetails['text']
#         cur = mysql.connection.cursor()
#         cur.execute(
#             'INSERT INTO posts(name,title,text) VALUES(%s, %s, %s)', (name, title, text))
#         mysql.connection.commit()
#         cur.close()
#         return redirect('/posts')
#     return render_template('create.html')
