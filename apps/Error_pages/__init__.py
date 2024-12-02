from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,session
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import timedelta
from bson import ObjectId

# DataBase
from data_base_string import *

# Token
from token_generation import *

# Blueprint
Error_page_bp = Blueprint("Error_page_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")


@Error_page_bp.route("/error")
def Something_wrong_route():

    return  render_template("some_thing_went_wrong.html")