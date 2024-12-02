from flask import Blueprint, render_template,request,session
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import timedelta
from bleach import clean
import re
from bson import ObjectId
from datetime import datetime
import uuid
import cv2
import numpy as np
import base64,os
import pytesseract
import json

# tessract path
from tesseract_path import *

# DataBase
from data_base_string import *


# Headers Verification
from Headers_Verify import *


# Blueprint
Voter_Redaction_api_bp = Blueprint("Voter_Redaction_api_bp",
                        __name__,
                        url_prefix="/api/v1/",
                        template_folder="templates")


# DB
Authentication_db = Regtch_services_UAT["User_Authentication"]
User_test_Api_history_db = Regtch_services_UAT['User_test_Api_history']
Api_Informations_db = Regtch_services_UAT["Api_Informations"]


# User Unique Id pettern
UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)


@Voter_Redaction_api_bp.route("/voter-id/redact",methods=['POST'])
@jwt_required()
def Voter_redaction_Api_route():
    if request.method == 'POST':
        try:
            data = request.get_json()

            check_user = get_jwt()
            jwt_store_details = json.loads(check_user['sub'])


            # Json IS Empty Or Not
            if data == {}:
                return jsonify({"data" : {"status_code": 400,
                                        "status": "Error",
                                        "response":"Invalid or missing JSON data!"
                                        }}) , 400
            
            key_of_request = ['UniqueID','image']
            
            # Extra Key Remove
            extra_keys = [key for key in data if key not in key_of_request]
        
            if extra_keys:
                return jsonify({"data":{
                    "status_code": 400,
                    "status": "Error",
                    "response":"Please Validate Your Data!"
                }}), 400


            # HTML Injection & Also Verify Key is Empy Or Null
            injection_error = check_html_injection(data, key_of_request)
            if injection_error:
                return injection_error
            
            uuid_to_check = data['UniqueID']
            # Check if the UUID matches the pattern
            if UUID_PATTERN.match(uuid_to_check):

                modify_request_data = {
                    "UniqueID" : data["UniqueID"],
                    # "doc_type" : data["doc_type"],
                }
                
                # Api Calling Time Start
                api_call_start_time = datetime.now()
                
                check_user = get_jwt()

                check_user_id_in_db = Authentication_db.find_one({"_id":ObjectId(jwt_store_details['client_id'])})

                if check_user_id_in_db != None:
                    if int(check_user_id_in_db["used_test_credits"]) > 0:
                        
                        
                        # UniqueID Check in DB

                        # If Tester Flag is true So don't check unique Id
                        if check_user_id_in_db['tester_flag'] == True:
                            unique_id_check = None
                        else:
                            unique_id_check = User_test_Api_history_db.find_one({"user_id":check_user_id_in_db["_id"],"User_Unique_id":data["UniqueID"]})
                        
                        api_status = ""
                        
                        if unique_id_check == None:
                            try:
                                ocr_image = data['image'].split(',')[1]
                            except:
                                ocr_image = data['image']
                            
                            return jsonify({"data":{
                                            "status_code": 200,
                                            "status": "Success",
                                            "response":{"Image":"base64......."}
                                        }})
                        
                        else:
                            return jsonify({"data":{
                                        "status_code": 400,
                                        "status": "Error",
                                        "response":"This ID has already been used. Verify Your UniqueID and try again!"
                                    }}), 400

                else:
                    return jsonify({"data":{
                                "status_code": 400,
                                "status": "Error",
                                "response":"This ID has already been used. Verify Your UniqueID and try again!"
                            }}), 400
        except:
            return jsonify({"data":{
                        "status_code": 400,
                        "status": "Error",
                        "response":"Something went wrong!"
                    }}), 400

    else:
        return jsonify({"data":{
                        "status_code": 400,
                        "status": "Error",
                        "response":"Something went wrong!"
                    }}), 400

                        