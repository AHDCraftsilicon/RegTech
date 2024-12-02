from flask import Blueprint, render_template,request,redirect,flash,jsonify,session
from flask_jwt_extended import JWTManager
from datetime import timedelta
from cryptography.fernet import Fernet
import base64

# DataBase
from data_base_string import *

# Blueprint
Admin_login_bp = Blueprint("Admin_login_bp",
                        __name__,
                        url_prefix="/BBRgt",
                        template_folder="templates")

# Database 
Admin_Authentication_db = Regtch_services_UAT["Admin_Authentication"]

@Admin_login_bp.route("/admin-login-RRtggR")
def Admin_login_main():

    return render_template("admin_login.html")


@Admin_login_bp.route("/gdo/i/RmRngoaa/lgnRl",methods=["POST"])
def Admin_validation_check():

    if request.method == "POST":
        if request.form["User_Name"] != "" and request.form["Password"] != "":

            if ".com" in request.form["User_Name"]:
                db_details_get = Admin_Authentication_db.find_one({"email":request.form["User_Name"]})
            else:
                db_details_get = Admin_Authentication_db.find_one({"username":request.form["User_Name"]})
            

            if db_details_get != None:

                if db_details_get["password"] == request.form["Password"]:

                    resp = jsonify({"data":{"response":"Admin Login Successful",
                                                "redirect":"/BBRgt/dashboard",
                                                "status":"Success",
                                                "status_code":200
                                                }})

                    session['am_bd_name'] = "Admin_Authentication"
                    session['am_bjde'] = str(db_details_get['_id'])
                    session['dir_direct'] = "/BBRgt/dashboard"

                    return resp
                else:
                    return jsonify({"data":{"response":"Incorrect email or password. Please try again!",
                                                "status":"Success",
                                                "status_code":400
                                                }})
            else:
                return jsonify({"data":{"response":"Incorrect email or password. Please try again!",
                                                "status":"Success",
                                                "status_code":400
                                                }})
        else:
            return jsonify({"data":{"response":"Incorrect email or password. Please try again!",
                                                "status":"Success",
                                                "status_code":400
                                                }})

    return redirect("/BBRgt/admin-login-RRtggR")




