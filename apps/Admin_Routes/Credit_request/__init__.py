from flask import Blueprint, render_template,request,redirect,flash,jsonify,session
from flask_jwt_extended import jwt_required,get_jwt
from datetime import timedelta
from cryptography.fernet import Fernet
from bson import ObjectId
from datetime import datetime
from flask_socketio import SocketIO, emit

# DataBase
from data_base_string import *

# Blueprint
Credit_request_bp = Blueprint("Credit_request_bp",
                        __name__,
                        url_prefix="/BBRgt",
                        template_folder="templates")



# Database 
Admin_Authentication_db = Regtch_services_UAT["Admin_Authentication"]
additional_credits_db = Regtch_services_UAT["Additional_credits"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
User_Testing_Credits_db = Regtch_services_UAT["User_Testing_Credits"]

def credit_req_socket(socketios):
    
    # Get user objid and return response user flag
    @socketios.on('basic_details',namespace='/')
    def check_user_flag(data):
        if(data['data'] != ""):
            credit_db = additional_credits_db.find_one({"_id":ObjectId(data['data'])})
            user_info = User_Authentication_db.find_one({"_id":ObjectId(credit_db['user_id'])})
            if user_info != None:
                emit('basic_flag', {'data': {"user_flag":user_info['user_flag'],
                                            "Company_Name":user_info['Company_Name'],
                                            "Mobile_No":user_info['Mobile_No'],
                                            "Email_Id":user_info['Email_Id'],}})
                
    # add more credits in db 
    @socketios.on('credits_add',namespace='/')
    def add_more_credits(data):
        if(data['data'] != ""):
            credit_db = additional_credits_db.find_one({"_id":ObjectId(data['data'])})
            user_info = User_Authentication_db.find_one({"_id":ObjectId(credit_db['user_id'])})
            if user_info != None:
                test_credit = User_Testing_Credits_db.find_one({"_id":ObjectId('66ecfbff621502ccf8852429')})
                User_Authentication_db.update_one({"_id":ObjectId(credit_db['user_id'])},
                                                  {"$set":{"used_test_credits":test_credit['total_credit']}})
                additional_credits_db.update_one({"_id":credit_db['_id']},
                                                 {"$set":{"granted_credits":True,"granted_date":datetime.now()}})
                emit('success_msg' ,'SuccessFully Add Credits!')

                

# Given User Credits Route
@Credit_request_bp.route("/credit-request")
def Credit_request_main():
    try:
        am_bd_name = session.get('am_bd_name')
        admin_objid = session.get('am_bjde')

        name = ""
        if am_bd_name == "Admin_Authentication" and admin_objid != "":
                
            admin_details = Admin_Authentication_db.find_one({"_id":ObjectId(admin_objid)})

            if admin_details != None:
                name = admin_details["name"]


            return render_template("credit_request.html",
                                    name=name)
        return redirect("/BBRgt/admin-login-RRtggR")
    except:
        return redirect("/error")
    

# Given User Credit Data-table
@Credit_request_bp.route("/credit-request/data-table",methods=["GET","POST"])
def Credit_request_data_table():

    quiry = {}
    sort_quiry = {"created_on":1}

    try:
        skp = int(int(request.form['start']) / int(request.form['length'])) - int(request.form['length'])
    except (KeyError, ValueError, ZeroDivisionError) as e:
        skp = 0  # default value if calculation fails
 
        
    if skp < 0:
        skp = 0
    per_page = int(request.form['length'])
    if per_page < 0:
        per_page = None


    finding = additional_credits_db.aggregate([{
                                '$lookup': {
                                    'from': 'User_Authentication', 
                                    'localField': 'user_id', 
                                    'foreignField': '_id', 
                                    'as': 'usr_detail'
                                }},
                                {"$match": quiry},
                                {'$sort': sort_quiry},
                                {"$skip": int(request.form['start'])},
                                {"$limit": int(request.form['length'])}
                                ])
    
    dictinory = []
    for x in finding:
        dictinory.append({
            "usr_comp_name" : x['usr_detail'][0]['Company_Name'],
            "usr_email": x['usr_detail'][0]['Email_Id'],
            "granted_credits":x['granted_credits'],
            "created_on": str((x["created_on"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
            "objid":str(x['_id']),
            "user_id":str(x['user_id'])
        })

    try:
        if quiry == {}:
            total_data = additional_credits_db.estimated_document_count()
        else:
            total_data = additional_credits_db.count_documents(quiry)
    except Exception as e:
        total_data = 0 

    data = {"iTotalDisplayRecords": total_data,
            'aaData': dictinory,
            "iTotalRecords": total_data/int(request.form['length']),
            }
    
    return jsonify(data)


