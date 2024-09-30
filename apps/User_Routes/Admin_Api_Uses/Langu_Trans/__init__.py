from flask import Blueprint, render_template,request,session,redirect
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta
from bson import ObjectId
import random
import pytz
from io import BytesIO
from werkzeug.utils import secure_filename
from googletrans import Translator , LANGUAGES
import uuid


# DataBase
from data_base_string import *

# Token
from token_generation import *


# Blueprint
Language_translate_bp = Blueprint("Language_translate_bp",
                        __name__,
                        url_prefix="/translate",
                        template_folder="templates")


User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
User_test_Api_history_db = Regtch_services_UAT['User_test_Api_history']
Api_Informations_db = Regtch_services_UAT["Api_Informations"]



# Translate
translator = Translator()



@Language_translate_bp.route("/language")
def Language_trans_main():

    encrypted_token = session.get('QtSld')
    ip_address = session.get('KLpi')

    if session.get('bkjid') != "":

        check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})

        if check_user_in_db != None:
            if encrypted_token and ip_address:
                token = decrypt_token(encrypted_token)

                about_api_details = Api_Informations_db.find_one({"_id":ObjectId("66ed0f3b9ce1846511541498")})

                test_credits = [{"Test_Credit": check_user_in_db["total_test_credits"],
                                        "Used_Credits":check_user_in_db["used_test_credits"]}]

                lang_list = []
                for code, lang in LANGUAGES.items():
                    lang_list.append({
                        "lang" : lang,
                        "lang_code" : code,
                    })

                user_name = check_user_in_db["Company_Name"]

                return render_template("language_translate_module.html",
                                        test_credit=test_credits ,
                                        lang_list=lang_list,
                                        user_name=user_name,
                                        about_api_details = about_api_details['long_api_description'])
        
        
        return redirect("/")
        

    return redirect("/")


# Random request id generate
def generate_random_id():
    return '-'.join(''.join(random.choices('0123456789abcdef', k=4)) for _ in range(5))




@Language_translate_bp.route('/test-api',methods=['POST'])
def Lang_Trans_test_api():
    if request.method == "POST":
        try:
            encrypted_token = session.get('QtSld')
            ip_address = session.get('KLpi')
            if session.get('bkjid') != "":

                check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})
                if check_user_in_db != None:
                    if check_user_in_db["total_test_credits"] >= check_user_in_db["used_test_credits"]:


                        completed_on_ = datetime.now()
                        completed_on = datetime.now(pytz.timezone('Asia/Kolkata'))
                        completed_on = completed_on.strftime('%Y-%m-%dT%H:%M:%S%z')
                        completed_on = completed_on[:-2] + ':' + completed_on[-2:]

                        chunks = [request.form["translate_textarea"][i:i+4900] for i in range(0, len(request.form["translate_textarea"]), 4900)]
                        all_string = ""
                        for chunk in chunks:
                            if chunk != "":
                                translation = translator.translate(chunk, src=request.form['FromLanguage'], dest=request.form['ToLanguage'])
                                if translation.text != "":
                                    all_string += translation.text



                        created_on = datetime.now(pytz.timezone('Asia/Kolkata'))
                        created_on = created_on.strftime('%Y-%m-%dT%H:%M:%S%z')
                        created_on = created_on[:-2] + ':' + created_on[-2:]


                        duration = datetime.now()- completed_on_ 
                        duration_seconds = duration.total_seconds()
                        if all_string != "":
                            store_response = { "status_code": 200,
                                                "status": "Success",
                                                "response": all_string,
                                                "created_on" : created_on,
                                                "completed_on":completed_on,
                                                "request_id":generate_random_id(),
                                                }
                            

                        modify_request_data = {
                                "translate_textarea" : request.form["translate_textarea"],
                            }
                        # DataBase Log
                        User_test_Api_history_db.insert_one({
                                    "user_id":check_user_in_db["_id"],
                                    "User_Unique_id":"Api Call From Dashboard",
                                    "api_name":"Lang_Translate",
                                    "api_start_time":completed_on_,
                                    "api_end_time":datetime.now(),
                                    "api_status": "Success",
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "request_data":str(modify_request_data),
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


                        return jsonify({"data":{"json_data": store_response,"result_in_seconds":duration_seconds}})

                    else:
                        return jsonify({"data":{
                                "status_code": 400,
                                "status": "Error",
                                "response":"You have zero credits left, please pay for more credits!"
                            }}), 400

                return jsonify({"data":{"json_data":"Something went wrong!"}})
            
            return jsonify({"data":{"json_data":"Something went wrong!"}})
        
        except:
            return redirect("/")
                 
    return jsonify({"msg":"method Not allowed!"})

