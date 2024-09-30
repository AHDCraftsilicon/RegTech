from flask import Blueprint, render_template,request,redirect,flash,session,make_response
from datetime import timedelta
from cryptography.fernet import Fernet
import base64
import jwt
from datetime import datetime, timedelta

# DataBase
from data_base_string import *

# token
from token_generation import *

# Blueprint
User_Admin_SignIn_bp = Blueprint("User_Admin_SignIn_bp",
                        __name__,
                        url_prefix="/login",
                        template_folder="templates")

# Database 
Authentication_db = Regtch_services_UAT["User_Authentication"]



@User_Admin_SignIn_bp.route("/user")
def User_Admin_SignIn_Main():

    return render_template("SingIn.html")



# Decrypt the password using the secret key
def decrypt_password(encrypted_password, secret_key):
    cipher_suite = Fernet(secret_key)
    decrypted_password = cipher_suite.decrypt(encrypted_password)
    return decrypted_password.decode('utf-8')

# Convert Base64 string to binary
def base64_to_binary(base64_str):
    return base64.b64decode(base64_str)



@User_Admin_SignIn_bp.route("/auth/singin",methods=["POST"])
def User_Admin_validate_check():

    
    if request.method == "POST":
        if request.form["Email_ID"] != "" and request.form["Password"] != "":
            email_check_db =  Authentication_db.find_one({"Email_Id" :request.form["Email_ID"]})

            if email_check_db != None:
                try:
                    encrypted_password_binary = base64_to_binary(email_check_db["encrypted_pass"])
                    secret_key_binary = base64_to_binary(email_check_db["secret_key_pass"])

                    decrypt_pass = decrypt_password(encrypted_password_binary,secret_key_binary)
                    if decrypt_pass == request.form["Password"]:
                        
                    
                        token = 'dDoLeSwTObEc4q6jmXhIDe70bZEvQwauIndiapu94wFMF8fUHkycci9dD6RJG2Tu26FjTs64RtqD9KO'  # Replace with actual token
                        encrypted_token = encrypt_token(token)
                        ip_address = request.remote_addr
                        session['QtSld'] = encrypted_token
                        session['KLpi'] = ip_address  
                        session['lmin'] = False
                        session['bkjid'] = str(email_check_db['_id'])

                        return redirect("/dashboard")
                    else:
                        flash('Incorrect email or password. Please try again.')
                        return redirect("/login/user")
                except:
                    flash('Incorrect email or password. Please try again.')
                    return redirect("/login/user")

            else:
                flash('Incorrect email or password. Please try again.')
                return redirect("/login/user")



            # remove after work





            




