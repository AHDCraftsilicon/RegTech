from flask import Blueprint, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required,get_jwt_identity
import time , os
from werkzeug.utils import secure_filename
from ocr_reading_files.pancard_ocr import *
from ocr_reading_files.election_Card_without_load import *
from ocr_reading_files.passport_id_ocr import *
from ocr_reading_files.addhar_ocr_without_load import *
import base64 , io
from data_base_string import *
from datetime import datetime
import random
import string

# Blueprint
ocr_image_reading_bp = Blueprint("ocr_image_reading_bp",
                        __name__,
                        url_prefix="/")


# Database
Api_request_history_db = Regtch_services_UAT["Api_request_history_test"]


def generate_random_alphanumeric(length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

# Generate a random 10-digit alphanumeric string



@ocr_image_reading_bp.route('/api/v1/readdocument/readiamgetext',methods=['POST'])
# @jwt_required()
def ocr_image_read_text_main():
    # try:
        if request.method == 'POST': 
            print("code start...") 

            api_call_start_time = datetime.now()

            data = request.get_json() 
            random_uniqu = generate_random_alphanumeric()

            keys_to_check = ['UniqueID', 'CorporateID', 'documenttype',"ImageBase64"]

            
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
                        check_log_db = Api_request_history_db.find_one({"unique_id":random_uniqu})
                        
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
                                            "unique_id":random_uniqu,
                                            "api_name":"OCR_img_reading",
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
                                            "unique_id":random_uniqu,
                                            "api_name":"OCR_img_reading",
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
                                            "unique_id":random_uniqu,
                                            "corporate_id":data["CorporateID"],
                                            "api_name":"OCR_img_reading",
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
            check_log_db = Api_request_history_db.find_one({"unique_id":random_uniqu})

        
            if check_log_db == None: 
                    
                try:
                    base64_string = data['ImageBase64'].split(',')[1]
                except:
                    base64_string = data['ImageBase64']


                if base64_string.startswith('data:image/jpeg;base64,'):
                    base64_string = base64_string.replace('data:image/jpeg;base64,', '')

                # Decode the base64 string into bytes
                image_path = base64.b64decode(base64_string)

                # Convert bytes data to PIL Image
                # image = Image.open(io.BytesIO(image_bytes))

                # # Save the image to a file (example: 'output.jpg')
                # filename_img = str(time.time()).replace(".", "")
                # # print(filename_img+".png")
                # static_file_name = filename_img+".png"

                # image.save(os.path.join('apps/static/ocr_image', secure_filename(static_file_name)))
                
                # image_path = "./apps/static/ocr_image/" +static_file_name

                if data['documenttype'] == "PanCard":
                    pancard = pancard_main(image_path)

                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    
                    Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "unique_id":random_uniqu,
                                "api_name":"OCR_img_reading",
                                "api_start_time":api_call_start_time,
                                "api_end_time":datetime.now(),
                                "status": "Success",
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "request_data":str(data),
                                "response_data" :str(pancard),
                                "creadte_date":datetime.now()
                                })
                    
                    if pancard['response'] == 200:
                        return jsonify(pancard),200
                    else:
                        return jsonify(pancard), 400
                    
                elif data['documenttype'] == "AadharCard":
                    # print(image_path)
                    addhar_Card = aadhar_ocr_image_read_main(image_path)

                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    
                    Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "unique_id":random_uniqu,
                                "api_name":"OCR_img_reading",
                                "api_start_time":api_call_start_time,
                                "api_end_time":datetime.now(),
                                "status": "Success",
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "request_data":str(data),
                                "response_data" :str(addhar_Card),
                                "creadte_date":datetime.now()
                                })

                    
                    if addhar_Card['response'] == 200:
                        return jsonify(addhar_Card),200
                    else:
                        return jsonify(addhar_Card),400

                elif data['documenttype'] == "VoterID":
                    election_Card = voter_ocr_main(image_path)

                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    
                    Api_request_history_db.insert_one({
                                    "corporate_id":data["CorporateID"],
                                    "unique_id":random_uniqu,
                                    "api_name":"OCR_img_reading",
                                    "api_start_time":api_call_start_time,
                                    "api_end_time":datetime.now(),
                                    "status": "Success",
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "request_data":str(data),
                                    "response_data" :str(election_Card),
                                    "creadte_date":datetime.now()
                                })

                    
                    if election_Card['response'] == 200:
                        return jsonify(election_Card),200
                    else:
                        return jsonify(election_Card),400
                elif data['documenttype'] == "PassportID":
                    passport = passport_main(image_path)

                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    
                    Api_request_history_db.insert_one({
                                    "corporate_id":data["CorporateID"],
                                    "unique_id":random_uniqu,
                                    "api_name":"OCR_img_reading",
                                    "api_start_time":api_call_start_time,
                                    "api_end_time":datetime.now(),
                                    "status": "Success",
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "request_data":str(data),
                                    "response_data" :str(passport),
                                    "creadte_date":datetime.now()
                                })

                    if passport['response'] == 200:
                        return jsonify(passport),200
                    else:
                        return jsonify(passport),400

                else:
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()

                    store_response = {"response": 400,
                            "message": "Error",
                            "responseValue": "Please add Valid documenttype!"
                        }
                    Api_request_history_db.insert_one({
                                    "corporate_id":data["CorporateID"],
                                    "unique_id":random_uniqu,
                                    "api_name":"OCR_img_reading",
                                    "api_start_time":api_call_start_time,
                                    "api_end_time":datetime.now(),
                                    "status": "Fail",
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "request_data":str(data),
                                    "response_data" :str(store_response),
                                    "creadte_date":datetime.now()
                                })
                    return jsonify(store_response),400

                
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
                                    "unique_id":random_uniqu,
                                    "api_name":"OCR_img_reading",
                                    "api_start_time":api_call_start_time,
                                    "api_end_time":datetime.now(),
                                    "status": "Fail",
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "request_data":str(data),
                                    "response_data" :str(store_response),
                                    "creadte_date":datetime.now()
                            })
                
                return jsonify(store_response),400

    # except:
    #     store_response = {"response": 400,
    #                     "message": "Error",
    #                     "responseValue": "Could not find Image!"
    #                 }
        
    #     return jsonify(store_response),400

            



    

