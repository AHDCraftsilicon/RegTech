from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import timedelta
from bleach import clean
import re
from bson import ObjectId
import difflib 
from datetime import datetime
import uuid
from flask_socketio import emit, SocketIO
# DataBase
from data_base_string import *
import requests , json

import threading
# Headers Verification
from Headers_Verify import *


# Aadhaar OCR
from apps.Every_Apis.OCR.aadhaar_text_to_details_ml_kit import *
# Pancard OCR
from apps.Every_Apis.OCR.pancard_ocr_with_verification import *
# Passport OCR
from apps.Every_Apis.OCR.passport_ocr_module import *
# Voter OCR
from apps.Every_Apis.OCR.voter_ocr_module import *


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



# Connection check
# @OCR_all_api_bp.route("/conn-check")
# def connection_Check():

#     return render_template('socket_connection_check.html')

qer = ""



# def init_socketio(socketios):
#     print("+++++++++")
#     @socketios.on('trigger_api', namespace='/')
#     def handle_trigger_api(data):
#         print('Received trigger_api:', data)  
#         ml_kit_responce = aadhaar_details(data['message'])

#         # print(ml_kit_responce)
#         json_responce = ""
#         if ml_kit_responce == {}:
#             json_responce =  {"status_code": 400,
#                 "status": "Error",
#                 "response": "Please upload a high-quality and readable image."}
#         else:
#             json_responce = {"status_code": 200,
#                             "status": "Success",
#                             "response": ml_kit_responce}
            
#         ML_kit_value_storage_db.update_one({"_id":ObjectId(data['objids'])},
#                                            {"$set": {"json_data":json_responce,
#                                                      "Google_kit":data['message']}})
        

# async def check_status(inseted_objid):
#     while True:
#         check_db_log = ML_kit_value_storage_db.find_one({"_id":ObjectId(inseted_objid)})
#         if check_db_log != None:

#             if check_db_log['json_data'] != "":
#                 print("Document found:", check_db_log['json_data'])
#                 return check_db_log['json_data'] 
#             else:
#                 print("Document not found. Retrying...")
#                 await asyncio.sleep(1)


