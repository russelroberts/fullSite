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
app.config['SQLALCHEMY_DATABASE_URI']='mysql+mysqlconnector://robertsru:SOPcourse123@localhost:13306/HAS12_db'
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)

#check if database exists
if not database_exists(engine.url):
    create_database(engine.url)
 #   redirect(url_for('/install'))
#else:
Base.metadata.create_all(engine)

db = SQLAlchemy(app)

#*************End INIT***************8

#************************************
#        install sample data
#************************************

@app.route('/install')
def install():
    queries = []

    def add_if_not_exists(model, data):
        """Helper function to check if data exists, if not insert it."""
        exists = db.session.query(model).first()
        if not exists:
            db.session.bulk_insert_mappings(model, data)
            db.session.commit()
            for d in data:
                queries.append(f"INSERT INTO {model.__tablename__} VALUES ({d})")

    # Add roles
    add_if_not_exists(Role, [
        {"name": "admin", "desc": "Administrator"},
        {"name": "consultant", "desc": "Doctor Role"},
        {"name": "Nurse", "desc": "Nurse Role"}
    ])

    hash = "doctor123" + app.secret_key
    hash = hashlib.sha256(hash.encode())
    password = hash.hexdigest()
    hash = "admin123" + app.secret_key
    hash = hashlib.sha256(hash.encode())
    adminpassword = hash.hexdigest()
            
    # Add users
    add_if_not_exists(User, [
        {"email": "admin@example.com", "pwd": adminpassword, "fname": "Admin", "lname": "User", "role_id": 1},
        {"email": "doctor1@example.com", "pwd": password, "fname": "Doctor1", "lname": "User", "role_id": 2},
        {"email": "doctor2@example.com", "pwd": password, "fname": "Doctor2", "lname": "User", "role_id": 2},
        {"email": "doctor3@example.com", "pwd": password, "fname": "Doctor3", "lname": "User", "role_id": 2},
        {"email": "nurse@example.com", "pwd": password, "fname": "Nurse", "lname": "User", "role_id": 3}
    ])
    # Add health centers
    add_if_not_exists(HealthCenter, [
        {"name": "Health Center 1", "district": "District A"},
        {"name": "Health Center 2", "district": "District B"},
        {"name": "Health Center 3", "district": "District C"},
        {"name": "Roseau", "district": "District A"},
        {"name": "Mahaut", "district": "District B"},
        {"name": "Georgetown", "district": "District C"}
    ])


    # Add patients
    add_if_not_exists(Patient, [
        {"fname": "John", "lname": "Doe", "tele1": "1234567890", "email": "johndoe@example.com", "healthcenter": 1},
        {"fname": "Jane", "lname": "Smith", "tele1": "0987654321", "email": "janesmith@example.com", "healthcenter": 2},
        {"fname": "Mike", "lname": "Brown", "tele1": "1122334455", "email": "mikebrown@example.com", "healthcenter": 3},
        {"fname": "James", "lname": "Doe", "tele1": "1234567890", "email": "johndoe@example.com", "healthcenter": 1},
        {"fname": "Johan", "lname": "Smith", "tele1": "0987654321", "email": "janesmith@example.com", "healthcenter": 2},
        {"fname": "Maria", "lname": "Brown", "tele1": "1122334455", "email": "mikebrown@example.com", "healthcenter": 3}
    ])

    # Add lookup values
    add_if_not_exists(LKP, [
        {"name": "called", "category": "patientstatus"},
        {"name": "notified", "category": "patientstatus"},
        {"name": "cancelled", "category": "patientstatus"},
        {"name": "seen- with follow-up", "category": "patientstatus"},
        {"name": "seen without follow-up", "category": "patientstatus"},
        {"name": "arrived", "category": "patientstatus"},
        {"name": "running late", "category": "patientstatus"},
        {"name": "unscheduled walk in", "category": "patientstatus"},
        {"name": "Created", "category": "bookingstatus"},
        {"name": "Pending", "category": "bookingstatus"},
        {"name": "Confirmed", "category": "bookingstatus"},
        {"name": "General Checkup", "category": "clinicalservices"},
        {"name": "maternity", "category": "clinicalservices"},
        {"name": "ENT", "category": "clinicalservices"},
        {"name": "mental health", "category": "clinicalservices"},
        {"name": "Eye exam", "category": "clinicalservices"},
        {"name": "vaccines", "category": "clinicalservices"},
        {"name": "tele Health Session", "category": "clinicalservices"}
    ])


    # Add bookings
    add_if_not_exists(Booking, [
        {"created_by": 1, "healthcenter": 1, "date": datetime.today(), "statusLKP": 2, "clinicalservices": "General Checkup"},
        {"created_by": 2, "healthcenter": 2, "date": datetime.today(), "statusLKP": 2, "clinicalservices": "Mental Health"},
        {"created_by": 3, "healthcenter": 3, "date": datetime.today(), "statusLKP": 2, "clinicalservices": "Eye Exam"}
    ])

    # Add patient bookings
   # add_if_not_exists(PatientBooking, [
   #     {"booking_id": 1, "patient_id": 1, "statusLKP": 2, "comments": "First visit"},
   #     {"booking_id": 2, "patient_id": 2, "statusLKP": 2, "comments": "Follow-up"},
   #     {"booking_id": 3, "patient_id": 3, "statusLKP": 2, "comments": "Emergency"}
   # ])

    return render_template('install.html', queries=queries)

