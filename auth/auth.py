from flask import Flask, render_template, request, url_for, redirect, flash, Blueprint, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import Users, db
import smtplib
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from dotenv import load_dotenv, find_dotenv
import os

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

secret_key = os.getenv("secret_key")

auth_bp = Blueprint("auth_bp", __name__, template_folder="templates")
s = URLSafeTimedSerializer(secret_key=secret_key)


@auth_bp.route("/register", methods = ["GET","POST"])
def register():
    if request.method == "POST":
        user_name = request.form.get("name")
        email = request.form.get("email")
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
        
        
        user = Users.query.filter_by(email = email ).first()
        existing_user_name = Users.query.filter_by(user_name = user_name ).first()
        if user:
            flash("User with this email already exists.", category="error")
        
        elif existing_user_name:
            flash("User with this name already exists.", category="error")


        elif len(password1) < 6:
            flash("Password is too short.", category="error")
        
        elif password1 != password2:
             flash("Password doesn't match", category="error")
        
        else:
            hashed_password = generate_password_hash(password1, method="pbkdf2:sha256")   
            user = Users(user_name=user_name,email = email,password1=hashed_password)
            db.session.add(user)
            db.session.commit()
            flash("Logged sucessfully", category = "success")
            login_user(user, remember=True)
            return redirect(url_for("home"))

        return redirect(url_for("auth_bp.register"))
    
    return render_template("auth/register_page.html", user = current_user)
       
   
@auth_bp.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        name  = request.form.get("name")
        password1 = request.form.get("password")
        user = Users.query.filter_by(user_name = name).first()
        
        if user and check_password_hash(user.password1, password1):
            login_user(user, remember=True)
            session.pop("food", None)
            
            
            flash("Logged sucesfully.", category="success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password.", category="error")
            return redirect(url_for("auth_bp.login"))
    return render_template("auth/login.html", user = current_user)
    

@auth_bp.route("/forgotpass", methods = ["GET", "POST"])
def forgot_pass():
    
    if request.method == "POST":
        email = request.form.get("em_to_pass")
        all_users = Users.query.filter_by(email = email).first()
        print(all_users)
        if all_users:
            
            passw = new_password()
            data = {"email" : email, "temp_password" : passw}
            token = s.dumps(data)
            sent_new_password(email, password= passw, token = token)
            flash("Confirm link in your email.")
            return redirect(url_for("auth_bp.login")) 
            
        else:
            flash("No account found for this email. Try again." ,category="error")
            return redirect(url_for("auth_bp.forgot_pass"))

    
    
    return render_template("auth/new_pass.html", user = current_user)

@auth_bp.route("/confirm_new_pass/<token>")
def confirm_new_pass(token):
    try:
        data = s.loads(token,max_age=10)
        email = data["email"]
        temp_password = data["temp_password"]
        user = Users.query.filter_by(email = email).first()
        print(user)

        if not user:
            flash("User not found.", category= "error")
            return redirect(url_for("auth_bp.login"))
        
        
        hashed_password = generate_password_hash(temp_password, method="pbkdf2:sha256")   
        user.password1 = hashed_password
        db.session.commit()
        flash("Password sucessfully changed. Login with new password.", category= "success")
        return redirect(url_for("auth_bp.login"))

    except SignatureExpired:
        flash("Confirmation link expired. Try again.", category= "success")
        return redirect(url_for("auth_bp.login"))


   

@auth_bp.route("/change_password", methods = ["GET", "POST"])
@login_required
def change_password():
    em = current_user.email
    user =  Users.query.filter_by(email = em).first()
    if request.method == "POST":
        current_pass = request.form.get("cur_pass", "").strip()
        password1 = request.form.get("password1")
        password2 = request.form.get("password2")
    
        if password1 == password2:

            if current_pass and check_password_hash(user.password1, current_pass):
                hashed_password = generate_password_hash(password1, method="pbkdf2:sha256")
                user.password1 = hashed_password
                db.session.commit()
                flash("Password sucessfully changed.", category="message")
                return redirect(url_for("home"))
            else:
                flash("Invalid password.", category="error")
                return redirect(url_for("auth_bp.change_password"))
        else:
            flash("Passwords doesnt match.", category="error")
            return redirect(url_for("auth_bp.change_password"))

    return render_template("auth/change_pass.html", user = current_user)






def sent_new_password(to_email, password, token):
    from email.mime.multipart import MIMEMultipart 
    from email.mime.text import MIMEText
   
     # sending form data to my personal email
        
    web_email = "jakubvecera.web@gmail.com"
    my_password = os.getenv("my_password")
    link = url_for("auth_bp.confirm_new_pass",token = token, _external = True)
    send_to = to_email

    msg = MIMEMultipart()
    msg['From'] = web_email
    msg['To'] = send_to
    msg['Subject'] = "Password reset"
    message = (f"Email sent from Calorie database website.\n"
                   "\n"
                   f"Your new password is: {password}\n"
                   
                   f"Confirm your apply for new password by clicking on this link: {link} and use password from above."
                
                 )
        
    msg.attach(MIMEText(message))
    try:
        mailserver = smtplib.SMTP('smtp.gmail.com',587)
        mailserver.ehlo()
        mailserver.starttls()
        mailserver.login(user=web_email, password=my_password)

        mailserver.sendmail(from_addr=web_email,to_addrs=send_to,msg=msg.as_string())
        

        mailserver.quit()
    except Exception as e:
        return e

def new_password():
    import secrets
    passw = secrets.token_urlsafe(6)
    return passw
    
    
    


# Logout route
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    
    session.pop("food", None)

    # session.clear()
    return redirect(url_for("home"))