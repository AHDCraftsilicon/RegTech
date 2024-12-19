from flask import Blueprint, render_template,request,session,redirect
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta
from bson import ObjectId
import random
import pytz
from PIL import Image
import cv2
import pytesseract
import numpy as np
import time , os
from werkzeug.utils import secure_filename


# Module
from apps.User_Routes.Admin_Api_Uses.ITR_Analysis.ITR1_Analysis_module import *


# DataBase
from data_base_string import *

# Token
from token_generation import *


# Blueprint
ITR_analysis_bp = Blueprint("ITR_analysis_bp",
                        __name__,
                        url_prefix="/ITR",
                        template_folder="templates")


User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
User_test_Api_history_db = Regtch_services_UAT['User_test_Api_history']
Api_Informations_db = Regtch_services_UAT["Api_Informations"]




@ITR_analysis_bp.route("/analysis")
def ITR_Analysis_main():

    encrypted_token = session.get('QtSld')
    ip_address = session.get('KLpi')

    if session.get('bkjid') != "":

        check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})

        # User Check in DB
        if check_user_in_db != None:

            if encrypted_token and ip_address:
                # Check User Api Status
                if check_user_in_db['api_status'] == "Enable":
                    token = decrypt_token(encrypted_token)

                    page_name = "ITR Analysis"

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

                    about_api_details = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3b9ce184651154149b")})

                    return render_template("ITR_Analysis_modal.html",
                                        page_info=page_info , 
                                        about_api_details = {"long_api_description": about_api_details['long_api_description'],
                                                            "credits_per_use": about_api_details['credits_per_use']
                                                            },
                                        user_details={"user_name": user_name,
                                                      "Email_Id":check_user_in_db['Email_Id'],
                                                    "user_type" :user_type},)
                
                else:
                    return redirect("/dashboard")
            
        return redirect("/")
    
    return redirect("/")


# Random request id generate
def generate_random_id():
    return '-'.join(''.join(random.choices('0123456789abcdef', k=4)) for _ in range(5))



@ITR_analysis_bp.route('/test-api',methods=['POST'])
def Bank_Statment_test_api():
    if request.method == "POST":

        # Api Start Time
        start_time = datetime.utcnow()


        pdf_file = request.files["ITR_pdf"]
        filename_ipdf = str(time.time()).replace(".", "")

        if pdf_file.filename != "":
            pdf_file.save(os.path.join('./apps/static/ITR_Analysis', secure_filename(
                filename_ipdf+"."+pdf_file.filename.split(".")[-1])))
            pdf_store_file = "apps/static/ITR_Analysis/"+filename_ipdf+"."+pdf_file.filename.split(".")[-1]
                
            if request.form["ITR_Type"] == "ITR-1":
                ITR1_Response = itr1_read_main(pdf_store_file)

            # Api End Time
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds() * 1000

            # Request Id
            request_id = generate_random_id()

            # name of api
            about_api_details = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3b9ce184651154149b")})

            json_msg = {"data":{
                            "status_code": 200,
                            "status": "Success",
                            "response": ITR1_Response,
                            "basic_response":{ "request_id" : request_id,
                                        "request_on" : start_time,
                                        "response_on":end_time,
                                        "api_name":about_api_details['api'],
                                        "duration":round(duration, 2),
                                        }
                            }}

            # store_response = {"response": 200,
            #                     "status": "Success",
            #                     "responseValue":ITR1_Response,
            #                     "created_on" : created_on,
            #                     "completed_on":completed_on,
            #                     "request_id":generate_random_id(),
            #                     }


            return jsonify(json_msg)
    
    return jsonify({"msg":"method Not allowed!"})