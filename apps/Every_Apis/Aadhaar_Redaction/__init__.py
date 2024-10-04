
from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import timedelta
from bleach import clean
import re
from bson import ObjectId
from datetime import datetime
import uuid
import cv2
import numpy as np
import base64,os , io , time
import pytesseract
from werkzeug.utils import secure_filename
from PIL import Image


# Aadhaar Masking Module
from apps.Every_Apis.Aadhaar_Redaction.Aadhaar_Redaction_Module import *

# DataBase
from data_base_string import *


# Headers Verification
from Headers_Verify import *


# Blueprint
Aadhaar_Redaction_api_bp = Blueprint("Aadhaar_Redaction_api_bp",
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



@Aadhaar_Redaction_api_bp.route("/aadhaar/masking",methods=['POST'])
@jwt_required()
#@check_headers
def Aadhaar_Redaction_Api_route():
    if request.method == 'POST':
        # try:
            data = request.get_json()

            # Json IS Empty Or Not
            if data == {}:
                return jsonify({"data" : {"status_code": 400,
                                        "status": "Error",
                                        "response":"Invalid or missing JSON data!"
                                        }}) , 400
            
            key_of_request = ['UniqueID','addhar_img']
            
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
            

            # Check Unique Id

            uuid_to_check = data['UniqueID']
            # Check if the UUID matches the pattern
            if UUID_PATTERN.match(uuid_to_check):

                modify_request_data = {
                    "UniqueID" : data["UniqueID"],
                }
                
                # Api Calling Time Start
                api_call_start_time = datetime.now()
                
                check_user = get_jwt()

                check_user_id_in_db = Authentication_db.find_one({"_id":ObjectId(check_user['sub']['client_id'])})

                if check_user_id_in_db != None:
                    if check_user_id_in_db["total_test_credits"] > check_user_id_in_db["used_test_credits"]:
                        
                        # UniqueID Check in DB
                        unique_id_check = User_test_Api_history_db.find_one({"user_id":check_user_id_in_db["_id"],"User_Unique_id":data["UniqueID"]})

                        if unique_id_check == None:
                            base64_string = data['addhar_img']
                            
                            if base64_string.startswith('data:image/jpeg;base64,'):
                                base64_string = base64_string.replace('data:image/jpeg;base64,', '')

                            image_bytes = base64.b64decode(base64_string)
                            image = Image.open(io.BytesIO(image_bytes))

                            filename_img = str(time.time()).replace(".", "")

                            static_file_name = filename_img+".png"
                            image.save(os.path.join('apps/static/Aadhaar_Masking/Aadhaar_Masking_Inputs', secure_filename(static_file_name)))
                            
                            store_image = "apps/static/Aadhaar_Masking/Aadhaar_Masking_Inputs/" +static_file_name

                            modify_request_data["addhar_img"] = store_image

                            # Addhar Image Masking Function
                            addhar_response = addhar_mask(store_image,SR=True, SR_Ratio=[1.5, 1.5])
                            

                            api_call_end_time = datetime.now()
                            duration = api_call_end_time - api_call_start_time
                            duration_seconds = duration.total_seconds()
                            store_response = {
                                            "status_code": 200,
                                            "status": "Success",
                                            "response": {"Image": 
                                                         addhar_response["base64_string"]}}
                            
                            # DataBase Log
                            User_test_Api_history_db.insert_one({
                                    "user_id":check_user_id_in_db["_id"],
                                    "User_Unique_id":data['UniqueID'],
                                    "api_name":"Aadhaar_Redaction",
                                    "api_start_time":api_call_start_time,
                                    "api_end_time":datetime.now(),
                                    "api_status": "Success",
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "request_data":str(modify_request_data),
                                    "response_data" :str(store_response),
                                    "creadted_on":datetime.now(),
                                    "System_Generated_Unique_id" : str(uuid.uuid4()),
                                    })

                            # Check Api Using Credits
                            api_use_credit_info = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3a9ce1846511541492")})
                            
                            if check_user_id_in_db["unlimited_test_credits"] == False:
                                # Credit 
                                Authentication_db.update_one({"_id":check_user_id_in_db["_id"]},{"$set":{
                                    "used_test_credits": check_user_id_in_db["used_test_credits"] + api_use_credit_info["credits_per_use"]
                                }})
                            
                            return jsonify({"data":store_response})

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
                                "response":"You have zero credits left, please pay for more credits!"
                            }}), 400
                    
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
            

    #     except:
    #         return jsonify({"data":{
    #                     "status_code": 400,
    #                     "status": "Error",
    #                     "response":"Something went wrong!"
    #                 }}), 400
        
    # else:
    #     return jsonify({"data":{
    #                     "status_code": 400,
    #                     "status": "Error",
    #                     "response":"Something went wrong!"
    #                 }}), 400
        
