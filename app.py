from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_login import UserMixin,login_user,logout_user,login_manager,LoginManager,current_user,login_required
from werkzeug.security import generate_password_hash,check_password_hash
import pymysql
pymysql.install_as_MySQLdb()


local_server=True
app=Flask(__name__) 
app.secret_key="srishti"


# app.config['SQLALCHEMY_DATABASE_URL']='mysql://username:password@localhost/database_table_name'

login_manager=LoginManager(app)
login_manager.login_view="login"

@login_manager.user_loader
def load_user(user_id):
    return User_info.query.get(int(user_id))

app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/hms'
db=SQLAlchemy(app)
 
class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))

class User_info(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))

class Patients(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    gender=db.Column(db.String(20))
    date=db.Column(db.String(50),nullable=False)
    slot=db.Column(db.String(50))
    time=db.Column(db.String(50),nullable=False)
    disease=db.Column(db.String(50))
    department=db.Column(db.String(50))
    phone_no=db.Column(db.String(50))
    address=db.Column(db.String(100))
    

class Doctors(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    d_name=db.Column(db.String(50))
    dept=db.Column(db.String(50))

class Trigr(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    action=db.Column(db.String(50))
    timestamp=db.Column(db.String(50))

@app.route("/")
def index():
    if current_user.is_authenticated:
        username=current_user.username
        return render_template('index.html',username=current_user.username)
    return render_template('index.html')

@app.route("/doctors",methods=['POST','GET'])
def doctors():
    if request.method=="POST":
        email=request.form.get('email')
        d_name=request.form.get('doctor_name')
        dept=request.form.get('department')
        db.session.execute(text("INSERT INTO doctors (email,d_name,dept) VALUES (:email,:d_name, :dept)"),{"email": email,"d_name": d_name,"dept":dept})
        db.session.commit()
        flash("Information Saved","info")
    return render_template('doctors.html')

@app.route("/patients",methods=['POST','GET'])
@login_required
def patients():
    doct=db.session.execute(text("select * from doctors")).fetchall()
    if request.method=="POST":
        email=request.form.get('email')
        name=request.form.get('full_name')
        gender=request.form.get('gender')
        date=request.form.get('date')
        slot=request.form.get('slot')
        time=request.form.get('timing')
        disease=request.form.get('disease')
        department=request.form.get('doctor_dep')
        phone_no=request.form.get('phone')
        address=request.form.get('address')
        db.session.execute(text("INSERT INTO patients (email,name, gender,date,slot,time,disease,department,phone_no,address) VALUES (:email,:name, :gender, :date,:slot,:time,:disease,:department,:phone_no,:address)"),{"email": email,"name": name,"gender":gender,"date":date,"slot":slot,"time":time,"disease":disease,"department":department,"phone_no":phone_no,"address":address})
        db.session.commit()
        flash("BOOKING CONFIRMED","info")

    return render_template('patients.html',doct=doct)

@app.route("/bookings")
@login_required
def bookings():
    em=current_user.email
    query=db.session.execute(text("select * from patients where email=:em"),{"em":em}).fetchall()
    return render_template('bookings.html',query=query)

@app.route("/edit/<string:id>",methods=['POST','GET'])
@login_required
def edit(id):
    posts=Patients.query.filter_by(id=id).first()
    if request.method=="POST":
        
        email=request.form.get('email')
        name=request.form.get('full_name')
        gender=request.form.get('gender')
        date=request.form.get('date')
        slot=request.form.get('slot')
        time=request.form.get('timing')
        disease=request.form.get('disease')
        department=request.form.get('doctor_dep')
        phone_no=request.form.get('phone')
        address=request.form.get('address')
        db.session.execute(
            text(
                "UPDATE patients SET name=:name, date=:date, slot=:slot, time=:time, "
                "disease=:disease, department=:department, phone_no=:phone_no, address=:address WHERE id=:id"
            ),
            {
                "name": name,
                "date": date,
                "slot": slot,
                "time": time,
                "disease": disease,
                "department": department,
                "phone_no": phone_no,
                "address": address,
                "id":id,
            },
        )
        db.session.commit ()
        flash("Details are updated","success")
        return redirect("/bookings")

    return render_template("edit.html",posts=posts)

@app.route("/delete/<string:id>",methods=['POST','GET'])
@login_required
def delete(id):
    db.session.execute(text("DELETE FROM patients WHERE id=:id"), {"id": id})
    db.session.commit()
    flash("Record deleted successfully!", "success")
    return redirect("/bookings")


@app.route("/signup",methods=['POST','GET']) 
def signup():
    if request.method=="POST":
        username=request.form.get("username")
        email=request.form.get("email")
        password=request.form.get("password")
        print(username,email,password)
        user=User_info.query.filter_by(email=email).first()
        if user:
            flash("email already exist","warning")
            return render_template('/signup.html')
        enc_pass=generate_password_hash(password)
        db.session.execute(text("INSERT INTO user_info (username, email, password) VALUES (:username, :email, :password)"),{"username": username, "email": email, "password": enc_pass})
        db.session.commit()
        flash("Signup Success, Please Login!","success")
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route("/login",methods=['POST','GET'])
def login():
    if request.method=="POST":
        email=request.form.get("email")
        password=request.form.get("password")
        user=User_info.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Successful","primary")
            return redirect(url_for('index'))
        else:
            flash("Invalid Credentials","danger")
            return render_template('login.html')
    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route("/test")
def test():
    try:
        Test.query.all()
        return "my database is connected"
    except:
        return "not connected"

@app.route("/search",methods=["POST","GET"])
@login_required
def search():
    if request.method=="POST":
        query=request.form.get("search")
        dept=Doctors.query.filter_by(dept=query).first()
        name=Doctors.query.filter_by(d_name=query).first()
        if dept:
            flash("Department is available","info")
        elif name:
            flash("Doctor is available","info")
    return redirect(url_for("index"))

@app.route("/details")
@login_required
def details():
    posts=Trigr.query.all()
    return render_template("trigers.html",posts=posts)





app.run(debug=True)

# username=current_user.username