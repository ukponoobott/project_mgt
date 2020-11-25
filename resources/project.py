from flask_restful import Resource, reqparse
from models.project import ProjectModel
from datetime import date


class Project(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name",
                        type=str,
                        required=True,
                        help="This is required"
                        )

    parser.add_argument("description",
                        type=str,
                        required=True,
                        help="This is required"
                        )

    parser.add_argument("completed",
                        type=bool,
                        required=True,
                        help="This is required"
                        )

    def get(self, project_id):
        project = ProjectModel.find_by_id(project_id)
        if project:
            return project.json()
        return {"message": "Project not found"}

    def patch(self, project_id):
        parser = reqparse.RequestParser()
        parser.add_argument("completed",
                            type=bool,
                            required=True,
                            help="This is required"
                            )

        project = ProjectModel.find_by_id(project_id)
        if project:
            data = parser.parse_args()
            project.completed = data["completed"]
            try:
                project.save_to_db()
            except:
                return {"message": "An error occurred"}, 500
            return project.json()

    def put(self, project_id):
        project = ProjectModel.find_by_id(project_id)
        if project:
            print(project.json())
            data = Project.parser.parse_args()
            project.name = data["name"]
            project.description = data["description"]
            project.completed = data["completed"]
            try:
                project.save_to_db
            except:
                return {"message": "An error occurred"}, 500
            return project.json()
        data = ProjectList.parser.parse_args()

        project = ProjectModel(data["name"], data["description"], data["completed"])
        try:
            project.save_to_db()

        except:
            return {"message": "An error occurred, cannot create project"}
        return project.json()

    def delete(self, project_id):
        project = ProjectModel.find_by_id(project_id)
        if project:
            project.delete_from_db()


class ProjectList(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument("name",
                        type=str,
                        required=True,
                        help="This is required"
                        )

    parser.add_argument("description",
                        type=str,
                        required=True,
                        help="This is required"
                        )

    parser.add_argument("completed",
                        type=bool
                        )

    parser.add_argument("duration",
                        type=int,
                        )

    parser.add_argument("user_id",
                        type=int)
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("search",
                            type=str,
                            required=True
                            )
        data = parser.parse_args()
        if data["search"]:
            s = "%{}%".format(data["search"])
            find = ProjectModel.query.filter(ProjectModel.name.like(s)).all()
            print(find)
            return find.json()
        return {"project": [project.json() for project in ProjectModel.query.all()]}

    def post(self):
        data = ProjectList.parser.parse_args()

        project = ProjectModel(name=data["name"], description=data["description"],
                               completed=data["completed"], duration=data["duration"], user_id=data["user_id"], start_date=date.today())
        try:
            project.set_end_date()
            project.save_to_db()
        except:
            return {"message": "An error occurred, cannot create project"}
        return project.json()


# class SearchProject(Resource):
#     def get(self, word):
#         s = "%{}%".format(word)
#         print(s)
#         find = ProjectModel.query.filter(ProjectModel.name.like(s)).all()
#         if find:
#             print(find)
#             return find.json()
#         return {"message": "No project matches the search criteria"}
