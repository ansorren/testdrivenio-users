# services/users/project/tests/test_users.py


import json
import unittest

from project import db
from project.tests.base import BaseTestCase
from project.api.models import User


def add_user(username, email):
    user = User(username=username, email=email)
    db.session.add(user)
    db.session.commit()
    return user


class TestUserService(BaseTestCase):
    """Tests for the Users Service."""

    def test_users(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get("/users/ping")
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn("pong!", data["message"])
        self.assertIn("success", data["status"])

    def test_add_user(self):
        """Ensure a new user can be added """
        with self.client:
            response = self.client.post(
                "/users",
                data=json.dumps({"username": "antonio", "email": "antonio@test.com"}),
                content_type="application/json",
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn("antonio@test.com was added", data["message"])
            self.assertIn("success", data["status"])

    def test_add_user_invalid_json(self):
        """Ensure error is thrown is the JSON object is empty"""
        with self.client:
            response = self.client.post(
                "/users", data=json.dumps({}), content_type="application/json"
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("Invalid payload", data["message"])
            self.assertIn("fail", data["status"])

    def test_add_user_invalid_json_keys(self):
        """Ensure error is thrown if keys are not valid"""
        with self.client:
            response = self.client.post(
                "/users",
                data=json.dumps({"email": "asd", "not_existing_key": "value"}),
                content_type="application/json",
            )

        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid payload", data["message"])
        self.assertIn("fail", data["status"])

    def test_add_user_duplicate_email(self):
        """Ensure error thrown if user already exists"""
        with self.client:
            self.client.post(
                "/users",
                data=json.dumps({"username": "antonio", "email": "antonio@test.com"}),
                content_type="application/json",
            )
            # do it twice
            response = self.client.post(
                "/users",
                data=json.dumps({"username": "antonio", "email": "antonio@test.com"}),
                content_type="application/json",
            )

            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn("email already exists", data["message"])
            self.assertIn("fail", data["status"])

    def test_single_user(self):
        """Ensure get single user behaves properly"""
        user = add_user("antonio", "antonio@test.com")
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.get(f"/user/{user.id}")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual("antonio", data["data"]["username"])
            self.assertEqual("antonio@test.com", data["data"]["email"])
            self.assertEqual("success", data["status"])

    def test_single_user_incorrect_id(self):
        """Ensure error is thrown if ID doesn't exist"""
        with self.client:
            response = self.client.get("/user/9999")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertEqual("fail", data["status"])
            self.assertEqual("User does not exists", data["message"])

    def test_single_user_no_id(self):
        """Ensure error is thrown if no ID is provided"""
        with self.client:
            response = self.client.get("/user/blah")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertEqual("fail", data["status"])
            self.assertEqual("User does not exists", data["message"])

    def test_all_users(self):
        """Ensure get all users behaves correctly."""
        add_user("antonio", "antonio@test.com")
        add_user("myfriend", "myfriend@youaremyfriend.com")
        with self.client:
            response = self.client.get("/users")
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(data["data"]["users"]), 2)
            self.assertIn("antonio", data["data"]["users"][0]["username"])
            self.assertIn("antonio@test.com", data["data"]["users"][0]["email"])
            self.assertIn("myfriend", data["data"]["users"][1]["username"])
            self.assertIn(
                "myfriend@youaremyfriend.com", data["data"]["users"][1]["email"]
            )
            self.assertIn("success", data["status"])

    def test_main_no_users(self):
        """Ensure / with no users behaves as expected"""
        with self.client:
            response = self.client.get("/")
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"All Users", response.data)
            self.assertIn(b"<p>No users!</p>", response.data)

    def test_main_with_users(self):
        """Ensure / with users behaves as expected"""
        add_user("antonio", "antonio@test.com")
        add_user("myfriend", "myfriend@youaremyfriend.com")
        with self.client:
            response = self.client.get("/")
            self.assertIn(b"All Users", response.data)
            self.assertNotIn(b"<p>No Users!</p>", response.data)
            self.assertIn(b"antonio", response.data)
            self.assertIn(b"myfriend", response.data)

    def test_main_add_users(self):
        """Ensure a new user can be added through the web interface"""
        with self.client:
            response = self.client.post(
                "/",
                data={"username": "antonio", "email": "antonio@test.com"},
                follow_redirects=True,
            )

            self.assertEqual(response.status_code, 200)
            self.assertIn(b"All Users", response.data)
            self.assertNotIn(b"<p>No users!</p>", response.data)
            self.assertIn(b"antonio", response.data)


if __name__ == "__main__":
    unittest.main()
