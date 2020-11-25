from db import db
import unittest
from models.user import UserModel
from models.project import ProjectModel
from models.task import TaskModel
from .app import app


class Tests(unittest.TestCase):
    def setUp(self) -> None:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        db.create_all()
        return "Created"
        

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()

    def test_registration(self):
        user = UserModel("Ukpono Obott", "ukpono@test.com", confirmed=False, password="strongpassword")
        res = user.save_to_db()
        assert res == "OK"

    def test_find_by_email(self):
        find_user = UserModel.find_by_email("ukpono@test.com")

        assert isinstance(find_user, UserModel)

    def test_find_by_email_no_user(self):
        find_no_user = UserModel.find_by_email("no_email@test.com")
        
        assert not find_no_user


if __name__ == '__main__':
    unittest.main()
