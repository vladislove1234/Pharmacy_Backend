from flask_bcrypt import generate_password_hash
from marshmallow import validate, Schema, fields, ValidationError

from models import *


def validate_email(email):
    if not (Session.query(User).filter(User.email == email).count() == 0):
        raise ValidationError("Email exists")


def validate_username(username):
    if Session.query(User).filter(User.username == username).count() > 0:
        raise ValidationError("UserName exists")


def validate_medicine(name):
    if not (Session.query(Medicine).filter(Medicine.name == name).count() == 0):
        raise ValidationError("Such medicine already supplied")


class UserToDo(Schema):
    username = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    phone = fields.Integer()
    email = fields.Email(validate=validate_email)
    password = fields.Function(
        deserialize=lambda obj: generate_password_hash(obj), load_only=True
    )


class UserLogin(Schema):
    username = fields.String()
    password = fields.String()


class UserData(Schema):
    id = fields.Integer()
    username = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    phone = fields.Integer()


class UserToUpdate(Schema):
    username = fields.String()
    firstName = fields.String()
    lastName = fields.String()
    phone = fields.Integer()
    email = fields.String(validate=validate.Email())
    password = fields.Function(
        deserialize=lambda obj: generate_password_hash(obj), load_only=True
    )


class MedicineToDo(Schema):
    name = fields.String(validate=validate_medicine)
    price = fields.Integer()
    description = fields.String()
    quantity = fields.Integer()
    availability = fields.Integer()


class MedicineData(Schema):
    id = fields.Integer()
    name = fields.String()
    price = fields.Integer()
    description = fields.String()
    quantity = fields.Integer()
    availability = fields.Integer()


class MedicineToUpdate(Schema):
    name = fields.String(validate=validate_medicine)
    price = fields.Integer()
    description = fields.String()
    quantity = fields.Integer()
    availability = fields.Integer()


class MedOrderToDo(Schema):
    medicine_id = fields.Integer()
    user_id = fields.Integer()
    quantity = fields.Integer()
    price = fields.Integer()


class MedOrderData(Schema):
    id = fields.Integer()
    medicine_id = fields.Integer()
    user_id = fields.Integer()
    quantity = fields.Integer()
    price = fields.Integer()


class DemandToDo(Schema):
    user_id = fields.Integer()
    medicine_id = fields.Integer()
    quantity = fields.Integer()


class DemandData(Schema):
    user_id = fields.Integer()
    medicine_id = fields.Integer()
    quantity = fields.Integer()
