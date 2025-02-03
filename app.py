from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from models.models import *
from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database
import hashlib

#*********************************
#    Init Section
#*********************************

app = Flask(__name__)
app.secret_key="somesupersecretkey"

#Please return to your default port 3306
app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqlconnector://robertsru:SOPcourse123@localhost:13306/HAS_db'
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)

#check if database exists
if not database_exists(engine.url):
    create_database(engine.url)


Base.metadata.create_all(engine)

db = SQLAlchemy(app)

#*************End INIT***************8

#***********************************
#    testing area
#***********************************

@app.route('/testing',methods=['GET','POST'])
def testing():
    # Generate unique IDs
    if request.method == 'POST':
        print(request.form)
        msg=request.form['mdp-demo'].__str__()
        healthcenter=request.form['healthcenter']
        dates=msg.split(',')
        for eachdate in dates:
            new_booking = Booking('')
        return render_template('index.html',msg=msg)
    return render_template('testing.html')

#***********************************
#   USer Authenticaion
#***********************************

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
#*********end user mgmt & authentication

""" block comment out old code
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
 """
#*************************
#          Roles Management
#**************************
@app.route('/list_roles')
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
    role = db.session.query(Role).get_or_404(id)
    if role:
        db.session.delete(role)
        db.session.commit()
    return redirect(url_for('list_roles'))
#********End Roles Management *****

#*******************************
#         booking Management
#*******************************
@app.route('/bookings')
def bookings():
    bookings = db.session.query(Booking).all()
    patientbookings = db.session.query(PatientBooking).all()
    healthcenters = db.session.query(HealthCenter).all()
    return render_template('bookings.html', bookings=bookings, patientbookings=patientbookings,healthcenters=healthcenters)

@app.route('/patient_bookings')
def patient_bookings():
    bookings=db.session.query(Booking).all()
    patientBookings=db.session.query(Patient).all()
    return render_template('patient_bookings.html',bookings=bookings, patientbookings=patientBookings)

@app.route('/create_booking', methods=['GET', 'POST'])
def create_booking():
    healthcenters=db.session.query(HealthCenter).all()
    if request.method == 'POST':
        created_by = request.form['created_by']
        healthcenter = request.form['healthcenter']
        date = request.form['date']
        statusLKP = request.form['statusLKP']
        clinicalservices = request.form['clinicalservices']
        new_booking = Booking(created_by=created_by, healthcenter=healthcenter, date=date, statusLKP=statusLKP, clinicalservices=clinicalservices)
        db.session.add(new_booking)
        db.session.commit()
        return redirect(url_for('bookings'))
    return render_template('create_booking.html',healthcenters=healthcenters)

@app.route('/update_booking/<int:id>', methods=['GET', 'POST'])
def update_booking(id):
    booking = db.session.query(Booking).get_or_404(id)
    if request.method == 'POST':
        booking.created_by = request.form['created_by']
        booking.healthcenter = request.form['healthcenter']
        booking.date = request.form['date']
        booking.statusLKP = request.form['statusLKP']
        booking.clinicalservices = request.form['clinicalservices']
        db.session.commit()
        return redirect(url_for('bookings'))
    return render_template('update_booking.html', booking=booking)

@app.route('/delete_booking/<int:id>')
def delete_booking(id):
    booking = db.session.query(Booking).get_or_404(id)
    db.session.delete(booking)
    db.session.commit()
    return redirect(url_for('bookings'))

@app.route('/create_patientbooking', methods=['GET', 'POST'])
def create_patientbooking():
    if request.method == 'POST':
        booking_id = request.form['booking_id']
        patient_id = request.form['patient_id']
        statusLKP = request.form['statusLKP']
        comments = request.form['comments']
        new_patientbooking = PatientBooking(booking_id=booking_id, patient_id=patient_id, statusLKP=statusLKP, comments=comments)
        db.session.add(new_patientbooking)
        db.session.commit()
        return redirect(url_for('patient_bookings'))
    return render_template('create_patientbooking.html')

@app.route('/update_patientbooking/<int:booking_id>/<int:patient_id>', methods=['GET', 'POST'])
def update_patientbooking(booking_id, patient_id):
    patientbooking = db.session.query(PatientBooking).get_or_404((booking_id, patient_id))
    if request.method == 'POST':
        patientbooking.statusLKP = request.form['statusLKP']
        patientbooking.comments = request.form['comments']
        db.session.commit()
        return redirect(url_for('patient_bookings'))
    return render_template('update_patientbooking.html', patientbooking=patientbooking)

@app.route('/delete_patientbooking/<int:booking_id>/<int:patient_id>')
def delete_patientbooking(booking_id, patient_id):
    patientbooking = db.session.query(PatientBooking).get_or_404((booking_id, patient_id))
    db.session.delete(patientbooking)
    db.session.commit()
    return redirect(url_for('patient_bookings'))



#********End Booking Management**



#*******************************
#           Patient Management
#*******************************
@app.route('/patients')
def patients():
    patients = db.session.query(Patient).all()
    return render_template('patients.html', patients=patients)

