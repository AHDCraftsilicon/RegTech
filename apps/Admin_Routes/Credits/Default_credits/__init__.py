from flask import Blueprint, render_template,request,redirect,flash,jsonify,session
from flask_jwt_extended import jwt_required,get_jwt
from datetime import timedelta
from cryptography.fernet import Fernet
from bson import ObjectId
from datetime import datetime

# DataBase
from data_base_string import *

# Blueprint
Default_credits_bp = Blueprint("Default_credits_bp",
                        __name__,
                        url_prefix="/BBRgt",
                        template_folder="templates")


# Database 
Admin_Authentication_db = Regtch_services_UAT["Admin_Authentication"]
User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]


# Given User Credits Route
@Default_credits_bp.route("/default-credits")
def User_given_credits():
    try:
        am_bd_name = session.get('am_bd_name')
        admin_objid = session.get('am_bjde')

        name = ""
        if am_bd_name == "Admin_Authentication" and admin_objid != "":
                
            admin_details = Admin_Authentication_db.find_one({"_id":ObjectId(admin_objid)})

            if admin_details != None:
                name = admin_details["name"]


            return render_template("default_credits.html",
                                    name=name)
        return redirect("/BBRgt/admin-login-RRtggR")
    except:
        return redirect("/error")


# Given User Credits Data table
@Default_credits_bp.route("/count-credit-given/api")
def Give_credit_info_data_table():

    data = []
    for x in User_Testing_Credits_db.find():
        data.append({
            "total_credit":str(x['total_credit']),
            "created_on": str((x["created_on"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
            "updated_on": str((x["updated_on"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
            "objid":str(x['_id'])
        })


    return jsonify({"data":data})


# Credits History 
@Default_credits_bp.route("/credit-history/api")
def credit_history_api():

    db_details = User_Testing_Credits_db.find_one({"_id":ObjectId('66ecfbff621502ccf8852429')})

    data = []
    for x in db_details['credit_history']:
        data.append({
            "credit" : x['credit'],
            "created_on": str((x["created_on"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),        
            })

    return jsonify({"data":data})

# Credit details
@Default_credits_bp.route("/get-credit-details/<objid>")
def credit_details(objid):

    if objid != "":
        data_list = []
        try:
           db_details = User_Testing_Credits_db.find_one({"_id":ObjectId(objid)}) 
           data_list.append({
               "total_credit":db_details['total_credit']
           })
        
        except:
            pass


    return jsonify({"data":data_list})


# Credit details Edit
@Default_credits_bp.route("/given-credit/edit/<objid>",methods=["GET","POST"])
def given_credits_edit(objid):
    if request.method == "POST":

        get_user_details = get_jwt()

        get_details = User_Testing_Credits_db.find_one({"_id":ObjectId(objid)})

        if request.form['total_credit'] == get_details['total_credit']:
            flash("This credit has already been mentioned!")
            return redirect("/BBRgt/default-credits")

        User_Testing_Credits_db.update_one({"_id": ObjectId(objid)} , {"$set": { 
            "total_credit" : request.form['total_credit'],
            "updated_on":datetime.now()
        }})

        User_Testing_Credits_db.update_one({"_id": ObjectId(objid)} , {"$push": { 
            "credit_history" :{"credit":request.form['total_credit'],
                                "created_on":datetime.now(),
                                "created_by":ObjectId(get_user_details['sub']['objid'])
             }
        }})

        flash("Data Edit SuccessFully!")
        return redirect("/BBRgt/default-credits")