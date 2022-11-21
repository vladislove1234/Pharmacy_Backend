from sqlalchemy import create_engine, Column, Integer, String, DECIMAL, Boolean, ForeignKey, Table
from sqlalchemy.orm import declarative_base, sessionmaker, scoped_session, relationship
from sqlalchemy import and_

engine = create_engine('mysql://root:759486@localhost/pp_var_15')
SessionFactory = sessionmaker(bind=engine)
Session = scoped_session(SessionFactory)
Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    id = Column('id', Integer, primary_key=True)
    username = Column('username', String(45))
    firstName = Column('firstName', String(45))
    lastName = Column('lastName', String(45))
    phone = Column('phone', Integer)
    isAdmin = Column('isAdmin', Boolean)
    email = Column('email', String(45))
    password = Column('password', String(400))


class Medicine(Base):
    __tablename__ = "medicines"

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String(45), nullable=False)
    price = Column('price', DECIMAL(10, 2), nullable=False)
    description = Column('description', String(45), nullable=False)
    quantity = Column('quantity', Integer, nullable=False)
    availability = Column('availability', Boolean, nullable=False)


class Demand(Base):
    __tablename__ = "demand"

    id = Column('id', Integer, primary_key=True)
    user_id = Column('user_id',ForeignKey(User.id))
    medicine_id = Column('medicine_id', ForeignKey(Medicine.id))
    quantity = Column(Integer)


class MedOrder(Base):
    __tablename__ = "medorder"

    id = Column('id', Integer, primary_key=True)
    price = Column('price', DECIMAL(10, 2), nullable=False)
    user_id = Column('user_id', Integer, ForeignKey(User.id))
    medicine_id = Column('medicine_id', Integer, ForeignKey(Medicine.id))
    quantity = Column('quantity', Integer)

