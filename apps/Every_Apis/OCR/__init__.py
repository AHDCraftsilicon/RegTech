from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import timedelta
import re
from bson import ObjectId
from datetime import datetime
from flask_socketio import emit, SocketIO
import io , json , time
import requests

# DataBase
from data_base_string import *

import threading
# Headers Verification
from Headers_Verify import *


# Aadhaar OCR
from apps.Every_Apis.OCR.aadhaar_text_to_details_ml_kit import *
# Pancard OCR
from apps.Every_Apis.OCR.pan_text_to_details_ml_kit import *
# Passport OCR
from apps.Every_Apis.OCR.passport_ocr_module import *
# Voter OCR
from apps.Every_Apis.OCR.voter_ocr_module import *

import requests
import json

from apps.socket_with_AML import *
# Socket
# socketio = SocketIO()


# Blueprint
OCR_all_api_bp = Blueprint("OCR_all_api_bp",
                        __name__,
                        url_prefix="/api/v1/",
                        template_folder="templates")


# DB
Authentication_db = Regtch_services_UAT["User_Authentication"]
User_test_Api_history_db = Regtch_services_UAT['User_test_Api_history']
Api_Informations_db = Regtch_services_UAT["Api_Informations"]
ML_kit_value_storage_db = Regtch_services_UAT['Google_ml_kit_Storage']



# User Unique Id pettern
UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)



