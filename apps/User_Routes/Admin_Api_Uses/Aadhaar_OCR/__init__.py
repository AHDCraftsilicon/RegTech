from flask import Blueprint, render_template,request,session,redirect
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta
from bson import ObjectId
import random
import pytz
import base64,io , time
import requests , json
from werkzeug.utils import secure_filename


# Aadhaar OCR
from apps.Every_Apis.OCR.aadhaar_text_to_details_ml_kit import *

# DataBase
from data_base_string import *

# Token
from token_generation import *

# Socket
from apps.socket_with_AML import *

# Blueprint
Aadhaar_OCR_bp = Blueprint("Aadhaar_OCR_bp",
                        __name__,
                        url_prefix="/aadhaar",
                        template_folder="templates")


User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
Api_Informations_db = Regtch_services_UAT["Api_Informations"]
ML_kit_value_storage_db = Regtch_services_UAT['Google_ml_kit_Storage']
Prod_user_api_history_db = Regtch_services_UAT['Prod_user_api_history']
Test_user_api_history_db = Regtch_services_UAT['Test_user_api_history']


@Aadhaar_OCR_bp.route("/ocr")
def Aadhaar_OCR_main():

    encrypted_token = session.get('QtSld')
    ip_address = session.get('KLpi')

    if session.get('bkjid') != "":

        check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})

        # User Check in DB
        if check_user_in_db != None:
            if encrypted_token and ip_address:
                # Check User Api Status
                if check_user_in_db['api_status'] == "Enable":

                    page_name = "Aadhaar OCR"

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

                    about_api_details = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3b9ce1846511541493")})

                    return render_template("Aadhaar_ocr_modal.html",
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
    
    return redirect("/")


# Random request id generate
def generate_random_id():
    return '-'.join(''.join(random.choices('0123456789abcdef', k=4)) for _ in range(5))

# Testing Apis
@Aadhaar_OCR_bp.route("/test-api",methods=["POST"])
def Aadhaar_ocr_test_api():
    if request.method == "POST":

        # try:
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

                            # name of api
                            about_api_details = Api_Informations_db.find_one({"_id":ObjectId("67346bc117763aa1336b4c17")})
                            
                            # Api Start Time
                            start_time = datetime.utcnow()

                            aadhaar_img = request.files['aadhaar_img']
                            if aadhaar_img.filename == '':
                                return jsonify({"data":{
                                        "status_code": 400,
                                        "status": "Error",
                                        "response":"Please select file!"
                                    }}), 400
                            
                            if aadhaar_img and allowed_file(aadhaar_img):

                                img_bytes = aadhaar_img.read()  # Read the image file as bytes
                                img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                                # Decode Base64 back into bytes (if needed for further processing)
                                image_bytes = base64.b64decode(img_base64)

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
                                            'created_on':datetime.now(),
                                            # this perameter only for OCR
                                            'which_type_of_ocr' : 'aadhaar_ocr'})

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
                                                    
                                # pass image for AML kit
                                else:

                                    inseted_objid = ML_kit_value_storage_db.insert_one({"status":"loading.......",
                                                        "message":""}).inserted_id

                                    # # inseted_objid = "6748479107f979147876a050"
                                    payload = json.dumps({
                                    "image": img_base64,
                                    "objid": str(inseted_objid)
                                    })

                                    # # api not working that's way call function     
                                    response_Data = another_way_get_func(payload)
                                    print("------ ", response_Data)
                                    # # check function response
                                    if int(response_Data['data']['status_code']) == 200:
                                        try:
                                            # check details in DB
                                            ML_db_storage = ML_kit_value_storage_db.find_one({"_id":ObjectId(inseted_objid)})
                                            print("--- ," , ML_db_storage['message'])
                                            if ML_db_storage['message'] != "":
                                                ml_kit_responce = aadhaar_details(ML_db_storage['message'])

                                                print("-------- ", ml_kit_responce)
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
                                                            'created_on':datetime.now(),
                                                            # this perameter only for OCR
                                                            'which_type_of_ocr' : 'aadhaar_ocr'})

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
                                                # Api End Time
                                                else:
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
                                                            'created_on':datetime.now(),
                                                            # this perameter only for OCR
                                                            'which_type_of_ocr' : 'aadhaar_ocr'})

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
                    
            return jsonify({"data":{
                                    "status_code": 400,
                                    "status": "Error",
                                    "response":"Something went wrong!"
                                }}), 400
        
        # except:
        #     return jsonify({"data":{
        #                             "status_code": 400,
        #                             "status": "Error",
        #                             "response":"Something went wrong!"
        #                         }}), 400
    
    return jsonify({"data":{
                            "status_code": 405,
                            "status": "Error",
                            "response":"Request method not allowed. Please use the correct HTTP method."
                        }}), 405



