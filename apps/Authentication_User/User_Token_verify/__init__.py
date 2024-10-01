from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta , datetime, timezone
from cryptography.fernet import Fernet
import base64

# DataBase
from data_base_string import *


# Blueprint
User_Token_Verify_bp = Blueprint("User_Token_Verify_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")


# Database 
Authentication_db = Regtch_services_UAT["User_Authentication"]



# Veriy Token Link Expired
@User_Token_Verify_bp.route("/verify/expired",methods=["GET","POST"])
def Token_Is_Expired_Unauth():
    
    return render_template("Link_Expired.html")


# Verify Token Page
@User_Token_Verify_bp.route("/verify",methods=["GET","POST"])
def User_Token_Verification_main():
    
    print(request.args.get("token"))
    if request.args.get("token") != None:
        database_document = Authentication_db.find_one({"verify_token":request.args.get("token")})
        
        print(database_document)
        if database_document != None:

            if database_document["flag"] == 1:
                return redirect("/login/user")

            now = datetime.now()

            time_str1 = str((database_document["verify_token_create_date"] +timedelta(hours=5,minutes=30)).strftime("%H:%M") )
            time_str2 = str(now.hour) + ":" + str(now.minute)

            time_format = "%H:%M"
            time1 = datetime.strptime(time_str1, time_format)
            time2 = datetime.strptime(str(time_str2), time_format)

            difference = (time2 - time1).total_seconds() / 60
            print("-------- ", difference)
            if difference > 30:
                return redirect("/verify/expired")

            
            
            start_time = datetime.strptime(str((database_document["creadte_date"]).strftime("%Y-%m-%d %H:%M:%S.%f")), '%Y-%m-%d %H:%M:%S.%f').replace(tzinfo=timezone.utc)

            current_time = datetime.now(timezone.utc)

            time_elapsed = current_time - start_time
      

            if time_elapsed >= timedelta(minutes=database_document["token_expired_time_duration_min"]):
                return redirect("/verify/expired")
            else:

                return render_template("User_Token_Verification.html")
        else:
            return redirect("/verify/expired")

    
    else:
        return redirect("/verify/expired")

   
# Secret Key Generate Automated Every Time
def generate_secret_key():
    key = Fernet.generate_key()
    return key


# Encrypt the password using the secret key
def encrypt_password(password, secret_key):
    cipher_suite = Fernet(secret_key)
    encrypted_password = cipher_suite.encrypt(password.encode('utf-8'))
    return encrypted_password


# Decrypt the password using the secret key
def decrypt_password(encrypted_password, secret_key):
    cipher_suite = Fernet(secret_key)
    decrypted_password = cipher_suite.decrypt(encrypted_password)
    return decrypted_password.decode('utf-8')

# Convert binary to Base64 string
def binary_to_base64(binary_data):
    return base64.b64encode(binary_data).decode('utf-8')


# Create Password
@User_Token_Verify_bp.route("/auth/pass/create",methods=["POST"])
def auth_create_pass():
    if request.method == "POST":
        if request.form["token"] == "":
            return jsonify({"redirect":"/verify/expired"})
        
        if request.form["token"] != "":
            print(request.form["token"])
            db_token_verify = Authentication_db.find_one({"verify_token":request.form["token"]})

            print(db_token_verify)
            if db_token_verify != None:
                print("---------")

                if request.form["Create_Password"] == request.form["Confirm_Password"]:
            
                    # Step 1: Generate a secret key
                    secret_key = generate_secret_key()
                    secret_key_str = binary_to_base64(secret_key)

                    # Step 2: Encrypt the password
                    encrypted = encrypt_password(request.form["Create_Password"], secret_key)
                    encrypted_password_str = binary_to_base64(encrypted)

                    # Step 3: Decrypt the password
                    # decrypted = decrypt_password(encrypted, secret_key)

                    # Store In DB
                    Authentication_db.update_one({"_id":db_token_verify["_id"]},
                                                 {"$set":{
                                                     "flag":1,
                                                     "secret_key_pass":secret_key_str,
                                                     "encrypted_pass":encrypted_password_str
                                                 }})
                    
                    # print(request.form["Create_Password"])
                    # print(request.form["Confirm_Password"])

                    return jsonify({"redirect":"/login/user"})
                else:
                    return jsonify({
                        "message": "Passwords do not match. Please ensure that both fields contain the same password. Please ensure that both fields contain the same password."
                    })

            else:
                print("Unauthorized")
                return jsonify({"redirect":"/verify/expired"})


        


    return jsonify({"data":""})