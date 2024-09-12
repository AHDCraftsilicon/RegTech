# from flask_jwt_extended import JWTManager, create_access_token, jwt_required,get_jwt_identity
from flask import Flask,jsonify,url_for,request,Blueprint
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta


# Blueprint
token_request_bp = Blueprint("token_request_bp",
                        __name__,
                        url_prefix="/")



@token_request_bp.route('/api/v1/token/getkey',methods=['POST'])
def request_connection_main():
    if request.method == 'POST':
        data = request.get_json()

        if not data or 'client_id' not in data:
            return jsonify({"error_description": "Invalid client authentication",
                            "error": "invalid_client"
                    }), 400
        elif not data or 'client_secret' not in data:
            return jsonify({"error_description": "Invalid client authentication",
                            "error": "invalid_client"
                    }), 400
        elif not data or 'grant_type' not in data:
            return jsonify({"grant_type": "Invalid grant_type authentication",
                            "error": "unsupported_grant_type"
                    }), 400
        
        if data['client_id'] == "raoCqJe1sOL5QZCyNqfHqC1wQXVEXME=":
            if data['client_secret'] == "raoCqJe1sMsKkTIZ9ExeUf5urE1TsQ0XZPwHBT0=":
                if data['grant_type'] == "client_credentials":
                    indentity_dict = {'client_id':data['client_id'],
                              'client_secret':data['client_secret'],
                              'grant_type':data['grant_type']}
                    duration = timedelta(minutes=1.5)
                    access_token = create_access_token(expires_delta=duration,identity=indentity_dict,
                                                       additional_claims={"is_api": True})
                    return jsonify({"token_type": "bearer",
                            "access_token": access_token,
                            "expires_in": 90}),200
                
                return jsonify({"grant_type": "Invalid grant_type authentication",
                            "error": "unsupported_grant_type"
                    }), 400

            return jsonify({"error_description": "Invalid client authentication",
                            "error": "invalid_client"
                    }), 400

        return jsonify({"error_description": "Invalid client authentication",
                        "error": "invalid_client"
                }), 400

            # data['client_secret'] == "7c5d229a-aeb6-4bcb-a09b-c4d78bbfb3af" and \
            # data['grant_type'] == "client_credentials":
    #         print("yess")
            
            
    # return jsonify()