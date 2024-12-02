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
import base64,requests
import json

# tessract path
from tesseract_path import *

# DataBase
from data_base_string import *


# Headers Verification
from Headers_Verify import *


# Blueprint
Image_Quality_Check_api_bp = Blueprint("Image_Quality_Check_api_bp",
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


# Image Quality Check Func
def quality_check_module(image_base64):
    # Decode the Base64 string to get the image
    image_data = base64.b64decode(image_base64)
    # Convert the byte data into a NumPy array
    np_arr = np.frombuffer(image_data, np.uint8)
    # Decode the NumPy array into an image
    image = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)

    resolution = ""
    Contrast_status = ""
    contrast_scrore = ""
    brightness_status = ""
    brightness_level = ""
    noise_level = ""
    noise_status = ""

    
    # Get the image dimensions (height, width)
    height, width = image.shape
    
    # Get image dimensions
    resolution = f"{width}x{height}"
    
    # Calculate the variance of the Laplacian(Sharpness)
    variance_of_laplacian = cv2.Laplacian(image, cv2.CV_64F).var()

    # Check brightness
    mean_brightness = np.mean(image)
    brightness_level = f"{mean_brightness:.2f}"
    if mean_brightness < 50:
        brightness_status = "Too Dark"
    elif mean_brightness > 200:
        brightness_status = "Overexposed"
    else:
        brightness_status = "Good"

    # Check contrast
    contrast = image.max() - image.min()
    contrast_scrore = f"{contrast:.2f}"
    if contrast < 200:  # Example threshold
        Contrast_status = "Poor"
    else:
        Contrast_status = "Good"

    # Check noise (standard deviation of Laplacian)
    noise = cv2.Laplacian(image, cv2.CV_64F).std()
    noise_level = f"{noise:.2f}"
    if noise > 15:  # Example threshold
        noise_status = "High Noise"
    else:
        noise_status = "Good"

    # Check file size (in KB)
    file_size_bytes = len(image_data)
    file_size_kb = file_size_bytes / 1024
    file_size_mb = file_size_kb / 1024
    
    
    if variance_of_laplacian < 100:
        return { 
            "Resolution" : resolution,
            "Sharpness":f"{variance_of_laplacian:.2f}",
            # "Contrast_status":Contrast_status,
            "Contrast_score":contrast_scrore,
            # "Brightness_status":brightness_status,
            "Brightness_level":brightness_level,            
            "Noise_level":noise_level,            
            # "Noise_status":noise_status, 
            "File_Size_KB" : f"{file_size_kb:.2f}",           
            "File_Size_MB" : f"{file_size_mb:.2f}",           
            "Overall_Quality": "Image quality is poor!"
        }
    else:
        return { 
            "Resolution" : resolution,
            "Sharpness":f"{variance_of_laplacian:.2f}",
            # "Contrast_status":Contrast_status,
            "Contrast_score":contrast_scrore,
            # "Brightness_status":brightness_status,
            "Brightness_level":brightness_level,            
            "Noise_level":noise_level,            
            # "Noise_status":noise_status, 
            "File_Size_KB" : file_size_kb,           
            "File_Size_MB" : file_size_mb, 
            "Overall_Quality": "Image quality is good!"
        }


