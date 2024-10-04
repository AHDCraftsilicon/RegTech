from flask import Blueprint, render_template,request,jsonify,Response , g
from flask_jwt_extended import create_access_token
from datetime import timedelta
from bleach import clean



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
       
        data = request.get_json()

        # Json IS Empty Or Not
        if data == {}:
            return jsonify({"data" : {"status_code": 400,
                                    "status": "Error",
                                    "response":"Invalid or missing JSON data!"
                                    }}) , 400
        
        key_of_request = ['client_id','client_secret_key','grant_type']
        
        # Extra Key Remove
        extra_keys = [key for key in data if key not in key_of_request]
    
        if extra_keys:
            return jsonify({"data":{
                "status_code": 400,
                "status": "Error",
                "response":"Please Validate Your Data!"
            }}), 400


        # HTML Injection & Also Verify Key is Empy Or Null
        injection_error = check_html_injection(data, key_of_request)
        if injection_error:
            return injection_error

        # Check In Database
        verify_auth = User_Authentication_db.find_one({"client_id":data["client_id"]})

        if verify_auth != None:
            if verify_auth["client_secret_key"] == data["client_secret_key"]:

                duration = timedelta(minutes=30)

                indentity_dict = {'api_user':True ,"client_id":str(verify_auth["_id"]) }

                access_token = create_access_token(expires_delta=duration,identity=indentity_dict,
                                                       additional_claims={"is_api": True})
                
                return jsonify({"data" :{"status_code": 200,
                        "status": "Success",
                        "response": {"token_type": "bearer",
                                        "access_token": access_token,
                                        "expires_in": 120}
                        }})
              

            return jsonify({"data" : {"status_code": 400,
                                    "status": "Error",
                                    "response":"The credentials provided are incorrect! Please verify and re-enter them!"
                                    }}) , 400
        
        return jsonify({"data" : {"status_code": 400,
                                    "status": "Error",
                                    "response":"The credentials provided are incorrect! Please verify and re-enter them!"
                                    }}) , 400
        


        return jsonify({"data":"yes"})
    
    return jsonify({})


