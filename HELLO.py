#coding=utf-8
from flask import Flask,request,flash,url_for,Blueprint,redirect
from flask_script import Manager
from flask_bootstrap import Bootstrap
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
import time
from flask_login import UserMixin,LoginManager,login_required,login_user,logout_user,current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField,BooleanField
from wtforms.validators import Required
# from MySQLdb import Table, Column, Integer, String, Date, Float
from sqlalchemy import Table, Column, BigInteger, String, Date, Float

#初始化flask login
app = Flask(__name__)
manager = Manager(app)
# current_user.is_authenticated=True
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.session_protection='strong'
login_manager.login_view='auth.login'
login_manager.init_app(app)


## 初始化数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:caokunlalala@localhost/lalal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
##修复flash bug
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'

db = SQLAlchemy(app)



# 登录表单
class LoginForm(FlaskForm):
    username = StringField('UserName',validators=[Required()])
    password = PasswordField('Password',validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

auth = Blueprint('auth', __name__)

# 建表结构
class User(UserMixin,db.Model):
    _tablename_='users'
    id=db.Column(db.BigInteger,primary_key = True)
    username=db.Column(db.String(64))
    password_hash =db.Column(db.String(128))
    stu_id=db.column(db.Integer,db.ForeignKey('student.id'))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username
# 回调函数
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/secret')
# @login_required
def secret():
    flash('Only authenticated users are allowed!','warning')
    return redirect(url_for('index'))

@app.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by( username=form.username.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            return redirect(request.args.get('next')or url_for('index'))
            flash ('login success','success')
        flash('Invailid username or pass word.','danger')
    return render_template('auth/login.html',form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you have been logged out.','warning')
    return redirect(url_for('index'))


class Student(db.Model):
    _tablenames_ = 'student'
    id = db.Column(db.BigInteger, nullable=False, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    sex = db.Column(db.String(16),nullable=False)
    login_year = db.Column(db.Integer,nullable=False)
    login_age=db.Column(db.Integer,nullable=False)
    cla = db.Column(db.Integer,nullable=False)

    def __init__(self, id, sex,name,login_year,login_age,cla):
        self.id = id
        self.name = name
        self.sex = sex
        self.login_age=login_age
        self.login_year=login_year
        self.cla=cla

    def __repr__(self):
        return self


class Course(db.Model):
    _tablenames_ = 'course'
    id = db.Column(db.BigInteger, nullable=False, primary_key=True)
    name = db.Column(db.String(16), nullable=False)
    tea_name = db.Column (db.String(16),nullable=False)
    credit= db.Column (db.Integer ,nullable=False)
    adapt_grade = db.Column(db.Integer,nullable = False)
    delete_year = db.Column(db.String(16) ,nullable = True)

    def __init__(self,id,name,tea_name,credit,adapt_grade,delete_year):
        self.id=id
        self.name=name
        self.tea_name=tea_name
        self.credit=credit
        self.adapt_grade=adapt_grade
        self.delete_year=delete_year

    def __repr__(self):
        return self
class Grade(db.Model):
    _tablenames_='grade'
    id = db.Column(db.String(100),nullable=True,primary_key=True)
    studentid=db.Column(db.BigInteger,db.ForeignKey('student.id'))
    courseid=db.Column(db.BigInteger,db.ForeignKey('course.id'))
    syear=db.Column(db.Integer)
    grade=db.Column(db.Integer)

    def __init__(self,studentid,courseid,syear,grade):
        self.studentid=studentid
        self.courseid=courseid
        self.syear=syear
        self.grade=grade
        self.id=time.time()

    def __repr__(self):
        return self
class Gradesc():
    def __init__(self,stuname,stuid,cname,syear,grade):
        self.studentname=stuname
        self.studentid=stuid
        self.coursename=cname
        self.syear=syear
        self.grade=grade
#处理url

#错误页面
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@app.route('/')
def index():
    name = "ck"
    return render_template('index.html',name=name)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)

#学生信息操作
@app.route('/add_stu',methods=["GET","POST"])
def add_stu():
    if request.method =="GET":
       return render_template('add_stu.html')
    else:
       name = request.form["name"]
       sex =request.form["sex"]
       id= request.form["id"]
       login_year=request.form["login_year"]
       login_age=request.form["login_age"]
       cla =request.form["cla"]
       a=Student(id, sex,name,login_year,login_age,cla)
       add(a)
       flash('add success','warning')
       return render_template('add_stu.html')

@app.route('/select_stu',methods=["GET","POST"])
def select_stu():
    if request.method =="GET":
        return render_template('select_stu.html')
    else:
        if request.form["name"]==u'':
            id=request.form["id"]
        else:
            name = request.form["name"]
        if request.form["name"] ==u'' and request.form["id"] ==u'':
            students=Student.query.all()
        elif request.form["name"] ==u'':
            students=Student.query.filter_by(id=id).all()
        else:
            students=Student.query.filter_by(name=name).all()
        # if request.form["studentid"]!=u'':
        #     id=request
        #     stu_d = Student.query.filter_by(id=id).first()
        #     selectscs = Grade.query.filter_by(id=stu_d.id).all()
        #     for selectsc in selectscs:
        #         delete(selectsc)

        return render_template('select_stu.html',students=students)

@app.route('/delete_stu',methods=["GET","POST"])
def delete_stu():
    if request.method =="GET":
        return render_template('delete_stu.html')
    else:
        lalala=request.form["name"]
        if  lalala !=u'':
           name=lalala
        else:
           id=int(request.form["id"])
        if lalala ==u'':
           stu_d=Student.query.filter_by(id=id).first()
           selectscs=Grade.query.filter_by(id=stu_d.id).all()
           for selectsc in selectscs:
               delete(selectsc)
        else:
           stu_d=Student.query.filter_by(name=name).first()
           selectscs=Grade.query.filter_by(studentid=stu_d.id).all()
           for selectsc in selectscs:
               delete(selectsc)
        delete(stu_d)
        flash('delete success','danger')
        lalala=None
        name=None
        return render_template('delete_stu.html')

@app.route('/alter_atu',methods=['GET','POST'])
def alter_stu():
    if request.method =="GET":
        return render_template('alter_atu.html')
    else:
        name = request.form["name"]
        sex =request.form["sex"]
        id= int(request.form["id"])
        login_year=request.form["login_year"]
        login_age=request.form["login_age"]
        cla =request.form["cla"]
        stu=Student.query.filter_by(id=id).first()
        if not stu:
            flash('no this student!','info')
            return render_template(url_for('alter_atu.html'))
        else:
            stu.name=name
            stu.sex=sex
            stu.login_year=int(login_year)
            stu.login_age=int(login_age)
            stu.cla = int(cla)
            add(stu)
            flash(u'alter success!','success')
            return render_template('alter_atu.html')


#课程操作
@app.route('/select_course',methods=['GET','POST'])
def select_course():
    if request.method == 'GET':
        return render_template('select_course.html')
    else :
        if request.form["name"]==u'':
            id=request.form["id"]
        else:
            name = request.form["name"]
        if request.form["name"] ==u'' and request.form["id"] ==u'':
            courses=Course.query.all()
        elif request.form["name"] ==u'':
            courses=Course.query.filter_by(id=id).all()
        else:
            courses=Course.query.filter_by(name=name).all()

        return render_template('select_course.html',courses=courses)

@app.route('/add_course',methods=['GET','POST'])
def add_course():
    if request.method == 'GET':
        return render_template('add_course.html')
    else :
        coursename=request.form["course_name"]
        courseid=request.form["course_id"]
        teacher = request.form["teacher"]
        credit=request.form["credit"]
        adaptyear = request.form["adapt_year"]
        deleteyear = request.form["delete_year"]
        if deleteyear==u'':
            course = Course(courseid, coursename, teacher, credit, adaptyear, None)
        else:
            course = Course(courseid, coursename, teacher, credit, adaptyear, deleteyear)
        add(course)
        flash('add success','success')
        return render_template('add_course.html')

@app.route('/add_sc',methods=['GET','POST'])
def add_sc():
    if request.method == "GET":
        return render_template('add_sc.html')
    else:
        stuname=request.form["stu_name"]
        student=Student.query.filter_by(name=stuname).first()
        studentid=student.id
        coursename=request.form["course_name"]
        course=Course.query.filter_by(name=coursename).first()
        courseid=int(course.id)
        syear=request.form["syear"]
        grade=request.form["grade"]
        lee=Grade(studentid,courseid,syear,grade)
        add(lee)
        flash('add success','success')
        return render_template('add_sc.html')

@app.route('/select_sc',methods=['GET','POST'])
def select_sc():
    if request.method =="GET":
        return render_template('select_sc.html')
    else:
        stuname=request.form["sname"]
        coursename =request.form["cname"]


        if stuname==u'' and coursename==u'':
            grades = Grade.query.all()
            gradescs=[]
            for grade in grades:
                sname=Student.query.filter_by(id=grade.studentid).first().name
                cname=Course.query.filter_by(id=grade.courseid).first().name
                a= Gradesc(sname,grade.studentid,cname,grade.syear,grade.grade)
                gradescs.append(a)
            return render_template('select_sc.html',gradescs=gradescs)
        elif stuname==u'':
            course = Course.query.filter_by(name=coursename).first()
            grades = Grade.query.filter_by(courseid=course.id).all()
            gradescs=[]
            for grade in grades:
                sname = Student.query.filter_by(id=grade.studentid).first().name
                cname = Course.query.filter_by(id=grade.courseid).first().name
                a = Gradesc(sname, grade.studentid, cname, grade.syear, grade.grade)
                gradescs.append(a)
            return render_template('select_sc.html', gradescs=gradescs)
        else:
            students = Student.query.filter_by(name=stuname).all()
            gradescs = []
            for student in students:
                grades = Grade.query.filter_by(studentid=student.id).all()
                for grade in grades:
                    sname = Student.query.filter_by(id=grade.studentid).first().name
                    cname = Course.query.filter_by(id=grade.courseid).first().name
                    a = Gradesc(sname, grade.studentid, cname, grade.syear, grade.grade)
                    gradescs.append(a)
            return render_template('select_sc.html',gradescs=gradescs)
@app.route('/course_grade',methods=['GET','POST'])
def course_grade():
    if request.method =="GET":
        return render_template("course_grade.html")
    else :
        courseid=request.form["courseid"]
        grades=Grade.query.filter_by(courseid=courseid).all()
        num=0
        i=0
        s = a = b = c = d = e = 0
        for grade in grades:
            i+=1
            num+=grade.grade
            if grade==100:
                s+=1
            elif grade.grade>=90:
                a+=1
            elif grade.grade >=80:
                b+=1
            elif grade.grade>=70:
                c+=1
            elif grade.grade>=60:
                d+=1
            else:
                e+=1
        if len(grades)==0:
            num=0
        else:
            num=num/len(grades)
        return render_template("course_grade.html",s=s,a=a,b=b,c=c,d=d,e=e,num=num)

@app.route('/allgrade',methods=['GET','POST'])
def allgrade():
    if request.method=="GET":
        class1 = getclassavg(1)
        class2 = getclassavg(2)
        class3 = getclassavg(3)
        class4 = getclassavg(4)
        return render_template('allgrade.html',class1=class1,class2=class2,class3=class3,class4=class4)
    else:
        class1 = getclassavg(1)
        class2 = getclassavg(2)
        class3 = getclassavg(3)
        class4 = getclassavg(4)
        studentname=request.form["name"]
        studentid = request.form["id"]
        if studentid==u'' and studentname==u'':
            students = Student.query.all()
            studentgs=[]
            for student in students:
                a=Gradesc(student.name,student.id,0,0,getavg(student.id))
                # a.studentname=student.name
                # a.studentid=student.id
                # a.grade=getavg(a.studentid)
                studentgs.append(a)
            return render_template('allgrade.html', class1=class1, class2=class2, class3=class3, class4=class4,students=studentgs)
        elif studentid==u'':
            students = Student.query.filter_by(name=studentname).all()
            studentgs=[]
            for student in students:
                a=Gradesc(student.name,student.id,0,0,getavg(student.id))
                # a.studentname=student.name
                # a.studentid=student.id
                # a.grade=getavg(a.studentid)
                studentgs.append(a)
            return render_template('allgrade.html', class1=class1, class2=class2, class3=class3, class4=class4,students=studentgs)
        else:
            students = Student.query.filter_by(id=studentid).all()
            studentgs=[]
            for student in students:
                a=Gradesc(student.name,student.id,0,0,getavg(student.id))
                # a.studentname=student.name
                # a.studentid=student.id
                # a.grade=getavg(a.studentid)
                studentgs.append(a)
            return render_template('allgrade.html', class1=class1, class2=class2, class3=class3, class4=class4,students=studentgs)


@app.route('/delete_sc',methods=['GET','POST'])
def delete_sc():
    if request.method=="GET":
        return  render_template('delete_sc.html')
    else :
        studentid=request.form["studentname"]
        courseid=request.form["coursename"]
        grade=Grade.query.filter_by(studentid=studentid,courseid=courseid).first()
        delete(grade)
        flash('delete success','success')
        return render_template('delete_sc.html')

##功能


def getavg(id):
    grades=Grade.query.filter_by(studentid=id).all()
    avg=0
    allcredit=0
    for grade in grades:
        credit = Course.query.filter_by(id=grade.courseid).first().credit
        avg+=grade.grade*credit
        allcredit+=credit
    if len(grades)==0:
        avg=0
    else:
        avg=avg/allcredit
    return avg

def getclassavg(classnum):
    students=Student.query.filter_by(cla=classnum).all()
    avg=0
    for student in students:
        avg+=getavg(student.id)
    if len(students)==0:
        avg=0
    else:
        avg=avg/len(students)
    return avg



# db操作
def add(item):
    db.session.add(item)
    db.session.commit()
    return None


def undo():
    db.session.rollback()


def delete(item):
    db.session.delete(item)
    db.session.commit()


# def query(condition):
#     if condition == None:


if __name__ == '__main__':
    # manager.run()
    # db.create_all()

    # u=User(id=100,username='ck',password='ck')
    # db.session.add(u)
    # db.session.commit()
    # a=Student(3,1,1,1,1,1)
    # db.session.add(a)
    # db.session.commit()
    #s=Student(12,'ckk')
    # db.session.add(s)
    # db.session.commit()
    # la=web.input(name="name")
    # db.session.delete(users)
    # db.session.commit
    # for stu_d in users:
    #     deleteone= Student(int(stu_d.id),stu_d.sex,stu_d.name,int(stu_d.login_year),(int)(stu_d.login_age),(int)(stu_d.cla))
    #     db.session.delete(deleteone)
    app.run(debug=True)
    la = None
    if not la:
        print"1"
    else:
        print"2"
