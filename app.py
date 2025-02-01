from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.models import *
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database
import hashlib


app = Flask(__name__)
app.secret_key="somesupersecretkey"

#Please return to your default port 3306
app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqlconnector://robertsru:SOPcourse123@localhost:13306/HAS_db'
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)

#assuming code will be deployed elsewhere
if not database_exists(engine.url):
    create_database(engine.url)


Base.metadata.create_all(engine)

db = SQLAlchemy(app)

@app.route('/testing')
def testing():
    return render_template('testing.html')

@app.route('/')
def index():
    if 'loggedin' in session:
         with engine.connect() as con:
            result = con.execute(text(f"Select name from role where id = {session['role_id']}"))
            rolename = result.fetchone()
            con.commit()
         return render_template('index.html', email=session['email'],rolename=rolename.name)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg =""
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        #get the form values
        email = request.form['email'].lower()
        password_entered = request.form['password']
        #decrypt the password
        hash = password_entered + app.secret_key
        hash = hashlib.sha256(hash.encode())
        password = hash.hexdigest()
        #check if the user exists in the database
        
        with engine.connect() as con:
            result = con.execute(text(f"Select * from user where email = '{email}' and pwd = '{password}'"))
            cur_user = result.fetchone()
            con.commit()

        if cur_user:
            session['loggedin'] = True
            session['id'] = cur_user.id
            session['email'] = cur_user.email
            session['role_id'] = cur_user.role_id
            msg = "Logged in successfully"
            return redirect(url_for('index', msg=msg))
        else:
            msg = "Incorrect username/password"
    return render_template('login.html', msg=msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg =""
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        #get the form values
        email = request.form['email'].lower()
        cemail = request.form['cemail'].lower()
        password = request.form['password']
        cpassword = request.form['cpassword']
        fname=request.form['fname'].lower()
        lname=request.form['lname'].lower()
        role=request.form['role']
        #perform validation checks
        if email!=cemail:
            msg = "Emails do not match"
            return render_template('register.html', msg=msg)
        if password!=cpassword:
            msg = "Passwords do not match"
            return render_template('register.html', msg=msg)
        with engine.connect() as con:
            result = con.execute(text(f"Select * from user where email = '{email}'"))
            account = result.fetchone()
            con.commit()
        if account:
            msg = "Account already exists"
            return render_template('register.html', msg=msg)
        
        if not email or not password or not cemail or not cpassword:
                msg = "Please fill out the form"
                return render_template('register.html', msg=msg)
        else:
            #encrypt the password
            hash = password + app.secret_key
            hash = hashlib.sha256(hash.encode())
            password = hash.hexdigest()
            #insert the user into the database
            new_user = User(email=email,pwd=password,fname=fname,lname=lname,role_id=role)
            db.session.add(new_user)
            db.session.commit()
            #with engine.connect() as con:
            #    con.execute(text(f"Insert into user (email, password,fname,lname,role) values ('{email}', '{password}')"))
            #    con.commit()
            msg = "Account created successfully"
            return redirect(url_for('login', msg=msg))
    #load role dropdownlist here
    roles= db.session.query(Role).all()
    return render_template('register.html', msg=msg, roles=roles)

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    session.pop('role_id',None)
    return redirect(url_for('index'))

# Route to show booking selection page
@app.route('/select_dates')
def select_dates():
    return render_template('select_dates.html')

@app.route('/create_bookings',methods=['GET','POST'])
def create_bookings():
    return render_template('create_bookings.html')
# Route to save multiple bookings
@app.route('/save_bookings', methods=['POST'])
def save_bookings():
    data = request.json
    dates = data.get('dates', [])
    healthcenter=data.get('healthcenter')
    
    for date_str in dates:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
      #  if not Booking.query.filter_by(date=date_obj).first():  # Avoid duplicate entries
        new_booking = Booking(date=date_obj,created_by=session['id'],healthcenter=healthcenter)
        db.session.add(new_booking)
    
    db.session.commit()
    return jsonify({"message": "Bookings saved successfully!"})

# Route to show confirmed bookings page
@app.route('/confirmed_bookings')
def confirmed_bookings():
    return render_template('confirmed_bookings.html')

# API to get confirmed bookings count
@app.route('/get_bookings', methods=['GET'])
def get_bookings():
    bookings = db.session.query(Booking.date, db.func.count(Booking.id)).filter_by(status="confirmed").group_by(Booking.date).all()
    booking_data = {date.strftime('%Y-%m-%d'): count for date, count in bookings}
    return jsonify(booking_data)

# Route to confirm a booking
@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    data = request.json
    date_str = data.get('date')
    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

    booking = Booking.query.filter_by(date=date_obj).first()
    if booking:
        booking.status = "confirmed"
        db.session.commit()
        return jsonify({"message": "Booking confirmed successfully!"})
    else:
        return jsonify({"error": "No booking found for this date."}), 400

### ROLES ###
@app.route('/roles')
def list_roles():
    roles = db.session.query(Role).all()
    return render_template('list_roles.html', roles=roles)

@app.route('/roles/add', methods=['GET', 'POST'])
def add_role():
    if request.method == 'POST':
        role = Role(
            name=request.form['name'],
            desc=request.form['desc']
        )
        db.session.add(role)
        db.session.commit()
        return redirect(url_for('list_roles'))

    return render_template('add_role.html')

@app.route('/roles/delete/<int:id>')
def delete_role(id):
    role = Role.query.get(id)
    if role:
        db.session.delete(role)
        db.session.commit()
    return redirect(url_for('list_roles'))


if __name__=='__main__':
    app.run(debug=True)