@Image_Quality_Check_api_bp.route("/check/image_quality",methods=['POST'])
@jwt_required()
def Image_Quality_Check_Api_route():
    if request.method == 'POST':
        # try:
            data = request.get_json()

            # Json IS Empty Or Not
            if data == {}:
                return jsonify({"data" : {"status_code": 400,
                                    "status": "Error",
                                    "response":"Invalid or missing JSON data. Please ensure that the request contains valid JSON!"
                                    }}) , 400
            
            key_of_request = ['UniqueID','image','env']
            
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
                
                # Api Calling Time Start
                api_call_start_time = datetime.now()
                
                check_user = get_jwt()

                jwt_store_details = json.loads(check_user['sub'])

                check_user_id_in_db = Authentication_db.find_one({"_id":ObjectId(jwt_store_details['client_id'])})

                if check_user_id_in_db != None:
                    # name of api
                    about_api_details = Api_Informations_db.find_one({"_id":ObjectId("674aff0526c34dbd8e5ba956")})

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
                                        # image in Base64 String 
                                        base64_string = data['image']

                                        if base64_string != "":
                                            
                                            if base64_string.startswith(('data:image/jpeg;base64,', 'data:image/png;base64,')):
                                                base64_string = base64_string.split(',', 1)[1]

                                            image_quality_module = quality_check_module(base64_string)

                                            # Api End Time
                                            end_time = datetime.utcnow()
                                            duration = (end_time - start_time).total_seconds() * 1000

                                            # Client Ip address
                                            response = requests.get('https://ifconfig.me')
                                            
                                            # Request Id
                                            request_id = generate_random_id()

                                            http_status = 200

                                            json_msg = {"data":{
                                                "status_code": 200,
                                                "status": "Success",
                                                "response": image_quality_module,
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
                                                    "user_id":check_user_id_in_db['_id'],
                                                    # Api call Status
                                                    'api_call_status' : "Api_status",
                                                    # Request id
                                                    "request_id" : request_id,
                                                    # Unique id
                                                    "unique_id":data["UniqueID"],
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
                                            if check_user_id_in_db['tester_flag'] == False:
                                                if int(check_user_id_in_db['used_test_credits']) >=  int(about_api_details['credits_per_use']):
                                                    # Reduce total credit to used credits
                                                    update_total_credit = int(check_user_id_in_db['used_test_credits']) - int(about_api_details['credits_per_use'])
                                                    Authentication_db.update_one({"_id":check_user_id_in_db["_id"]},{"$set":{
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

                                # UniqueID Check in DB
                                unique_id_check = Prod_user_api_history_db.find_one({"user_id":check_user_id_in_db["_id"],
                                                                                     "unique_id":data["UniqueID"]})
                                if unique_id_check == None:
                                    # image in Base64 String 
                                        base64_string = data['image']

                                        if base64_string != "":
                                            
                                            if base64_string.startswith(('data:image/jpeg;base64,', 'data:image/png;base64,')):
                                                base64_string = base64_string.split(',', 1)[1]

                                            image_quality_module = quality_check_module(base64_string)

                                            # Api End Time
                                            end_time = datetime.utcnow()
                                            duration = (end_time - start_time).total_seconds() * 1000

                                            # Client Ip address
                                            response = requests.get('https://ifconfig.me')
                                            
                                            # Request Id
                                            request_id = generate_random_id()

                                            http_status = 200

                                            json_msg = {"data":{
                                                "status_code": 200,
                                                "status": "Success",
                                                "response": image_quality_module,
                                                "basic_response":{ "request_id" : request_id,
                                                            "request_on" : start_time,
                                                            "response_on":end_time,
                                                            "api_name":about_api_details['api'],
                                                            "duration":round(duration, 2),
                                                            }
                                                }}
                                            
                                            # Log store in db
                                            Prod_user_api_history_db.insert_one({
                                                    # aadhaar redaction objid
                                                    "api_name": about_api_details['_id'],
                                                    # Enviroment Set
                                                    'env':'Test',
                                                    # ip address
                                                    "ip_address":response.text.strip(),
                                                    # user id
                                                    "user_id":check_user_id_in_db['_id'],
                                                    # Api call Status
                                                    'api_call_status' : "Api_status",
                                                    # Request id
                                                    "request_id" : request_id,
                                                    # Unique id
                                                    "unique_id":data["UniqueID"],
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

                                            return jsonify(json_msg)
                                else:
                                    return jsonify({"data":{
                                                "status_code": 409,
                                                "status": "Error",
                                                "response":"This ID has already been used. Verify Your UniqueID and try again!"
                                            }}), 409

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
            

        # except:
        #     return jsonify({"data":{
        #                 "status_code": 400,
        #                 "status": "Error",
        #                 "response":"Something went wrong!"
        #             }}), 400
        
    else:
        return jsonify({"data":{
                        "status_code": 400,
                        "status": "Error",
                        "response":"Something went wrong!"
                    }}), 400
        
