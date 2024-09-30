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


# DataBase
from data_base_string import *

# Token
from token_generation import *

# Blueprint
KYC_Quality_check_bp = Blueprint("KYC_Quality_check_bp",
                        __name__,
                        url_prefix="/quality",
                        template_folder="templates")


User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
User_test_Api_history_db = Regtch_services_UAT['User_test_Api_history']
Api_Informations_db = Regtch_services_UAT["Api_Informations"]




@KYC_Quality_check_bp.route("/check")
def KYC_quality_main():

    encrypted_token = session.get('QtSld')
    ip_address = session.get('KLpi')

    if session.get('bkjid') != "":

        check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})

        if check_user_in_db != None:

            if encrypted_token and ip_address:
                token = decrypt_token(encrypted_token)

                user_name = check_user_in_db["Company_Name"]
                test_credits = [{"Test_Credit": check_user_in_db["total_test_credits"],
                                 "Used_Credits":check_user_in_db["used_test_credits"]}]




                return render_template("kyc_quality_check_module.html",
                                    test_credit=test_credits ,
                                    user_name=user_name )
    
    return redirect("/")


# Random request id generate
def generate_random_id():
    return '-'.join(''.join(random.choices('0123456789abcdef', k=4)) for _ in range(5))



def quality_check_module(image_path):

    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    # Get the image dimensions (height, width)
    height, width = image.shape

    variance_of_laplacian = cv2.Laplacian(image, cv2.CV_64F).var()

    if variance_of_laplacian < 100:
        return { "Width":width,
                "Height":height,
                "Message": "Image quality is poor"}
    else:
        return { "Width":width,
                "Height":height,
                "Message": "Image quality is good!"}
    



# Testing Apis
@KYC_Quality_check_bp.route("/kyc/test-api",methods=["POST"])
def Aadhaar_redaction_api_test():
    if request.method == "POST":
        completed_on_ = datetime.now()
        completed_on = datetime.now(pytz.timezone('Asia/Kolkata'))
        completed_on = completed_on.strftime('%Y-%m-%dT%H:%M:%S%z')
        completed_on = completed_on[:-2] + ':' + completed_on[-2:]
        

        kyc_quality_img = request.files['kyc_quality_img']
        # Convert image to Base64
        img_bytes = kyc_quality_img.read()  # Read the image file as bytes
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        img_decoded = base64.b64decode(img_base64)

        image = Image.open(io.BytesIO(img_decoded))

        filename_img = str(time.time()).replace(".", "")

        static_file_name = filename_img+".png"
        image.save(os.path.join('apps/static/KYC_Quality/KYC_Quality_inputs', secure_filename(static_file_name)))
        
        store_image = "apps/static/KYC_Quality/KYC_Quality_inputs/" +static_file_name


        aadhaar_Red_res = quality_check_module(store_image)      

        created_on = datetime.now(pytz.timezone('Asia/Kolkata'))
        created_on = created_on.strftime('%Y-%m-%dT%H:%M:%S%z')
        created_on = created_on[:-2] + ':' + created_on[-2:]


        duration = datetime.now()- completed_on_ 
        duration_seconds = duration.total_seconds()

        store_response = {"response": 200,
                            "status": "Success",
                            "responseValue":aadhaar_Red_res,
                            "created_on" : created_on,
                            "completed_on":completed_on,
                            "request_id":generate_random_id(),
                            }


        return jsonify({"data":
                        {"json_data": store_response,
                         "result_in_seconds":duration_seconds}})
    
    return jsonify({"msg":"method Not allowed!"})
