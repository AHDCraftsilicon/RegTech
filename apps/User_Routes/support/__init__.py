from flask import Blueprint, render_template,request,session,redirect , flash
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta
from bson import ObjectId
import random
import pytz


# DataBase
from data_base_string import *

# Token
from token_generation import *

# Blueprint
User_Support_bp = Blueprint("User_Support_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")




User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
User_support_db = Regtch_services_UAT["User_support"]


@User_Support_bp.route("/support")
def Api_support_main():
    encrypted_token = session.get('QtSld')
    ip_address = session.get('KLpi')
    get_objid = session.get('bkjid')

    if session.get('bkjid') != "":

        check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})
        
        if check_user_in_db != None:

            if encrypted_token and ip_address:
                token = decrypt_token(encrypted_token)
              
                page_name = "Customer Support"

                user_type = "Test Credits"

                if check_user_in_db['user_flag'] == "0":
                    user_type = "Live Credits"


                user_name = check_user_in_db["Company_Name"]
                page_info = [{"Test_Credit": check_user_in_db["total_test_credits"],
                            "Used_Credits":check_user_in_db["used_test_credits"] ,
                            "user_type" : user_type ,
                            "page_name":page_name
                            }]

                return render_template('support.html',
                                        page_info=page_info,
                                        user_details={"user_name": user_name,
                                                      "Email_Id":check_user_in_db['Email_Id'],
                                                    "user_type" :user_type},)
                        
                
            return redirect("/")
            
        return redirect("/")
    
    return redirect("/")


@User_Support_bp.route("/support-form",methods=["POST","GET"])
def Api_support_form():
    encrypted_token = session.get('QtSld')
    ip_address = session.get('KLpi')
    get_objid = session.get('bkjid')

    if request.method == "POST":

        if session.get('bkjid') != "":

            check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})
            
            if check_user_in_db != None:

                if encrypted_token and ip_address:
                    token = decrypt_token(encrypted_token)

                    test_credit = User_Testing_Credits_db.find_one({"_id":ObjectId("66ecfbff621502ccf8852429")})["total_credit"]

                    if get_objid != "":
                        access_credential = User_Authentication_db.find_one({"_id":ObjectId(get_objid)})

                        if access_credential != None:
                            User_support_db.insert_one({"subject":request.form["subject"],
                                                        "Message":request.form["Message"],
                                                        "created_on" : datetime.now()
                                                        })

                            
                            flash("Request Submmited Successfully!")
                            return redirect("/support")
                            
                        return redirect("/")
                    
                    return redirect("/")
                
            return redirect("/")
        
        return redirect("/")



