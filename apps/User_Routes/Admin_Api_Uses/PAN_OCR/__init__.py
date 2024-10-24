from flask import Blueprint, render_template,request,session,redirect
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta
from bson import ObjectId
import random
import pytz
import uuid


# Name Comparision Module
from apps.User_Routes.Admin_Api_Uses.PAN_OCR.pancard_ocr_with_verification import *

# DataBase
from data_base_string import *

# Token
from token_generation import *

# Blueprint
PAN_OCR_bp = Blueprint("PAN_OCR_bp",
                        __name__,
                        url_prefix="/pan",
                        template_folder="templates")


User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
User_test_Api_history_db = Regtch_services_UAT['User_test_Api_history']
Api_Informations_db = Regtch_services_UAT["Api_Informations"]



@PAN_OCR_bp.route("/ocr")
def Aadhaar_OCR_main():

    encrypted_token = session.get('QtSld')
    ip_address = session.get('KLpi')

    if session.get('bkjid') != "":

        check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})

        if check_user_in_db != None:
            if encrypted_token and ip_address:
                # token = decrypt_token(encrypted_token)


                about_api_details = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3b9ce1846511541496")})
                
                user_name = check_user_in_db["Company_Name"]
                test_credits = [{"Test_Credit": check_user_in_db["total_test_credits"],
                                    "Used_Credits":check_user_in_db["used_test_credits"]}]


                return render_template("PAN_ocr_modal.html",
                                    test_credit=test_credits ,
                                    about_api_details = about_api_details['long_api_description'],
                                    user_name=user_name)
        
        return redirect("/")
    
    return redirect("/")



# Random request id generate
def generate_random_id():
    return '-'.join(''.join(random.choices('0123456789abcdef', k=4)) for _ in range(5))

# Testing Apis
@PAN_OCR_bp.route("/test-api",methods=["POST"])
def Aadhaar_ocr_test_api():
    if request.method == "POST":

        # try:
            encrypted_token = session.get('QtSld')
            ip_address = session.get('KLpi')
            if session.get('bkjid') != "":

                check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})
                
                if check_user_in_db != None:
                    if check_user_in_db["total_test_credits"] > check_user_in_db["used_test_credits"]:
                        completed_on_ = datetime.now()
                        completed_on = datetime.now(pytz.timezone('Asia/Kolkata'))
                        completed_on = completed_on.strftime('%Y-%m-%dT%H:%M:%S%z')
                        completed_on = completed_on[:-2] + ':' + completed_on[-2:]
                        

                        aadhaar_img = request.files['aadhaar_img']
                        # Convert image to Base64
                        img_bytes = aadhaar_img.read()  # Read the image file as bytes
                        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
                        img_decoded = base64.b64decode(img_base64)

                        addhar_Card = pancard_main(img_decoded)

                        created_on = datetime.now(pytz.timezone('Asia/Kolkata'))
                        created_on = created_on.strftime('%Y-%m-%dT%H:%M:%S%z')
                        created_on = created_on[:-2] + ':' + created_on[-2:]


                        duration = datetime.now()- completed_on_ 
                        duration_seconds = duration.total_seconds()

                        store_response = {"status_code": 200,
                                            "status": "Success",
                                            "response":addhar_Card['response'],
                                            "created_on" : created_on,
                                            "completed_on":completed_on,
                                            "request_id":generate_random_id(),
                                            }
                        # DataBase Log
                        User_test_Api_history_db.insert_one({
                                    "user_id":check_user_in_db["_id"],
                                    "User_Unique_id":"Api Call From Dashboard",
                                    "api_name":"Aadhaar_OCR",
                                    "api_start_time":completed_on_,
                                    "api_end_time":datetime.now(),
                                    "api_status": "Success",
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "request_data":str({}),
                                    "response_data" :str(store_response),
                                    "creadted_on":datetime.now(),
                                    "System_Generated_Unique_id" : str(uuid.uuid4()),
                                    })
                        
                        # Check Api Using Credits
                        api_use_credit_info = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3a9ce1846511541492")})
                            
                        if check_user_in_db["unlimited_test_credits"] == False:
                            # Credit 
                            User_Authentication_db.update_one({"_id":check_user_in_db["_id"]},{"$set":{
                                "used_test_credits": check_user_in_db["used_test_credits"] + api_use_credit_info["credits_per_use"]
                            }})

                        return jsonify({"data":
                                        {"json_data": store_response,
                                        "result_in_seconds":duration_seconds}})

                    else:
                        return jsonify({"data":{
                                "status_code": "400",
                                "status": "Error",
                                "response":"You have zero credits left, please pay for more credits!"
                            }})
                    
                return jsonify({"data":{"json_data":"Something went wrong!"}})
            
            return jsonify({"data":{"json_data":"Something went wrong!"}})
        
    #     except:
    #         return redirect("/")
    
    # return jsonify({"msg":"method Not allowed!"})