@app.route('/create_patient', methods=['GET', 'POST'])
def create_patient():
    my_healthcenters =db.session.query(HealthCenter).all()
    if request.method == 'POST':
        fname = request.form['fname']
        lname = request.form['lname']
        tele1 = request.form['tele1']
        tele2 = request.form['tele2']
        email = request.form['email']
        comments = request.form['comments']
        healthcenter = request.form['healthcenter']
        new_patient = Patient(fname=fname, lname=lname, tele1=tele1, tele2=tele2, email=email, comments=comments, healthcenter=healthcenter)
        db.session.add(new_patient)
        db.session.commit()
        return redirect(url_for('patients',healthcenters=my_healthcenters))
    return render_template('create_patient.html',healthcenters=my_healthcenters)

@app.route('/update_patient/<int:id>', methods=['GET', 'POST'])
def update_patient(id):
    my_healthcenters =db.session.query(HealthCenter).all()
    patient = db.session.query(Patient).get_or_404(id)
    if request.method == 'POST':
        patient.fname = request.form['fname']
        patient.lname = request.form['lname']
        patient.tele1 = request.form['tele1']
        patient.tele2 = request.form['tele2']
        patient.email = request.form['email']
        patient.comments = request.form['comments']
        patient.healthcenter = request.form['healthcenter']
        db.session.commit()
        return redirect(url_for('patients',healthcenters=my_healthcenters))
    return render_template('update_patient.html', patient=patient,healthcenters=my_healthcenters)

@app.route('/delete_patient/<int:id>')
def delete_patient(id):
    patient = db.session.query(Patient).get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('patients'))


#*************END PATIENT MANAGEMENT*****************

#***************************************
#     LKP Management
#**************************************

@app.route('/lkps')
def lkps():
    my_lkps = db.session.query(LKP).all()
    return render_template('lkps.html', lkps=my_lkps)

@app.route('/create_lkp', methods=['GET', 'POST'])
def create_lkp():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        desc = request.form['desc']
        new_lkp = LKP(name=name, category=category, desc=desc)
        db.session.add(new_lkp)
        db.session.commit()
        return redirect(url_for('lkps'))
    return render_template('create_lkp.html')

@app.route('/update_lkp/<int:id>', methods=['GET', 'POST'])
def update_lkp(id):
    lkp = db.session.query(LKP).get_or_404(id)
    if request.method == 'POST':
        lkp.name = request.form['name']
        lkp.category = request.form['category']
        lkp.desc = request.form['desc']
        db.session.commit()
        return redirect(url_for('lkps'))
    return render_template('update_lkp.html', lkp=lkp)

@app.route('/delete_lkp/<int:id>')
def delete_lkp(id):
    lkp = db.session.query(LKP).get_or_404(id)
    db.session.delete(lkp)
    db.session.commit()
    return redirect(url_for('lkps'))

#**********END LKP MAnagement********


#***********************************
#    USer Management
#***********************************
@app.route('/users')
def users():
    my_users = db.session.query(User).all()
    return render_template('users.html', users=my_users)

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    roles= db.session.query(Role).all()
    if request.method == 'POST':
        email = request.form['email']
        pwd = request.form['pwd']
        fname = request.form['fname']
        lname = request.form['lname']
        role_id = request.form['role_id']
        new_user = User(email=email, pwd=pwd, fname=fname, lname=lname, role_id=role_id)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('users'))
    return render_template('create_user.html',roles=roles)

@app.route('/update_user/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    user = db.session.query(User).get_or_404(id)
    roles= db.session.query(Role).all()
    if request.method == 'POST':
        user.email = request.form['email']
        user.pwd = request.form['pwd']
        user.fname = request.form['fname']
        user.lname = request.form['lname']
        user.role_id = request.form['role_id']
        db.session.commit()
        return redirect(url_for('users'))
    return render_template('update_user.html', user=user,roles=roles)

@app.route('/delete_user/<int:id>')
def delete_user(id):
    user = db.session.query(User).get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('users'))

#********END USer Management *******

#***********************************
#     Health center Management
#**********************************
@app.route('/healthcenters')
def healthcenters():
    my_healthcenters = db.session.query(HealthCenter).all()
    return render_template('healthcenters.html', healthcenters=my_healthcenters)

@app.route('/create_healthcenter', methods=['GET', 'POST'])
def create_healthcenter():
    if request.method == 'POST':
        name = request.form['name']
        district = request.form['district']
        new_healthcenter = HealthCenter(name=name, district=district)
        db.session.add(new_healthcenter)
        db.session.commit()
        return redirect(url_for('healthcenters'))
    return render_template('create_healthcenter.html')

@app.route('/update_healthcenter/<int:id>', methods=['GET', 'POST'])
def update_healthcenter(id):
    healthcenter = db.session.query(HealthCenter).get_or_404(id)
    if request.method == 'POST':
        healthcenter.name = request.form['name']
        healthcenter.district = request.form['district']
        db.session.commit()
        return redirect(url_for('healthcenters'))
    return render_template('update_healthcenter.html', healthcenter=healthcenter)

@app.route('/delete_healthcenter/<int:id>')
def delete_healthcenter(id):
    healthcenter = db.session.query(HealthCenter).get_or_404(id)
    db.session.delete(healthcenter)
    db.session.commit()
    return redirect(url_for('healthcenters'))

#******END HEALTH CENTER LKP MANAGEMENT


if __name__=='__main__':
    app.run(debug=True)