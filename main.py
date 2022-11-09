from flask import Flask, render_template, redirect, url_for
from flask import request
from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from flask_ckeditor import CKEditor
from datetime import date
from functools import wraps

from requests import Session
from sqlalchemy import ForeignKey
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_ckeditor import CKEditorField

from flask_gravatar import Gravatar

from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from wtforms import SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__, template_folder="template")

app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)
gravatar = Gravatar(app, size=100, rating='g', default='retro', force_default=False, force_lower=False, use_ssl=False,
                    base_url=None)

##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///DataBaseTables.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)






@login_manager.user_loader
def load_user(user_id):
    return Client.query.get(int(user_id))



def st():
    @login_manager.user_loader
    def load_user1(user_id):
        return staff.query.get(int(user_id))


class Client(UserMixin,db.Model):
    __tablenname__ = "Client"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    Address = db.Column(db.String(1000))
    PhoneNo = db.Column(db.Integer)
db.create_all()

##________________________________________________________________________
class Bugs(UserMixin,db.Model):
    __tablename__ = "Bugs"
    id = db.Column(db.Integer, primary_key=True)
    BugName = db.Column(db.String(100), unique=True)
    Description = db.Column(db.String(1000))
    Environment= db.Column(db.String(100))
    BugDate = db.Column(db.Integer)
    Client_Name = db.Column(db.String(100))
    BugPriority=db.Column(db.String(100))
    Phone_No = db.Column(db.Integer)
    Email_of_client = db.Column(db.String(1000))
    staff_Name=db.Column(db.String(1000))
    comment = relationship("Comment", back_populates="Parent_Bug")
    Status = db.Column(db.String(100))
db.create_all()
@app.route('/addBug',methods=["GET","POST"])
def addBug():
    if request.method == "POST":
        BugName = request.form.get("BugName")
        Description = request.form.get("description")
        Environment = request.form.get("environment")
        BugPriority=request.form.get("Bug_Priority")
        BugDate = request.form.get("Date")
        Client_Name = current_user.name

        Phone_No = current_user.PhoneNo
        Email_of_Client = current_user.email


        Status = "To Do"

        new_bug = Bugs(BugName=BugName, Description=Description,Environment=Environment,BugPriority=BugPriority,
                       BugDate=BugDate,Email_of_client=Email_of_Client,
                       Client_Name=Client_Name,  Phone_No=Phone_No,

                        Status=Status,
                       )
        db.session.add(new_bug)
        db.session.commit()
        return redirect(url_for("ClientPage"))
    return render_template("addBug.html")

##______________________________________________________________________________________________________________

class staff(UserMixin,db.Model):
    __tablename__ = "staff"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))
    comment=relationship("Comment",back_populates="comment_staff")

db.create_all()
##_______________________________________________________________________________________________________________

class Comment(db.Model):
    __tablename__ = "Comments"
    id = db.Column(db.Integer, primary_key=True)
    Bug_id = db.Column(db.Integer, db.ForeignKey("Bugs.id"))
    Staff_id = db.Column(db.Integer, db.ForeignKey("staff.id"))
    Parent_Bug = relationship("Bugs", back_populates="comment")
    comment_staff=relationship("staff",back_populates="comment")

    text = db.Column(db.Text, nullable=False)

db.create_all()

##________________________________________________________________________________________________________________

class admin(db.Model):
    __tablename__ = "admin"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

db.create_all()
def registerAdmin():
    hash_and_salted_password = generate_password_hash("12345", method='pbkdf2:sha256',
                                                      salt_length=8)
    Admin=admin(id=1,email="skdutta679@gmail.com",password=hash_and_salted_password,name="skdutta")
    db.session.add(Admin)
    db.session.commit()


Admin= admin.query.all()
if len(Admin)==0:
    registerAdmin()





##_________________________________________________________________________________________________________________


@app.route("/")
def home():
    return render_template("index.html")







@app.route("/registerClient", methods=["GET", "POST"])
def registerClient():


 if request.method == "POST":
      if Client.query.filter_by(email=request.form.get("email")).first():
            print(Client.query.filter_by(email=request.form.get("email")).first())
            flash("You have already signed up with that email,log in instead!","error")
            return redirect(url_for("loginClient"))

      hash_and_salted_password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256',
                                                              salt_length=8)
      new_client = Client(email=request.form.get("email"),
                                    name=request.form.get("Name"),
                                    Address=request.form.get("Address"),
                                   PhoneNo=request.form.get("phoneNo"),
                                    password=hash_and_salted_password)
      db.session.add(new_client)
      db.session.commit()

      login_user(client)
      return redirect(url_for("ClientPage"))


 return render_template("registerClient.html")


@app.route("/loginClient",methods=["GET", "POST"])
def loginClient():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        client = Client.query.filter_by(email=email).first()
        if not client:
            flash("That email does not exist,please try again","error")
            return redirect(url_for("loginClient"))

        elif not check_password_hash(client.password, password):
            print(client.password)
            flash("Password incorrect,please try again","error")
            return redirect(url_for("loginClient"))
        else:

            login_user(client)
            print(client.name)
            print(current_user.name)
            return redirect(url_for("ClientPage"))
    return render_template("loginClient.html")


@app.route('/ClientPage')
def ClientPage():
    print(current_user.name)
    return render_template("ClientPage.html")













