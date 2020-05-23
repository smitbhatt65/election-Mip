from flask import Flask, render_template,request,redirect,session,flash,url_for
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
    password = 'eminem@eminem'
    message = """\
    MIME-Version: 1.0
    Content-type: text/html
    Subject: verify token
    
    <b>{}</b>
    
    """.format(url_for('verify') + "?token=" + token)


    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)




def generate_token(email, userid):
    # cursor.execute("SELECT admin_id FROM admin WHERE admin_email={}".format(email))

    # aisa use krr k userid nikal
    user = { "userid" : userid }
    token = jwt.encode(user, app.secret_key)
    #mail(token, email)
    print("http://127.0.0.1:5000/verify?token=" + str(token) )



@app.route('/verify')
def verify():

    token = request.args.get("token")
    if token:
        try:
            user = jwt.decode(token, app.secret_key)
            userid = user['userid']
            session['admin_id'] = userid
            return redirect('/admin_dashboard')
            
            # Idhar verify krne ka code likh de.
            # Jo bhi sql query hai wagere, fir redirect to homepage
        except Exception as e:
            flash("token is invalid")

            return redirect('/admin_login')
            print(e)
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
            userid =admins[0][0]
            generate_token(email, userid)
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

@app.route('/evaluate candidate/<int:cid>',methods=['GET'])
def candidate_form(cid):
    cursor.execute("SELECT * FROM candidate WHERE can_id='{}'".format(cid))
    data=cursor.fetchall()
    return render_template('display_can_form.html',candidate=data)

@app.route('/accept/<string:id_data>',methods=['GET'])
def accept(id_data):
    flash("Record has been accepted")
    cursor.execute("UPDATE candidate SET can_verified=1 WHERE can_id=%s",(id_data,))
    conn.commit()
    return redirect('/admin_dashboard')

@app.route('/reject/<string:id_data>', methods = ['GET'])
def delete(id_data):
    flash("Record Has Been Deleted Successfully")
    cursor.execute("DELETE FROM candidate WHERE can_id=%s", (id_data,))
    conn.commit()
    return redirect('/admin_dashboard')





@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_id')
    return redirect('/')




@app.route('/voter_login')
def voter_login():
    if ('voter_id' in session):
        return redirect('voter_dashboard')
    else :
        return render_template('voter_login.html')

@app.route('/voter_register')
def voter_register():
    if ('voter_id' in session):
        return redirect('/voter_dashboard')
    else :
        return render_template('voter_reg.html')


@app.route('/voter_dashboard')
def voter_dashboard():
    if ('voter_id' in session):
        try:
            cursor.execute("SELECT * FROM candidate WHERE can_verified=1")
            data = cursor.fetchall()
            return render_template('voter_dashboard.html', candidate=data)
        except mysql.connector.Error as err:
            print(err)
            return redirect('/voter_login')
    else:
        return redirect('/voter_login')

@app.route('/vlogin_validation', methods=['POST'])
def vlogin_validation():
    email=request.form.get('email')
    password=request.form.get('password')

    try :
        cursor.execute("SELECT * FROM voter WHERE voter_email ='{}' AND voter_pwd='{}'".format(email,password))
        voters=cursor.fetchall()
        if len(voters) > 0:
            session['voter_id']=voters[0][0]
            return redirect('/voter_dashboard')
        else :
            flash("Incorrect email or password !!")
            return redirect('/voter_login')
    except mysql.connector.Error as err:
        print(err)
        return redirect('/voter_login')

@app.route('/add_voter',methods=['POST'])
def add_voter():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    email = request.form.get('email')
    gender = request.form.get('gender')
    branch = request.form.get('branch')
    current_year = request.form.get('cyear')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    ip_vars = [fname, lname, email, gender, branch, current_year, password, confirm_password]
    if(None in ip_vars or '' in ip_vars or 'select branch' in ip_vars):
        flash("All fields are required")
        return redirect('/voter_register')

    query = "INSERT INTO voter (voter_fname,voter_lname,voter_email,voter_gender,voter_branch,\
          voter_cuyear,voter_pwd) VALUES(%s, %s, %s, %s, %s, %s, %s)"

    try:
        params = (fname, lname, email, gender, branch, current_year, password)
        cursor.execute(query, params)
        conn.commit()
    except mysql.connector.Error as err:
        print(err)
        return redirect('/voter_register')
    finally:
        cursor.execute("SELECT * FROM voter WHERE voter_email LIKE '{}'".format(email))
        add_voter = cursor.fetchall()
        session['voter_id'] = add_voter[0][0]
        return redirect('/voter_dashboard')

@app.route('/voter_logout')
def voter_logout():
    session.pop('voter_id')
    return redirect('/')



@app.route('/candidate_login')
def candidate_login():
    if ('can_id' in session):
        return redirect('candidate_dashboard')
    else :
        return render_template('candidate_login.html')


@app.route('/candidate_register')
def candidate_register():
    if ('can_id' in session):
        return redirect('/candidate_dashboard')
    else:
        return render_template('candidate_reg.html')

