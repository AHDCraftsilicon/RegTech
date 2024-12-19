from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta , datetime
import random
import string
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from bson import ObjectId


# DataBase
from data_base_string import *

# Headers Verify
from Headers_Verify import *


# Blueprint
User_Admin_SignUp_bp = Blueprint("User_Admin_SignUp_bp",
                        __name__,
                        url_prefix="/register",
                        template_folder="templates")


# Database 
Authentication_db = Regtch_services_UAT["User_Authentication"]
User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]

# Generate Token 120 character
def generate_token(length=120):
    characters = string.ascii_letters + string.digits
    token = ''.join(random.choice(characters) for _ in range(length))
    return token

# Sent Email
def user_to_sent_mail(receiver_emailid , token_url,Reciver_name):
    sender_email = "verification@bluBeetle.ai"
    subject = "Complete Your Registration – Set Your Password"
    token_url = token_url


    html_body = f"""
            <table style="width: 655px;margin: 0 auto;font-family: sans-serif;font-size: 13px; padding: 10px; background-color: #ffffff; border: 1px solid #139af6; box-sizing: content-box; border-bottom: 5px solid #046ee4;">
                <tbody>
                <tr>
                    <td style="text-align: center; ">
                        <div>
                            <div style="width: 200px;margin: 0 auto;">
                                <img  src="cid:image1"  style="padding: 10px 15px;"
                               width="150">
                            </div>
                            <div style="width: 580px; margin: 0 auto;">
                                <div>                                    
                                </div>
                            </div>
                        </div>   
                    </td>
                </tr>
                <tr>
                    <td>
                        <table style="width: 100%;">
                            
                            <tbody>
                                
                                <tr>
                                <td style="text-align: center; padding: 10px 10px;" colspan="2">
                                
                                    <p style="text-align: left;"><b> Dear """+Reciver_name+""",</b></p>
                                
                                    <p style="text-align: left; line-height: 17px;">Welcome to bluBeetle! </p>
                                    <p style="text-align: left; line-height: 17px;"> </p>
                                    <p style="text-align: left; line-height: 17px;">You have successfully registered on our platform. To complete your setup and access your account, please set your password by clicking the button below:</p>
                                    <p style="text-align: left; line-height: 17px;">&nbsp;</p>
                                    <a href='"""+token_url+"""' target="_blank"><b>
                                                                <span style="font-size: 10.5pt;
                                                                color: white;
                                                                background: #139AF6;
                                                                text-decoration: none;
                                                                padding: 0.1in 0.1in;
                                                                border-radius: 0.1in;
                                                                ">Click Here</span></b></a>
                                    <p style="text-align: left; line-height: 17px;">&nbsp;</p>
                                    <p style="text-align: left; line-height: 17px;">For security reasons, this link is valid for the next 30 Minutes and will expire after that. If you do not complete the process within this time, you can request a new link by visiting our Portal.</p>
                                    
                                
                                    <p style="text-align: left; line-height: 17px;">Thank you for choosing bluBeetle. We look forward to serving you!</p>
                                    <br> 
                                    <p style="text-align: left; font-weight: bold;">Best regards,<br>

                                        bluBeetle Team</p>
                                </td>
                            </tr>
                        
                        
                            </tbody>
                        </table>
                    </td>
                </tr>
                
            
                </tbody>
            </table>
        """
    
    msg = MIMEMultipart()
    msg.attach(MIMEText(html_body, "html"))
    
    with open("./apps/static/images/small-logo.png", "rb") as img_file:
        img = MIMEImage(img_file.read())
        img.add_header('Content-ID', '<image1>')
        msg.attach(img)

    # Gmail SMTP server details
    smtp_server = "secure.emailsrvr.com"
    smtp_port = 587
    password = "4TT1rP8rex1X"  # Use App-specific password for better security

    # Create the email
    msg["From"] = sender_email
    msg["To"] = receiver_emailid
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




@User_Admin_SignUp_bp.route("/user/new",methods=["GET","POST"])
def User_Admin_Signup_Main():

    return render_template("SingUp.html")



@User_Admin_SignUp_bp.route("/usr/signup",methods=["POST"])
def User_Signup_api():
    if request.method == "POST":
        if request.form['Company_Name'] != "" and request.form["Mobile_No"] != "" and request.form["Email_Id"] != "":
            
            database_document = Authentication_db.find_one({"Email_Id":request.form['Email_Id']})
            
            mobile_number_check = Authentication_db.find_one({"Mobile_No":request.form['Mobile_No']})
            if database_document == None:

                if mobile_number_check == None:
                                
                    verify_token = generate_token()

                    url_for_token_verify = "http://192.168.10.121/verify?token=" + "HceTgeR."+ verify_token

                    user_mail_verify = user_to_sent_mail(request.form["Email_Id"],url_for_token_verify,request.form['Company_Name'])

                    test_credit = User_Testing_Credits_db.find_one({"_id":ObjectId("66ecfbff621502ccf8852429")})
                    if user_mail_verify["data"] == "SuccessFully Mail Sent!":
                        Authentication_db.insert_one({
                            # basic info
                            "Company_Name" : request.form['Company_Name'],
                            "Mobile_No" : request.form['Mobile_No'],
                            "Email_Id" : request.form['Email_Id'],
                            # verify token for pass (create, forgot)
                            "verify_token" : "HceTgeR."+ verify_token,
                            # password create or not check using this flag
                            "flag":0,
                            # when password forgot or create pass check expired time
                            "token_expired_time_duration_min":30,
                            # Token created date
                            "verify_token_create_date":datetime.now(),
                            # api access purpose 
                            "client_id" : generate_random_client_id(),
                            "client_secret_key" : generate_random_client_secret_key(),
                            # by default set credit in our authority
                            "total_test_credits":test_credit['total_credit'],
                            # first set default credit and after reduce credits 
                            "used_test_credits": test_credit['total_credit'],
                            # unlimited test credits set for tester
                            "unlimited_test_credits":False,
                            # if tester flag is true that means thius user crafts user
                            "tester_flag":False,
                            # default all user Test User
                            "user_type": "Test User",
                            # if user flag is 2 that mean this user only for testing purpose
                            "user_flag":"2",
                            # api status disable not access any api 
                            "api_status":"Enable",
                            # user tatus disable not access any user 
                            "user_status":"Enable",
                            "created_date":datetime.now(),
                        })

                        return jsonify({"data":{"response":"Verification link has been successfully sent on your registered email ID!",
                                                "status":"Success",
                                                "status_code":200
                                                }})
                    
                    else:
                        return jsonify({"data":{"response":"Email ID entered is invaild, please check the id entered or retry!",
                                                "status":"Success",
                                                "status_code":400
                                                }})
                
                else:
                    return jsonify({"data":{"response":"Mobile Number already exists, please try with a new Number!",
                                            "status":"Success",
                                            "status_code":400
                                            }})
                
                

            else:
                return jsonify({"data":{"response":"Email ID already exists, please try with a new ID!",
                                            "status":"Success",
                                            "status_code":409
                                            }})
        else:
            return jsonify({"data":{"response":"Please Enter All details!",
                                                "status":"Success",
                                                "status_code":409
                                                }})