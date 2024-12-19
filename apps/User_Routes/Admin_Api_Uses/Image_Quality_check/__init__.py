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
from PIL import Image
import re , os ,io
import base64
from io import BytesIO
import shutil , time
from werkzeug.utils import secure_filename
import requests


# DataBase
from data_base_string import *

# Token
from token_generation import *

# Blueprint
Image_Quality_check_bp = Blueprint("Image_Quality_check_bp",
                        __name__,
                        url_prefix="/image_quality",
                        template_folder="templates")


User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
Api_Informations_db = Regtch_services_UAT["Api_Informations"]
Prod_user_api_history_db = Regtch_services_UAT['Prod_user_api_history']
Test_user_api_history_db = Regtch_services_UAT['Test_user_api_history']




@Image_Quality_check_bp.route("/check")
def Image_quality_check_main():

    encrypted_token = session.get('QtSld')
    ip_address = session.get('KLpi')

    if session.get('bkjid') != "":

        check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})

        if check_user_in_db != None:

            if encrypted_token and ip_address:

                # Check User Api Status
                if check_user_in_db['api_status'] == "Enable":
                    token = decrypt_token(encrypted_token)

                    page_name = "Image Quality Check"

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

                    about_api_details = Api_Informations_db.find_one({"_id":ObjectId("674aff0526c34dbd8e5ba956")})


                    return render_template("image_quality_check_module.html",
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


# Random request id generate
def generate_random_id():
    return '-'.join(''.join(random.choices('0123456789abcdef', k=4)) for _ in range(5))


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
    sharpness_score = ""

    
    # Get the image dimensions (height, width)
    height, width = image.shape
    
    # Get image dimensions
    resolution = f"{width}x{height}"
    
    # Calculate the variance of the Laplacian(Sharpness)
    variance_of_laplacian = cv2.Laplacian(image, cv2.CV_64F).var()
    sharpness_score = variance_of_laplacian

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

    # Confidence Score Calculation
    weights = {
        "sharpness": 0.4,  # Sharpness is 40% of the score
        "brightness": 0.2,  # Brightness is 20%
        "contrast": 0.3,  # Contrast is 30%
        "noise": 0.1       # Noise is 10%
    }


    # Normalize each metric (set ranges based on example thresholds)
    sharpness_norm = min(1, max(0, (sharpness_score - 50) / (200 - 50)))  # Normalize sharpness
    brightness_norm = min(1, max(0, (mean_brightness - 50) / (200 - 50)))  # Normalize brightness
    contrast_norm = min(1, max(0, (contrast - 50) / (255 - 50)))  # Normalize contrast
    noise_norm = 1 - min(1, max(0, (noise - 5) / (20 - 5)))  # Inverse normalization for noise

    # Calculate confidence score
    confidence_score = (
        weights["sharpness"] * sharpness_norm +
        weights["brightness"] * brightness_norm +
        weights["contrast"] * contrast_norm +
        weights["noise"] * noise_norm
    ) * 100  # Convert to percentage

    # Determine overall quality verdict
    quality_verdict = "Good" if confidence_score > 75 else "Average" if confidence_score > 50 else "Poor"
    
    
    if variance_of_laplacian < 100:
        return [
            {
                "score" : resolution,
                "type" : "Resolution",
                "flag" : True,
            },
            {
                "score" : f"{variance_of_laplacian:.2f}",
                "flag":"Law",
                "type" : "Sharpness",
            },
            {
                "score" : contrast_scrore,
                "flag":Contrast_status,
                "type" : "Contrast",
            },
            {
                "score" : brightness_level,
                "flag":brightness_status,
                "type" : "Brightness",
            },
            {
                "score" : noise_level,
                "flag":noise_status,
                "type" : "Noise Level",
            },
            {
                "score" : f"{confidence_score:.2f}",
                "type" : "Overall Quality",
                "flag" : "Fail"
            },
        ]
    else:
        # return { 
        #     "Resolution" : resolution,
        #     "Sharpness":f"{variance_of_laplacian:.2f}",
        #     # "Contrast_status":Contrast_status,
        #     "Contrast_score":contrast_scrore,
        #     # "Brightness_status":brightness_status,
        #     "Brightness_level":brightness_level,            
        #     "Noise_level":noise_level,     
        #     "Confidence Score (%)": f"{confidence_score:.2f}",       
        #     # "Noise_status":noise_status, 
        #     # "File_Size_KB" : file_size_kb,           
        #     # "File_Size_MB" : file_size_mb, 
        #     "Overall_Quality": "Image quality is good!"
        # }

        return [
            {
                "score" : resolution,
                "type" : "Resolution",
                "flag" : True,
            },
            {
                "score" : f"{variance_of_laplacian:.2f}",
                "flag":"High",
                "type" : "Sharpness",
            },
            {
                "score" : contrast_scrore,
                "flag":Contrast_status,
                "type" : "Contrast",
            },
            {
                "score" : brightness_level,
                "flag":brightness_status,
                "type" : "Brightness",
            },
            {
                "score" : noise_level,
                "flag":noise_status,
                "type" : "Noise Level",
            },
            {
                "score" : f"{confidence_score:.2f}",
                "type" : "Overall Quality",
                "flag" : "Pass",
            }        ]



# Testing Apis
@Image_Quality_check_bp.route("/checks/test-api",methods=["POST"])
def Image_Quality_api_test():
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

                            image_quality_img = request.files['image_quality_img']
                            if image_quality_img.filename == '':
                                return jsonify({"data":{
                                        "status_code": 400,
                                        "status": "Error",
                                        "response":"Please select file!"
                                    }}), 400
                            
                            if image_quality_img and allowed_file(image_quality_img):

                                img_bytes = image_quality_img.read()  # Read the image file as bytes
                                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                                img_decoded = base64.b64decode(img_base64)

                                # Image Open
                                image = Image.open(io.BytesIO(img_decoded))
                                # File save
                                filename_img = str(time.time()).replace(".", "")
                                static_file_name = filename_img+".png"
                                image.save(os.path.join('apps/static/KYC_Quality/KYC_Quality_inputs', secure_filename(static_file_name)))
        
                                store_image = "apps/static/KYC_Quality/KYC_Quality_inputs/" +static_file_name

                                with open(store_image, "rb") as image_file:
                                    # Read image as binary and encode in Base64
                                    base64_string = base64.b64encode(image_file.read()).decode('utf-8')

                                image_quality_res = quality_check_module(base64_string)

                                # Api End Time
                                end_time = datetime.utcnow()
                                duration = (end_time - start_time).total_seconds() * 1000

                                # Remove File
                                os.remove(store_image)

                                # Client Ip address
                                response = requests.get('https://ifconfig.me')
                                
                                # Request Id
                                request_id = generate_random_id()

                                # name of api
                                about_api_details = Api_Informations_db.find_one({"_id":ObjectId("674aff0526c34dbd8e5ba956")})

                                http_status = 200

                                json_msg = {"data":{
                                    "status_code": 200,
                                    "status": "Success",
                                    "response": image_quality_res,
                                    "basic_response":{ "request_id" : request_id,
                                                "request_on" : start_time,
                                                "response_on":end_time,
                                                "api_name":str(about_api_details['api']),
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
                                        "response":"Invalid file format. Only JPG and PNG are allowed!"
                                    }}), 400
                                
        
                        else:
                            return jsonify({"data":{
                                    "status_code": 400,
                                    "status": "Error",
                                    "response":"You have zero credits left, please pay for more credits!"
                                }}), 400
                        
                    else:
                        return redirect("/dashboard")
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