@OCR_all_api_bp.route("/ocr",methods=['POST'])
@jwt_required()
def Ocr_Api_route():
    if request.method == 'POST':
        # try:
            data = request.get_json()
         

            if data == {}:
                return jsonify({"data" : {"status_code": 400,
                                    "status": "Error",
                                    "response":"Invalid or missing JSON data. Please ensure that the request contains valid JSON!"
                                    }}) , 400
            
            key_of_request = ['UniqueID','doc_type','base64_image','env']
            
            # Extra Key Remove
            extra_keys = [key for key in data if key not in key_of_request]
        
            if extra_keys:
                return jsonify({"data":{
                        "status_code": 400,
                        "status": "Error",
                        "response":"Please validate your data. Some fields are missing or incorrect!"
                    }}), 400


            # HTML Injection & Also Verify Key is Empy Or Null
            injection_error = check_html_injection(data, key_of_request)
            if injection_error:
                return injection_error
            

            # Check Unique Id

            uuid_to_check = data['UniqueID']
            # Check if the UUID matches the pattern
            if UUID_PATTERN.match(uuid_to_check):

                check_user = get_jwt()
                # print("-------- ", check_user['sub'])
                jwt_store_details = json.loads(check_user['sub'])

                check_user_id_in_db = Authentication_db.find_one({"_id":ObjectId(jwt_store_details['client_id'])})
                
                if check_user_id_in_db != None:
                    # name of api
                    about_api_details = Api_Informations_db.find_one({"_id":ObjectId("67346bc117763aa1336b4c17")})
                    # Check Env with db
                    if data['env'].lower() in check_user_id_in_db['user_type'].lower():
                        # Test Enviroment 
                        if data['env'] == "test":
                            # Check User Api Status
                            if check_user_id_in_db['api_status'] == "Enable":
                                # Check Credit Limit
                                if int(check_user_id_in_db["used_test_credits"]) > 0:
                                    # Api Start Time
                                    start_time = datetime.utcnow()

                                    # UniqueID Check in DB
                                    unique_id_check = Test_user_api_history_db.find_one({"user_id":check_user_id_in_db["_id"],
                                                                                         "unique_id":data["UniqueID"]})
                                    
                                    if unique_id_check == None or check_user_id_in_db['tester_flag'] ==  True:
                                        # image in Base64 String 
                                        base64_string = data['base64_image']

                                        if base64_string != "":
                                            
                                            if base64_string.startswith(('data:image/jpeg;base64,', 'data:image/png;base64,')):
                                                base64_string = base64_string.split(',', 1)[1]
                                            
                                            # decode base64
                                            image_bytes = base64.b64decode(base64_string)

                                            # Aadhaar OCR
                                            if data["doc_type"] == "Aadhaarcard":

                                                # If aadhaar card have a Qr code and that scanned by in python so use this method
                                                qr_Code_response = aadhaar_Qr_scan(image_bytes)
                                                # If scan with QR code pass here and also add in db
                                                if qr_Code_response['status_code'] == 200:
                                                    # Api End Time
                                                    end_time = datetime.utcnow()
                                                    duration = (end_time - start_time).total_seconds() * 1000

                                                    # Client Ip address
                                                    response = requests.get('https://ifconfig.me')
                                                    
                                                    # Request Id
                                                    request_id = generate_random_id()

                                                    http_status = 200

                                                    json_msg = {"data":{
                                                    "status_code": 200,
                                                    "status": "Success",
                                                    "response": qr_Code_response['response'][0],
                                                    "basic_response":{ "request_id" : request_id,
                                                                "request_on" : start_time,
                                                                "response_on":end_time,
                                                                "api_name":about_api_details['api'],
                                                                "duration":round(duration, 2),
                                                                }}}
                                                    
                                                    # Log store in db
                                                    Test_user_api_history_db.insert_one({
                                                            # aadhaar redaction objid
                                                            "api_name": about_api_details['_id'],
                                                            # Enviroment Set
                                                            'env':'Test',
                                                            # ip address
                                                            "ip_address":response.text.strip(),
                                                            # user id
                                                            "user_id":check_user_id_in_db['_id'],
                                                            # Api call Status
                                                            'api_call_status' : "Api_status",
                                                            # Request id
                                                            "request_id" : request_id,
                                                            # Unique id
                                                            "unique_id":data["UniqueID"],
                                                            # Request time
                                                            "request_on" : start_time,
                                                            # Response time
                                                            "response_on":end_time,
                                                            # Time Duration of api taken time
                                                            "time_duration":round(duration, 2),
                                                            # http status
                                                            'http_status':http_status,
                                                            # date store
                                                            'created_on':datetime.now(),
                                                            # this perameter only for OCR
                                                            'which_type_of_ocr' : 'aadhaar_ocr'
                                                            })

                                                    # user Cut credits
                                                    if check_user_id_in_db['tester_flag'] == False:
                                                        if int(check_user_id_in_db['used_test_credits']) >=  int(about_api_details['credits_per_use']):
                                                            # Reduce total credit to used credits
                                                            update_total_credit = int(check_user_id_in_db['used_test_credits']) - int(about_api_details['credits_per_use'])
                                                            Authentication_db.update_one({"_id":check_user_id_in_db["_id"]},{"$set":{
                                                                            "used_test_credits":update_total_credit}})
                                                            json_msg['data']['basic_response'] ['test_credits'] = update_total_credit
                                                        else:
                                                            return jsonify({"data":{
                                                                "status_code": 402,
                                                                "status": "Error",
                                                                "response":"Not sufficient credit to use this API. Please contact our support team to purchase more credits!"
                                                            }}), 402
                                                    
                                                    return jsonify(json_msg)
                                                
                                                # pass image for AML kit
                                                else:

                                                    inseted_objid = ML_kit_value_storage_db.insert_one({"status":"loading.......",
                                                        "message":""}).inserted_id

                                                    # inseted_objid = "6748479107f979147876a050"
                                                    payload = json.dumps({
                                                    "image": base64_string,
                                                    "objid": str(inseted_objid)
                                                    })

                                                    # api not working that's way call function     
                                                    response_Data = another_way_get_func(payload)
                                                    # check function response
                                                    if int(response_Data['data']['status_code']) == 200:
                                                        try:
                                                            # check details in DB
                                                            ML_db_storage = ML_kit_value_storage_db.find_one({"_id":ObjectId(inseted_objid)})
                                                            # print("--- ," , ML_db_storage['message'])
                                                            if ML_db_storage['message'] != "":
                                                                ml_kit_responce = aadhaar_details(ML_db_storage['message'])
                                                                # If aadhaar details get successfully
                                                                if ml_kit_responce['status_code'] == 200:
                                                                    # Api End Time
                                                                    end_time = datetime.utcnow()
                                                                    duration = (end_time - start_time).total_seconds() * 1000

                                                                    # Client Ip address
                                                                    response = requests.get('https://ifconfig.me')
                                                                    
                                                                    # Request Id
                                                                    request_id = generate_random_id()

                                                                    http_status = 200

                                                                    json_msg = {"data":{
                                                                    "status_code": 200,
                                                                    "status": "Success",
                                                                    "response": ml_kit_responce['response'][0],
                                                                    "basic_response":{ "request_id" : request_id,
                                                                                "request_on" : start_time,
                                                                                "response_on":end_time,
                                                                                "api_name":about_api_details['api'],
                                                                                "duration":round(duration, 2),
                                                                                }}}
                                                                                                                                        
                                                                else:
                                                                    # Api End Time
                                                                    end_time = datetime.utcnow()
                                                                    duration = (end_time - start_time).total_seconds() * 1000

                                                                    # Client Ip address
                                                                    response = requests.get('https://ifconfig.me')
                                                                    
                                                                    # Request Id
                                                                    request_id = generate_random_id()

                                                                    http_status = 200

                                                                    json_msg = {"data":{
                                                                    "status_code": 400,
                                                                    "status": "Error",
                                                                    "response": "Please upload a high-quality and readable image. The current image is not clear enough for processing!",
                                                                    "basic_response":{ "request_id" : request_id,
                                                                                "request_on" : start_time,
                                                                                "response_on":end_time,
                                                                                "api_name":about_api_details['api'],
                                                                                "duration":round(duration, 2),
                                                                                }}}
                                                                    
                                                                
                                                                # AML through user log in DB
                                                        #         # Log store in db
                                                                Test_user_api_history_db.insert_one({
                                                                        # aadhaar redaction objid
                                                                        "api_name": about_api_details['_id'],
                                                                        # Enviroment Set
                                                                        'env':'Test',
                                                                        # ip address
                                                                        "ip_address":response.text.strip(),
                                                                        # user id
                                                                        "user_id":check_user_id_in_db['_id'],
                                                                        # Api call Status
                                                                        'api_call_status' : "Api_status",
                                                                        # Request id
                                                                        "request_id" : request_id,
                                                                        # Unique id
                                                                        "unique_id":data["UniqueID"],
                                                                        # Request time
                                                                        "request_on" : start_time,
                                                                        # Response time
                                                                        "response_on":end_time,
                                                                        # Time Duration of api taken time
                                                                        "time_duration":round(duration, 2),
                                                                        # http status
                                                                        'http_status':http_status,
                                                                        # date store
                                                                        'created_on':datetime.now(),
                                                                        # this perameter only for OCR
                                                                        'which_type_of_ocr' : 'aadhaar_ocr'
                                                                        })

                                                        #         # user Cut credits
                                                                if check_user_id_in_db['tester_flag'] == False:
                                                                    if int(check_user_id_in_db['used_test_credits']) >=  int(about_api_details['credits_per_use']):
                                                                        # Reduce total credit to used credits
                                                                        update_total_credit = int(check_user_id_in_db['used_test_credits']) - int(about_api_details['credits_per_use'])
                                                                        Authentication_db.update_one({"_id":check_user_id_in_db["_id"]},{"$set":{
                                                                                        "used_test_credits":update_total_credit}})
                                                                        json_msg['data']['basic_response'] ['test_credits'] = update_total_credit
                                                                    else:
                                                                        return jsonify({"data":{
                                                                            "status_code": 402,
                                                                            "status": "Error",
                                                                            "response":"Not sufficient credit to use this API. Please contact our support team to purchase more credits!"
                                                                        }}), 402
                                                                
                                                                return jsonify(json_msg)

                                                            print(response_Data['data'])
                                                            return jsonify({"data":{
                                                                        "status_code": 500,
                                                                        "status": "Error",
                                                                        "response":"Please try again, something went wrong. If the issue persists, contact support!"
                                                                    }}), 500
                                                        except:

                                                            return jsonify({"data":{
                                                                "status_code": 503,
                                                                "status": "Error",
                                                                "response":"Please wait for a few minutes, server performance is high. We are working to resolve the issue!"
                                                            }}), 503

                                                    else:
                                                        return jsonify({"data":{
                                                                    "status_code": 500,
                                                                    "status": "Error",
                                                                    "response":"Please try again, something went wrong. If the issue persists, contact support!"
                                                                }}), 500
                                            
                                            # PAN OCR
                                            if data["doc_type"] == "PANcard":

                                                inseted_objid = ML_kit_value_storage_db.insert_one({"status":"loading.......",
                                                        "message":""}).inserted_id
                                                
                                                # inseted_objid = "6748479107f979147876a050"
                                                payload = json.dumps({
                                                "image": base64_string,
                                                "objid": str(inseted_objid)
                                                })

                                                # api not working that's way call function     
                                                response_Data = another_way_get_func(payload)
                                                # check function response
                                                if int(response_Data['data']['status_code']) == 200:
                                                    try:
                                                            # check details in DB
                                                            ML_db_storage = ML_kit_value_storage_db.find_one({"_id":ObjectId(inseted_objid)})
                                                            print("--- ," , ML_db_storage['message'])
                                                            if ML_db_storage['message'] != "":

                                                                pan_ml_responce = pan_details(ML_db_storage['message'])
                                                                if pan_ml_responce['status_code'] == 200:
                                                                    # Api End Time
                                                                    end_time = datetime.utcnow()
                                                                    duration = (end_time - start_time).total_seconds() * 1000

                                                                    # Client Ip address
                                                                    response = requests.get('https://ifconfig.me')
                                                                    
                                                                    # Request Id
                                                                    request_id = generate_random_id()

                                                                    http_status = 200

                                                                    json_msg = {"data":{
                                                                    "status_code": 200,
                                                                    "status": "Success",
                                                                    "response": pan_ml_responce['response'][0],
                                                                    "basic_response":{ "request_id" : request_id,
                                                                                "request_on" : start_time,
                                                                                "response_on":end_time,
                                                                                "api_name":about_api_details['api'],
                                                                                "duration":round(duration, 2),
                                                                                }}}
                                                                                                                                        
                                                                else:
                                                                    # Api End Time
                                                                    end_time = datetime.utcnow()
                                                                    duration = (end_time - start_time).total_seconds() * 1000

                                                                    # Client Ip address
                                                                    response = requests.get('https://ifconfig.me')
                                                                    
                                                                    # Request Id
                                                                    request_id = generate_random_id()

                                                                    http_status = 200

                                                                    json_msg = {"data":{
                                                                    "status_code": 400,
                                                                    "status": "Error",
                                                                    "response": "Please upload a high-quality and readable image. The current image is not clear enough for processing!",
                                                                    "basic_response":{ "request_id" : request_id,
                                                                                "request_on" : start_time,
                                                                                "response_on":end_time,
                                                                                "api_name":about_api_details['api'],
                                                                                "duration":round(duration, 2),
                                                                                }}}
                                                                    
                                                                # AML through user log in DB
                                                        #         # Log store in db
                                                                Test_user_api_history_db.insert_one({
                                                                        # aadhaar redaction objid
                                                                        "api_name": about_api_details['_id'],
                                                                        # Enviroment Set
                                                                        'env':'Test',
                                                                        # ip address
                                                                        "ip_address":response.text.strip(),
                                                                        # user id
                                                                        "user_id":check_user_id_in_db['_id'],
                                                                        # Api call Status
                                                                        'api_call_status' : "Api_status",
                                                                        # Request id
                                                                        "request_id" : request_id,
                                                                        # Unique id
                                                                        "unique_id":data["UniqueID"],
                                                                        # Request time
                                                                        "request_on" : start_time,
                                                                        # Response time
                                                                        "response_on":end_time,
                                                                        # Time Duration of api taken time
                                                                        "time_duration":round(duration, 2),
                                                                        # http status
                                                                        'http_status':http_status,
                                                                        # date store
                                                                        'created_on':datetime.now(),
                                                                        # this perameter only for OCR
                                                                        'which_type_of_ocr' : 'pan_ocr'
                                                                        })

                                                        #         # user Cut credits
                                                                if check_user_id_in_db['tester_flag'] == False:
                                                                    if int(check_user_id_in_db['used_test_credits']) >=  int(about_api_details['credits_per_use']):
                                                                        # Reduce total credit to used credits
                                                                        update_total_credit = int(check_user_id_in_db['used_test_credits']) - int(about_api_details['credits_per_use'])
                                                                        Authentication_db.update_one({"_id":check_user_id_in_db["_id"]},{"$set":{
                                                                                        "used_test_credits":update_total_credit}})
                                                                        json_msg['data']['basic_response'] ['test_credits'] = update_total_credit
                                                                    else:
                                                                        return jsonify({"data":{
                                                                            "status_code": 402,
                                                                            "status": "Error",
                                                                            "response":"Not sufficient credit to use this API. Please contact our support team to purchase more credits!"
                                                                        }}), 402
                                                                
                                                                return jsonify(json_msg)
                                                    
                                                    except:

                                                            return jsonify({"data":{
                                                                "status_code": 503,
                                                                "status": "Error",
                                                                "response":"Please wait for a few minutes, server performance is high. We are working to resolve the issue!"
                                                            }}), 503                                                    

                                                # return jsonify({"data":{
                                                #     "status_code": 501,
                                                #     "status": "Error",
                                                #     "response":"PANcard OCR is not accepted currently. We are working on supporting this feature!"
                                                # }}), 501
                                            
                                            # Voter OCR
                                            if data["doc_type"] == "VoterID":
                                                # inseted_objid = ML_kit_value_storage_db.insert_one({"status":"loading.......",
                                                #         "message":""}).inserted_id
                                                
                                                # inseted_objid = "674944b5ebc4e1a111aaa758"
                                                # payload = json.dumps({
                                                # "image": base64_string,
                                                # "objid": str(inseted_objid)
                                                # })

                                                # # api not working that's way call function     
                                                # response_Data = another_way_get_func(payload)
                                                # # check function response
                                                # if int(response_Data['data']['status_code']) == 200:
                                                #     # check details in DB
                                                #     ML_db_storage = ML_kit_value_storage_db.find_one({"_id":ObjectId(inseted_objid)})

                                                #     print("--- ," , ML_db_storage['message'])
                                                #     if ML_db_storage['message'] != "":
                                                #         print(ML_db_storage['message'])


                                                
                                                return jsonify({"data":{
                                                    "status_code": 501,
                                                    "status": "Error",
                                                    "response":"VoterID OCR is not accepted currently. We are working on supporting this feature!"
                                                }}), 501
                                            
                                            # Passport OCR
                                            if data["doc_type"] == "Passport":
                                                return jsonify({"data":{
                                                    "status_code": 501,
                                                    "status": "Error",
                                                    "response":"Passport OCR is not accepted currently. We are working on supporting this feature!"
                                                }}), 501
                                            
                                            else:
                                                return jsonify({"data":{
                                                    "status_code": 400,
                                                    "status": "Error",
                                                    "response":"Please enter a valid document! Document type must be Aadhaarcard, PANcard, VoterID, or Passport!"
                                                }}), 400

                                            
                                            

                                        return jsonify({"data":{
                                            "status_code": 500,
                                            "status": "Error",
                                            "response":"Please try again, something went wrong. If the issue persists, contact support!"
                                        }}), 500
                                    
                                    else:
                                        return jsonify({"data":{
                                                    "status_code": 409,
                                                    "status": "Error",
                                                    "response":"This ID has already been used. Verify Your UniqueID and try again!"
                                                }}), 409
                                
                                else:
                                    return jsonify({"data":{
                                            "status_code": 402,
                                            "status": "Error",
                                            "response":"You have zero credits left, please pay for more credits to continue using this service!"
                                        }}), 402
                            else:
                                return jsonify({"data":{
                                            "status_code": 403,
                                            "status": "Error",
                                            "response":"You are not eligible for this API. Please contact support for access!"
                                        }}), 403

                        else:
                            # Check User Api Status
                            if check_user_id_in_db['api_status'] == "Enable":
                                return jsonify({"env":"prod"})
                    else:
                        return jsonify({"data":{
                                    "status_code": 500,
                                    "status": "Error",
                                    "response":"Please check your environment configuration and ensure all required settings are properly define!"
                                }}), 500
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
            
    return jsonify({"data":{
                            "status_code": 405,
                            "status": "Error",
                            "response":"Request method not allowed. Please use the correct HTTP method."
                        }}), 405

