from flask import Flask, jsonify, request
import db_utils
from db_utils import *
from schemas import *
from models import *
from marshmallow import exceptions
from sqlalchemy.exc import IntegrityError
from sqlalchemy import exc
from flask_httpauth import HTTPBasicAuth
from flask_bcrypt import check_password_hash

app = Flask(__name__)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    try:
        user = Session.query(User).filter_by(username=username).one()
        if check_password_hash(user.password, password):
            return username
    except exc.NoResultFound:
        return False


@auth.get_user_roles
def get_user_roles(user):
    try:
        user_db = Session.query(User).filter_by(username=user).one()
        if user_db.isAdmin:
            return 'admin'
        else:
            return ''
    except exc.NoResultFound:
        return ''


# MEDICINE ----------------------------------------------------------------------------


@app.route("/api/v1/medicine", methods=["POST"])
@auth.login_required(role='admin')
def add_medicine():
    try:
        med_data = MedicineToDo().load(request.json)
        t_med = db_utils.create_entry(Medicine, **med_data)
        return jsonify(MedicineData().dump(t_med))

    except exceptions.ValidationError as err:
        return jsonify({"Error": "ValidationError"}), 405


@app.route("/api/v1/medicine/<int:medicine_id>", methods=["GET"])
@auth.login_required
def get_medicine_by_id(medicine_id):
    try:
        medicine = db_utils.get_entry_byid(Medicine, medicine_id)
        return jsonify(MedicineData().dump(medicine)), 200

    except exc.NoResultFound:
        return jsonify({"Error": "Medicine not found"}), 404


@app.route("/api/v1/medicine/<int:medicine_id>", methods=["PUT"])
@auth.login_required(role='admin')
def upd_medicine_by_id(medicine_id):
    try:
        medicine_data = MedicineToUpdate().load(request.json)
        medicine = db_utils.get_entry_byid(Medicine, medicine_id)
        db_utils.update_entry(medicine, **medicine_data)
        return jsonify({"code": 200})

    except exc.NoResultFound:
        return jsonify({"Error404": "Medicine not found"}), 404

    except ValidationError as err:
        return jsonify({"Error": "ValidationError"}), 405


@app.route("/api/v1/medicine/<int:medicine_id>", methods=["DELETE"])
@auth.login_required(role='admin')
def delete_medicine_by_id(medicine_id):
    if Session.query(Medicine).filter_by(id=medicine_id).count() == 0:
        return jsonify({"Error": "Medicine not found"}), 404

    Session.query(MedOrder).filter(MedOrder.medicine_id == medicine_id).delete()
    Session.query(Demand).filter(Demand.medicine_id == medicine_id).delete()
    Session.query(Medicine).filter(Medicine.id == medicine_id).delete()

    Session.commit()
    return jsonify({"Succes": "Medicine deleted"}), 200


# PHARMACY (ORDER) ------------------------------------------------------------------------------------------


@app.route("/api/v1/pharmacy/medorder", methods=["POST"])
@auth.login_required()
def add_order():
    try:
        med_data = MedOrderToDo().load(request.json)

        user = get_user_by_username(auth.username())
        if user.id != med_data.get('user_id') and not user.isAdmin:
            return "Authorization error", 403

        t_med_ord = db_utils.create_entry(MedOrder, **med_data)
        return jsonify(MedicineData().dump(t_med_ord))

    except exceptions.ValidationError:
        return jsonify({"error": "Invalid input"}), 405

    except IntegrityError as err:
        return str(err), 401


@app.route("/api/v1/pharmacy/medorder/<int:order_id>", methods=["GET"])
@auth.login_required()
def get_order_by_id(order_id):
    try:
        order = db_utils.get_entry_byid(MedOrder, order_id)

        user = get_user_by_username(auth.username())
        if user.id != order.user_id and not user.isAdmin:
            return "Authorization error", 403

        return jsonify(MedOrderData().dump(order)), 200

    except exc.NoResultFound:
        return jsonify({"Error": "Order not found"}), 404


@app.route("/api/v1/pharmacy/medorder/<int:order_id>", methods=["DELETE"])
@auth.login_required()
def delete_order_by_id(order_id):
    if Session.query(MedOrder).filter_by(id=order_id).count() == 0:
        return jsonify({"Error": "Order not found"}), 404

    order = Session.query(MedOrder).filter_by(id=order_id).one()
    user = get_user_by_username(auth.username())
    if user.id != order.user_id and not user.isAdmin:
        return "Authorization error", 403

    Session.query(MedOrder).filter_by(id=order_id).delete()
    Session.commit()
    return jsonify({"Succes": "Order deleted"}), 200


