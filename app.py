from flask import Flask, flash,  request, redirect, render_template, session, url_for
import db

from models.user import UserModel
from models.project import ProjectModel
from models.task import TaskModel

from werkzeug.security import check_password_hash
from default_config import DefaultConfig
from dotenv import load_dotenv

from libs.token import generate_confirmation_token, confirm_token
from libs.mailgun import MailGunException, MailGun


app = Flask(__name__)
load_dotenv('.env', verbose=True)
app.config.from_object(DefaultConfig)
app.config.from_envvar('APPLICATION_SETTINGS')



@app.route('/')
def index():
    return render_template('index.html')


@app.route("/register", methods=["POST"])
def register():
    email = request.form["email"]
    if UserModel.find_by_email(email):
        flash("User already exists")
    else:
        full_name = request.form["full_name"]
        password = request.form["password"]
        user = UserModel(full_name=full_name, email=email, confirmed=False, password=password)
        user.save_to_db()

        token = generate_confirmation_token(email)
        confirm_url = url_for('confirm_email', token=token, _external=True)
        html = render_template('activate.html', confirm_url=confirm_url)
        link = "Click here to confirm your account {}".format(confirm_url)

        # Send email

        subject = "Please confirm your email"
        try:
            MailGun.send_email(email, subject, link, html)
            flash("A confirmation link has been sent to your email")
        except MailGunException as err:
            flash("an error occurred {}".format(err))
        except:
            user.delete_from_db()
            flash("Please try creating an account again")

        return redirect(url_for('index'))



@app.route("/confirm/<token>")
def confirm_email(token):
    try:
        email = confirm_token(token)
        print(email)
    except:
        flash("The confirmation link is invalid")
    user = UserModel.find_by_email(email)
    print(user)
    if user.confirmed:
        flash("User already confirmed, Please login")
    else:
        user.confirmed = True
        user.save_to_db()
        flash("You have confirmed your account"), 200

    return redirect(url_for('index'))


@app.route("/unconfirmed")
def unconfirmed():
    return render_template("unconfirmed.html")


@app.route("/resend_confirmation")
def resend_confirmation():
    if "email" in session:
        user_email = session["email"]
        user = UserModel.find_by_email(user_email)
        if not user:
            return {"message": "User not found"}, 404
        if user.confirmed:
            flash("User has been confirmed, Please login")
            redirect(url_for('index'))
        else:
            token = generate_confirmation_token(user_email)
            confirm_url = url_for('confirm_email', token=token, _external=True)
            print(confirm_url)
            # html = render_template("activate.html", confirm_url=confirm_url)
            link = "Click here to confirm your account {}".format(confirm_url)
            html = None
            subject = "Please confirm your email"
            try:
                MailGun.send_email(user_email, subject, link, html)
                flash("A confirmation link has been sent to your email")
            except MailGunException as err:
                flash("an error occurred {}".format(err))
            except:
                user.delete_from_db()
                flash("Please try creating an account again")

            return redirect(url_for('index'))