# if check_user_id_in_db != None:
#     if check_user_id_in_db["total_test_credits"] > check_user_id_in_db["used_test_credits"]:
        
        
#         # UniqueID Check in DB

#         # If Tester Flag is true So don't check unique Id
#         if check_user_id_in_db['tester_flag'] == True:
#             unique_id_check = None
#         else:
#             unique_id_check = User_test_Api_history_db.find_one({"user_id":check_user_id_in_db["_id"],"User_Unique_id":data["UniqueID"]})
        
#         api_status = ""
        
#         if unique_id_check == None:
#             try:
#                 ocr_image = data['image'].split(',')[1]
#             except:
#                 ocr_image = data['image']

#             if ocr_image.startswith('data:image/jpeg;base64,'):
#                 ocr_image = ocr_image.replace('data:image/jpeg;base64,', '')
            
            
#             if ocr_image.startswith('data:image/png;base64,'):
#                 ocr_image = ocr_image.replace('data:image/png;base64,', '')
            
#             if data["doc_type"] == "Aadhaarcard":

#                 img_decoded = base64.b64decode(ocr_image)
#                 qr_Code_scan_response = aadhaar_Qr_scan(img_decoded)
#                 api_status = "Aadhaar_OCR"

#                 if len(qr_Code_scan_response) != 0:
#                     store_response = {"status_code": 200,
#                                 "status": "Success",
#                                 "response": qr_Code_scan_response}
#                 else:

