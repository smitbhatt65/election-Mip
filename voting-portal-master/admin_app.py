from flask import Flask, render_template,request,redirect,session,flash
import jwt
import mysql.connector
import os
from flask_mail import Mail,Message
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import mysql.connector
import os

app = Flask(__name__)
app.secret_key=os.urandom(24)

conn = mysql.connector.connect(host="127.0.0.1",user="root",password = "",database="election")
cursor=conn.cursor()


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/admin_login')
def admin_login():
    if ('admin_id' in session):
        return redirect('admin_dashboard')
    else :
        return render_template('admin_login.html')

def mail(token, email):
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "mihirsharma999@gmail.com"  # Enter your address
    receiver_email = email# Enter receiver address
    token=token
    password = eminem@eminem
    message = """\
    MIME-Version: 1.0
    Content-type: text/html
    Subject: verify token
    
    <b>{url_for=verify+?token=token}</b>
    
    """


    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)

    pass


def generate_token(email):
    userid = cursor.execute("SELECT admin_id FROM admin WHERE admin_email=email")
    # aisa use krr k userid nikal
    user = { "userid" : userid }
    token = jwt.encode(user, app.secret_key)
    mail(token, email)



@app.route('/verify')
def verify():
    generate_token(email)
    token = request.args.get("token")
    if token:
        try:
            user = jwt.decode(token, app.secret_key)
            userid = user['userid']
            session['admin_id'] = userid
            return redirect('/admin_dashboard')
            
            # Idhar verify krne ka code likh de.
            # Jo bhi sql query hai wagere, fir redirect to homepage
        except:
            flash("token is invalid")
            return redirect('/admin_login')
            pass
            # Idhar aaya iska matlab token invalid hai. To login page pe redirect krr de
    else:
        flash("token missing")
        return redirect('/admin_login')
        # Idhar aaya matlab token hi nai hai. To login page pe redirect krr de
        pass

@app.route('/alogin_validation' ,methods=['POST'])
def alogin_validation():
    email=request.form.get('email')
    password=request.form.get('password')

    try:
        cursor.execute("SELECT * FROM admin WHERE admin_email ='{}' and admin_password ='{}'".format(email,password))
        admins = cursor.fetchall()
        if len(admins) > 0:
            session['admin_id'] =admins[0][0]
            generate_token(email)
            return "<h1>We Have Sent Email</h1>"
        else :
            flash("Incorrect email or password !!")
            return  redirect('/admin_login')
    except mysql.connector.Error as err:
        print(err)
        return redirect('/admin_login')


@app.route('/admin_dashboard')
def admin_dashboard():
    if ('admin_id' in session):
        try:
            cursor.execute("SELECT * FROM candidate WHERE can_verified=0")
            data = cursor.fetchall()
            return render_template('admin_dashboard.html',candidate=data)
        except mysql.connector.Error as err:
            print(err)
            return redirect('/admin_login')
    else:
        return redirect('/admin_login')