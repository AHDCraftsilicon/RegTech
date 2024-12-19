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

    try:

        encrypted_token = session.get('QtSld')
        ip_address = session.get('KLpi')
        get_objid = session.get('bkjid')

        if session.get('bkjid') != "":

            check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})
            
            if check_user_in_db != None:

                if encrypted_token and ip_address:
                    token = decrypt_token(encrypted_token)

                    page_name = "Usage Insights"

                    user_type = "Test Credits"

                    if check_user_in_db['user_flag'] == "0":
                        user_type = "Live Credits"


                    user_name = check_user_in_db["Company_Name"]
                    page_info = [{"Test_Credit": check_user_in_db["total_test_credits"],
                                "Used_Credits":check_user_in_db["used_test_credits"] ,
                                "user_type" : user_type ,
                                "page_name":page_name,
                                "user_name": user_name
                                }]

                    return render_template('Usage_insights.html',
                                            page_info=page_info,
                                            user_details={"user_name": user_name,
                                                      "Email_Id":check_user_in_db['Email_Id'],
                                                    "user_type" :user_type},)
                            
                    
                return redirect("/")
                
            return redirect("/")
        
        return redirect("/")
    except:
        return redirect("/error")
