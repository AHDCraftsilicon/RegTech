from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import timedelta
from bleach import clean
import re
from bson import ObjectId
from datetime import datetime
import uuid
from googletrans import Translator , LANGUAGES
import json , requests

# DataBase
from data_base_string import *


# Headers Verification
from Headers_Verify import *


# Blueprint
Language_Translator_api_bp = Blueprint("Language_Translator_api_bp",
                        __name__,
                        url_prefix="/api/v1/",
                        template_folder="templates")

# DB
Authentication_db = Regtch_services_UAT["User_Authentication"]
Api_Informations_db = Regtch_services_UAT["Api_Informations"]
Prod_user_api_history_db = Regtch_services_UAT['Prod_user_api_history']
Test_user_api_history_db = Regtch_services_UAT['Test_user_api_history']

# User Unique Id pettern
UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)


translator = Translator()


@Language_Translator_api_bp.route("/language/translator",methods=['POST'])
@jwt_required()
def Language_Translator_Api_route():
    if request.method == 'POST':
        try:
            data = request.get_json()

            # Json IS Empty Or Not
            if data == {}:
                return jsonify({"data" : {"status_code": 400,
                                    "status": "Error",
                                    "response":"Invalid or missing JSON data. Please ensure that the request contains valid JSON!"
                                    }}) , 400
            
            key_of_request = ['UniqueID','SampleText','FromLanguage','ToLanguage','env']
            
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
                print("-------- ", check_user['sub'])
                jwt_store_details = json.loads(check_user['sub'])

                check_user_id_in_db = Authentication_db.find_one({"_id":ObjectId(jwt_store_details['client_id'])})

                if check_user_id_in_db != None:
                    # name of api
                    about_api_details = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3b9ce1846511541498")})

                    # Check Env with db
                    if data['env'].lower() in check_user_id_in_db['user_type'].lower():
                        # Test Enviroment 
                        if data['env'] == "test":
                            # Check User Api Status
                            if check_user_id_in_db['api_status'] == "Enable":
                            #     # Check Credit Limit
                                if int(check_user_id_in_db["used_test_credits"]) > 0:
                                    # Api Start Time
                                    start_time = datetime.utcnow()

                                    # UniqueID Check in DB
                                    unique_id_check = Test_user_api_history_db.find_one({"user_id":check_user_id_in_db["_id"],
                                                                                         "unique_id":data["UniqueID"]})

                                    if unique_id_check == None or check_user_id_in_db['tester_flag'] ==  True:
                                        
                                        all_string = ""
                                        
                                        # if character more than 5000 that senario break phresh
                                        chunks = [data['SampleText'][i:i+4900] for i in range(0, len(data['SampleText']), 4900)]
                                        
                                        for chunk in chunks:
                                            if chunk != "":
                                                translation = translator.translate(chunk, src=data['FromLanguage'], dest=data['ToLanguage'])
                                                if translation.text != "":
                                                    all_string += translation.text

                                        # Api End Time
                                        end_time = datetime.utcnow()
                                        duration = (end_time - start_time).total_seconds() * 1000

                                        # Client Ip address
                                        response = requests.get('https://ifconfig.me')
                                        
                                        # Request Id
                                        request_id = generate_random_id()


                                        if all_string != "":
                                            http_status = 200

                                            json_msg = {"data":{
                                                "status_code": 200,
                                                "status": "Success",
                                                "response": {"translate_string": all_string},
                                                "basic_response":{ "request_id" : request_id,
                                                            "request_on" : start_time,
                                                            "response_on":end_time,
                                                            "api_name":about_api_details['api'],
                                                            "duration":round(duration, 2),
                                                            }
                                                }}
                                            
                                            # Log store in db
                                            Test_user_api_history_db.insert_one({
                                                    # Lang Trans objid
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
                                                    'created_on':datetime.now()})

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
                                        else:
                                            http_status = 400

                                            json_msg = {"data":{
                                                "status_code": 400,
                                                "status": "Error",
                                                "response": "Please check your string. The input format or content is incorrect!",
                                                "basic_response":{ "request_id" : request_id,
                                                            "request_on" : start_time,
                                                            "response_on":end_time,
                                                            "api_name":about_api_details['api'],
                                                            "duration":round(duration, 2),
                                                            }
                                                }}
                                            
                                            # Log store in db
                                            Test_user_api_history_db.insert_one({
                                                    # Lang Trans objid
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
                                                    'created_on':datetime.now()})

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
                                # Api Start Time
                                start_time = datetime.utcnow()

                                # UniqueID Check in DB
                                unique_id_check = Prod_user_api_history_db.find_one({"user_id":check_user_id_in_db["_id"],
                                                                                    "unique_id":data["UniqueID"]})
                                if unique_id_check == None:
                                    all_string = ""
                                        
                                    # if character more than 5000 that senario break phresh
                                    chunks = [data['SampleText'][i:i+4900] for i in range(0, len(data['SampleText']), 4900)]
                                    
                                    for chunk in chunks:
                                        if chunk != "":
                                            translation = translator.translate(chunk, src=data['FromLanguage'], dest=data['ToLanguage'])
                                            if translation.text != "":
                                                all_string += translation.text

                                    # Api End Time
                                    end_time = datetime.utcnow()
                                    duration = (end_time - start_time).total_seconds() * 1000

                                    # Client Ip address
                                    response = requests.get('https://ifconfig.me')
                                    
                                    # Request Id
                                    request_id = generate_random_id()

                                    if all_string != "":
                                        http_status = 200

                                        json_msg = {"data":{
                                            "status_code": 200,
                                            "status": "Success",
                                            "response": {"translate_string": all_string},
                                            "basic_response":{ "request_id" : request_id,
                                                        "request_on" : start_time,
                                                        "response_on":end_time,
                                                        "api_name":about_api_details['api'],
                                                        "duration":round(duration, 2),
                                                        }
                                            }}
                                    else:
                                        http_status = 400

                                        # Api End Time
                                        end_time = datetime.utcnow()
                                        duration = (end_time - start_time).total_seconds() * 1000

                                        # Client Ip address
                                        response = requests.get('https://ifconfig.me')
                                        
                                        # Request Id
                                        request_id = generate_random_id()

                                        json_msg = {"data":{
                                            "status_code": 400,
                                            "status": "Error",
                                            "response": "Please check your string. The input format or content is incorrect!",
                                            "basic_response":{ "request_id" : request_id,
                                                        "request_on" : start_time,
                                                        "response_on":end_time,
                                                        "api_name":about_api_details['api'],
                                                        "duration":round(duration, 2),
                                                        }
                                            }}
                                        
                                    # Log store in db
                                        Prod_user_api_history_db.insert_one({
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
                                                'created_on':datetime.now()})

                                        return jsonify(json_msg)
                                
                                else:
                                    return jsonify({"data":{
                                                "status_code": 409,
                                                "status": "Error",
                                                "response":"This ID has already been used. Verify Your UniqueID and try again!"
                                            }}), 409
                                
                            else:
                                return jsonify({"data":{
                                            "status_code": 403,
                                            "status": "Error",
                                            "response":"You are not eligible for this API. Please contact support for access!"
                                        }}), 403
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
        
   


@Language_Translator_api_bp.route('/getlanguages',methods=['GET'])
def languages_list():
    details = []
    for code, lang in LANGUAGES.items():
        details.append({
            "lang" : lang,
            "lang_code" : code,
        })

    return jsonify({"data" : {
                    "status_code": 200,
                    "status": "Success",
                    "Lang_list":details
                    }}) , 200