#******END INSTALL SAMPLE DATA******

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
            session['rolename'] = rolename.name
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
    bookings =( db.session.query(Booking,User,HealthCenter,LKP)
        .join(User, User.id==Booking.created_by)
        .join(HealthCenter, HealthCenter.id==Booking.healthcenter)
        .join(LKP,LKP.id==Booking.statusLKP)
        .filter(Booking.created_by==session['id'])
        .all()
    )
    patientbookings = db.session.query(PatientBooking).all()
    healthcenters = db.session.query(HealthCenter).all()
    return render_template('bookings.html', bookings=bookings, patientbookings=patientbookings,healthcenters=healthcenters)

@app.route('/patient_bookings')
def patient_bookings():
    #Bookings=db.session.query(Booking).all()
    Bookings = (
        db.session.query(User.fname, User.lname, Booking, HealthCenter.name.label("healthcenter_name"))
        .join(Role, User.role_id == Role.id)
        .join(Booking, User.id == Booking.created_by)
        .join(HealthCenter, Booking.healthcenter == HealthCenter.id)
        .filter(Role.name == 'consultant') #this should not be hardcoded
        .all()
    )
    Patients=(
        db.session.query(Patient,HealthCenter.name.label('healthcenter_name'))
        .join(HealthCenter, Patient.healthcenter == HealthCenter.id)
        .all()
    )
    PatientBookings = (db.session.query(PatientBooking,Booking,Patient,LKP,User)
                       .join(Booking,Booking.id == PatientBooking.booking_id)
                       .join(Patient, Patient.id == PatientBooking.patient_id)
                       .join(LKP, LKP.id == PatientBooking.statusLKP)
                       .join(User, User.id== Booking.created_by)
                       .all()
    )
                       
    Status = db.session.query(LKP).filter_by(category='patientstatus')
    Healthcenters=db.session.query(HealthCenter).all()
    
    return render_template('patient_bookings.html',
                           patientstatus=Status,
                           bookings=Bookings, 
                           patients=Patients, 
                           healthcenters=Healthcenters,
                           patientbookings=PatientBookings)

@app.route('/save_patientbooking', methods=['POST'])
def save_patientbooking():
    data = request.json
    booking_id = data.get('booking_id')
    patients = data.get('patients', [])
    print(patients)
    for p in patients:
        patientbooking = db.session.query(PatientBooking).filter_by(patient_id=p['patient_id'], booking_id=booking_id).first()
        if patientbooking:
            patientbooking.comments = p['comments']
            patientbooking.statusLKP = p['status']
        else:
            new_patientBooking = PatientBooking(booking_id=booking_id, patient_id=p['patient_id'], comments=p['comments'], statusLKP=p['status'])
            db.session.add(new_patientBooking)
    
    db.session.commit()
    return jsonify({'message': 'Records updated successfully'}), 200


