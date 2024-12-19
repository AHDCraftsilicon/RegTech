from flask import Blueprint, render_template,request,session,redirect
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta
from bson import ObjectId
from flask_socketio import SocketIO, emit

# DataBase
from data_base_string import *

# Token
from token_generation import *

# Headers Verification
from Headers_Verify import *

# Blueprint
User_Admin_Api_Credentials_bp = Blueprint("User_Admin_Api_Credentials_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")




User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]


# Validate Client ID
def is_valid_uuid_client_id(custom_uuid: str) -> bool:
    try:
        # Split the custom UUID into part1 and part2
        part1, part2 = custom_uuid.split('/')

        # Check if part1 is a 12-character hexadecimal string
        if not re.fullmatch(r"[a-fA-F0-9]{12}", part1):
            return False

        # Check if part2 is a valid UUID
        uuid.UUID(part2)  # This will raise ValueError if part2 is not valid

        return True
    except (ValueError, AttributeError):
        return False
    
# Validate Secret Key
def is_valid_standard_uuid_secret_key(standard_uuid: str) -> bool:
    try:
        # Validate if the string is a proper UUID
        uuid.UUID(standard_uuid)  # This will raise ValueError if not valid
        return True
    except ValueError:
        return False

def api_Cred_socketio(socketios):
    
    # Get user objid and return response user flag
    @socketios.on('generate-trigger',namespace='/')
    def check_user_flag(data):
        if(data['data'] == "Trigger"):
            client_id =  generate_random_client_id()
            secret_key = generate_random_client_secret_key()
            emit("generate_suffle",{"data":{"status":200,
                                  "client_id" : client_id,
                                  "secret_key" : secret_key,
                                  }})
            
    # Change Client ID & Secret Key
    @socketios.on('save-credentials',namespace='/')
    def save_crential(data):
        if data['data']['client-id'] != "" and data['data']['client-secret'] != "":
            client_id =  is_valid_uuid_client_id(data['data']['client-id'])
            secret_key = is_valid_standard_uuid_secret_key(data['data']['client-secret'])
            if client_id == True and secret_key == True:
                User_Authentication_db.update_one({"_id":ObjectId(data['data']['objid'])},
                                                  {"$set":{"client_id": data['data']['client-id'],
                                                           "client_secret_key": data['data']['client-secret'],
                                                           "credential_changing_date": datetime.now(),
                                                            }}
                                                  )
                emit("change-msg",{"data":{"status":200}})
            else:
                emit("change-msg",{"data":{"status":400}})

@User_Admin_Api_Credentials_bp.route("/credentials")
def Api_Credentials_main():
    encrypted_token = session.get('QtSld')
    ip_address = session.get('KLpi')
    get_objid = session.get('bkjid')

    if session.get('bkjid') != "":

        check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})
        
        if check_user_in_db != None:

            if encrypted_token and ip_address:
                token = decrypt_token(encrypted_token)

                page_name = "Credentials"

                user_type = "Test Credits"

                if check_user_in_db['user_flag'] == "0":
                    user_type = "Live Credits"

                objid = str(check_user_in_db['_id'])

                user_name = check_user_in_db["Company_Name"]
                page_info = [{"Test_Credit": check_user_in_db["total_test_credits"],
                            "Used_Credits":check_user_in_db["used_test_credits"] ,
                            "user_type" : user_type,
                            "page_name":page_name,
                            "user_name": user_name
                            }]
                

                # Credentials
                sccess_id_key = [{"client_id":check_user_in_db['client_id'],
                                "client_secret_key" :check_user_in_db["client_secret_key"]}]
                

                return render_template('api_credentials.html',
                                        sccess_id_key=sccess_id_key,
                                        page_info=page_info,
                                        user_details={"user_name": user_name,
                                                      "Email_Id":check_user_in_db['Email_Id'],
                                                    "user_type" :user_type},
                                        objid = objid
                                        )
                        
                
            return redirect("/")
            
        return redirect("/")
    
    return redirect("/")



