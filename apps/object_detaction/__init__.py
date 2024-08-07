from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file
import os , base64
import torch
import cv2
from pathlib import Path
from collections import Counter
import time , io
from werkzeug.utils import secure_filename
from PIL import Image
from data_base_string import *
from datetime import datetime
from flask_jwt_extended import  jwt_required

# Blueprint
object_detaction_bp = Blueprint("object_detaction_bp",
                        __name__,
                        url_prefix="/")

model = torch.hub.load('./apps/yolov5','custom', path='./apps/yolov5/yolov5s.pt', source='local')


# Database
Api_request_history_db = Regtch_services_UAT["Api_request_history"]


@object_detaction_bp.route("/api/v1/objectdetection/imagedetection",methods=['POST'])
# @jwt_required()
def object_detaction_main():
    if request.method == 'POST':
        api_call_start_time = datetime.now()
        data = request.get_json()

        keys_to_check = ['UniqueID', 'CorporateID', 'image']

        # Check for missing keys and items can't be empty

        for key in keys_to_check:
            if key not in data or not data[key]:
                # UniqueID Check 
                if key == "UniqueID":
                    store_response = {"response": 400,
                            "message": "Error",
                            "responseValue": key +" cannot be null or empty."
                        }
                    return jsonify(store_response), 400
            
                else:
                    check_log_db = Api_request_history_db.find_one({"unique_id":data["UniqueID"]})
                    
                    if check_log_db != None:
                        api_call_end_time = datetime.now()
                        duration = api_call_end_time - api_call_start_time
                        duration_seconds = duration.total_seconds()
                        store_response = {"response": 400,
                                        "message": "Error",
                                        "responseValue": "Request with the same unique ID has already been processed!"
                                    }

                        Api_request_history_db.insert_one({
                                        "corporate_id":data["CorporateID"],
                                        "unique_id":data["UniqueID"],
                                        "api_name":"Object_detaction",
                                        "api_start_time":api_call_start_time,
                                        "api_end_time":datetime.now(),
                                        "status": "Fail",
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "request_data":str(data),
                                        "response_data" :str(store_response),
                                        "creadte_date":datetime.now(),
                                    })
                        
                        return jsonify(store_response),400
                    
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    # CorporateId
                    if key == "CorporateID":
                        store_response = {"response": 400,
                                "message": "Error",
                                "responseValue": key +" cannot be null or empty."
                            }
                        
                        Api_request_history_db.insert_one({
                                        "unique_id":data["UniqueID"],
                                        "api_name":"Object_detaction",
                                        "api_start_time":api_call_start_time,
                                        "api_end_time":datetime.now(),
                                        "status": "Fail",
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "request_data":str(data),
                                        "response_data" :str(store_response),
                                        "creadte_date":datetime.now(),
                                    })
                        
                    else:
                        store_response = {"response": 400,
                                "message": "Error",
                                "responseValue": key +" cannot be null or empty."
                            }
                        
                        Api_request_history_db.insert_one({
                                        "unique_id":data["UniqueID"],
                                        "corporate_id":data["CorporateID"],
                                        "api_name":"Object_detaction",
                                        "api_start_time":api_call_start_time,
                                        "api_end_time":datetime.now(),
                                        "status": "Fail",
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "request_data":str(data),
                                        "response_data" :str(store_response),
                                        "creadte_date":datetime.now(),
                                    })

                    
                    return jsonify(store_response), 400


        # Check UniqueID
        check_log_db = Api_request_history_db.find_one({"unique_id":data["UniqueID"]})
    
        if check_log_db == None:
            try:
                base64_string = data['image'].split(',')[1]
            except:
                base64_string = data['image']

            # print(base64_string.split(',')[1])

            # Base64 Convert To Image
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

            image.save(os.path.join('apps/static/object_Detaction', secure_filename(static_file_name)))
            
            image_path = "apps/static/object_Detaction/" +static_file_name

            # Response Store List
            responce_list = []

            # Yolo Model Work Start
            imgss = cv2.imread(image_path)
            
            # Image validation
            if imgss is None:
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                store_response = {"response": 400,
                            "message": "Error",'responseValue':"Please Upload Valid Image"}
                Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "unique_id":data["UniqueID"],
                                "api_name":"Object_detaction",
                                "api_start_time":api_call_start_time,
                                "api_end_time":datetime.now(),
                                "status": "Fail",
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "request_data":str(data),
                                "response_data" :str(store_response),
                                "creadte_date":datetime.now(),
                            })
            
                return jsonify(store_response), 400

            results = model(imgss)
            # results.show()

            output_path = './static/obj_dect_output/test.jpg'
            results.save(output_path)

            # time.sleep(2)
            img_rgb = cv2.cvtColor(imgss, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(img_rgb)

            # Create a BytesIO object to save the image in-memory
            buffered = io.BytesIO()
            pil_img.save(buffered, format="JPEG")

            # Encode image to Base64
            img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

            responce_list.append({"image":img_base64})


            object_list = []


            item_counts = Counter(results.pandas().xyxy[0]['name'].tolist())
            for x,y in zip(item_counts.keys(), item_counts.values()):
                object_list.append({"object_name":y,"object_count":x})
                # print(x,y)

            responce_list.append({"object_list":object_list})

            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": 200,
                        "message": "Success",
                        "responseValue": {
                            "Table1":responce_list}}
            Api_request_history_db.insert_one({
                             "corporate_id":data["CorporateID"],
                                "unique_id":data["UniqueID"],
                                "api_name":"Object_detaction",
                                "api_start_time":api_call_start_time,
                                "api_end_time":datetime.now(),
                                "status": "Success",
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "request_data":str(data),
                                "response_data" :str(store_response),
                                "creadte_date":datetime.now(),
                        })

            return jsonify(store_response), 200
            
        else:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": 400,
                            "message": "Error",
                            "responseValue": "Request with the same unique ID has already been processed!"
                        }

            Api_request_history_db.insert_one({
                            "corporate_id":data["CorporateID"],
                            "unique_id":data["UniqueID"],
                            "api_name":"Object_detaction",
                            "api_start_time":api_call_start_time,
                            "api_end_time":datetime.now(),
                            "status": "Fail",
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "request_data":str(data),
                            "response_data" :str(store_response),
                            "creadte_date":datetime.now(),
                        })
            
            return jsonify(store_response),400
    