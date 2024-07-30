from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import JWTManager, jwt_required,get_jwt_identity,get_jwt,verify_jwt_in_request


# Blueprint
string_compartion_bp = Blueprint("string_compartion_bp",
                        __name__,
                        url_prefix="/")


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


@string_compartion_bp.route('/api/v1/namematching/getstringsimilarity',methods=['POST'])
@jwt_required()
def compare_strings():
    if request.method == 'POST':
        data = request.get_json()

        if not data or 'name1' not in data:
            return jsonify({"response": "400",
                        "message": "Error",
                        "responseValue": "name1 cannot be null or empty."
                    }), 400
        
        if not data or 'name2' not in data:
            return jsonify({"response": "400",
                        "message": "Error",
                        "responseValue": "name2 cannot be null or empty."
                    }), 400
        
        if not data or 'isCaseSensitive' not in data:
            return jsonify({"response": "400",
                        "message": "Error",
                        "responseValue": "isCaseSensitive cannot be null or empty."
                    }), 400
        
        if not data or 'CorporateID' not in data:
            return jsonify({"response": "400",
                        "message": "Error",
                        "responseValue": "CorporateID cannot be null or empty."
                    }), 400
        
        print(data["CorporateID"])
        print("Name_Match")
        current_day = datetime.now().day
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        # pare
        print(current_year)
        print(datetime.strptime(str(current_month), "%m").strftime("%b"))
        print(current_day)
        print(data)

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
                        return jsonify({"response": "200",
                                    "message": "Success",
                                    "responseValue": {
                                        "Table1": [
                                            {
                                                "String": str2,
                                                "SimilarityPercentage": 100.0
                                            }
                                        ]
                                    }}), 200
                    similarity = calculate_jaccard_index_n_gram(str1, str2,3)
                    return jsonify({"response": "200",
                                    "message": "Success",
                                    "responseValue": {
                                        "Table1": [
                                            {
                                                "String": str2,
                                                "SimilarityPercentage": f"{similarity:.2f}%"
                                            }
                                        ]
                                    }}), 200

                
                return jsonify({"response": "400",
                        "message": "Error",
                        "responseValue": "isCaseSensitive cannot be null or empty"
                    }),400
            
            return jsonify({"response": "400",
                        "message": "Error",
                        "responseValue": "name2 cannot be null or empty"
                    }),400
            
        return jsonify({"response": "400",
                        "message": "Error",
                        "responseValue": "name1 cannot be null or empty"
                    }),400
        
        
