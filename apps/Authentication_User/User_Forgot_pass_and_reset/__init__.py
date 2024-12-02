from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta , datetime, timezone
from cryptography.fernet import Fernet
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
import random
import string

# DataBase
from data_base_string import *


# Blueprint
User_Forgot_pass_and_reset_bp = Blueprint("User_Forgot_pass_and_reset_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")


# Database 
Authentication_db = Regtch_services_UAT["User_Authentication"]



# Veriy Token Link Expired
@User_Forgot_pass_and_reset_bp.route("/password_reset",methods=["GET","POST"])
def Token_Is_Expired_Unauth():
    
    return render_template("reset_password.html")


# Sent Email
def user_to_sent_mail(receiver_emailid , token_url,Reciver_name):
    sender_email = "verification@bluBeetle.ai"
    subject = "Reset Your Password"
    token_url = token_url

    print(token_url)


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
                                
                                    <p style="text-align: left; line-height: 17px;">We received a request to reset the password for your """+Reciver_name+""" account. If you requested this reset, please click the link below to set up a new password. </p>
                                    <p style="text-align: left; line-height: 17px;"> </p>
                                    <p style="text-align: left; line-height: 0px;">&nbsp;</p>
                                    <a href='"""+token_url+"""' target="_blank"><b>
                                                                <span style="font-size: 10.5pt;
                                                                color: white;
                                                                background: #139AF6;
                                                                text-decoration: none;
                                                                padding: 0.1in 0.1in;
                                                                border-radius: 0.1in;
                                                                ">Click Here</span></b></a>
                                    <p style="text-align: left; line-height: 17px;">For security, this link will expire in 5 minutes. If it expires, please request a new password reset.</p>                                    
                                    <p style="text-align: left; line-height: 17px;">If you didn’t request a password reset, no further action is required. Your account remains secure, and you can ignore this email.</p>
                                    <p style="text-align: left; line-height: 17px;">If you have any questions or need assistance, please reach out to our support team at info@bluebeetle.ai</p>
                                    <br> 
                                    <p style="text-align: left; font-weight: bold;">Thank you,<br>
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


# ReGenerate Token 120 character
def generate_token(length=120):
    characters = string.ascii_letters + string.digits
    token = ''.join(random.choice(characters) for _ in range(length))
    return token


@User_Forgot_pass_and_reset_bp.route("/email-verification",methods=["POST"])
def email_verification():
    if request.method == "POST":
        try:
            if request.form["Email_Id"] != "":
                database_document = Authentication_db.find_one({"Email_Id":request.form['Email_Id']})
                if database_document != None:
                    verify_token = generate_token()

                    Authentication_db.update_one({"_id":database_document['_id']},
                                                 {"$set":{"verify_token":"HceTgeR."+ verify_token,
                                                          "token_expired_time_duration_min":5,
                                                          "verify_token_create_date" : datetime.now(),
                                                          "flag":0,
                                                          }})
                    
                    url_for_token_verify = "https://regtech.bluBeetle.ai/verify?token=" + "HceTgeR."+ verify_token
                    user_mail_verify = user_to_sent_mail(database_document['Email_Id'],url_for_token_verify,database_document['Company_Name'])

                    if user_mail_verify["data"] == "SuccessFully Mail Sent!":
                        return jsonify({"data":{"response":"We have sent a Password reset link to this email! Password link will expire in 5 minutes!",
                                                    "status":"Success",
                                                    "status_code":200
                                                    }})
                    else:
                        return jsonify({"data":{"response":"Email ID entered is invaild, please check the id entered or retry!",
                                                "status":"Success",
                                                "status_code":400
                                                }})
                    
                else:
                    return jsonify({"data":{"response":"Email ID entered is invaild, please check the id entered or retry!",
                                                "status":"Success",
                                                "status_code":400
                                                }})
                
            return jsonify({"data":{"response":"Incorrect email id. Please try again!",
                                                "status":"Success",
                                                "status_code":400
                                                }})


        except:
            return jsonify({"data":{"response":"Something Want Wrong!",
                                                    "status":"Success",
                                                    "status_code":400
                                                    }})




