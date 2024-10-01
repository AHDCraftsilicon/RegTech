from flask import Blueprint, render_template,request,session,redirect
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

                test_credit = User_Testing_Credits_db.find_one({"_id":ObjectId("66ecfbff621502ccf8852429")})["total_credit"]

                if get_objid != "":
                    access_credential = User_Authentication_db.find_one({"_id":ObjectId(get_objid)})

                    if access_credential != None:
                        sccess_id_key = [{"client_id":access_credential['client_id'],
                                        "client_secret_key" :access_credential["client_secret_key"]
                                        }]
                        user_name = check_user_in_db["Company_Name"]
                        test_credits = [{"Test_Credit": check_user_in_db["total_test_credits"],
                                    "Used_Credits":check_user_in_db["used_test_credits"]}]

                        return render_template('support.html',
                                                test_credit=test_credits,
                                                sccess_id_key=sccess_id_key,
                                                user_name=user_name)
                        
                    return redirect("/")
                
                return redirect("/")
            
        return redirect("/")
    
    return redirect("/")



