from db_utils import *
from app import *
from models import *
from unittest.mock import ANY
from flask import url_for
from flask_bcrypt import generate_password_hash
from flask_testing import TestCase
import base64


class BaseTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.create_tables()

        self.admin_data = {
            "username": "admin",
            "firstName": "First1",
            "lastName": "Last1",
            "phone": 380,
            "email": "admin@gmail.com",
            "password": generate_password_hash("admin"),
            "isAdmin": True
        }

        self.user_1_data = {
            "username": "user1",
            "firstName": "First1",
            "lastName": "Last1",
            "phone": 380,
            "email": "user1@gmail.com",
            "password": "1"
        }

        self.user_1_data_get = {
            "username": "user1",
            "firstName": "First1",
            "lastName": "Last1",
            "phone": 380,
            "email": "user1@gmail.com",
            "password": generate_password_hash("1")
        }

        self.user_1_data_upd = {
            "username": "user12",
            "firstName": "First1",
            "lastName": "Last1",
            "phone": 380
        }

        self.user_1_data_upd_error = {
            "username1": "user12",
            "firstName": "First1",
            "lastName": "Last1",
            "phone": 380
        }

        self.user_1_data_hashed = {
            **self.user_1_data,
            "password": generate_password_hash(self.user_1_data["password"]),
        }

        self.user_1_data_validationError = {
            "username": "user12",
            "firstName": "First12",
            "lastName": "Last12",
            "phone": 380,
            "email": "user1gmail.com",
            "password": "1111"
        }

        self.user_1_credentials = {
            "username": self.user_1_data["username"],
            "password": self.user_1_data["password"],
        }

        self.user_2_data = {
            "username": "user2",
            "firstName": "First2",
            "lastName": "Last2",
            "phone": 380,
            "email": "user2@gmail.com",
            "password": "2222"
        }
        self.user_2_data_upd = {
            "username": "user2",
            "firstName": "First2",
            "lastName": "Last2",
            "phone": 380,
            "email": "user2@gmail.com",
            "password": "2222"
        }
        self.user_2_data_hashed = {
            **self.user_2_data,
            "password": generate_password_hash(self.user_2_data["password"]),
        }
        self.user_2_credentials = {
            "username": self.user_2_data["username"],
            "password": self.user_2_data["password"],
        }

        self.medicine_1_data = {
            "name": "medicine1",
            "price": 500,
            "description": "description",
            "quantity": 38,
            "availability": 1,

        }
        self.medicine_2_err = {
            "name21313": "medicine12",
            "price": 550,
            "description": "description1",
            "quantity": 34,
            "availability": 2,
        }

        self.medicine_1_data_val_err = {
            "name": "medicine1",
            "price1": 500,
            "description": "description",
            "quantity": 38,
            "availability": 1,

        }

        self.medicine_1_data_upd = {
            "name": "medicine12",
        }

        self.medicine_1_data_upd_err = {
            "name111": "1",
        }

        self.order_1 = {
            "medicine_id": 1,
            "user_id": 1,
            "quantity": 32,
            "price": 380
        }

        self.order_1_err = {
            "medicine_id12": 1,
            "user_id231": 1,
            "quantity": 32,
            "price": 380
        }

    def tearDown(self):
        self.close_session()

    def create_tables(self):
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def close_session(self):
        Session().close()

    def create_app(self):
        return app