@app.route('/viewBugsClient')
def viewBugsClient():
    print(current_user.name)
    ClientBug = Bugs.query.filter_by(Client_Name=current_user.name).all()
    return render_template("ClientBugReport.html", Bugs=ClientBug)


@app.route('/BugInfoClient<int:TicketNo>',methods=["GET", "POST"])
def BugInfoClient(TicketNo):
    comments=[]
    BugToDisplay = Bugs.query.filter_by(id=TicketNo).one()
    comment=Comment.query.all()
    print(comment)
    for c in comment:
        if c.Bug_id== BugToDisplay.id:
            comments.append(c)
            print(comments)
    if request.method=="POST":
        TicketNo=BugToDisplay.id
        print(TicketNo)
        return redirect(url_for("approve",TicketNo=TicketNo) )
    return render_template("BugDisplayClient.html", Bug=BugToDisplay,comments=comments)

@app.route('/approve<int:TicketNo>')
def approve(TicketNo):
    Bug=Bugs.query.filter_by(id=TicketNo).one()
    print(Bug)
    Bug.Status="Done"
    db.session.commit()
    ClientBug = Bugs.query.filter_by(Client_Name=current_user.name).all()
    return render_template("ClientBugReport.html", Bugs=ClientBug)


def decline(TicketNo):
    Bug=Bugs.query.get(id=TicketNo).one()

    return render_template("ClientBugReport.html",Bug=Bug)



@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for(home))



@app.route("/registerStaff", methods=["GET", "POST"])
def registerStaff():
    if request.method == "POST":
     if staff.query.filter_by(email=request.form.get("email")).first():
        print(staff.query.filter_by(email=request.form.get("email")).first())
        flash("This email id already exists!!","error")
        return redirect(url_for("registerStaff"))
    if request.method == "POST":
        hash_and_salted_password = generate_password_hash(request.form.get("password"), method='pbkdf2:sha256',
                                                          salt_length=8)
        new_staff = staff(email=request.form.get("email"),
                          name=request.form.get("Name"),
                          password=hash_and_salted_password)
        db.session.add(new_staff)
        db.session.commit()

        return redirect(url_for("AdminPage"))
    return render_template("registerStaff.html")


@app.route("/loginStaff", methods=["GET", "POST"])
def loginStaff():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        Staff = staff.query.filter_by(email=email).first()
        print(Staff)
        if not Staff:
            flash("That email does not exist,please try again","error")
            return redirect(url_for("loginStaff"))

        elif not check_password_hash(Staff.password, password):
            flash("Password incorrect,please try again","error")
            return redirect(url_for("loginStaff"))
        else:
            st()
            login_user(Staff)
            return redirect(url_for("StaffPage"))
    return render_template("loginStaff.html")


@app.route("/StaffPage")
def StaffPage():

    return render_template("StaffPage.html")


@app.route("/viewBugsStaff")
def viewBugsStaff():
    print(current_user.name)
    StaffBugs = Bugs.query.filter_by(staff_Name=current_user.name).all()

    return render_template("StaffBugReport.html", Bugs=StaffBugs)




@app.route("/BugDisplayStaff<int:TicketNo>", methods=["GET", "POST"])
def BugDisplayStaff(TicketNo):
    BugToDisplay = Bugs.query.filter_by(id=TicketNo).one()


    if request.method=="POST":
        textdata=request.form.get("comment")
        new_comment = Comment(text=textdata, comment_staff=current_user,Parent_Bug=BugToDisplay)
        db.session.add(new_comment)
        db.session.commit()
        return redirect(url_for("viewBugsStaff"))


    return render_template("BugDisplayStaff.html", Bug=BugToDisplay ,staffName=current_user.name)
















@app.route("/loginAdmin", methods=["GET", "POST"])
def loginAdmin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        Admin = admin.query.filter_by(email=email).first()
        if not Admin:
            flash("That email does not exist,please try again","error")
            return redirect(url_for("loginAdmin"))

        elif not check_password_hash(Admin.password, password):
            flash("Password incorrect,please try again","error")
            return redirect(url_for("loginAdmin"))
        else:

            return redirect(url_for("AdminPage"))
    return render_template("loginAdmin.html")



@app.route("/AdminPage")
def AdminPage():
    return render_template("AdminPage.html")


@app.route("/BugReportAdmin")
def BugReportAdmin():
    all_bugs = Bugs.query.all()
    return render_template("AdminBugReport.html", Bugs=all_bugs)


@app.route("/BugInfoAdmin<int:TicketNo>", methods=["GET", "POST"])
def BugInfoAdmin(TicketNo):
    BugToDisplay = Bugs.query.filter_by(id=TicketNo).one()
    Staff = staff.query.all()
    print(Staff)
    if request.method == "POST":

        selected_staff=request.form.get("selectedStaff")

        BugToDisplay.staff_Name=selected_staff

        BugToDisplay.Status="In Progress"
        db.session.commit()
        return redirect(url_for("BugReportAdmin"))

    return render_template("BugDisplayAdmin.html", Bug=BugToDisplay, All_staff=Staff)

@app.route("/Service")
def Service():
    return render_template("services.html")





@app.route("/tableDisplay")
def tableDisplay():
    return render_template("StaffBugReport.html")

if __name__ == "__main__":
    app.run(debug=True)
