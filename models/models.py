from sqlalchemy import Date, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import mapped_column, Mapped, DeclarativeBase
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime


class Base(DeclarativeBase):
    pass

class BaseModel:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class Base(DeclarativeBase):
    pass

class User(Base, BaseModel):
    __tablename__ = 'user'
    id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email:Mapped[str] = mapped_column(String(200), unique=True)
    pwd:Mapped[str] = mapped_column(String(255))
    fname:Mapped[str]=mapped_column(String(200), nullable=True)
    lname:Mapped[str]=mapped_column(String(200),nullable=True)
    role_id:Mapped[int]=mapped_column(Integer,ForeignKey("role.id",onupdate="CASCADE", ondelete="CASCADE"))

class Role(Base,BaseModel):
    __tablename__='role'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name:Mapped[str]=mapped_column(String(255))
    desc:Mapped[str]=mapped_column(String(255))
    
class Patient(Base,BaseModel):
    __tablename__ = 'patient'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fname: Mapped[str] = mapped_column(String(150), nullable=False)
    lname: Mapped[str] = mapped_column(String(150), nullable=False)
    tele1: Mapped[str] = mapped_column(String(20), nullable=True)
    tele2: Mapped[str] = mapped_column(String(20), nullable=True)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    comments: Mapped[str] = mapped_column(String(255), nullable=True)
    healthcenter:Mapped[int]=mapped_column(Integer, ForeignKey('LKP.id'))

class LKP(Base,BaseModel):
    __tablename__ = 'LKP'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    category:Mapped[str] = mapped_column(String(255), nullable=False) #categories can be Healthcenterlkp,bookingstatuslkp,clinicalservicelkp etc.
    desc: Mapped[str] = mapped_column(String(255), nullable=True)

class HealthCenter(Base,BaseModel):
    __tablename__ = 'HealthCenter'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    district:Mapped[str] = mapped_column(String(255), nullable=True) #districts

class Booking(Base,BaseModel):
    __tablename__="booking"
    id:Mapped[int]= mapped_column(Integer, primary_key=True, autoincrement=True)
    created_by:Mapped[int] = mapped_column(Integer, ForeignKey('user.id'))
    healthcenter:Mapped[int]=mapped_column(Integer, ForeignKey('LKP.id'))
    date:Mapped[datetime.date]=mapped_column(Date,nullable=False) 
    statusLKP:Mapped[int]=mapped_column(Integer, ForeignKey('LKP.id'))
    clinicalservices:Mapped[str] = mapped_column(String(255))

class PatientBooking(Base,BaseModel):
    __tablename__='patientbookings'
    #create multi field primary Key
    booking_id:Mapped[int]=mapped_column(Integer,ForeignKey('booking.id'), primary_key=True )
    patient_id:Mapped[int]=mapped_column(Integer,ForeignKey('patient.id'),primary_key=True)
    statusLKP:Mapped[int]=mapped_column(Integer, ForeignKey('LKP.id'))
    Comments:Mapped[str] = mapped_column(String(255))