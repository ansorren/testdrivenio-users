# services/users/projects/tests/test_config.py

import os
import unittest

from flask import current_app
from flask_testing import TestCase

from project import create_app

app = create_app()


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object("project.config.DevelopmentConfig")
        return app

    def test_app_is_development(self):
        """test app is development """
        self.assertTrue(app.config["SECRET_KEY"] == "my_precious")
        self.assertFalse(current_app is None)
        self.assertTrue(app.config["SQLALCHEMY_DATABASE_URI"] == os.environ.get("DATABASE_URL"))
        self.assertTrue(app.config["DEBUG_TB_ENABLED"])



class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object("project.config.TestingConfig")
        return app

    def test_app_is_testing(self):
        """test app is testing """
        self.assertTrue(app.config["SECRET_KEY"] == "my_precious")
        self.assertFalse(current_app is None)
        self.assertTrue(
            app.config["SQLALCHEMY_DATABASE_URI"] == os.environ.get("DATABASE_TEST_URL")
        )
        self.assertTrue(app.config["TESTING"])
        self.assertFalse(app.config["DEBUG_TB_ENABLED"])


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object("project.config.ProductionConfig")
        return app

    def test_app_is_production(self):
        """test app is production"""
        self.assertTrue(app.config["SECRET_KEY"] == "my_precious")
        self.assertFalse(current_app is None)
        self.assertTrue(
            app.config["SQLALCHEMY_DATABASE_URI"] == os.environ.get("DATABASE_URL")
        )
        self.assertFalse(app.config["TESTING"])
        self.assertFalse(app.config["DEBUG_TB_ENABLED"])


if __name__ == "__main__":
    unittest.main()
