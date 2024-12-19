from flask import Blueprint, render_template,request,jsonify,Response , g
from flask_jwt_extended import create_access_token
from datetime import timedelta
from bleach import clean
import json


# DataBase
from data_base_string import *


# Headers Verification
from Headers_Verify import *

# Blueprint
Access_Token_api_bp = Blueprint("Access_Token_api_bp",
                        __name__,
                        url_prefix="/api/v1/",
                        template_folder="templates")

User_Authentication_db = Regtch_services_UAT["User_Authentication"]


@Access_Token_api_bp.route("/token/getkey",methods=['POST'])
#@check_headers
def Token_access_main_api():
    
    if request.method == 'POST':

        try:
       
            data = request.get_json()

            # Json IS Empty Or Not
            if data == {}:
                return jsonify({"data" : {"status_code": 400,
                                        "status": "Error",
                                        "response":"Invalid or missing JSON data. Please ensure that the request contains valid JSON!"
                                        }}) , 400
            
            key_of_request = ['client_id','client_secret_key','grant_type']
            
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

            # Check In Database
            verify_auth = User_Authentication_db.find_one({"client_id":data["client_id"]})

            if verify_auth != None:
                if verify_auth["client_secret_key"] == data["client_secret_key"]:

                    duration = timedelta(minutes=2)

                    indentity_dict = {'api_user':True ,"client_id":str(verify_auth["_id"]),"user_type":str(verify_auth['user_type']) }

                    access_token = create_access_token(expires_delta=duration,
                                                    identity=json.dumps(indentity_dict),
                                                        additional_claims={"is_api": True})
                    
                    return jsonify({"data" :{"status_code": 200,
                            "status": "Success",
                            "response": {"token_type": "bearer",
                                            "access_token": access_token,
                                            "expires_in": 120}
                            }})
                
                else:
                    return jsonify({"data" : {"status_code": 401,
                                            "status": "Error",
                                            "response":"The credentials provided are incorrect! Please verify and re-enter them!"
                                            }}) , 401
            else:
                return jsonify({"data" : {"status_code": 401,
                                            "status": "Error",
                                            "response":"The credentials provided are incorrect! Please verify and re-enter them!"
                                            }}) , 401
            
        except:
            return jsonify({"data" : {"status_code": 400,
                                    "status": "Error",
                                    "response":"Invalid or missing form data. Please ensure that the request contains valid data!"
                                    }}) , 400
            
    else:
        if request.method != 'POST':
            return jsonify({"data" : {"status_code": 405,
                                    "status": "Error",
                                    "response":"POST method expected. Please use POST to submit data!"
                                    }}) , 405

