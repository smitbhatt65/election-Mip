from flask import Flask,jsonify,request,make_response
import jwt
import datetime
from functools import wraps

app=Flask(__name__)

app.config['SECRET_KEY']='thisisthesecretkey'
def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token=request.args.get('token')
        if not token:
            return jsonify({'message':'token is missing'}),403
        try:
            data=jwt.decode(token,app.config['SECRET_KEY'])
        except:
            return jsonify({'message':'token is invalid'}),403
        return f(*args,**kwargs)
    return decorated

@app.route('/admin_login/')
def login():
    auth=request.authorization
    if auth and auth.password=('smit'or'sanika'or'aniket') :
    token=jwt.encode({'user':auth.username,'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes=2),app.config['SECRET_KEY']})
    return jsonify({'token':token.decode('UTF-8')})

    return make_response('could not verify',401,{})


@app.route('/admin_dashboard')
@token_required
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





if __name__='__main__':
    app.run(debug=True)