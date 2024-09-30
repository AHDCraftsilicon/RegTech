from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from flask_jwt_extended import jwt_required ,get_jwt
from datetime import timedelta
from cryptography.fernet import Fernet
import base64
from bson import ObjectId


# DataBase
from data_base_string import *

# Blueprint
Admin_Dashboard_bp = Blueprint("Admin_Dashboard_bp",
                        __name__,
                        url_prefix="/BBRgt",
                        template_folder="templates")


# Database 
Admin_Authentication_db = Regtch_services_UAT["Admin_Authentication"]


@Admin_Dashboard_bp.route("/dashboard")
@jwt_required(locations=['cookies'])
def admin_dashboard_main():

    claims = get_jwt()

    name = ""
    if claims["sub"]["db_name"] == "Admin_Authentication":
        if claims["sub"]["objid"] != "":
            print(claims["sub"]["objid"])
            admin_details = Admin_Authentication_db.find_one({"_id":ObjectId(claims["sub"]["objid"])})

            if admin_details != None:
                name = admin_details["name"]




    return render_template("admin_dashboard.html" , 
                           name=name)