@app.route("/login", methods=["GET", "POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]
    user = UserModel.find_by_email(email)
    if user:
        print(user.email)
        if check_password_hash(user.password_hash, password):
            session["email"] = user.email
            if user.confirmed:
                return redirect(url_for("account"))
            else:
                return redirect(url_for('unconfirmed'))
        flash("wrong password")
        return render_template('index.html')
    else:
        flash("User does not exist")
    return render_template('index.html')


@app.route("/account", methods=["GET", "PATCH", "DELETE"])
def account():
    if request.method == "GET":
        if "email" in session:
            user_email = session["email"]
            user = UserModel.find_by_email(user_email)
            if not user:
                return {"message": "User not found"}, 404
            if user.confirmed:
                return render_template("account.html", user=user)
            return redirect(url_for('unconfirmed'))


@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for('index'))


@app.route("/project/create", methods=["GET", "POST"])
def new():
    if "email" in session:
        user_email = session["email"]
        if request.method == "POST":
            name = request.form["name"]
            description = request.form["description"]
            duration = request.form["duration"]
            user = UserModel.find_by_email(user_email)
            print(user.id)
            new_project = ProjectModel(name, description, int(duration), user.id)
            new_project.set_end_date()
            new_project.save_to_db()
        return render_template("create_project.html")
    return redirect(url_for("index"))


@app.route("/projects")
def projects():
    if "email" in session:
        user_email = session["email"]
        user = UserModel.find_by_email(user_email)
        if user and user.confirmed:
            user_projects = ProjectModel.find_by_user_id(user.id)
            return render_template("projects.html", projects=user_projects)
    return redirect(url_for('index'))


@app.route("/project00<int:project_id>", methods=["GET", "POST"])
def single_project(project_id):

    if request.method == "GET":
        if session:
            user_email = session["email"]
            user = UserModel.find_by_email(user_email)
            if user:
                project = ProjectModel.find_by_id(project_id)
                if project and user.id == project.user:
                    return render_template("project.html", project=project)
                elif not project:
                    return {"message": "Project not found"}
                elif user.id != project.user:
                    return {"message": "not authorised"}
            return {"message": "Please login"}
        return {"message": "login"}

    elif request.method == "POST":
        user_email = session["email"]
        user = UserModel.find_by_email(user_email)
        if user:
            project = ProjectModel.find_by_id(project_id)
            if project and user.id == project.user:
                project.delete_from_db()
                return {"message": "Project deleted"}


@app.route("/edit/project-00<int:project_id>", methods=["GET", "POST"])
def edit_project(project_id):
    if "email" in session:
        if request.method == "POST":
            user_email = session["email"]
            user = UserModel.find_by_email(user_email)
            if user:
                project = ProjectModel.find_by_id(project_id)
                if project and user.id == project.user:
                    project.name = request.form["name"] or project.name
                    project.description = request.form["description"] or project.description
                    # project.start_date = request.form["start_date"] or project.start_date
                    project.duration = request.form["duration"] or project.duration
                    project.save_to_db()
                    return {"message": "Project updated"}
        elif request.method == "GET":
            user_email = session["email"]
            user = UserModel.find_by_email(user_email)
            if user:
                project = ProjectModel.find_by_id(project_id)
                if project and user.id == project.user:
                    return render_template("edit_project.html", project=project)
                elif not project:
                    return {"message": "Project not found"}
                elif user.id != project.user:
                    return {"message": "not authorised"}
        return redirect(url_for("index"))


# @app.route("/project/<int:project_id>/update-status", methods=["GET", "POST"])
# def update_status(project_id):
#     if "email" in session:
#         user_email = session["email"]
#         user = UserModel.find_by_email(user_email)
#         if user:
#             project = ProjectModel.find_by_id(project_id)
#             if project and user.id != project.user:
#                 return {"message": "Not authorized to access this project"}
#             elif not project:
#                 return {"message": "Project not found"}
#             elif project and user.id == project.user:
#                 if request.method == "POST":
#                     pass
#                     return {"message": "Status updated"}
#
#                 elif request.method == "GET":
#                     return render_template("status.html")



@app.route("/create_task/project-00<int:project_id>", methods=["GET", "POST"])
def create_action(project_id):
    if "email" in session:
        user_email = session["email"]
        user = UserModel.find_by_email(user_email)
        project = ProjectModel.find_by_id(project_id)
        if project and user.id != project.user:
            return {"message": "Not authorized to access this project"}
        elif not project:
            return {"message": "Project not found"}
        elif project and user.id == project.user:
            if request.method == "POST":
                description = request.form["description"]
                note = request.form["note"]
                new_action = TaskModel(project_id, description, note)
                new_action.save_to_db()
                return {"message": "New action added"}
            return render_template("create_task.html", project=project)
    return redirect(url_for('index'))


@app.route("/actions/project-00<int:project_id>")
def project_actions(project_id):
    if "email" in session:
        user_email = session["email"]
        user = UserModel.find_by_email(user_email)
        if user:
            project = ProjectModel.find_by_id(project_id)
            if project and user.id != project.user:
                return {"message": "Not authorized to access this project"}
            elif not project:
                return {"message": "Project not found"}
            elif project and user.id == project.user:
                actions = TaskModel.find_by_project_id(project_id)
                return render_template("project_actions.html", actions=actions)


@app.route("/action/project-00<int:project_id>action-00<int:action_id>", methods=["GET", "POST"])
def single_action_for_project(project_id, action_id):
    if "email" in session:
        user_email = session["email"]
        user = UserModel.find_by_email(user_email)
        if user:
            project = ProjectModel.find_by_id(project_id)
            if project and user.id != project.user:
                return {"message": "Not authorized to access this project"}
            elif not project:
                return {"message": "Project not found"}
            elif project and user.id == project.user:
                action = TaskModel.find_project_task(action_id, project_id)
                if request.method == "GET":
                    return render_template("single_task_for_project.html", action=action, project=project)
                elif request.method == "POST":
                    action.delete_from_db()
                    flash("Task Deleted")
                    return redirect(url_for('project_actions'))
    else:
        flash("Please Login")
        return redirect(url_for('index'))



@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=3500, debug=True)
