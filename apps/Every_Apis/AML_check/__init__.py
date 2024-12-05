from flask import Blueprint, render_template,request,session
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import timedelta
from bleach import clean
from bson import ObjectId
from datetime import datetime
import numpy as np
import re , json , requests

# tessract path
from tesseract_path import *

# DataBase
from data_base_string import *


# Headers Verification
from Headers_Verify import *


# Blueprint
AML_check_api_bp = Blueprint("AML_check_api_bp",
                        __name__,
                        url_prefix="/api/v1/",
                        template_folder="templates")

# DB
Authentication_db = Regtch_services_UAT["User_Authentication"]
Api_Informations_db = Regtch_services_UAT["Api_Informations"]
Prod_user_api_history_db = Regtch_services_UAT['Prod_user_api_history']
Test_user_api_history_db = Regtch_services_UAT['Test_user_api_history']



# User Unique Id pettern
UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)

@AML_check_api_bp.route("/AML/check",methods=['POST'])
@jwt_required()
def AML_check_Api_route():
    if request.method == 'POST':
        try:
            data = request.get_json()

            # Json IS Empty Or Not
            if data == {}:
                return jsonify({"data" : {"status_code": 400,
                                    "status": "Error",
                                    "response":"Invalid or missing JSON data. Please ensure that the request contains valid JSON!"
                                    }}) , 400
            
            key_of_request = ['UniqueID','first_name','last_name','dob','nationality','env']
            
            # Extra Key Remove
            extra_keys = [key for key in data if key not in key_of_request]

            if extra_keys:
                return jsonify({"data":{
                        "status_code": 400,
                        "status": "Error",
                        "response":"Please validate your data. Some fields are missing or incorrect!"
                    }}), 400
            
            # HTML Injection & Also Verify Key is Empy Or Null
            injection_error = check_html_injection(data, key_of_request)
            if injection_error:
                return injection_error
            

            # Check Unique Id

            uuid_to_check = data['UniqueID']
            # Check if the UUID matches the pattern
            if UUID_PATTERN.match(uuid_to_check):

                check_user = get_jwt()
                print("-------- ", check_user['sub'])
                jwt_store_details = json.loads(check_user['sub'])

                check_user_id_in_db = Authentication_db.find_one({"_id":ObjectId(jwt_store_details['client_id'])})

                if check_user_id_in_db != None:
                    # Check Env with db
                    if data['env'].lower() in check_user_id_in_db['user_type'].lower():
                        # Test Enviroment 
                        if data['env'] == "test":
                            # Check User Api Status
                            if check_user_id_in_db['api_status'] == "Enable":
                            #     # Check Credit Limit
                                if int(check_user_id_in_db["used_test_credits"]) > 0:
                                    # Api Start Time
                                    start_time = datetime.utcnow()

                                    # UniqueID Check in DB
                                    unique_id_check = Test_user_api_history_db.find_one({"user_id":check_user_id_in_db["_id"],
                                                                                         "unique_id":data["UniqueID"]})

                                    if unique_id_check == None or check_user_id_in_db['tester_flag'] ==  True:
                                        # Api End Time
                                        end_time = datetime.utcnow()
                                        duration = (end_time - start_time).total_seconds() * 1000

                                        # Client Ip address
                                        response = requests.get('https://ifconfig.me')
                                        
                                        # Request Id
                                        request_id = generate_random_id()

                                        json_msg = {"data":{
                                                        "status_code": 200,
                                                        "status": "Success",
                                                        "response": {"message": "Check completed successfully.",
                                                                    "result": "Match Found",
                                                                    "riskScore": 85,},
                                                        "basic_response":{ "request_id" : request_id,
                                                                    "request_on" : start_time,
                                                                    "response_on":end_time,
                                                                    "api_name":"AML_check",
                                                                    "duration":round(duration, 2),
                                                                    }
                                                        }}
                                        
                                        return jsonify(json_msg)                                    
                                    else:
                                        return jsonify({"data":{
                                                    "status_code": 409,
                                                    "status": "Error",
                                                    "response":"This ID has already been used. Verify Your UniqueID and try again!"
                                                }}), 409
                            
                                else:
                                    return jsonify({"data":{
                                            "status_code": 402,
                                            "status": "Error",
                                            "response":"You have zero credits left, please pay for more credits to continue using this service!"
                                        }}), 402
                            else:
                                return jsonify({"data":{
                                            "status_code": 403,
                                            "status": "Error",
                                            "response":"You are not eligible for this API. Please contact support for access!"
                                        }}), 403
                        
                        else:

                            # Check User Api Status
                            if check_user_id_in_db['api_status'] == "Enable":
                                # Api Start Time
                                start_time = datetime.utcnow()

                                # Api End Time
                                end_time = datetime.utcnow()
                                duration = (end_time - start_time).total_seconds() * 1000

                                # Client Ip address
                                response = requests.get('https://ifconfig.me')
                                
                                # Request Id
                                request_id = generate_random_id()

                                json_msg = {"data":{
                                                "status_code": 200,
                                                "status": "Success",
                                                "response": {"message": "Check completed successfully.",
                                                            "result": "Match Found",
                                                            "riskScore": 85,},
                                                "basic_response":{ "request_id" : request_id,
                                                            "request_on" : start_time,
                                                            "response_on":end_time,
                                                            "api_name":"AML_check",
                                                            "duration":round(duration, 2),
                                                            }
                                                }}
                                
                                return jsonify(json_msg)
                            

                    else:
                        return jsonify({"data":{
                                    "status_code": 500,
                                    "status": "Error",
                                    "response":"Please check your environment configuration and ensure all required settings are properly define!"
                                }}), 500
                else:
                    return jsonify({"data":{
                        "status_code": 400,
                        "status": "Error",
                        "response":"Invalid user, Please Register Your User!"
                    }}), 400
                
            else:
                return jsonify({"data":{
                        "status_code": 400,
                        "status": "Error",
                        "response":"Error! Please Validate the UniqueID format!"
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