@OCR_all_api_bp.route("/ocr",methods=['POST'])
@jwt_required()
#@check_headers
def Ocr_Api_route():
    if request.method == 'POST':
        # try:
            # ev = threading.Event()
            data = request.get_json()
         

            # Json IS Empty Or Not
            if data == {}:
                return jsonify({"data" : {"status_code": 400,
                                        "status": "Error",
                                        "response":"Invalid or missing JSON data!"
                                        }}) , 400
            
            key_of_request = ['UniqueID','doc_type','image']
            
            # Extra Key Remove
            extra_keys = [key for key in data if key not in key_of_request]
        
            if extra_keys:
                return jsonify({"data":{
                    "status_code": 400,
                    "status": "Error",
                    "response":"Please Validate Your Data!"
                }}), 400


            # HTML Injection & Also Verify Key is Empy Or Null
            injection_error = check_html_injection(data, key_of_request)
            if injection_error:
                return injection_error
            

            # Check Unique Id

            uuid_to_check = data['UniqueID']
            # Check if the UUID matches the pattern
            if UUID_PATTERN.match(uuid_to_check):

                modify_request_data = {
                    "UniqueID" : data["UniqueID"],
                    "doc_type" : data["doc_type"],
                }
                
                # Api Calling Time Start
                api_call_start_time = datetime.now()
                
                check_user = get_jwt()

                check_user_id_in_db = Authentication_db.find_one({"_id":ObjectId(check_user['sub']['client_id'])})

                if check_user_id_in_db != None:
                    if check_user_id_in_db["total_test_credits"] > check_user_id_in_db["used_test_credits"]:
                        
                        
                        # UniqueID Check in DB

                        # If Tester Flag is true So don't check unique Id
                        if check_user_id_in_db['tester_flag'] == True:
                            unique_id_check = None
                        else:
                            unique_id_check = User_test_Api_history_db.find_one({"user_id":check_user_id_in_db["_id"],"User_Unique_id":data["UniqueID"]})
                        
                        api_status = ""
                        
                        if unique_id_check == None:
                            try:
                                ocr_image = data['image'].split(',')[1]
                            except:
                                ocr_image = data['image']

                            if ocr_image.startswith('data:image/jpeg;base64,'):
                                ocr_image = ocr_image.replace('data:image/jpeg;base64,', '')
                            
                            
                            if ocr_image.startswith('data:image/png;base64,'):
                                ocr_image = ocr_image.replace('data:image/png;base64,', '')
                            
                            if data["doc_type"] == "Aadhaarcard":

                                img_decoded = base64.b64decode(ocr_image)
                                qr_Code_scan_response = aadhaar_Qr_scan(img_decoded)
                                api_status = "Aadhaar_OCR"

                                if len(qr_Code_scan_response) != 0:
                                    store_response = {"status_code": 200,
                                                "status": "Success",
                                                "response": qr_Code_scan_response}
                                else:

                                    url = "http://103.206.57.30/image-api"

                                    payload = json.dumps({"image": ocr_image })
                                    headers = {'Content-Type': 'application/json'
                                        }
                                    try:
                                        response = requests.request("POST", url, headers=headers, data=payload)
                                        if response.json() == {}:
                                            return jsonify({"status_code": 521,
                                            "status": "Error",
                                            "response": "OCR server is down!"}) , 521 
                                        
                                        else:
                                            response_Data = response.json()
                                            print(response_Data)
                                            # print(response_Data)
                                            if response_Data['Objid_id'] != "":
                                                check_db_log = ML_kit_value_storage_db.find_one({"_id":ObjectId(response_Data['Objid_id'])})
                                                # print(check_db_log)
                                                if check_db_log != None:
                                                    ml_kit_responce = aadhaar_details(check_db_log['message'])
                                                    
                                                    if ml_kit_responce == {}:
                                                        store_response =  {"status_code": 400,
                                                            "status": "Error",
                                                            "response": "Please upload a high-quality and readable image."}
                                                    else:
                                                        store_response = {"status_code": 200,
                                                                        "status": "Success",
                                                                        "response": ml_kit_responce}
                                                else:
                                                    store_response = {"status_code": 521,
                                                                "status": "Error",
                                                                "response": "OCR server is down!"}
                                            else:
                                                store_response = {"status_code": 521,
                                                            "status": "Error",
                                                            "response": "OCR server is down!"}
                                    except:
                                        return jsonify({"status_code": 521,
                                        "status": "Error",
                                        "response": "OCR server is down!"}) , 521     
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
                            
                            
                            elif data["doc_type"] == "PANcard":
                                img_decoded = base64.b64decode(ocr_image)
                                pan_responce = pancard_main(img_decoded)
                                api_status = "PAN_OCR"

                                if len(pan_responce) != 0:
                                    store_response = {"status_code": 200,
                                                "status": "Success",
                                                "response": pan_responce}
                                else:
                                    store_response = {"status_code": 400,
                                    "status": "Error",
                                    "response": "Please upload a high-quality and readable image."}

                            elif data["doc_type"] == "Passport":
                                img_decoded = base64.b64decode(ocr_image)
                                passport_responce = passport_main(img_decoded)
                                api_status = "Passport_OCR"


                                if passport_responce != {}:
                                    store_response = {"status_code": 200,
                                                "status": "Success",
                                                "response": passport_responce}
                                else:
                                    store_response = {"status_code": 400,
                                    "status": "Error",
                                    "response": "Please upload a high-quality and readable image."}

                            elif data["doc_type"] == "VoterID":
                                img_decoded = base64.b64decode(ocr_image)
                                voterid_responce = voter_ocr_main(img_decoded)
                                api_status = "VoterID_OCR"


                                if voterid_responce != {}:
                                    store_response = {"status_code": 200,
                                                "status": "Success",
                                                "response": voterid_responce}
                                else:
                                    store_response = {"status_code": 400,
                                    "status": "Error",
                                    "response": "Please upload a high-quality and readable image."}

                            else:
                                return jsonify({"data":{
                                        "status_code": 400,
                                        "status": "Error",
                                        "response":"Please Select Valid doc_type!"
                                    }}) , 400

                            api_call_end_time = datetime.now()
                            duration = api_call_end_time - api_call_start_time
                            duration_seconds = duration.total_seconds()
                                
                            
                            # DataBase Log
                            User_test_Api_history_db.insert_one({
                                    "user_id":check_user_id_in_db["_id"],
                                    "User_Unique_id":data['UniqueID'],
                                    "api_name":api_status,
                                    "api_start_time":api_call_start_time,
                                    "api_end_time":datetime.now(),
                                    "api_status": "Success",
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "request_data":str(modify_request_data),
                                    "response_data" :str(store_response),
                                    "creadted_on":datetime.now(),
                                    "System_Generated_Unique_id" : str(uuid.uuid4()),
                                    })

                            # Check Api Using Credits
                            api_use_credit_info = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3b9ce1846511541493")})
                            
                            if check_user_id_in_db["unlimited_test_credits"] == False:
                                # Credit 
                                Authentication_db.update_one({"_id":check_user_id_in_db["_id"]},{"$set":{
                                    "used_test_credits": check_user_id_in_db["used_test_credits"] + api_use_credit_info["credits_per_use"]
                                }})
                            
                            return jsonify({"data":store_response})

                        else:
                            return jsonify({"data":{
                                        "status_code": 400,
                                        "status": "Error",
                                        "response":"This ID has already been used. Verify Your UniqueID and try again!"
                                    }}), 400
                    else:
                        return jsonify({"data":{
                                "status_code": 400,
                                "status": "Error",
                                "response":"You have zero credits left, please pay for more credits!"
                            }}), 400
                    
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