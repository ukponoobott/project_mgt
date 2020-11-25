from db import db


class TaskModel(db.Model):
    __tablename__ = 'task'
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    note = db.Column(db.String(80), nullable=False)
    project = db.relationship("ProjectModel", backref=db.backref('tasks', lazy=True))

    def __init__(self, project_id, description, note):
        self.project_id = project_id
        self.description = description
        self.note = note

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def json(self):
        return {"project_id": self.project_id, "action_id": self.id, "description": self.description,
                "note": self.note}

    @classmethod
    def find_by_id(cls, _id):
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_project_id(cls, project_id):
        return cls.query.filter_by(project_id=project_id).all()

    @classmethod
    def find_project_task(cls, _id, project_id):
        return cls.query.filter_by(id=_id, project_id=project_id).first()

    @classmethod
    def find_all_tasks(cls):
        pass
