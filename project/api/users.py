# services/users/project/api/users.py

from flask import Blueprint, jsonify, request, render_template
from project.api.models import User
from project import db
from sqlalchemy import exc

users_blueprint = Blueprint("users", __name__, template_folder="./templates")


@users_blueprint.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        db.session.add(User(username=username, email=email))
        db.session.commit()
    users = User.query.all()
    return render_template("index.html", users=users)


@users_blueprint.route("/users/ping", methods=["GET"])
def ping_pong():
    return jsonify({"message": "pong!", "status": "success"})


@users_blueprint.route("/users", methods=["GET"])
def get_all_users():
    """Get all users"""
    response_object = {
        "status": "success",
        "data": {"users": [user.to_json() for user in User.query.all()]},
    }
    return jsonify(response_object), 200


@users_blueprint.route("/users", methods=["POST"])
def add_user():
    """Add an user to the DB"""
    post_data = request.get_json()

    response_object = {"message": "Invalid payload", "status": "fail"}
    if "username" not in post_data or "email" not in post_data:
        return jsonify(response_object), 400

    username = post_data.get("username")
    email = post_data.get("email")
    try:
        existing_email = User.query.filter_by(email=email).first()
        existing_user = User.query.filter_by(username=username).first()
        if not existing_email and not existing_user:
            db.session.add(User(username=username, email=email))
            db.session.commit()
            response_object = {
                "message": "{} was added".format(email),
                "status": "success",
            }
            return jsonify(response_object), 201
        else:
            response_object = {
                "message": "User or email already exists",
                "status": "fail",
            }
            return jsonify(response_object), 400
    except exc.IntegrityError:
        db.session.rollback()
        return jsonify(response_object), 400


@users_blueprint.route("/user/<user_id>", methods=["GET"])
def get_user(user_id):
    """Get single user details"""
    response_object = {"status": "fail", "message": "User does not exists"}
    try:
        user = User.query.filter_by(id=int(user_id)).first()
        if not user:
            return jsonify(response_object), 404
        else:
            response_object = {
                "status": "success",
                "data": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "active": user.active,
                },
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404