@app.route('/candidate_dashboard')
def candidate_dashboard():
    if ('can_id' in session):
        id=session.get('can_id')
        cursor.execute("SELECT * FROM candidate WHERE can_id ='{}'".format(id))
        candidates =cursor.fetchall()
        return render_template('candidate_dashboard.html', candidate=candidates)
    else:
        return redirect('/candidate_login')

@app.route('/clogin_validation', methods=['POST'])
def clogin_validation():
    email=request.form.get('email')
    password=request.form.get('password')
    try :
        cursor.execute("SELECT * FROM candidate WHERE can_email ='{}' AND can_password='{}'".format(email,password))
        candidates=cursor.fetchall()
        if len(candidates) > 0:
            session['can_id'] = candidates[0][0]
            return redirect('/candidate_dashboard')
        else :
            flash("Incorrect email or password !!")
            return redirect('/candidate_login')
    except mysql.connector.Error as err:
        print(err)
        return redirect('/candidate_login')

@app.route('/add_candidate',methods=['POST'])
def add_candidate():
    fname = request.form.get('fname')
    lname = request.form.get('lname')
    address = request.form.get('address')
    dob = request.form.get('dob')
    email = request.form.get('email')
    pno = request.form.get('pno')
    gender = request.form.get('gender')
    branch = request.form.get('branch')
    current_year = request.form.get('cy')
    cgpa = request.form.get('cgpa')
    bio = request.form.get('bio')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    image_name = request.files['profile_img'].filename


    ip_vars = [fname, lname, address, dob, email, pno, gender, branch, current_year, cgpa, bio, image_name,
               password,confirm_password]

    if(None in ip_vars or '' in ip_vars or 'select branch' in ip_vars):
        flash("All fields are required")
        return redirect('/candidate_register')


    ALLOWED_EXTENSIONS =['.png', '.jpg', '.jpeg']
    image_ext =  os.path.splitext(image_name)[1]
    if image_ext not in ALLOWED_EXTENSIONS:
        flash("Allowed Extensions are : jpg, jpeg, png ")
    image_path = "./static/candidate_images/" + image_name
    request.files['profile_img'].save(image_path)



    query = "INSERT INTO candidate(can_fname,can_lname,can_add,can_dob,can_email,can_pno,can_gen, \
            can_branch,can_cy,can_cgpa,can_bio,can_pro_img,can_password) VALUES (%s, %s, %s, %s, %s, %s, %s, \
             %s,%s,%s,%s,%s,%s)"
    try:
        params = (fname, lname, address, dob, email, pno, gender, branch, current_year, cgpa, bio, image_path[1:], password)
        cursor.execute(query, params)
        conn.commit()
    except mysql.connector.Error as err:
        print(err)
        return redirect('/candidate_register')
    finally:
        cursor.execute("SELECT * FROM candidate WHERE can_email = '{}'".format(email))
        add_can = cursor.fetchall()
        session['can_id'] = add_can[0][0]
        return redirect('/candidate_dashboard')

@app.route('/candidate_logout')
def candidate_logout():
    session.pop('can_id')
    return redirect('/')

@app.route('/update_bio',methods=['POST'])
def update_bio() :
    bio = request.form.get('up_bio')
    id = session.get('can_id')
    try:
        cursor.execute("UPDATE candidate SET can_bio='{}' where can_id='{}'".format(bio,id))
        conn.commit()
    except mysql.connector.Error as err:
        print(err)
        flash("Update failed")
    finally:
        return  redirect('/candidate_dashboard')

@app.route('/update_profileimg',methods=['POST'])
def update_profileimg() :
    ALLOWED_EXTENSIONS = ['.png', '.jpg', '.jpeg']

    image_name = request.files['up_profile_img'].filename
    image_ext = os.path.splitext(image_name)[1]
    if image_ext not in ALLOWED_EXTENSIONS:
        flash("Allowed Extensions are : jpg, jpeg, png ")
    image_path = "./static/candidate_images/" + image_name
    request.files['up_profile_img'].save(image_path)
    id = session.get('can_id')
    try:
        cursor.execute("UPDATE candidate SET can_pro_img='{}' where can_id='{}'".format(image_path[1:], id))
        conn.commit()
    except mysql.connector.Error as err:
        print(err)
        flash("Update failed")
    finally:
        return redirect('/candidate_dashboard')


@app.route('/voting_portal')
def voting_portal():
    if ('voter_id' in session):
        id = session.get('voter_id')
        cursor.execute("SELECT * FROM voter WHERE voter_id ='{}'".format(id))
        voter = cursor.fetchall()

        if voter[0][9] == 'TRUE':
            cursor.execute("SELECT * FROM candidate WHERE can_verified=1")
            can_list = cursor.fetchall()
            return render_template('/voting_portal.html', candidates=can_list, )
        else:
            flash('You have already voted')
            print('you have voted')
            return redirect('/')
    else:
        return redirect('/voter_login.html')

@app.route('/voting_portal/<int:cid>',methods=['GET'])
def vote_cal(cid):
    print(cid)
    vid = session.get('voter_id')

    cursor.execute("UPDATE candidate SET votes=votes+1 WHERE can_id='{}'".format(cid))
    conn.commit()

    cursor.execute("UPDATE voter SET eligible='FALSE' WHERE voter_id ='{}'".format(vid))
    conn.commit()


    flash('Your vote has been successfully counted')
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)