@app.route('/create_booking', methods=['GET', 'POST'])
def create_booking():
    bookingStatus = db.session.query(LKP).filter_by(category ='bookingstatus')
    my_services = db.session.query(LKP).filter_by(category ='clinicalservices')
    healthcenters=db.session.query(HealthCenter).all()
    if request.method == 'POST':
        created_by = request.form['created_by']
        healthcenter = request.form['healthcenter']
        #date = request.form['date']
        statusLKP = request.form['statusLKP']
        clinicalservices = request.form['selServices']
        dateCollection = request.form['date']
        dates=dateCollection.split(',')
        for eachDate in dates:
             # Convert date to yyyy-mm-dd format for MySQL
            date_obj = datetime.strptime(eachDate, "%m/%d/%Y").strftime("%Y-%m-%d")
            new_booking = Booking(created_by=created_by, healthcenter=healthcenter, date=date_obj, statusLKP=statusLKP, clinicalservices=clinicalservices)
            db.session.add(new_booking)
        db.session.commit()
        return redirect(url_for('bookings'))
    return render_template('create_booking.html',healthcenters=healthcenters,bookingstatus=bookingStatus,clinicalServices=my_services)

@app.route('/update_booking/<int:id>', methods=['GET', 'POST'])
def update_booking(id):
     bookingStatus = db.session.query(LKP).filter_by(category ='bookingstatus')
     my_services = db.session.query(LKP).filter_by(category ='clinicalservices')
     healthcenters=db.session.query(HealthCenter).all()
     booking = db.session.query(Booking).get_or_404(id)
     #date_obj=datetime.strptime(str(booking.date), "%Y-%m-%d").strftime("%m/%d/%Y")
     #booking.date=date_obj.__str__()
     if request.method == 'POST':
        booking.created_by = request.form['created_by']
        booking.healthcenter = request.form['healthcenter']
        booking.date = request.form['date']
        booking.statusLKP = request.form['statusLKP']
        booking.clinicalservices = request.form['selServices']
        db.session.commit()
        return redirect(url_for('bookings'))
     return render_template('update_booking.html', booking=booking,bookingstatus=bookingStatus,healthcenters=healthcenters,clinicalservices=my_services)

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
    patients = (
        db.session.query(Patient,HealthCenter)
        .join(HealthCenter,HealthCenter.id == Patient.healthcenter)
        .all()
    )
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
    my_users = (
        db.session.query(User,Role)
        .join(Role, Role.id==User.role_id)
        .all()
    )
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
        hash = request.form['pwd'] + app.secret_key
        hash = hashlib.sha256(hash.encode())
        password = hash.hexdigest()
            
        user.email = request.form['email']
        user.pwd = password
        user.fname = request.form['fname']
        user.lname = request.form['lname']
        user.role_id = request.form['role_id']
        db.session.commit()
        return redirect(url_for('users'))
    return render_template('update_user.html', user=user,roles=roles)

@app.route('/update_profile/<int:id>', methods=['GET', 'POST'])
def update_profile(id):
    user = db.session.query(User).get_or_404(id)
    roles= db.session.query(Role).all()
    if request.method == 'POST':
        hash = request.form['pwd'] + app.secret_key
        hash = hashlib.sha256(hash.encode())
        password = hash.hexdigest()
        
        user.email = request.form['email']
        user.pwd = password
        user.fname = request.form['fname']
        user.lname = request.form['lname']
        #user.role_id = request.form['role_id']
        db.session.commit()
        return redirect(url_for('index'))
        #    return redirect(url_for('users'))
    return render_template('update_profile.html', user=user,roles=roles)


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
    Base.metadata.create_all(engine)  # Ensure tables exist
    app.run(debug=True)