@app.route("/api/v1/pharmacy/demand/<int:medicine_id>", methods=["GET"])
@auth.login_required()
def get_demand_by_id(medicine_id):
    try:
        demand = Session.query(Demand).filter_by(medicine_id=medicine_id).one()

        user = get_user_by_username(auth.username())
        if user.id != demand['user_id'] and not user.isAdmin:
            return "Authorization error", 403

        return jsonify(DemandData().dump(demand)), 200

    except exc.NoResultFound:
        return jsonify({"Error": "Demand record not found"}), 404


@app.route("/api/v1/pharmacy/demand/", methods=["POST"])
@auth.login_required()
def add_demand():
    try:
        demand_data = DemandToDo().load(request.json)

        user = get_user_by_username(auth.username())
        if user.id != demand_data['user_id'] and not user.isAdmin:
            return "Authorization error", 403

        t_demand = db_utils.create_entry(Demand, **demand_data)
        return jsonify(DemandData().dump(t_demand)), 200
    except exceptions.ValidationError:
        return jsonify({"error": "Invalid input"}), 405
    except IntegrityError as err:
        return jsonify({"error": "IntegrityError"}), 401


@app.route("/api/v1/pharmacy/demand", methods=["DELETE"])
@auth.login_required()
def delete_demand():
    args = request.json
    user_id = args.get('user_id')
    medicine_id = args.get('medicine_id')

    user = get_user_by_username(auth.username())

    if str(user.id) != str(user_id) and not user.isAdmin:
        return "Authorization error", 403

    if Session.query(Demand).filter(and_(Demand.user_id == user_id, Demand.medicine_id == medicine_id)).count() == 0:
        return jsonify({"Error": "Demand not found"}), 404

    Session.query(Demand).filter(and_(Demand.user_id == user_id, Demand.medicine_id == medicine_id)).delete()
    Session.commit()
    return "Demand deleted", 200


# USER -----------------------------------------------------------------------------------------------------------------

@app.route("/user", methods=["POST"])
def create_user():
    try:
        user_data = UserToDo().load(request.json)
        user_data['isAdmin'] = False
        t_user = db_utils.create_entry(User, **user_data)
        return jsonify(UserData().dump(t_user)), 200
    except ValidationError as err:
        return jsonify({"Error": "ValidationError"}), 405


@app.route("/user/<int:user_id>", methods=["GET"])
@auth.login_required
def get_user_by_id(user_id):
    user = get_user_by_username(auth.username())

    if Session.query(User).filter_by(id=user_id).count() == 0:
        return jsonify({"Error": "User not found"}), 404
    if user.id != user_id and not user.isAdmin:
        return jsonify({"Error403": "Authorization error"}), 403
    try:
        user = db_utils.get_entry_byid(User, user_id)
        return jsonify(UserData().dump(user)), 200
    except exc.NoResultFound:
        return jsonify({"Error": "User not found"}), 404


@app.route("/api/v1/user/<int:user_id>", methods=["PUT"])
@auth.login_required
def upd_user(user_id):
    if Session.query(User).filter_by(id=user_id).count() == 0:
        return jsonify({"Error": "User not found"}), 404
    user = get_user_by_username(auth.username())
    if user.id != user_id:
        return jsonify({"Error403": "Authorization error"}), 403
    try:
        user_data = UserToUpdate().load(request.json)
        user = db_utils.get_entry_byid(User, user_id)
        db_utils.update_entry(user, **user_data)
        return jsonify({"code": 200}), 200

    except exceptions.ValidationError:
        return jsonify({"error405": "Invalid input"}), 405


@app.route("/api/v1/user/<int:user_id>", methods=["DELETE"])
@auth.login_required
def delete_user(user_id):
    user = get_user_by_username(auth.username())

    if Session.query(User).filter_by(id=user_id).count() == 0:
        return jsonify({"Error": "User not found"}), 404

    if user.id != user_id and not user.isAdmin:
        return jsonify({"Error403": "Authorization error"}), 403

    try:
        Session.query(MedOrder).filter(MedOrder.user_id == user_id).delete()
        Session.query(Demand).filter(Demand.user_id == user_id).delete()
        Session.query(User).filter(User.id == user_id).delete()

        Session.commit()
        return jsonify({"Succes": "User deleted"}), 200

    except exc.NoResultFound:
        return jsonify("Error404: Medicine not found"), 404


def get_user_by_username(username):
    return Session.query(User).filter_by(username=username).one()


if __name__ == '__main__':
    app.run(debug=True)
