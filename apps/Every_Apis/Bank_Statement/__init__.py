from flask import Blueprint, render_template,request,session
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import timedelta
from bleach import clean
import re
from bson import ObjectId
from datetime import datetime
import uuid
import cv2
import numpy as np
import base64,os
import pytesseract
import time

# tessract path
from tesseract_path import *

# DataBase
from data_base_string import *


# Headers Verification
from Headers_Verify import *


# Blueprint
Bank_Statement_api_bp = Blueprint("Bank_Statement_api_bp",
                        __name__,
                        url_prefix="/api/v1/",
                        template_folder="templates")


# User Unique Id pettern
UUID_PATTERN = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE
)


@Bank_Statement_api_bp.route("/bank-statement/analyser",methods=['POST'])
@jwt_required()
def BANK_statement_analyser_Api_route():
    if request.method == 'POST':
        try:
            encrypted_token = session.get('QtSld')
            ip_address = session.get('KLpi')
            if session.get('bkjid') != "":

                # Sanitize the value
                sanitized_value = clean(request.form["BankName"], strip=True)
                if request.form["BankName"] != sanitized_value:
                    return jsonify({
                        "data": {
                            "status_code": 400,
                            "status": "Error",
                            "response": "The input contains disallowed HTML tags or attributes! Please remove any unsafe HTML!"
                        }
                    }), 400
                
                sanitized_value = clean(request.form["UniqueID"], strip=True)
                if request.form["UniqueID"] != sanitized_value:
                    return jsonify({
                        "data": {
                            "status_code": 400,
                            "status": "Error",
                            "response": "The input contains disallowed HTML tags or attributes! Please remove any unsafe HTML!"
                        }
                    }), 400
                

                pdf_file = request.files["PDF_File"]
                filename_ipdf = str(time.time()).replace(".", "")

                # Check Unique Id

                uuid_to_check = request.form['UniqueID']
                # Check if the UUID matches the pattern
                if UUID_PATTERN.match(str(uuid_to_check)):

                    if pdf_file.filename != "":
                        
                        if request.form["BankName"] == "ICICIBANK":
                        
                            return jsonify({"data":{
                                        "status_code": 200,
                                        "status": "Success",
                                        "response":{"bank_name":"ICICI"}
                                    }})
                        else:
                            return jsonify({"data":{
                                "status_code": 400,
                                "status": "Error",
                                "response":"Error! Please Enter Valid Bank!"
                            }}), 400

                        
                else:
                    return jsonify({"data":{
                            "status_code": 400,
                            "status": "Error",
                            "response":"Error! Please Validate the UniqueID format!"
                        }}), 400

        except:
            return jsonify({"data" : {"status_code": 400,
                                    "status": "Error",
                                    "response":"Invalid or missing form data. Please ensure that the request contains valid data!"
                                    }}) , 400

    else:
        return jsonify({"data":{
                        "status_code": 400,
                        "status": "Error",
                        "response":"Something went wrong!"
                    }}), 400

                        