class TestGetUsers(BaseTestCase):
    def test_get_user_by_id(self):
        db_utils.create_entry(User, **self.user_1_data_get)
        valid_credentials = base64.b64encode(b"user1:1").decode("utf-8")

        resp = self.client.get(
            url_for("get_user_by_id", user_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json,
                         {
                             'id': ANY,
                             'username': self.user_1_data['username'],
                             'firstName': self.user_1_data['firstName'],
                             'lastName': self.user_1_data['lastName'],
                             'phone': self.user_1_data['phone'],
                         }
                         )

    def test_get_user_by_id_auth_error(self):
        db_utils.create_entry(User, **self.user_1_data_get)
        valid_credentials = base64.b64encode(b"user1:11").decode("utf-8")

        resp = self.client.get(
            url_for("get_user_by_id", user_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 401)

    def test_get_user_by_id_not_found(self):
        db_utils.create_entry(User, **self.user_1_data_get)
        valid_credentials = base64.b64encode(b"user1:1").decode("utf-8")

        resp = self.client.get(
            url_for("get_user_by_id", user_id=5),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {"Error": "User not found"})


class TestCreateUser(BaseTestCase):
    def test_create_user(self):
        resp = self.client.post(
            url_for("create_user"),
            json=self.user_1_data
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'id': ANY,
            'username': self.user_1_data['username'],
            'firstName': self.user_1_data['firstName'],
            'lastName': self.user_1_data['lastName'],
            'phone': self.user_1_data['phone'],
        })
        self.assertTrue(
            Session().query(User).filter_by(username=self.user_1_data['username']).one()
        )

    def test_create_user_validationError(self):
        resp = self.client.post(
            url_for("create_user"),
            json=self.user_1_data_validationError
        )
        self.assertEqual(resp.status_code, 405)
        self.assertEqual(resp.json, {
            "Error": "ValidationError"
        })


class TestUpdUser(BaseTestCase):
    def test_upd_user(self):
        db_utils.create_entry(User, **self.user_1_data_get)
        valid_credentials = base64.b64encode(b"user1:1").decode("utf-8")

        resp = self.client.put(
            url_for("upd_user", user_id=1),
            json=self.user_2_data_upd,
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            "code": 200
        })

    def test_upd_user_validationError(self):
        db_utils.create_entry(User, **self.user_1_data_get)
        valid_credentials = base64.b64encode(b"user1:1").decode("utf-8")

        resp = self.client.put(
            url_for("upd_user", user_id=1),
            json=self.user_1_data_upd_error,
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(resp.status_code, 405)
        self.assertEqual(resp.json, {
            "error405": "Invalid input"
        })

    def test_upd_user_auth_error(self):
        db_utils.create_entry(User, **self.user_1_data_get)
        valid_credentials = base64.b64encode(b"user1:12").decode("utf-8")

        resp = self.client.put(
            url_for("upd_user", user_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 401)

    def test_delete_user_not_found(self):
        db_utils.create_entry(User, **self.user_1_data_get)
        valid_credentials = base64.b64encode(b"user1:1").decode("utf-8")

        resp = self.client.put(
            url_for("upd_user", user_id=5),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {"Error": "User not found"})


class TestDeleteUser(BaseTestCase):
    def test_delete_user_auth_error(self):
        db_utils.create_entry(User, **self.user_1_data_get)
        valid_credentials = base64.b64encode(b"user1:11").decode("utf-8")

        resp = self.client.delete(
            url_for("delete_user", user_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 401)

    def test_delete_user_not_found(self):
        db_utils.create_entry(User, **self.user_1_data_get)
        valid_credentials = base64.b64encode(b"user1:1").decode("utf-8")

        resp = self.client.delete(
            url_for("delete_user", user_id=5),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {"Error": "User not found"})

    def test_delete_user(self):
        db_utils.create_entry(User, **self.user_1_data_get)
        valid_credentials = base64.b64encode(b"user1:1").decode("utf-8")

        resp = self.client.delete(
            url_for("delete_user", user_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {"Succes": "User deleted"})


class TestCreateMedicine(BaseTestCase):
    def test_add_medicine(self):
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"admin:admin").decode("utf-8")
        resp = self.client.post(
            url_for("add_medicine"),
            json=self.medicine_1_data,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'id': ANY,
            'name': self.medicine_1_data['name'],
            'price': self.medicine_1_data['price'],
            'description': self.medicine_1_data['description'],
            'quantity': self.medicine_1_data['quantity'],
            'availability': self.medicine_1_data['availability']
        })
        self.assertTrue(
            Session().query(Medicine).filter_by(name=self.medicine_1_data['name']).one()
        )

    def test_add_medicine_validationError(self):
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"admin:admin").decode("utf-8")
        resp = self.client.post(
            url_for("add_medicine"),
            json=self.medicine_1_data_val_err,
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(resp.status_code, 405)
        self.assertEqual(resp.json, {
            "Error": "ValidationError"
        })

    def test_add_medicine_auth_err(self):
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"admin:admin15").decode("utf-8")
        resp = self.client.post(
            url_for("add_medicine"),
            json=self.medicine_1_data,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 401)


class TestGetMedicine(BaseTestCase):
    def test_get_medicine(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"admin:admin").decode("utf-8")
        resp = self.client.get(
            url_for("get_medicine_by_id", medicine_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'id': ANY,
            'name': self.medicine_1_data['name'],
            'price': self.medicine_1_data['price'],
            'description': self.medicine_1_data['description'],
            'quantity': self.medicine_1_data['quantity'],
            'availability': self.medicine_1_data['availability']
        })
        self.assertTrue(
            Session().query(Medicine).filter_by(name=self.medicine_1_data['name']).one()
        )

    def test_get_medicine_not_found(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"admin:admin").decode("utf-8")
        resp = self.client.get(
            url_for("get_medicine_by_id", medicine_id=10),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {"Error": "Medicine not found"})

    def test_get_medicine_auth_err(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"admin:admin251").decode("utf-8")
        resp = self.client.get(
            url_for("get_medicine_by_id", medicine_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 401)


class TestUpdMedicine(BaseTestCase):
    def test_upd_medicine(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"admin:admin").decode("utf-8")
        resp = self.client.put(
            url_for("upd_medicine_by_id", medicine_id=1),
            json=self.medicine_1_data_upd,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {"code": 200})

    def test_upd_medicine_not_found(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"admin:admin").decode("utf-8")
        resp = self.client.put(
            url_for("upd_medicine_by_id", medicine_id=10),
            json=self.medicine_1_data_upd,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {"Error404": "Medicine not found"})

    def test_upd_medicine_val_err(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"admin:admin").decode("utf-8")
        resp = self.client.put(
            url_for("upd_medicine_by_id", medicine_id=1),
            json=self.medicine_2_err,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 405)
        self.assertEqual(resp.json, {"Error": "ValidationError"})

    def test_upd_medicine_auth_err(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"admin:admi5815n").decode("utf-8")
        resp = self.client.put(
            url_for("upd_medicine_by_id", medicine_id=1),
            json=self.medicine_2_err,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 401)


class TestDeleteMedicine(BaseTestCase):
    def test_delete_medicine_not_found(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"admin:admin").decode("utf-8")
        resp = self.client.delete(
            url_for("delete_medicine_by_id", medicine_id=10),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {"Error": "Medicine not found"})

    def test_delete_medicine(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"admin:admin").decode("utf-8")
        resp = self.client.delete(
            url_for("delete_medicine_by_id", medicine_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {"Succes": "Medicine deleted"})

    def test_upd_medicine_auth_err(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.admin_data)
        valid_credentials = base64.b64encode(b"ad515min:admin").decode("utf-8")
        resp = self.client.delete(
            url_for("delete_medicine_by_id", medicine_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 401)


class TestCreateOrder(BaseTestCase):
    def test_add_order(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.user_1_data_get)
        valid_credentials = base64.b64encode(b"user1:1").decode("utf-8")
        resp = self.client.post(
            url_for("add_order"),
            json=self.order_1,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'id': ANY,
            'quantity': self.order_1['quantity'],
            'price': self.order_1['price'],
        })

    def test_add_order_auth_err(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.user_1_data_get)
        valid_credentials = base64.b64encode(b"user1:11").decode("utf-8")
        resp = self.client.post(
            url_for("add_order"),
            json=self.order_1,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 401)

    def test_get_add_order_val_err(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.user_1_data_get)
        valid_credentials = base64.b64encode(b"user1:1").decode("utf-8")
        resp = self.client.post(
            url_for("add_order"),
            json=self.order_1_err,
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 405)
        self.assertEqual(resp.json, {"error": "Invalid input"})


class TestGetOrder(BaseTestCase):
    def test_add_order(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.user_1_data_get)
        db_utils.create_entry(MedOrder, **self.order_1)
        valid_credentials = base64.b64encode(b"user1:1").decode("utf-8")
        resp = self.client.get(
            url_for("get_order_by_id", order_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {
            'id': ANY,
            'quantity': self.order_1['quantity'],
            'price': self.order_1['price'],
            'user_id': self.order_1['user_id'],
            'medicine_id': self.order_1['medicine_id']
        })

    def test_add_order_not_found(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.user_1_data_get)
        db_utils.create_entry(MedOrder, **self.order_1)
        valid_credentials = base64.b64encode(b"user1:1").decode("utf-8")
        resp = self.client.get(
            url_for("get_order_by_id", order_id=2),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {"Error": "Order not found"})

    def test_add_order_auth_err(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.user_1_data_get)
        db_utils.create_entry(MedOrder, **self.order_1)
        valid_credentials = base64.b64encode(b"user1:101").decode("utf-8")
        resp = self.client.get(
            url_for("get_order_by_id", order_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 401)


class TestDeleteOrder(BaseTestCase):
    def test_delete_order_by_id(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.user_1_data_get)
        db_utils.create_entry(MedOrder, **self.order_1)
        valid_credentials = base64.b64encode(b"user1:1").decode("utf-8")
        resp = self.client.delete(
            url_for("get_order_by_id", order_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json, {"Succes": "Order deleted"})

    def test_delete_order_by_id_not_found(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.user_1_data_get)
        db_utils.create_entry(MedOrder, **self.order_1)
        valid_credentials = base64.b64encode(b"user1:1").decode("utf-8")
        resp = self.client.delete(
            url_for("get_order_by_id", order_id=2),
            headers={"Authorization": "Basic " + valid_credentials}
        )

        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json, {"Error": "Order not found"})

    def test_delete_order_by_id_auth_err(self):
        db_utils.create_entry(Medicine, **self.medicine_1_data)
        db_utils.create_entry(User, **self.user_1_data_get)
        db_utils.create_entry(MedOrder, **self.order_1)
        valid_credentials = base64.b64encode(b"user1:101").decode("utf-8")
        resp = self.client.delete(
            url_for("get_order_by_id", order_id=1),
            headers={"Authorization": "Basic " + valid_credentials}
        )
        self.assertEqual(resp.status_code, 401)


