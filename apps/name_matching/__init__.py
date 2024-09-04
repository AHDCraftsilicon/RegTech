from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import  jwt_required
from data_base_string import *
from datetime import datetime
import random
import string
import difflib , re


# Blueprint
name_matching_bp = Blueprint("name_matching_bp",
                        __name__,
                        url_prefix="/")



# Database
Api_request_history_db = Regtch_services_UAT["Api_request_history_test"]


def calculate_similarity(s1, s2):
    # Normalize the strings
    s1 = s1.lower().strip()
    s2 = s2.lower().strip()
    
    # Basic similarity ratio
    basic_ratio = difflib.SequenceMatcher(None, s1, s2).ratio()
    
    # Split strings into components for name reordering check
    s1_parts = sorted(re.split(r'\s+', s1))
    s2_parts = sorted(re.split(r'\s+', s2))
    
    # Check for exact match or reordered names
    if s1 == s2:
        return str(100.00)
    elif s1_parts == s2_parts:
        return str(100.00)
    elif basic_ratio > 0.8:  # Adjust this threshold as needed
        return str(round(basic_ratio * 100, 2))
    else:
        return str(round(basic_ratio * 100 * 0.9, 2))




@name_matching_bp.route('/api/v1/namematching/getstringsimilarity',methods=['POST'])
@jwt_required()
def compare_strings():
    if request.method == 'POST':
        try:
            api_call_start_time = datetime.now()
            data = request.get_json()

            keys_to_check = ['UniqueID', 'CorporateID', 'name1','name2','isCaseSensitive']

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
                        check_log_db = Api_request_history_db.find_one({"unique_id":data['UniqueID']})
                        
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
                                            "unique_id":data['UniqueID'],
                                            "api_name":"Name_Match",
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
                                            "unique_id":data['UniqueID'],
                                            "api_name":"Name_Match",
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
                                            "unique_id":data['UniqueID'],
                                            "corporate_id":data["CorporateID"],
                                            "api_name":"Name_Match",
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
            check_log_db = Api_request_history_db.find_one({"unique_id":data['UniqueID']})
            

            # Check database documents
            if check_log_db == None:
                case_sensitive = data['isCaseSensitive']

                if case_sensitive == 'false':
                    str1 = data['name1'].lower()
                    str2 = data['name2'].lower()
                else:
                    str1 = data['name1']
                    str2 = data['name2']
            
                # Match String
                if str1 == str2:
                    
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    store_response = {"response": 200,
                                "message": "Success",
                                "responseValue": {
                                    "Table1": [
                                        {
                                            "String": str2,
                                            "SimilarityPercentage": 100.0
                                        }
                                    ]
                                }}
                    Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "unique_id":data['UniqueID'],
                                "api_name":"Name_Match",
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
                    similarity = calculate_similarity(str1, str2)


                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    store_response = {
                                    "status": 200,
                                    "message": "Success",
                                    "response": {
                                                "String": str2,
                                                "SimilarityPercentage": similarity
                                    }}
                    Api_request_history_db.insert_one({
                                    "corporate_id":data["CorporateID"],
                                    "unique_id":data['UniqueID'],
                                    "api_name":"Name_Match",
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
                                "unique_id":data['UniqueID'],
                                "api_name":"Name_Match",
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
            

        except Exception as e:
            return jsonify({"data":e})
        