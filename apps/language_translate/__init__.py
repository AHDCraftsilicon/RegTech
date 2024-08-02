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
Api_request_history_db = Regtch_services_UAT["Api_request_history"]

@language_translate_bp.route('/api/v1/languagetransalator/getlanguagetranslator',methods=['POST'])
@jwt_required()
def language_translator_main():
    if request.method == 'POST':
        api_call_start_time = datetime.now()
        data = request.get_json()

        if not data or 'UniqueID' not in data:
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "UniqueID cannot be null or empty."
                    }
        
            return jsonify(store_response), 400
        


        if not data or 'CorporateID' not in data:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "CorporateID cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                            "api_name":"Lang_Translate",                            
                            # "unique_id":data["UniqueID"],
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
                            "api_name":"Lang_Translate",
                            "unique_id":data["UniqueID"],
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
            
            return jsonify(store_response), 400


        if not data or 'SampleText' not in data:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                    "message": "Error",
                    "responseValue": "SampleText cannot be null or empty."
                }
            Api_request_history_db.insert_one({
                            "corporate_id":data["CorporateID"],
                            "unique_id":data["UniqueID"],
                            "api_name":"Lang_Translate",
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
        
            return jsonify(store_response), 400
       
        if not data or 'ToLanguage' not in data:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                    "message": "Error",
                    "responseValue": "ToLanguage cannot be null or empty."
                }
            Api_request_history_db.insert_one({
                            "corporate_id":data["CorporateID"],
                            "unique_id":data["UniqueID"],
                            "api_name":"Lang_Translate",
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
        
            return jsonify(store_response), 400
          
        if not data or 'FromLanguage' not in data:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                    "message": "Error",
                    "responseValue": "FromLanguage cannot be null or empty."
                }
            Api_request_history_db.insert_one({
                            "corporate_id":data["CorporateID"],
                            "unique_id":data["UniqueID"],
                            "api_name":"Lang_Translate",
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
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "UniqueID cannot be null or empty."
                    }
            
            return jsonify(store_response), 400
        

        if check_log_db == None:
            
            
            if data['SampleText'] == "":
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                store_response = {"response": "400",
                            "message": "Error",
                            "responseValue": "SampleText cannot be null or empty."
                        }
                Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "api_name":"Lang_Translate",
                                "unique_id":data["UniqueID"],
                                "current_date_time":datetime.now(),
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "return_response" :str(store_response),
                                "request_data":str(data)
                            })
                
                return jsonify(store_response), 400
            
            if data['ToLanguage'] == "":
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                store_response = {"response": "400",
                            "message": "Error",
                            "responseValue": "ToLanguage cannot be null or empty."
                        }
                Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "api_name":"Lang_Translate",
                                "unique_id":data["UniqueID"],
                                "current_date_time":datetime.now(),
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "return_response" :str(store_response),
                                "request_data":str(data)
                            })
                
                return jsonify(store_response), 400

            
            if data['FromLanguage'] == "":
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                store_response = {"response": "400",
                            "message": "Error",
                            "responseValue": "FromLanguage cannot be null or empty."
                        }
                Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "api_name":"Lang_Translate",
                                "unique_id":data["UniqueID"],
                                "current_date_time":datetime.now(),
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "return_response" :str(store_response),
                                "request_data":str(data)
                            })
                
                return jsonify(store_response), 400



            translation = translator.translate(data['SampleText'], src=data['ToLanguage'], dest=data['FromLanguage'])
            
            if translation.text != "":
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()

                store_response = {"response": "200",
                                "message": "Success",
                                "responseValue": {
                                    "Table1": [{
                                            "TranslatedText": translation.text}]}}
                Api_request_history_db.insert_one({
                                "api_name":"Lang_Translate",
                                "unique_id":data["UniqueID"],
                                "corporate_id":data["CorporateID"],
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
                                'responseValue':"Please Choose Correct language!"}
                Api_request_history_db.insert_one({
                                "api_name":"Lang_Translate",
                                "unique_id":data["UniqueID"],
                                "corporate_id":data["CorporateID"],
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
                            "responseValue": "Request with the same unique ID has already been processed!"
                        }

            Api_request_history_db.insert_one({
                            "corporate_id":data["CorporateID"],
                            "unique_id":data["UniqueID"],
                            "api_name":"Lang_Translate",
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
            
            return jsonify(store_response),400
    

