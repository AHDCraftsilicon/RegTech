from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,session
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import timedelta
from bson import ObjectId
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# DataBase
from data_base_string import *

# Token
from token_generation import *

# Blueprint
User_Admin_Api_Dashboard_bp = Blueprint("User_Admin_Api_Dashboard_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")


# Database 
User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
User_test_Api_history_db = Regtch_services_UAT['User_test_Api_history']
Api_Informations_db = Regtch_services_UAT["Api_Informations"]
additional_credits_db = Regtch_services_UAT["Additional_credits"]


@User_Admin_Api_Dashboard_bp.route("/dashboard")
def User_Api_Dashboard_main():

    try:
        encrypted_token = session.get('QtSld')
        ip_address = session.get('KLpi')

        if session.get('bkjid') != "":

            check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})

            if check_user_in_db != None:
                

                if encrypted_token and ip_address:
                    token = decrypt_token(encrypted_token)

                    page_name = "Home"

                    user_type = "Test Credits"

                    if check_user_in_db['user_flag'] == "0":
                        user_type = "Live Credits"
                    
                    api_info = Api_Informations_db.find()
                        
                    api_list = []
                    objid_list = []
                
                    for x in api_info:
                        api_list.append({
                            "api_name":x["api_name"],
                            "long_api_description":x["long_api_description"],
                            "sort_api_description":x["sort_api_description"],
                            "api_logo": x["api_logo"],
                            "page_url":x["page_url"],
                            "status":x["status"],
                            "view_permission":x["view_permission"],
                            "created_on":str((x["created_on"]).strftime("%d-%m-%Y %H:%M:%S")),
                            "objid":str(x["_id"])
                        })

                        objid_list.append({
                            "objid":str(x["_id"])
                        })

                    user_name = check_user_in_db["Company_Name"]
                    page_info = [{"Test_Credit": check_user_in_db["total_test_credits"],
                                "Used_Credits":check_user_in_db["used_test_credits"] ,
                                "user_type" : user_type ,
                                "page_name":page_name,
                                "user_name": user_name
                                }]
                    return render_template("Api_dashboard.html",
                                api_list=api_list,api_count = objid_list,
                                page_info=page_info,
                                user_details={"user_name": user_name,
                                                      "Email_Id":check_user_in_db['Email_Id'],
                                                    "user_type" :user_type},)
            
            return redirect("/")
        
        return redirect("/")
    
    except:
        return redirect("/error")
    

# Request for additional credits
def request_for_additional_credits(receiver_emailid,Company_Name):
    sender_email = "verification@bluBeetle.ai"
    subject = "Request for additional credits"

    html_body = """<table style="width: 100%;">
                        <tbody>
                            <tr>
                                <td style="text-align: center; padding: 10px 10px;" colspan="2">
                                    <p style="text-align: left;"><b> Dear bluBeetle.ai,</b></p>
                                    <p style="text-align: left; line-height: 17px;">We kindly request additional credits. This will enable us ensure smooth operations.</p>
                                    <p style="text-align: left;"><b>Thanks and Regards,</b></p>
                                    <p style="text-align: left;">"""+Company_Name+"""</p>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                """
    
    msg = MIMEMultipart()
    msg.attach(MIMEText(html_body, "html"))

    # Gmail SMTP server details
    smtp_server = "secure.emailsrvr.com"
    smtp_port = 587
    password = "4TT1rP8rex1X"  # Use App-specific password for better security

    # Create the email
    msg["From"] = receiver_emailid
    msg["To"] = sender_email
    msg["Subject"] = subject

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        
        # Send the email
        server.sendmail(sender_email, receiver_emailid, msg.as_string())
        return {"data":"SuccessFully Mail Sent!"}
        
    except Exception as e:
        return {"data":"Error Email ID Is Wrong!"}


@User_Admin_Api_Dashboard_bp.route("/request-for-more/credits")
def more_credits_email_sent():

    try:
        encrypted_token = session.get('QtSld')
        ip_address = session.get('KLpi')

        if session.get('bkjid') != "":

            check_user_in_db = User_Authentication_db.find_one({"_id":ObjectId(session.get('bkjid'))})

            if check_user_in_db != None:

                if encrypted_token and ip_address:
                    token = decrypt_token(encrypted_token)

                    user_mail_verify = request_for_additional_credits(check_user_in_db['Email_Id'],check_user_in_db['Company_Name'])

                    additional_credits_db.insert_one({
                        "user_id": check_user_in_db['_id'],
                        "granted_credits":False,
                        "created_on":datetime.now(),
                        "granted_date":""
                    })
                    
                    if user_mail_verify["data"] == "SuccessFully Mail Sent!":
                        return jsonify({"status_code": 200,
                                "status": "Success",
                                "response": "Thank you for your request!"}),200
                    else:
                        return jsonify({"status_code": 400,
                                "status": "Error",
                                "response": "Something went wrong!"}),400


            return redirect("/")
        return redirect("/")
    except:
        return redirect("/error")

    


       
    

    



    


