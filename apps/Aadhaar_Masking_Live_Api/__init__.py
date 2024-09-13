
from flask import Blueprint, request, jsonify
import cv2
import numpy as np
import regex as re
from PIL import Image
import pytesseract
import os
from werkzeug.utils import secure_filename
import time
import base64,io
from flask_jwt_extended import  jwt_required
from data_base_string import *
from datetime import datetime
import random
import string , json
import tempfile , subprocess
from apps.Aadhaar_Masking_Live_Api.addhar_masking_module import *

# Blueprint
Aadhaar_Masking_Api_bp = Blueprint("Aadhaar_Masking_Api_bp",
                        __name__,
                        url_prefix="/",
                        static_folder='static')

# Tesseract exe path

# try:
#     pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# except:
#     os.environ['TESSDATA_PREFIX'] = '/usr/local/share/tessdata/'
#     pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'


# # Database
Api_request_history_db = Regtch_services_UAT["Api_Request_History"]
Login_db = Regtch_services_UAT["Login_db"]



@Aadhaar_Masking_Api_bp.route('/api/v1/aadhaar/masking',methods=['POST'])
@jwt_required()
def addhar_masking_main():
    if request.method == 'POST':
        try:
            data = request.get_json()
            if data == {}:
                return jsonify({
                    "response": "400",
                    "message": "Error",
                    "responseValue":"Invalid or missing JSON data!"
                    }) , 400
            
            keys_to_check = ['UniqueID', 'addhar_img',"CorporateID"]

            
            for key in keys_to_check:
                if key not in data or not data[key]:
                    # UniqueID Check 
                    store_response = {"response": 400,
                            "message": "Error",
                            "responseValue": key +" cannot be null or empty."
                        }
                    return jsonify(store_response), 400
                    
            
            
            api_call_start_time = datetime.now()
            modify_request_data = {}
            modify_request_data["UniqueID"] = data["UniqueID"]

            if len(data['UniqueID']) > 40:
                return jsonify({
                        "response": "400",
                        "message": "Error",
                        "responseValue":"Maximum Length Of UniqueID is 40 Character!"
                        }) , 400
            
            verify_corporate_id =  Login_db.find_one({"corporate_id":data["CorporateID"]})

            if verify_corporate_id == None:
                return jsonify({
                    "response": "400",
                    "message": "Error",
                    "responseValue":"The corporate ID entered is invalid! Please check the ID and try again!"
                    }) , 400
            else:
                modify_request_data["CorporateID"] = data["CorporateID"]

            # # ## Check UniqueID
            check_log_db = Api_request_history_db.find_one({"unique_id":data['UniqueID']})


            if check_log_db == None:

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
                

                # Response Check 
                if addhar_response['response'] == "200":
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()

                    image = Image.open(addhar_response['Image_path'])

                    filename_img = str(time.time()).replace(".", "")
                    new_static_file_name = filename_img+".png"
                    image.save(os.path.join('apps/static/Aadhaar_Masking/Aadhaar_Masking_Outputs', secure_filename(new_static_file_name)),
                               format='JPEG',
                                quality=85)

                    store_response_database = {"response": "200",
                                                "message": "Success",
                                                "responseValue": "apps/static/Aadhaar_Masking/Aadhaar_Masking_Outputs/"+ new_static_file_name
                                                }
                    

                    Api_request_history_db.insert_one({
                                    "corporate_id":verify_corporate_id["_id"],
                                    "unique_id":data['UniqueID'],
                                    "api_name":"Aadhar_Masking",
                                    "api_start_time":api_call_start_time,
                                    "api_end_time":datetime.now(),
                                    "status": "Success",
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "request_data":str(modify_request_data),
                                    "response_data" :str(store_response_database),
                                    "creadte_date":datetime.now(),
                                })
                
                    return jsonify({"data":{"response": "200",
                                    "message": "Success",
                                    "responseValue": {"Image": addhar_response["base64_string"]}}}),200
  
                else:
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    Api_request_history_db.insert_one({
                                    "corporate_id":verify_corporate_id["_id"],
                                    "unique_id":data['UniqueID'],
                                    "api_name":"Aadhar_Masking",
                                    "api_start_time":api_call_start_time,
                                    "api_end_time":datetime.now(),
                                    "status": "Error",
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "request_data":str(modify_request_data),
                                    "response_data" :str(addhar_response),
                                    "creadte_date":datetime.now(),
                                })



                    return jsonify(addhar_response) , 400

            else:
                store_response = {"response": 400,
                                "message": "Error",
                                "responseValue": "Request with the same unique ID has already been processed!"
                            }

                
                return jsonify(store_response),400
        
        
        except Exception as e:
            return jsonify({
                    "response": "400",
                    "message": "Error",
                    "responseValue":"Please upload a clear and legible image of the entire document in JPEG, PNG format."
                    }) , 400
            
            # return jsonify({"data":str(e)})
        

        