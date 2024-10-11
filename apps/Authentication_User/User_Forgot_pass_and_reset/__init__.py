from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta , datetime, timezone
from cryptography.fernet import Fernet
import base64

# DataBase
from data_base_string import *


# Blueprint
User_Forgot_pass_and_reset_bp = Blueprint("User_Forgot_pass_and_reset_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")


# Database 
Authentication_db = Regtch_services_UAT["User_Authentication"]



# Veriy Token Link Expired
@User_Forgot_pass_and_reset_bp.route("/password_reset",methods=["GET","POST"])
def Token_Is_Expired_Unauth():
    
    
    return render_template("reset_password.html")



@User_Forgot_pass_and_reset_bp.route("/email-verification",methods=["POST"])
def email_verification():
    if request.method == "POST":
        try:
            if request.form["Email_Id"] != "":
                database_document = Authentication_db.find_one({"Email_Id":request.form['Email_Id']})
                if database_document != None:
                    print()

                    return jsonify()
                else:
                    return jsonify({"data":"Email ID entered is invaild, please check the id entered or retry."})
                
            return jsonify({"data":"Incorrect email. Please try again."})


        except:
             return jsonify({"data":"Something Want Wrong!"})




