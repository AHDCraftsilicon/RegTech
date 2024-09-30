from flask import Blueprint, render_template,request,session,redirect
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta
from bson import ObjectId
import random
import pytz
from PIL import Image
import cv2
import pytesseract
import numpy as np
import time , os
from werkzeug.utils import secure_filename


# Module
from apps.User_Routes.Admin_Api_Uses.ITR_Analysis.ITR1_Analysis_module import *


# DataBase
from data_base_string import *

# Token
from token_generation import *


# Blueprint
ITR_analysis_bp = Blueprint("ITR_analysis_bp",
                        __name__,
                        url_prefix="/ITR",
                        template_folder="templates")


User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
User_test_Api_history_db = Regtch_services_UAT['User_test_Api_history']
Api_Informations_db = Regtch_services_UAT["Api_Informations"]




@ITR_analysis_bp.route("/analysis")
def ITR_Analysis_main():

    encrypted_token = session.get('QtSld')
    ip_address = session.get('KLpi')

    if session.get('bkjid') != "":

        check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})

        if check_user_in_db != None:

            if encrypted_token and ip_address:
                token = decrypt_token(encrypted_token)

                user_name = check_user_in_db["Company_Name"]
                test_credits = [{"Test_Credit": check_user_in_db["total_test_credits"],
                                 "Used_Credits":check_user_in_db["used_test_credits"]}]
                
                return render_template("ITR_Analysis_modal.html",
                                    test_credit=test_credits ,
                                     user_name=user_name)
    
    return redirect("/")


# Random request id generate
def generate_random_id():
    return '-'.join(''.join(random.choices('0123456789abcdef', k=4)) for _ in range(5))



@ITR_analysis_bp.route('/test-api',methods=['POST'])
def Bank_Statment_test_api():
    if request.method == "POST":

        completed_on_ = datetime.now()
        completed_on = datetime.now(pytz.timezone('Asia/Kolkata'))
        completed_on = completed_on.strftime('%Y-%m-%dT%H:%M:%S%z')
        completed_on = completed_on[:-2] + ':' + completed_on[-2:]


        pdf_file = request.files["ITR_pdf"]
        filename_ipdf = str(time.time()).replace(".", "")

        if pdf_file.filename != "":
            pdf_file.save(os.path.join('./apps/static/ITR_Analysis', secure_filename(
                filename_ipdf+"."+pdf_file.filename.split(".")[-1])))
            pdf_store_file = "apps/static/ITR_Analysis/"+filename_ipdf+"."+pdf_file.filename.split(".")[-1]
                
            if request.form["ITR_Type"] == "ITR-1":
                ITR1_Response = itr1_read_main(pdf_store_file)


            created_on = datetime.now(pytz.timezone('Asia/Kolkata'))
            created_on = created_on.strftime('%Y-%m-%dT%H:%M:%S%z')
            created_on = created_on[:-2] + ':' + created_on[-2:]


            duration = datetime.now()- completed_on_ 
            duration_seconds = duration.total_seconds()

            store_response = {"response": 200,
                                "status": "Success",
                                "responseValue":ITR1_Response,
                                "created_on" : created_on,
                                "completed_on":completed_on,
                                "request_id":generate_random_id(),
                                }


            return jsonify({"data":
                            {"json_data": store_response,
                            "result_in_seconds":duration_seconds}})
    
    return jsonify({"msg":"method Not allowed!"})