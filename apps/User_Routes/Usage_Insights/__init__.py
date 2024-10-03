from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,session
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import timedelta
from bson import ObjectId

# DataBase
from data_base_string import *

# Token
from token_generation import *

# Blueprint
User_Api_Usage_bp = Blueprint("User_Api_Usage_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")


# Database 
User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
User_test_Api_history_db = Regtch_services_UAT['User_test_Api_history']
Api_Informations_db = Regtch_services_UAT["Api_Informations"]


@User_Api_Usage_bp.route("/usage-insights")
def User_Api_Usage_insights():

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

                        return render_template('Usage_insights.html',
                                                test_credit=test_credits,
                                                sccess_id_key=sccess_id_key,
                                                user_name=user_name)
                        
                    return redirect("/")
                
                return redirect("/")
            
        return redirect("/")
    
    return redirect("/")