#                     url = "http://103.206.57.30/image-api"

#                     payload = json.dumps({"image": ocr_image })
#                     headers = {'Content-Type': 'application/json'
#                         }
#                     try:
#                         response = requests.request("POST", url, headers=headers, data=payload)
#                         if response.json() == {}:
#                             return jsonify({"status_code": 521,
#                             "status": "Error",
#                             "response": "OCR server is down!"}) , 521 
                        
#                         else:
#                             response_Data = response.json()
#                             # print(response_Data)
#                             if response_Data['Objid_id'] != "":
#                                 check_db_log = ML_kit_value_storage_db.find_one({"_id":ObjectId(response_Data['Objid_id'])})
#                                 # print(check_db_log)
#                                 if check_db_log != None:
#                                     ml_kit_responce = aadhaar_details(check_db_log['message'])
                                    
#                                     if ml_kit_responce == {}:
#                                         store_response =  {"status_code": 400,
#                                             "status": "Error",
#                                             "response": "Please upload a high-quality and readable image."}
#                                     else:
#                                         store_response = {"status_code": 200,
#                                                         "status": "Success",
#                                                         "response": ml_kit_responce}
#                                 else:
#                                     store_response = {"status_code": 521,
#                                                 "status": "Error",
#                                                 "response": "OCR server is down!"}
#                             else:
#                                 store_response = {"status_code": 521,
#                                             "status": "Error",
#                                             "response": "OCR server is down!"}
#                     except:
#                         return jsonify({"status_code": 521,
#                         "status": "Error",
#                         "response": "OCR server is down!"}) , 521     

            
            
