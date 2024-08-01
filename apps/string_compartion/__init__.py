from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import  jwt_required
from data_base_string import *
from datetime import datetime



# Blueprint
string_compartion_bp = Blueprint("string_compartion_bp",
                        __name__,
                        url_prefix="/")



# Database
Api_request_history_db = Regtch_services_UAT["Api_request_history"]


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

@string_compartion_bp.route('/api/v1/namematching/getstringsimilarity',methods=['POST'])
@jwt_required()
def compare_strings():
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
                            "api_name":"Name_Match",
                            # "unique_id":data["UniqueID"],
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })

            return jsonify(store_response), 400


       
        
        

        if not data or 'name1' not in data:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "name1 cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                            "corporate_id":data["CorporateID"],
                            "unique_id":data["UniqueID"],
                            "api_name":"Name_Match",
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
        
            return jsonify(store_response), 400
            
        if not data or 'name2' not in data:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "name2 cannot be null or empty"
                    }
            Api_request_history_db.insert_one({
                            "corporate_id":data["CorporateID"],
                            "unique_id":data["UniqueID"],
                            "api_name":"Name_Match",
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
        
            return jsonify(store_response), 400
 
        
        if not data or 'isCaseSensitive' not in data:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "isCaseSensitive cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                            "corporate_id":data["CorporateID"],
                            "unique_id":data["UniqueID"],
                            "api_name":"Name_Match",
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
    
        
        if data["CorporateID"] == "":
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "CorporateID cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                            "api_name":"Name_Match",
                            "unique_id":data["UniqueID"],
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
            
            return jsonify(store_response), 400


        if check_log_db == None:

            if data['name1'] != "":
                if data['name2'] != "":
                    if data['isCaseSensitive'] != "":
                        case_sensitive = data['isCaseSensitive']

                        if case_sensitive == 'false':
                            str1 = data['name1'].lower()
                            str2 = data['name2'].lower()
                        else:
                            str1 = data['name1']
                            str2 = data['name2']
                    

                        if str1 == str2:
                            
                            api_call_end_time = datetime.now()
                            duration = api_call_end_time - api_call_start_time
                            duration_seconds = duration.total_seconds()
                            store_response = {"response": "200",
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
                                            "unique_id":data["UniqueID"],
                                            "api_name":"Name_Match",
                                            "current_date_time":datetime.now(),
                                            "response_duration":str(duration),
                                            "response_time":duration_seconds,
                                            "return_response" :str(store_response),
                                            "request_data":str(data)
                                        })
                
                            return jsonify(store_response), 200

                        similarity = calculate_jaccard_index_n_gram(str1, str2,3)


                        api_call_end_time = datetime.now()
                        duration = api_call_end_time - api_call_start_time
                        duration_seconds = duration.total_seconds()
                        store_response = {"response": "200",
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
                                        "unique_id":data["UniqueID"],
                                        "api_name":"Name_Match",
                                        "current_date_time":datetime.now(),
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "return_response" :str(store_response),
                                        "request_data":str(data)
                                    })
            
                        return jsonify(store_response), 200

                    
                    # CaseSensitive Can't null
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    store_response = {"response": "400",
                                "message": "Error",
                                "responseValue": "isCaseSensitive cannot be null or empty."
                            }
                    Api_request_history_db.insert_one({
                                    "corporate_id":data["CorporateID"],
                                    "unique_id":data["UniqueID"],
                                    "api_name":"Name_Match",
                                    "current_date_time":datetime.now(),
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "return_response" :str(store_response),
                                    "request_data":str(data)
                                })
        
                    return jsonify(store_response), 400
                
                
                # Name2 can't null
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                store_response = {"response": "400",
                            "message": "Error",
                            "responseValue": "name2 cannot be null or empty"
                        }
                Api_request_history_db.insert_one({
                                "corporate_id":data["CorporateID"],
                                "unique_id":data["UniqueID"],
                                "api_name":"Name_Match",
                                "current_date_time":datetime.now(),
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "return_response" :str(store_response),
                                "request_data":str(data)
                            })
            
                return jsonify(store_response), 400
            
            # name1 can't null
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "name1 cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                            "corporate_id":data["CorporateID"],
                            "unique_id":data["UniqueID"],
                            "api_name":"Name_Match",
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
        
            return jsonify(store_response), 400
        
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
                            "api_name":"Name_Match",
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
            
            return jsonify(store_response),400
        

