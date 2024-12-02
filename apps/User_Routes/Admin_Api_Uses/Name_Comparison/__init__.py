from flask import Blueprint, render_template,request,session,redirect
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta
from bson import ObjectId
import random
import pytz
import requests


# Name Comparision Module
from apps.User_Routes.Admin_Api_Uses.Name_Comparison.name_comparision_module import *

# DataBase
from data_base_string import *

# Token
from token_generation import *

# Blueprint
Admin_Api_Uses_Name_Comparison_bp = Blueprint("Admin_Api_Uses_Name_Comparison_bp",
                        __name__,
                        url_prefix="/name",
                        template_folder="templates")


User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
Api_Informations_db = Regtch_services_UAT["Api_Informations"]
Prod_user_api_history_db = Regtch_services_UAT['Prod_user_api_history']
Test_user_api_history_db = Regtch_services_UAT['Test_user_api_history']


@Admin_Api_Uses_Name_Comparison_bp.route("/matching")
def Name_compare_main():

    encrypted_token = session.get('QtSld')
    ip_address = session.get('KLpi')

    if session.get('bkjid') != "":

        check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})
        
        if check_user_in_db != None:
            if encrypted_token and ip_address:
                # Check User Api Status
                if check_user_in_db['api_status'] == "Enable":

                    token = decrypt_token(encrypted_token)

                    page_name = "Name Matching"

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

                    about_api_details = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3b9ce1846511541497")})


                    return render_template("Name_comparison_modal.html",
                                            page_info=page_info , 
                                            about_api_details = {"long_api_description": about_api_details['long_api_description'],
                                                                "credits_per_use": about_api_details['credits_per_use']
                                                                },
                                            user_details={"user_name": user_name,
                                                        "user_type" :user_type})
                else:
                    return redirect("/dashboard")
                
        return redirect("/")
    
    return redirect("/")


# Random request id generate
def generate_random_id():
    return '-'.join(''.join(random.choices('0123456789abcdef', k=4)) for _ in range(5))

# Testing Apis
@Admin_Api_Uses_Name_Comparison_bp.route("/test-api",methods=["POST"])
def Name_compare_testing_api():
    if request.method == "POST":
        try:
            encrypted_token = session.get('QtSld')
            ip_address = session.get('KLpi')
            if session.get('bkjid') != "":

                check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})
                # User Check in DB
                if check_user_in_db != None:
                    # Check User Api Status
                    if check_user_in_db['api_status'] == "Enable":
                        # Check Credit Limit
                        if int(check_user_in_db["used_test_credits"]) > 0:
                            
                            # Api Start Time
                            start_time = datetime.utcnow()
                            # Name Match Function
                            Name_match_percantage = calculate_similarity(request.form['name1'],request.form['name2'])

                            # Api End Time
                            end_time = datetime.utcnow()
                            duration = (end_time - start_time).total_seconds() * 1000

                            # Client Ip address
                            response = requests.get('https://ifconfig.me')
                            
                            # Request Id
                            request_id = generate_random_id()

                            # name of api
                            about_api_details = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3b9ce1846511541497")})
                            http_status = 200

                            json_msg = {"data":{
                                "status_code": 200,
                                "status": "Success",
                                "response": {"match_percentage": Name_match_percantage},
                                "basic_response":{ "request_id" : request_id,
                                            "request_on" : start_time,
                                            "response_on":end_time,
                                            "api_name":about_api_details['api'],
                                            "duration":round(duration, 2),
                                            }
                                }}
                            
                            # Log store in db
                            Test_user_api_history_db.insert_one({
                                    # aadhaar redaction objid
                                    "api_name": about_api_details['_id'],
                                    # Enviroment Set
                                    'env':'Test',
                                    # ip address
                                    "ip_address":response.text.strip(),
                                    # user id
                                    "user_id":check_user_in_db['_id'],
                                    # Api call Status
                                    'api_call_status' : "Dashboard_status",
                                    # Request id
                                    "request_id" : request_id,
                                    # Unique id
                                    "unique_id":"Dashboard",
                                    # Request time
                                    "request_on" : start_time,
                                    # Response time
                                    "response_on":end_time,
                                    # Time Duration of api taken time
                                    "time_duration":round(duration, 2),
                                    # http status
                                    'http_status':http_status,
                                    # date store
                                    'created_on':datetime.now()})

                            # user Cut credits
                            if check_user_in_db['tester_flag'] == False:
                                if int(check_user_in_db['used_test_credits']) >=  int(about_api_details['credits_per_use']):
                                    # Reduce total credit to used credits
                                    update_total_credit = int(check_user_in_db['used_test_credits']) - int(about_api_details['credits_per_use'])
                                    User_Authentication_db.update_one({"_id":check_user_in_db["_id"]},{"$set":{
                                                    "used_test_credits":update_total_credit}})
                                    
                                    json_msg['data']['basic_response'] ['test_credits'] = update_total_credit

                                else:
                                    return jsonify({"data":{
                                                    "status_code": 402,
                                                    "status": "Error",
                                                    "response":"Not sufficient credit to use this API. Please contact our support team to purchase more credits!"
                                                }}), 402
                                
                            return jsonify(json_msg)
                    
                        else:
                            return jsonify({"data":{
                                    "status_code": 400,
                                    "status": "Error",
                                    "response":"You have zero credits left, please pay for more credits!"
                                }}), 400
                    else:
                        return redirect("/dashboard")
                            
            
            return jsonify({"data":{
                                    "status_code": 400,
                                    "status": "Error",
                                    "response":"Something went wrong!"
                                }}), 400
        
        except:
            return jsonify({"data":{
                                    "status_code": 400,
                                    "status": "Error",
                                    "response":"Something went wrong!"
                                }}), 400
        
    return jsonify({"data":{
                            "status_code": 405,
                            "status": "Error",
                            "response":"Request method not allowed. Please use the correct HTTP method."
                        }}), 405

