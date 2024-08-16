from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import  jwt_required
from data_base_string import *
from datetime import datetime
import random
import string


# Blueprint
name_matching_bp = Blueprint("name_matching_bp",
                        __name__,
                        url_prefix="/")



# Database
Api_request_history_db = Regtch_services_UAT["Api_request_history_test"]


def calculate_jaccard_index_n_gram(str1, str2, n):
    n_grams1 = get_n_grams(str1, n)
    n_grams2 = get_n_grams(str2, n)
 
    intersection = len(n_grams1.intersection(n_grams2))
    union = len(n_grams1.union(n_grams2))
 
    jaccard_index = intersection / union
    similarity_percentage = jaccard_index * 100
 
    return similarity_percentage
 
def get_n_grams(input_str, n):
    n_grams = set()
    for i in range(len(input_str) - n + 1):
        n_grams.add(input_str[i:i + n])
    return n_grams


def convert_time(duration):
    return {
        'seconds': duration,
        'milliseconds': duration * 1000,
        'minutes': duration / 60
    }


# Generate Random Number
def generate_random_alphanumeric(length=10):
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


@name_matching_bp.route('/api/v1/namematching/getstringsimilarity',methods=['POST'])
# @jwt_required()
def compare_strings():
    if request.method == 'POST':
        api_call_start_time = datetime.now()
        data = request.get_json()

        random_uniqu = generate_random_alphanumeric()
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
                    check_log_db = Api_request_history_db.find_one({"unique_id":random_uniqu})
                    
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
                                        "unique_id":random_uniqu,
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
                                        "unique_id":random_uniqu,
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
                                        "unique_id":random_uniqu,
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
        check_log_db = Api_request_history_db.find_one({"unique_id":random_uniqu})
        

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
                            "unique_id":random_uniqu,
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
                similarity = calculate_jaccard_index_n_gram(str1, str2,3)


                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                store_response = {"response": 200,
                                "message": "Success",
                                "responseValue": {
                                    "Table1": [
                                        {
                                            "String": str2,
                                            "SimilarityPercentage": f"{similarity:.2f}%"
                                        }
                                    ]
                                }}
                Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "unique_id":random_uniqu,
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
                            "unique_id":random_uniqu,
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
        

