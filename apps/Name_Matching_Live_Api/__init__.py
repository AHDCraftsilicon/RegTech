from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import  jwt_required
from data_base_string import *
from datetime import datetime
import random
import string
import difflib , re
from werkzeug.exceptions import BadRequest


# Blueprint
Name_Matching_Api_bp = Blueprint("Name_Matching_Api_bp",
                        __name__,
                        url_prefix="/")



# # Database
Api_request_history_db = Regtch_services_UAT["Api_Request_History"]
Login_db = Regtch_services_UAT["Login_db"]

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




@Name_Matching_Api_bp.route('/api/v1/name/matching',methods=['POST'])
@jwt_required()
def compare_strings():
    if request.method == 'POST':
        try:

            data = request.get_json()  # This may raise BadRequest
            if data == {}:
                return jsonify({
                    "response": "400",
                    "message": "Error",
                    "responseValue":"Invalid or missing JSON data!"
                    }) , 400
            
            keys_to_check = ['UniqueID','CorporateID' , 'name1','name2',"isCaseSensitive"]

            for key in keys_to_check:
                if key not in data or not data[key]:
                    # UniqueID Check 
                    store_response = {"response": 400,
                            "message": "Error",
                            "responseValue": key +" cannot be null or empty."
                        }
                    return jsonify({"data":store_response}), 400
            
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
                modify_request_data["name1"] = data["name1"]
                modify_request_data["name2"] = data["name2"]
                modify_request_data["isCaseSensitive"] = data["isCaseSensitive"]

            

            check_log_db = Api_request_history_db.find_one({"unique_id":data['UniqueID']})
            

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
                                                "String": str2,
                                                "SimilarityPercentage": 100.0}}
                    
                    Api_request_history_db.insert_one({
                                "corporate_id":verify_corporate_id["_id"],
                                "unique_id":data['UniqueID'],
                                "api_name":"Name_Match",
                                "api_start_time":api_call_start_time,
                                "api_end_time":datetime.now(),
                                "status": "Success",
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "request_data":str(modify_request_data),
                                "response_data" :str(store_response),
                                "creadte_date":datetime.now(),
                                })
        
                    return jsonify({"data":store_response}), 200

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
                                    "corporate_id":verify_corporate_id["_id"],
                                    "unique_id":data['UniqueID'],
                                    "api_name":"Name_Match",
                                    "api_start_time":api_call_start_time,
                                    "api_end_time":datetime.now(),
                                    "status": "Success",
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "request_data":str(modify_request_data),
                                    "response_data" :str(store_response),
                                    "creadte_date":datetime.now(),
                                })

                    return jsonify({"data":store_response}), 200

            else:
                store_response = {"response": 400,
                                "message": "Error",
                                "responseValue": "Request with the same unique ID has already been processed!"
                            }

                
                return jsonify({"data":store_response}),400

    
        except Exception as e:
            if str(e) == "400 Bad Request: Errored to decode JSON object: Expecting value: line 7 column 1 (char 149)":
                return jsonify({"response": 400,
                        "message": "Error",
                        "responseValue": "isCaseSensitive cannot be null or empty!"
                    }), 400
            
            else:
                return jsonify({"response": 400,
                        "message": "Error",
                        "responseValue": str(e)
                    }), 400


        
        