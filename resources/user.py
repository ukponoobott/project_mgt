from models.user import UserModel
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from flask import request, redirect, render_template, url_for
from werkzeug.security import check_password_hash
from app import app


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        if UserModel.find_by_email(email):
            return {"message": "User already exists"}
        full_name = request.form["full_name"]
        password = request.form["password"]
        user = UserModel(full_name, email, password)
        user.save_to_db()
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        user = UserModel.find_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            access_token = create_access_token(identity=user.id, fresh=True)
            return redirect(url_for("account", access_token=access_token))
    else:
        return render_template("login.html")


@app.route("/account", methods=["GET", "PATCH", "DELETE"])
def account():
    if request.method == "GET":
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        if not user:
            return {"message": "User not found"}, 404
        return render_template("account.html", user=user)

    # @classmethod
    # @jwt_required
    # def delete(cls):
    #     user_id = get_jwt_identity()
    #     user = UserModel.find_by_id(user_id)
    #     if not user:
    #         return {"message": "User not found"}, 404
    #     user.delete_from_db()
    #     return {"message": "User deleted"}, 200
