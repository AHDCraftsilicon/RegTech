from flask import Blueprint, request, jsonify
# from flask_jwt_extended import JWTManager, jwt_required,get_jwt_identity
import time , os
from werkzeug.utils import secure_filename
from ocr_reading_files.pancard_ocr import *
from ocr_reading_files.electoion_card_ocr import *
from ocr_reading_files.passport_id_ocr import *
from ocr_reading_files.addhar_ocr_without_load import *
import base64 , io
from data_base_string import *
from datetime import datetime

# Blueprint
ocr_image_reading_bp = Blueprint("ocr_image_reading_bp",
                        __name__,
                        url_prefix="/")


# Database
Api_request_history_db = Regtch_services_UAT["Api_request_history"]


@ocr_image_reading_bp.route('/api/v1/readdocument/readiamgetext',methods=['POST'])
def ocr_image_read_text_main():
    if request.method == 'POST':  

        try:
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
                                "api_name":"OCR_img_reading",
                                # "unique_id":data["UniqueID"],
                                "current_date_time":datetime.now(),
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "return_response" :str(store_response),
                                "request_data":str(data)
                            })

                return jsonify(store_response), 400


            if not data or 'UniqueID' not in data:
                store_response = {"response": "400",
                            "message": "Error",
                            "responseValue": "UniqueID cannot be null or empty."
                        }

                return jsonify(store_response), 400
        
        
            
            # Check UniqueID
            if data["UniqueID"] != "":
                check_log_db = Api_request_history_db.find_one({"unique_id":data["UniqueID"]})
            
            else:
              
                store_response = {"response": "400",
                            "message": "Error",
                            "responseValue": "UniqueID cannot be null or empty."
                        }
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
                                "api_name":"OCR_img_reading",
                                "unique_id":data["UniqueID"],
                                "current_date_time":datetime.now(),
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "return_response" :str(store_response),
                                "request_data":str(data)
                            })
                
                return jsonify(store_response), 400



            if not data or 'ImageBase64' not in data:
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                store_response = {"response": "400",
                            "message": "Error",
                            "responseValue": "ImageBase64 cannot be null or empty."
                        }
                Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "unique_id":data["UniqueID"],
                                "api_name":"OCR_img_reading",
                                "current_date_time":datetime.now(),
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "return_response" :str(store_response),
                                "request_data":str(data)
                            })

                return jsonify(store_response), 400
            
            if not data or 'documenttype' not in data:
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                store_response = {"response": "400",
                            "message": "Error",
                            "responseValue": "documenttype cannot be null or empty."
                        }
                Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "unique_id":data["UniqueID"],
                                "api_name":"OCR_img_reading",
                                "current_date_time":datetime.now(),
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "return_response" :str(store_response),
                                "request_data":str(data)
                            })

                return jsonify(store_response), 400

            if check_log_db == None: 
                if data['ImageBase64'] != "":
                    
                    try:
                        base64_string = data['ImageBase64'].split(',')[1]
                    except:
                        base64_string = data['ImageBase64']


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

                    image.save(os.path.join('apps/static/ocr_image', secure_filename(static_file_name)))
                    
                    image_path = "./apps/static/ocr_image/" +static_file_name

                    if data['documenttype'] == "PanCard":
                        pancard = pancard_main(image_path)

                        api_call_end_time = datetime.now()
                        duration = api_call_end_time - api_call_start_time
                        duration_seconds = duration.total_seconds()
                      
                        Api_request_history_db.insert_one({
                                        "corporate_id":data["CorporateID"],
                                        "unique_id":data["UniqueID"],
                                        "api_name":"OCR_img_reading",
                                        "current_date_time":datetime.now(),
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "return_response" :str(pancard),
                                        "request_data":str(data)
                                    })

                        
                        
                        if pancard['response'] == "200":
                            return jsonify(pancard),200
                        else:
                            return jsonify(pancard), 400
                        
                    elif data['documenttype'] == "AadharCard":
                        addhar_Card = aadhar_ocr_image_read_main(image_path)

                        api_call_end_time = datetime.now()
                        duration = api_call_end_time - api_call_start_time
                        duration_seconds = duration.total_seconds()
                      
                        Api_request_history_db.insert_one({
                                        "corporate_id":data["CorporateID"],
                                        "unique_id":data["UniqueID"],
                                        "api_name":"OCR_img_reading",
                                        "current_date_time":datetime.now(),
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "return_response" :str(addhar_Card),
                                        "request_data":str(data)
                                    })

                        
                        if addhar_Card['response'] == "200":
                            return jsonify(addhar_Card),200
                        else:
                            return jsonify(addhar_Card),400

                    elif data['documenttype'] == "VoterID":
                        election_Card = voter_id_read(image_path)

                        api_call_end_time = datetime.now()
                        duration = api_call_end_time - api_call_start_time
                        duration_seconds = duration.total_seconds()
                      
                        Api_request_history_db.insert_one({
                                        "corporate_id":data["CorporateID"],
                                        "unique_id":data["UniqueID"],
                                        "api_name":"OCR_img_reading",
                                        "current_date_time":datetime.now(),
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "return_response" :str(election_Card),
                                        "request_data":str(data)
                                    })

                        
                        if election_Card['response'] == "200":
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
                                        "unique_id":data["UniqueID"],
                                        "api_name":"OCR_img_reading",
                                        "current_date_time":datetime.now(),
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "return_response" :str(passport),
                                        "request_data":str(data)
                                    })

                        if passport['response'] == "200":
                            return jsonify(passport),200
                        else:
                            return jsonify(passport),400

                    else:
                        api_call_end_time = datetime.now()
                        duration = api_call_end_time - api_call_start_time
                        duration_seconds = duration.total_seconds()

                        store_response = {"response": "400",
                                "message": "Error",
                                "responseValue": "Please add Valid documenttype!"
                            }
                        Api_request_history_db.insert_one({
                                        "corporate_id":data["CorporateID"],
                                        "unique_id":data["UniqueID"],
                                        "api_name":"OCR_img_reading",
                                        "current_date_time":datetime.now(),
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "return_response" :str(passport),
                                        "request_data":str(data)
                                    })
                        return jsonify(store_response),400

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
                                "api_name":"OCR_img_reading",
                                "current_date_time":datetime.now(),
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "return_response" :str(store_response),
                                "request_data":str(data)
                            })
                
                return jsonify(store_response),400
        
   
        except:

            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                            "message": "Error",
                            "responseValue": "Error Processing your request"
                        }

            Api_request_history_db.insert_one({
                            "corporate_id":data["CorporateID"],
                            "unique_id":data["UniqueID"],
                            "api_name":"OCR_img_reading",
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
            
            return jsonify(store_response),400


        # f = request.files["ImageBase64"]
        # filename_img = str(time.time()).replace(".", "")
        # if f.filename != "":
        #     f.save(os.path.join('./apps/static/ocr_image', secure_filename(
        #         filename_img+"."+f.filename.split(".")[-1])))
        #     img = "/static/ocr_image/"+filename_img+"."+f.filename.split(".")[-1]

        
                



    

