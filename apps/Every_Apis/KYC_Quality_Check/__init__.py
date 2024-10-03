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
import base64,os
import pytesseract


# DataBase
from data_base_string import *


# Headers Verification
from Headers_Verify import *


# Blueprint
KYC_Quality_Check_api_bp = Blueprint("KYC_Quality_Check_api_bp",
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

# Tesseract exe path local
# try:
#     os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'
#     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# except:
#     # Linux Server
#     os.environ['TESSDATA_PREFIX'] = '/usr/local/share/tessdata/'
#     pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' 


os.environ['TESSDATA_PREFIX'] = '/usr/local/share/tessdata/'
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' 
    

def quality_check_module(image_base64):
    # Decode the Base64 string to get the image
    image_data = base64.b64decode(image_base64)
    # Convert the byte data into a NumPy array
    np_arr = np.frombuffer(image_data, np.uint8)
    # Decode the NumPy array into an image
    image = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
    
    # Get the image dimensions (height, width)
    height, width = image.shape
    
    # Calculate the variance of the Laplacian
    variance_of_laplacian = cv2.Laplacian(image, cv2.CV_64F).var()
    
    if variance_of_laplacian < 100:
        return { 
            "Width": width,
            "Height": height,
            "Message": "Image quality is poor"
        }
    else:
        return { 
            "Width": width,
            "Height": height,
            "Message": "Image quality is good!"
        }

# Function to decode base64 image
def decode_base64_image(image_base64):
    image_data = base64.b64decode(image_base64)
    np_arr = np.frombuffer(image_data, np.uint8)
    image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    return image

# Function to check if an image is a KYC document
def is_kyc_document(image_base64):
    # Decode the base64 image
    image = decode_base64_image(image_base64)
    
    # Convert image to grayscale for OCR
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Use OCR to extract text
    extracted_text = pytesseract.image_to_string(gray_image)
    
    # Convert extracted text to lowercase for uniformity
    extracted_text_lower = extracted_text.lower()

    # Define patterns or keywords for various KYC documents
    kyc_patterns = [
        r'\baadhaar\b',           # Aadhaar card
        r'\bpan\b',               # PAN card
        r'\bpassport\b',          # Passport
        r'\bvoter id\b',          # Voter ID
        r'\bdriving license\b',   # Driving License
        r'\buidai\b',             # Unique Identification Authority of India (for Aadhaar)
        r'\bincome tax\b',        # Income Tax (for PAN)
    ]
    
    # Check if any pattern matches the extracted text
    for pattern in kyc_patterns:
        if re.search(pattern, extracted_text_lower):
            return {
                "is_kyc_document": True,
                "document_type": pattern
            }
    
    # If no pattern matches, it's not a KYC document
    return {
        "is_kyc_document": False,
        "message": "No KYC-related text found in the image"
    }


@KYC_Quality_Check_api_bp.route("/image/imagequality",methods=['POST'])
@jwt_required()
@check_headers
def KYC_Quality_Check_Api_route():
    if request.method == 'POST':
        try:
            data = request.get_json()

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
                    if check_user_id_in_db["total_test_credits"] >= check_user_id_in_db["used_test_credits"]:
                        
                        # UniqueID Check in DB
                        unique_id_check = User_test_Api_history_db.find_one({"user_id":check_user_id_in_db["_id"],"User_Unique_id":data["UniqueID"]})

                        if unique_id_check == None:
                            image_quality_module = quality_check_module(data["image"])


                            api_call_end_time = datetime.now()
                            duration = api_call_end_time - api_call_start_time
                            duration_seconds = duration.total_seconds()
                            store_response = {
                                            "status_code": 200,
                                            "status": "Success",
                                            "response": image_quality_module}
                            
                            # DataBase Log
                            User_test_Api_history_db.insert_one({
                                    "user_id":check_user_id_in_db["_id"],
                                    "User_Unique_id":data['UniqueID'],
                                    "api_name":"KYC_Image_Quality",
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
                            api_use_credit_info = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3b9ce1846511541499")})
                            
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
        
