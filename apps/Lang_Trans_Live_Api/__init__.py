from flask import Blueprint, request, jsonify
from googletrans import Translator , LANGUAGES
from flask_jwt_extended import  jwt_required
from data_base_string import *
from datetime import datetime

# Blueprint
Lang_Trans_bp = Blueprint("Lang_Trans_bp",
                        __name__,
                        url_prefix="/")

translator = Translator()


# # Database
Api_request_history_db = Regtch_services_UAT["Api_Request_History"]
Login_db = Regtch_services_UAT["Login_db"]

@Lang_Trans_bp.route('/api/v1/language/translator',methods=['POST'])
@jwt_required()
def language_translator_main():

    try:
        if request.method == 'POST':
            data = request.get_json()
            if data == {}:
                return jsonify({
                    "response": "400",
                    "message": "Error",
                    "responseValue":"Invalid or missing JSON data!"
                    }) , 400
            
            keys_to_check = ['UniqueID', 'CorporateID', 'SampleText','ToLanguage','FromLanguage']

            
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
                modify_request_data["SampleText"] = data["SampleText"]
                modify_request_data["ToLanguage"] = data["ToLanguage"]
                modify_request_data["FromLanguage"] = data["FromLanguage"]

            # # ## Check UniqueID
            check_log_db = Api_request_history_db.find_one({"unique_id":data['UniqueID']})


            if check_log_db == None:

                chunks = [data['SampleText'][i:i+4900] for i in range(0, len(data['SampleText']), 4900)]
                all_string = ""
                for chunk in chunks:
                    if chunk != "":
                        translation = translator.translate(chunk, src=data['FromLanguage'], dest=data['ToLanguage'])
                        if translation.text != "":
                            all_string += translation.text

                if all_string != "":
                    store_response = {"response": 200,
                                    "message": "Success",
                                    "responseValue": all_string}
                    
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    
                    Api_request_history_db.insert_one({
                                    "corporate_id":verify_corporate_id["_id"],
                                    "unique_id":data["UniqueID"],
                                    "api_name":"Lang_Translate",
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
                    return jsonify({"response": 400,
                                "message": "Error",
                                'responseValue':"Please Choose Correct language!"}) , 400
                
            else:
                store_response = {"response": 400,
                                "message": "Error",
                                "responseValue": "Request with the same unique ID has already been processed!"
                            }

                
                return jsonify(store_response),400
            
    except Exception as e:
        return jsonify({"data":str(e)})




@Lang_Trans_bp.route('/api/v1/getlanguages',methods=['GET'])
# @jwt_required()
def languages_list():
    details = []
    for code, lang in LANGUAGES.items():
        details.append({
            "lang" : lang,
            "lang_code" : code,
        })

    return jsonify({
                    "response": 200,
                    "message": "Success",
                    "data":details
                    }) , 200