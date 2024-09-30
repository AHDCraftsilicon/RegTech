from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
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

                    duration = timedelta(hours=3)
                    access_token = create_access_token(expires_delta=duration, identity={'data':'Admin Login SuccessFully!',
                                                                "db_name":"Admin_Authentication",
                                                                'objid':str(db_details_get['_id'])}
                                                        )
                        
                    resp = redirect("/BBRgt/dashboard")

                    set_access_cookies(resp, access_token)
                    return resp
                else:
                    flash('Incorrect email or password. Please try again.')
                    return redirect("/BBRgt/admin-login-RRtggR")
            else:
                flash('Incorrect email or password. Please try again.')
                return redirect("/BBRgt/admin-login-RRtggR")
        else:
            flash('Incorrect email or password. Please try again.')
            return redirect("/BBRgt/admin-login-RRtggR")

    return redirect("/BBRgt/admin-login-RRtggR")