#             elif data["doc_type"] == "PANcard":
#                 # img_decoded = base64.b64decode(ocr_image)

#                 api_status = "PAN_OCR"

#                 url = "http://103.206.57.30/image-api"

#                 payload = json.dumps({"image": ocr_image })
#                 headers = {'Content-Type': 'application/json'
#                     }
#                 try:
#                     response = requests.request("POST", url, headers=headers, data=payload)
#                     if response.json() == {}:
#                         return jsonify({"status_code": 521,
#                         "status": "Error",
#                         "response": "OCR server is down!"}) , 521 
                    
#                     else:
#                         response_Data = response.json()
#                         # print(response_Data)
#                         if response_Data['Objid_id'] != "":
#                             check_db_log = ML_kit_value_storage_db.find_one({"_id":ObjectId(response_Data['Objid_id'])})

#                             if check_db_log != None:
#                                 pan_ml_responce = pan_details(check_db_log['message'])

#                                 if len(pan_ml_responce) == 0:
#                                     store_response = {"status_code": 400,
#                                                     "status": "Error",
#                                                     "response": "Please upload a high-quality and readable image."}
#                                 else:
#                                     store_response = {"status_code": 200,
#                                                 "status": "Success",
#                                                 "response": pan_ml_responce}

#                 except:
#                         return jsonify({"status_code": 521,
#                         "status": "Error",
#                         "response": "OCR server is down!"}) , 521 
                

