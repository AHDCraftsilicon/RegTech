from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file
from PIL import Image
import cv2
import numpy as np
import os,time
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required
import base64,io
from data_base_string import *
from datetime import datetime
from werkzeug.exceptions import BadRequest

# Blueprint
Image_Quality_bp = Blueprint("Image_Quality_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")

# Database
Api_request_history_db = Regtch_services_UAT["Api_Request_History"]
Login_db = Regtch_services_UAT["Login_db"]



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
    



@Image_Quality_bp.route('/api/v1/image/imagequality',methods=['POST'])
@jwt_required()
def quality_check_image_main():
    if request.method == 'POST':
        try:

            data = request.get_json() 
            if data == {}:
                return jsonify({
                    "response": "400",
                    "message": "Error",
                    "responseValue":"Invalid or missing JSON data!"
                    }) , 400
            
            
            keys_to_check = ['UniqueID', 'CorporateID', 'image']

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

                base64_string = data['image']
                if base64_string.startswith('data:image/jpeg;base64,'):
                    base64_string = base64_string.replace('data:image/jpeg;base64,', '')

                image_bytes = base64.b64decode(base64_string)
                image = Image.open(io.BytesIO(image_bytes))

                filename_img = str(time.time()).replace(".", "")

                static_file_name = filename_img+".png"
                image.save(os.path.join('apps/static/Image_Quality/Image_Quality_Images', secure_filename(static_file_name)))
                
                store_image = "apps/static/Image_Quality/Image_Quality_Images/" +static_file_name

                modify_request_data["image"] = store_image

                Quality_status = quality_check_module(store_image)

                store_response = {"response": 200,
                                    "message": "Success",
                                    "responseValue":Quality_status}
                
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                
                Api_request_history_db.insert_one({
                        "corporate_id":verify_corporate_id["_id"],
                        "unique_id":data["UniqueID"],
                        "api_name":"Image_Quality",
                        "api_start_time":api_call_start_time,
                        "api_end_time":datetime.now(),
                        "status": "Success",
                        "response_duration":str(duration),
                        "response_time":duration_seconds,
                        "request_data":str(modify_request_data),
                        "response_data" :str(store_response),
                        "creadte_date":datetime.now(),
                    })


                return jsonify({"data":store_response}) , 200

            else:
                
                store_response = {"response": 400,
                                "message": "Error",
                                "responseValue": "Request with the same unique ID has already been processed!"
                            }
                
                return jsonify(store_response),400



        except Exception as e:
            return jsonify({"response": 400,
                        "message": "Error",
                        "responseValue": str(e)
                    }), 400
