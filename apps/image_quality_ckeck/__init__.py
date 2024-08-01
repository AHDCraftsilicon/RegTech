from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file
from PIL import Image
import cv2
import numpy as np
import os,time
import pandas as pd
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required
import base64,io
from data_base_string import *
from datetime import datetime

# Blueprint
image_quality_check_bp = Blueprint("image_quality_check_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")

# Database
Api_request_history_db = Regtch_services_UAT["Api_request_history"]




def get_image_resolution(image_path):
    with Image.open(image_path) as img:
        return img.size

def calculate_sharpness(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    laplacian = cv2.Laplacian(image, cv2.CV_64F)
    variance = laplacian.var()
    return variance

def calculate_noise(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    mean, stddev = cv2.meanStdDev(image)
    return stddev[0][0]

def calculate_compression_artifacts(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    dct = cv2.dct(np.float32(image) / 255.0)
    return np.mean(np.abs(dct[1:, 1:]))

def classify_sharpness(variance):
    if variance < 50:
        return "poor"
    elif variance < 100:
        return "weak"
    elif variance < 150:
        return "middle"
    else:
        return "best"

def classify_noise_level(noise):
    if noise > 50:
        return "poor"
    elif noise > 30:
        return "weak"
    elif noise > 10:
        return "middle"
    else:
        return "best"

def classify_compression_artifacts(artifacts):
    if artifacts > 0.2:
        return "poor"
    elif artifacts > 0.1:
        return "weak"
    elif artifacts > 0.05:
        return "middle"
    else:
        return "best"

def classify_resolution(width, height):
    if width < 640 or height < 480:
        return "poor"
    elif width < 1280 or height < 720:
        return "weak"
    elif width < 1920 or height < 1080:
        return "middle"
    else:
        return "best"


@image_quality_check_bp.route('/api/v1/imagequalitycheck/imagequality',methods=['POST'])
@jwt_required()
def quality_check_image_main():
    if request.method == 'POST':
        api_call_start_time = datetime.now()
        data = request.get_json()

        if not data or 'CorporateID' not in data:

            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "CorporateID cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                            "api_name":"Image_quality_check",
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })

            return jsonify(store_response), 400


        if not data or 'UniqueID' not in data:

            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "UniqueID cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                            "corporate_id":data["CorporateID"],
                            "api_name":"Image_quality_check",
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })

            return jsonify(store_response), 400
        


        if not data or 'image' not in data:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "image cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                            "corporate_id":data["CorporateID"],
                            "unique_id":data["UniqueID"],
                            "api_name":"Image_quality_check",
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })

            return jsonify(store_response), 400
        


                # Check UniqueID
        
        
        
        if data["UniqueID"] != "":
            check_log_db = Api_request_history_db.find_one({"unique_id":data["UniqueID"]})
        
        else:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "UniqueID cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                            "api_name":"Aadhar_Masking",
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
            
            return jsonify(store_response), 400
        
        if data["CorporateID"] == "":
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "CorporateID cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                            "api_name":"Aadhar_Masking",
                            "unique_id":data["UniqueID"],
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
            
            return jsonify(store_response), 400



        if check_log_db == None:
            if data['image'] != "":
                try:
                    base64_string = data['image'].split(',')[1]
                except:
                    base64_string = data['image']

                if base64_string.startswith('data:image/jpeg;base64,'):
                    base64_string = base64_string.replace('data:image/jpeg;base64,', '')

                # Decode the base64 string into bytes
                image_bytes = base64.b64decode(base64_string)

                # Convert bytes data to PIL Image
                image = Image.open(io.BytesIO(image_bytes))

                # Save the image to a file (example: 'output.jpg')
                filename_img = str(time.time()).replace(".", "")
                # print(filename_img+".png")
                static_file_name = filename_img+".png"

                image.save(os.path.join('apps/static/quality_check', secure_filename(static_file_name)))
                
                image_path = "apps/static/quality_check/" +static_file_name

                sharpness = calculate_sharpness(image_path)
                compression_artifacts = calculate_compression_artifacts(image_path)

                sharpness_class = classify_sharpness(sharpness)
                compression_class = classify_compression_artifacts(compression_artifacts)
                
                width = 0
                heigth = 0
                with Image.open(image_path) as img:
                    width = img.size[0]
                    heigth = img.size[1]
                
                os.remove("apps/static/quality_check/" +static_file_name)  

                if sharpness_class == "best" or compression_class == "best":
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    store_response = {"response": "200",
                                        "message": "Success",
                                        "responseValue": {
                                            "Table1": [{
                                                    "Width":width,
                                                    "Height":heigth,
                                                    "Message": "Image quality is good."}]}}
                    Api_request_history_db.insert_one({
                                    "corporate_id":data["CorporateID"],
                                    "unique_id":data["UniqueID"],
                                    "api_name":"Image_quality_check",
                                    "current_date_time":datetime.now(),
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "return_response" :str(store_response),
                                    "request_data":str(data)
                                })

                    return jsonify(store_response), 200

                else:
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    store_response = {"response": "200",
                                        "message": "Success",
                                        "responseValue": {
                                            "Table1": [{
                                                    "Width":width,
                                                    "Height":heigth,
                                                    "Message": "Image quality is poor."}]}}
                    Api_request_history_db.insert_one({
                                    "corporate_id":data["CorporateID"],
                                    "unique_id":data["UniqueID"],
                                    "api_name":"Image_quality_check",
                                    "current_date_time":datetime.now(),
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "return_response" :str(store_response),
                                    "request_data":str(data)
                                })

                    return jsonify(store_response), 200
            
            else:
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                store_response = {"response": "400",
                            "message": "Error",
                            "responseValue": "image cannot be null or empty."
                        }
                Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "unique_id":data["UniqueID"],
                                "api_name":"Image_quality_check",
                                "current_date_time":datetime.now(),
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "return_response" :str(store_response),
                                "request_data":str(data)
                            })

                return jsonify(store_response), 400

        else:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                            "message": "Error",
                            "responseValue": "Request with the same unique ID has already been processed!"
                        }

            Api_request_history_db.insert_one({
                            "corporate_id":data["CorporateID"],
                            "unique_id":data["UniqueID"],
                            "api_name":"Aadhar_Masking",
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
            
            return jsonify(store_response),400

    