#             elif data["doc_type"] == "Passport":
#                 img_decoded = base64.b64decode(ocr_image)
#                 passport_responce = passport_main(img_decoded)
#                 api_status = "Passport_OCR"


#                 if passport_responce != {}:
#                     store_response = {"status_code": 200,
#                                 "status": "Success",
#                                 "response": passport_responce}
#                 else:
#                     store_response = {"status_code": 400,
#                     "status": "Error",
#                     "response": "Please upload a high-quality and readable image."}

#             elif data["doc_type"] == "VoterID":
#                 img_decoded = base64.b64decode(ocr_image)
#                 voterid_responce = voter_ocr_main(img_decoded)
#                 api_status = "VoterID_OCR"


#                 if voterid_responce != {}:
#                     store_response = {"status_code": 200,
#                                 "status": "Success",
#                                 "response": voterid_responce}
#                 else:
#                     store_response = {"status_code": 400,
#                     "status": "Error",
#                     "response": "Please upload a high-quality and readable image."}

#             else:
#                 return jsonify({"data":{
#                         "status_code": 400,
#                         "status": "Error",
#                         "response":"Please Select Valid doc_type!"
#                     }}) , 400

#             api_call_end_time = datetime.now()
#             duration = api_call_end_time - api_call_start_time
#             duration_seconds = duration.total_seconds()
                
            
#             # DataBase Log
#             User_test_Api_history_db.insert_one({
#                     "user_id":check_user_id_in_db["_id"],
#                     "User_Unique_id":data['UniqueID'],
#                     "api_name":api_status,
#                     "api_start_time":api_call_start_time,
#                     "api_end_time":datetime.now(),
#                     "api_status": "Success",
#                     "response_duration":str(duration),
#                     "response_time":duration_seconds,
#                     "request_data":str(modify_request_data),
#                     "response_data" :str(store_response),
#                     "creadted_on":datetime.now(),
#                     "System_Generated_Unique_id" : str(uuid.uuid4()),
#                     })

