from db import db
from datetime import date, timedelta



class ProjectModel(db.Model):
    __tablename__ = 'project'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    completed = db.Column(db.Boolean, default=False)
    start_date = db.Column(db.DateTime, nullable=False, default=date.today())
    duration = db.Column(db.Integer, nullable=False)
    end_date = db.Column(db.DateTime)

    user = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_by = db.relationship("UserModel", backref=db.backref('projects', lazy=True))

    def __init__(self, name, description, duration, user):
        self.name = name
        self.description = description
        self.completed = False
        self.start_date = date.today()
        self.duration = duration
        self.user = user

    def set_end_date(self):
        self.end_date = self.start_date + timedelta(days=self.duration)
        self.save_to_db()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def json(self):
        return {"project_id": self.id, "name": self.name, "description": self.description,
                "completed": self.completed, "start_date": self.start_date.__str__(), "duration": self.duration,
                "end_date": self.end_date.__str__(), "manager":self.user_id}

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_user_id(cls, user):
        return cls.query.filter_by(user=user).all()
