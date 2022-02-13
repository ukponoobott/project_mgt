# # from db import db
import unittest
from datetime import date, timedelta
from sqlalchemy import false
from models.user import UserModel
from models.project import ProjectModel
# from models.task import TaskModel
# from app import app

class BaseCase(unittest.TestCase):

    def test_registration(self):
        user = UserModel("Ukpono Obott", "ukpono@test.com", confirmed=False, password="strongpassword")
        
        assert user.full_name == "Ukpono Obott"
        assert user.email == "ukpono@test.com"
        assert user.confirmed == False
        assert user.password_hash != "strongpassword"

    def test_project(self):
        project = ProjectModel("Linux Deployment", "Deploy a linux server on Azure", 20, "Ukpono")
        assert project.completed == False
        assert project.end_date != date.today()

if __name__ == "__main__":
    unittest.main()