#             # Check Api Using Credits
#             api_use_credit_info = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3b9ce1846511541493")})
            
#             if check_user_id_in_db["unlimited_test_credits"] == False:
#                 # Credit 
#                 Authentication_db.update_one({"_id":check_user_id_in_db["_id"]},{"$set":{
#                     "used_test_credits": check_user_id_in_db["used_test_credits"] + api_use_credit_info["credits_per_use"]
#                 }})
            
#             return jsonify({"data":store_response})

#         else:
#             return jsonify({"data":{
#                         "status_code": 400,
#                         "status": "Error",
#                         "response":"This ID has already been used. Verify Your UniqueID and try again!"
#                     }}), 400
#     else:
#         return jsonify({"data":{
#                 "status_code": 400,
#                 "status": "Error",
#                 "response":"You have zero credits left, please pay for more credits!"
#             }}), 400
    
# else:
#     return jsonify({"data":{
#         "status_code": 400,
#         "status": "Error",
#         "response":"Invalid user, Please Register Your User!"
#     }}), 400

            
# OCR_all_api_bp.socketios.emit('image_updates', {'image_url': 
#                                                 {"image": ocr_image,
#                                                 "objid":str(inseted_objid)}},
#                                                 )
# OCR_all_api_bp.socketios.sleep(8)



# check_db_log = ML_kit_value_storage_db.find_one({"_id":ObjectId(inseted_objid)})
# if check_db_log != None:

#     if check_db_log['json_data'] != "":
#         # print("Document found:", check_db_log['json_data'])
#         store_response =  check_db_log['json_data'] 
#     else:
# store_response = {"status_code": 400,
#     "status": "Error",
#     "response": "Please upload a high-quality and readable image."}

# ML_kit_value_storage_db.delete_one({"_id":ObjectId(inseted_objid)})

# ml_kit_responce = aadhaar_details(ocr_image)

# 

    #     except:
    #         return jsonify({"data":{
    #                     "status_code": 400,
    #                     "status": "Error",
    #                     "response":"Something went wrong!"
    #                 }}), 400
        
    # else:
    #     return jsonify({"data":{
    #                     "status_code": 400,
    #                     "status": "Error",
    #                     "response":"Something went wrong!"
    #                 }}), 400
        
# def register_socketio(blueprint, socketio_instance):
#     blueprint.socketio = socketio_instance

# register_socketio(OCR_all_api_bp, OCR_all_api_bp.socketio)


# @OCR_all_api_bp.socketios.on('trigger_api')  # Ensure namespace matches
# def handle_trigger_api(data):
#     print(f"Received data in blueprint: {data}")
#     # emit('response_event', {'response': 'Data received!'})




# @OCR_all_api_bp.route("/textstoredb/ocr",methods=['POST'])
# def image_text_store():
#     try:
#         if request.method == 'POST':
#             objid_data = request.form['objid']
#             image_to_string = request.form['image_to_string']

#             if image_to_string != "" and objid_data !="":
#                 ML_kit_value_storage_db.update_one({"_id":ObjectId(objid_data)},
#                                                 {"$set":{"json_data":image_to_string}}
#                                                 )
                
#                 return jsonify({"data":"Store data"}) 
            
#         return jsonify({"data":"Something Wrong!"})
#     except:
#         return jsonify({"data":"Something Wrong!"})