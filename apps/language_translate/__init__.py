from flask import Blueprint, request, jsonify
from googletrans import Translator , LANGUAGES
from flask_jwt_extended import  jwt_required
from data_base_string import *
from datetime import datetime

# Blueprint
language_translate_bp = Blueprint("language_translate_bp",
                        __name__,
                        url_prefix="/")

translator = Translator()


# Database
Api_request_history_db = Regtch_services_UAT["Api_request_history_test"]

@language_translate_bp.route('/api/v1/languagetransalator/getlanguagetranslator',methods=['POST'])
# @jwt_required()
def language_translator_main():
    if request.method == 'POST':
        api_call_start_time = datetime.now()
        data = request.get_json()

        keys_to_check = ['UniqueID', 'CorporateID', 'SampleText','ToLanguage','FromLanguage']
        
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
                                        "api_name":"Lang_Translate",
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
                                        "api_name":"Lang_Translate",
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
                                        "api_name":"Lang_Translate",
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

        
        check_log_db = Api_request_history_db.find_one({"unique_id":data["UniqueID"]})
        

        if check_log_db == None:
            
            try:
            
                chunks = [data['SampleText'][i:i+4900] for i in range(0, len(data['SampleText']), 4900)]
                all_string = ""
                for chunk in chunks:
                    if chunk != "":
                        translation = translator.translate(chunk, src=data['ToLanguage'], dest=data['FromLanguage'])
                        if translation.text != "":
                            all_string += translation.text


                if all_string != "":
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()

                    store_response = {"response": 200,
                                    "message": "Success",
                                    "responseValue": {
                                        "Table1": [{
                                                "TranslatedText": all_string}]}}
                    Api_request_history_db.insert_one({
                                    "corporate_id":data["CorporateID"],
                                    "unique_id":data["UniqueID"],
                                    "api_name":"Lang_Translate",
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

            except:
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                store_response = {"response": 400,
                                "message": "Error",
                                'responseValue':"Please Choose Correct language!"}
                Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "unique_id":data["UniqueID"],
                                "api_name":"Lang_Translate",
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
                            "api_name":"Lang_Translate",
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
    

