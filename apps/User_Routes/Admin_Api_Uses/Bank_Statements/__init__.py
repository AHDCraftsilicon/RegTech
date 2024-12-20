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
import uuid
import ast


# Module
from apps.User_Routes.Admin_Api_Uses.Bank_Statements.icici_statment_module import *


# DataBase
from data_base_string import *

# Token
from token_generation import *


# Blueprint
Bank_Statments_bp = Blueprint("Bank_Statments_bp",
                        __name__,
                        url_prefix="/bank",
                        template_folder="templates")


User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
User_test_Api_history_db = Regtch_services_UAT['User_test_Api_history']
Api_Informations_db = Regtch_services_UAT["Api_Informations"]




@Bank_Statments_bp.route("/statement",methods=["GET","POST"])
def Bank_Statment_main():

    encrypted_token = session.get('QtSld')
    ip_address = session.get('KLpi')

    if session.get('bkjid') != "":

        check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})

        if check_user_in_db != None:

            if encrypted_token and ip_address:
                # Check User Api Status
                if check_user_in_db['api_status'] == "Enable":
                    token = decrypt_token(encrypted_token)

                    page_name = "Bank Statement"

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

                    about_api_details = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3b9ce184651154149a")})

                    return render_template("bank_statment_modal.html",
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


@Bank_Statments_bp.route('/test-api',methods=['POST'])
def Bank_Statment_test_api():

    if request.method == "POST":
        # try:
            encrypted_token = session.get('QtSld')
            ip_address = session.get('KLpi')
            if session.get('bkjid') != "":

                check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})
                if check_user_in_db != None:
                    if int(check_user_in_db["used_test_credits"]) > 0:

                        # Api Start Time
                        start_time = datetime.utcnow()


                        pdf_file = request.files["PDF_File"]
                        filename_ipdf = str(time.time()).replace(".", "")


                        System_Generated_Unique_id = str(uuid.uuid4())
                        if pdf_file.filename != "":
                            pdf_file.save(os.path.join('./apps/static/bank_statement_analysing', secure_filename(
                                filename_ipdf+"."+pdf_file.filename.split(".")[-1])))
                            pdf_store_file = "apps/static/bank_statement_analysing/"+filename_ipdf+"."+pdf_file.filename.split(".")[-1]
                                
                            if request.form["BankName"] == "ICICIBANK":
                                icici_response = icic_bank_statement_main(pdf_store_file)

                                # Api End Time
                                end_time = datetime.utcnow()
                                duration = (end_time - start_time).total_seconds() * 1000

                                # Request Id
                                request_id = generate_random_id()

                                # name of api
                                about_api_details = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3b9ce184651154149a")})

                                os.remove(pdf_store_file)

                                json_msg = {"data":{
                                    "status_code": 200,
                                    "status": "Success",
                                    "response": icici_response,
                                    "System_Generated_Unique_id" : System_Generated_Unique_id,
                                    "basic_response":{ "request_id" : request_id,
                                                "request_on" : start_time,
                                                "response_on":end_time,
                                                "api_name":about_api_details['api'],
                                                "duration":round(duration, 2),
                                                }
                                    }}

                                # store_response = {"status_code": 200,
                                #                     "status": "Success",
                                #                     "response": icici_response,
                                #                     "created_on" : created_on,
                                #                     "completed_on":completed_on,
                                #                     "request_id":generate_random_id(),
                                #                     "System_Generated_Unique_id" : System_Generated_Unique_id
                                #                     }
                                

                                # # DataBase Log
                                User_test_Api_history_db.insert_one({
                                            "user_id":check_user_in_db["_id"],
                                            "User_Unique_id":"Api Call From Dashboard",
                                            "api_name":"Bank_Statement",
                                            "api_start_time":start_time,
                                            "api_end_time":datetime.now(),
                                            "api_status": "Success",
                                            "response_duration":str(duration),
                                            "response_time":end_time,
                                            "request_data":{},
                                            "response_data" :str(icici_response),
                                            "creadted_on":datetime.now(),
                                            "System_Generated_Unique_id" : System_Generated_Unique_id,
                                            })
                                
                                # Check Api Using Credits
                                # api_use_credit_info = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3b9ce184651154149a")})
                                    
                                # if check_user_in_db["unlimited_test_credits"] == False:
                                #     # Credit 
                                #     User_Authentication_db.update_one({"_id":check_user_in_db["_id"]},{"$set":{
                                #         "used_test_credits": check_user_in_db["used_test_credits"] + api_use_credit_info["credits_per_use"]
                                #     }})


                                return jsonify(json_msg)
                            
                            else:
                                return jsonify({"data":{
                                "status_code": 400,
                                "status": "Error",
                                "response":"Please Mention BankName!"
                            }}), 400


                    else:
                        return jsonify({"data":{
                                "status_code": 400,
                                "status": "Error",
                                "response":"You have zero credits left, please pay for more credits!"
                            }}), 400

        
            return jsonify({"data":{"json_data":"Something went wrong!"}})
        
        # except:
        #     return redirect("/")
        

    return jsonify({"msg":"method Not allowed!"})

                        




@Bank_Statments_bp.route("/statement-Analysis-report",methods=["GET","POST"])
def Bank_statement_analysis_report_page():


    print("---------- " ,request.args.get("_id"))

    if request.args.get("_id") != "":

        encrypted_token = session.get('QtSld')
        ip_address = session.get('KLpi')

        if session.get('bkjid') != "":

            check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})
        
            check_system_id = User_test_Api_history_db.find_one({"System_Generated_Unique_id":request.args.get("_id")})
            page_name = "Bank Statement Analysis Report"

            user_type = "Test Credits"

            if check_user_in_db['user_flag'] == "0":
                user_type = "Live Credits"

            user_name = check_user_in_db["Company_Name"]
            page_info = [{"Test_Credit": check_user_in_db["total_test_credits"],
                        "Used_Credits":check_user_in_db["used_test_credits"] ,
                        "user_type" : user_type ,
                        "page_name":page_name
                        }]
            
            if check_system_id != None:
                satement_details = check_system_id["response_data"]
                # satement_details = json.loads(satement_details)

                data_dict = ast.literal_eval(satement_details)
                print(data_dict)

                return render_template("bank_statement_analysis_report.html",
                                    satement_details = data_dict,
                                    page_info=page_info,
                                    user_details={"user_name": user_name,
                                                      "Email_Id":check_user_in_db['Email_Id'],
                                                    "user_type" :user_type},
                                    )
            
            else:
                return redirect("/")
        else:
            return redirect("/")







