from flask import Blueprint, render_template,request,session,redirect
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta
from bson import ObjectId
import random
from PIL import Image
import numpy as np
from PIL import Image
import re , os ,io
import base64
import time
from werkzeug.utils import secure_filename
import requests
from ultralytics import YOLO


model = YOLO("apps/AI_models/kyc_check_model.pt")

# DataBase
from data_base_string import *

# Token
from token_generation import *

# Blueprint
Document_validation_bp = Blueprint("Document_validation_bp",
                        __name__,
                        url_prefix="/document",
                        template_folder="templates")


User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
Api_Informations_db = Regtch_services_UAT["Api_Informations"]
Prod_user_api_history_db = Regtch_services_UAT['Prod_user_api_history']
Test_user_api_history_db = Regtch_services_UAT['Test_user_api_history']



@Document_validation_bp.route("/validation")
def Document_validation_main():

    encrypted_token = session.get('QtSld')
    ip_address = session.get('KLpi')

    if session.get('bkjid') != "":

        check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})

        if check_user_in_db != None:

            if encrypted_token and ip_address:

                # Check User Api Status
                if check_user_in_db['api_status'] == "Enable":
                    token = decrypt_token(encrypted_token)

                    page_name = "Document Validation"

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

                    about_api_details = Api_Informations_db.find_one({"_id":ObjectId("675a6952011e13d17cd074a6")})


                    return render_template("document_valid_module.html",
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


# Testing Apis
@Document_validation_bp.route("/valid/test-api",methods=["POST"])
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

                            doc_valid_input = request.files['doc_valid_input']
                            if doc_valid_input.filename == '':
                                return jsonify({"data":{
                                        "status_code": 400,
                                        "status": "Error",
                                        "response":"Please select file!"
                                    }}), 400
                            
                            if doc_valid_input and allowed_file(doc_valid_input):

                                img_bytes = doc_valid_input.read()  # Read the image file as bytes
                                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                                img_decoded = base64.b64decode(img_base64)

                                # Image Open
                                image = Image.open(io.BytesIO(img_decoded))
                                # File save
                                filename_img = str(time.time()).replace(".", "")
                                static_file_name = filename_img+".png"
                                image.save(os.path.join('apps/static/Document_validation/Document_validation_inputs', secure_filename(static_file_name)))
        
                                store_image = "apps/static/Document_validation/Document_validation_inputs/" +static_file_name

                                # Ai Modal
                                # Run inference using the YOLO model
                                results = model(store_image)

                                # Extract the boxes, confidence scores, and classes
                                boxes = results[0].boxes
                                best_label = None
                                max_combined_score = -1
                                for box in boxes:
                                    x1, y1, x2, y2 = box.xyxy[0]  # Bounding box coordinates
                                    area = (x2 - x1) * (y2 - y1)  # Compute area
                                    confidence = box.conf.item()  # Confidence score
                                    print("----------------",confidence)
                                    print("----------------",int(box.cls))
                                    combined_score = area * confidence  # Combined score (area * confidence)

                                    if combined_score > max_combined_score:
                                        max_combined_score = combined_score
                                        best_label = {
                                            "class": int(box.cls),
                                            "confidence": confidence * 100,  # Multiply by 100 for percentage
                                        }

                                # If best label is found, return the result
                                print("**** ", best_label)
                                if best_label:

                                    if best_label['confidence'] < 80:
                                      doc_vaild_json =  {
                                        'detected_doc_type': "unknown",
                                        'confidence': best_label['confidence']
                                    }
                                    
                                    elif best_label['class'] == 0:
                                        doc_vaild_json = {
                                        'detected_doc_type': "aadhaar_card",
                                        'confidence': best_label['confidence']
                                    }
                                    elif best_label['class'] == 1:
                                        doc_vaild_json = {
                                        'detected_doc_type': "pan_card",
                                        'confidence': best_label['confidence']
                                    }
                                    elif best_label['class'] == 2:
                                        doc_vaild_json = {
                                        'detected_doc_type': "voter_id_card",
                                        'confidence': best_label['confidence']
                                    }
                                    else:
                                        doc_vaild_json = {
                                        'detected_doc_type': "",
                                    }
                                else:
                                        doc_vaild_json = {
                                        'detected_doc_type': "unknown",
                                    }

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
                                about_api_details = Api_Informations_db.find_one({"_id":ObjectId("675a6952011e13d17cd074a6")})

                                http_status = 200


                                json_msg = {"data":{
                                    "status_code": 200,
                                    "status": "Success",
                                    "response": doc_vaild_json,
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