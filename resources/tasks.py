from flask_restful import Resource, reqparse
from models.task import ActionModel
from models.project import ProjectModel


class Actions(Resource):
    def get(self, action_id):
        action = ActionModel.find_by_id(action_id)
        return action.json()


class ActionsList(Resource):
    def get(self):
        return {"actions": [action.json() for action in ActionModel.query.all()]}


class ProjectActions(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument("description",
                        type=str,
                        required=True,
                        help="This is required"
                        )

    parser.add_argument("note",
                        type=str,
                        required=True,
                        help="This is required"
                        )

    def get(self, project_id):
        actions = ActionModel.find_by_project_id(project_id)
        return {"actions": [action.json() for action in actions]}

    def post(self, project_id):
        data = ProjectActions.parser.parse_args()

        project = ProjectModel.find_by_id(project_id)

        if project:

            action = ActionModel(project_id, data["description"], data["note"])
            try:
                action.save_to_db()
            except:
                return {"message": "An error occurred, cannot create action"}
            return action.json()
        return {"message": "Project does not exist"}


class SingleActionForProject(Resource):
    def get(self, project_id, action_id):
        action = ActionModel.find_project_action(action_id, project_id).first()
        return action.json()

    def put(self, project_id, action_id):
        parser = reqparse.RequestParser()

        parser.add_argument("description",
                            type=str,
                            required=True,
                            help="This is required"
                            )

        parser.add_argument("note",
                            type=str,
                            required=True,
                            help="This is required"
                            )
        action = ActionModel.find_project_action(action_id, project_id).first()
        if action:
            data = parser.parse_args()
            action.description = data["description"]
            action.note = data["note"]
            try:
                action.save_to_db()
            except:
                return {"message": "An error occurred, cannot update action"}
            return action.json()

    def delete(self, project_id, action_id):
        action = ActionModel.find_project_action(action_id, project_id).first()
        if action:
            action.delete_from_db()
