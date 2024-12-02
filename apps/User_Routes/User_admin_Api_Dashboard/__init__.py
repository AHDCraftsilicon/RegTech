from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,session
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import timedelta
from bson import ObjectId

# DataBase
from data_base_string import *

# Token
from token_generation import *

# Blueprint
User_Admin_Api_Dashboard_bp = Blueprint("User_Admin_Api_Dashboard_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")


# Database 
User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
User_test_Api_history_db = Regtch_services_UAT['User_test_Api_history']
Api_Informations_db = Regtch_services_UAT["Api_Informations"]


@User_Admin_Api_Dashboard_bp.route("/dashboard")
def User_Api_Dashboard_main():

    try:
        encrypted_token = session.get('QtSld')
        ip_address = session.get('KLpi')

        if session.get('bkjid') != "":

            check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})

            if check_user_in_db != None:
                

                if encrypted_token and ip_address:
                    token = decrypt_token(encrypted_token)

                    page_name = "Home"

                    user_type = "Test Credits"

                    if check_user_in_db['user_flag'] == "0":
                        user_type = "Live Credits"
                    
                    api_info = Api_Informations_db.find()
                        
                    api_list = []
                    objid_list = []
                
                    for x in api_info:
                        api_list.append({
                            "api_name":x["api_name"],
                            "long_api_description":x["long_api_description"],
                            "sort_api_description":x["sort_api_description"],
                            "api_logo": x["api_logo"],
                            "page_url":x["page_url"],
                            "status":x["status"],
                            "view_permission":x["view_permission"],
                            "created_on":str((x["created_on"]).strftime("%d-%m-%Y %H:%M:%S")),
                            "objid":str(x["_id"])
                        })

                        objid_list.append({
                            "objid":str(x["_id"])
                        })

                    user_name = check_user_in_db["Company_Name"]
                    page_info = [{"Test_Credit": check_user_in_db["total_test_credits"],
                                "Used_Credits":check_user_in_db["used_test_credits"] ,
                                "user_type" : user_type ,
                                "page_name":page_name,
                                "user_name": user_name
                                }]
                    return render_template("Api_dashboard.html",
                                api_list=api_list,api_count = objid_list,
                                page_info=page_info,
                                user_details={"user_name": user_name,"user_type" :user_type})
            
            return redirect("/")
        
        return redirect("/")
    
    except:
        return redirect("/error")
    

@User_Admin_Api_Dashboard_bp.route("/request-for-more/credits")
def more_credits_email_sent():

    try:
        encrypted_token = session.get('QtSld')
        ip_address = session.get('KLpi')

        if session.get('bkjid') != "":

            check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})

            if check_user_in_db != None:
                

                if encrypted_token and ip_address:
                    token = decrypt_token(encrypted_token)

                    print(check_user_in_db['Email_Id'])

                    return jsonify({"status_code": 200,
                            "status": "Success",
                            "response": "Thank you for your request!"}),200

            return redirect("/")
        return redirect("/")
    except:
        return redirect("/error")

    


       
    

    



    


