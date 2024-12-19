from flask import Blueprint, render_template,request,redirect,flash,jsonify,session
from flask_jwt_extended import jwt_required,get_jwt
from datetime import timedelta
from cryptography.fernet import Fernet
from bson import ObjectId
from flask_socketio import SocketIO, emit
from datetime import datetime

# DataBase
from data_base_string import *

# Blueprint
Admin_Users_Info_bp = Blueprint("Admin_Users_Info_bp",
                        __name__,
                        url_prefix="/BBRgt",
                        template_folder="templates")



# Database 
Admin_Authentication_db = Regtch_services_UAT["Admin_Authentication"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
pincodes_db = Regtch_services_UAT["pincodes"]
Api_Informations_db = Regtch_services_UAT["Api_Informations"]
Production_User_db = Regtch_services_UAT["Production_User"]
Test_user_api_history_db = Regtch_services_UAT['Test_user_api_history']
additional_credits_db = Regtch_services_UAT["Additional_credits"]
Prod_user_api_history_db = Regtch_services_UAT['Prod_user_api_history']



# Socket
def init_socketio(socketios):
    
    # Get user objid and return response user flag
    @socketios.on('user_objid',namespace='/')
    def check_user_flag(data):
        if(data['data'] != ""):
            user_info = User_Authentication_db.find_one({"_id":ObjectId(data['data'])})
            if user_info != None:
                emit('flag_info', {'data': {"user_flag":user_info['user_flag'],
                                            "Company_Name":user_info['Company_Name'],
                                            "Mobile_No":user_info['Mobile_No'],
                                            "Email_Id":user_info['Email_Id'],}})
        
    # Set User Flag in db
    @socketios.on('set_user_flag',namespace='/')
    def set_user_flag(data):
        if data['data']['user_objid'] != "":
            User_Authentication_db.update_one({"_id":ObjectId(data['data']['user_objid'])},
                                              {"$set":{"user_flag":data['data']['user_flag']}})
            
    # Password Verification
    @socketios.on('validate_pass',namespace='/')
    def validate_pass_msg(data):
        if data['data'] != "":
            # CraftsMakarba@380051
            if data['data'] == "1234":
                emit("verify_identity",{"data":{"status":200,'msg':"Go ahead"}})
            else:
                # password wrong
                emit("verify_identity",{"data":{"status":400,'msg':"Wrong Password!"}})
        # enter valid password
        # else:
        #     emit("verify_identity",{"data":{"status":400,'msg':"Please Enter Password!"}})

    # Set Flag DB
    @socketios.on('flag_setter',namespace='/')
    def flag_setter(data):
        if data['data'] != "":
            tester_flag = False
            if data['data']['tester_flag'] == "True":
                tester_flag = True
            User_Authentication_db.update_one({"_id":ObjectId(data['data']['user_objid'])},
                                              {"$set":{"tester_flag":tester_flag,
                                                       "user_status":data['data']['user_status'],
                                                       "api_flag":data['data']['api_flag'],
                                                        }})
            emit("configure_flag",{"data":{"status":200,'msg':"Go ahead"}})


def get_previous_month_dates():
    # Get the current date
    today = datetime.today()
    
    # Get the first day of the current month
    first_day_of_current_month = today.replace(day=1)
    
    # Get the last day of the previous month by subtracting one day
    last_day_of_previous_month = first_day_of_current_month - timedelta(days=1)
    
    # Get the first day of the previous month
    first_day_of_previous_month = last_day_of_previous_month.replace(day=1)
    
    return first_day_of_previous_month, last_day_of_previous_month

# User Route
@Admin_Users_Info_bp.route("/user-details")
def admin_user_info():
    try:

        am_bd_name = session.get('am_bd_name')
        admin_objid = session.get('am_bjde')

        name = ""
        if am_bd_name == "Admin_Authentication" and admin_objid != "":
                
            admin_details = Admin_Authentication_db.find_one({"_id":ObjectId(admin_objid)})

            user_list = []
            user_details = User_Authentication_db.aggregate([{
                                        '$project': {
                                            'Company_Name': -1, 
                                            'id_str': {
                                                '$toString': '$_id'
                                            }}}])
            
            for x in list(user_details):
                user_list.append({"Company_Name":x['Company_Name'],"objid":x['id_str']})

            if admin_details != None:
                name = admin_details["name"]


            return render_template("Users_info.html",
                                    name=name , user_list=user_list,
                                    )
        return redirect("/BBRgt/admin-login-RRtggR")
    except:
        return redirect("/error")



# User Data-Table
@Admin_Users_Info_bp.route("/user-details/data-table",methods=["GET","POST"])
def Admin_usersinfo_data_table():
    quiry = {}
    dictinory = []
    
    sort_quiry = {"created_date" : 1}

    # Searching
    if request.form['columns[0][search][value]'] != "":
        quiry = {'_id': ObjectId(request.form['columns[0][search][value]'])}

    if request.form['columns[1][search][value]'] != "":
        quiry = {"Mobile_No":{"$regex":request.form['columns[1][search][value]'],"$options": "i"}}

    if request.form['columns[2][search][value]'] != "":
        quiry = {"Email_Id":{"$regex":request.form['columns[2][search][value]'],"$options": "i"}}

    if request.form['columns[3][search][value]'] != "":
        quiry = {"user_type":request.form['columns[3][search][value]']}

    if request.form["columns[4][search][value]"] != "":
        if datetime.now().date() == datetime.strptime(request.form["columns[4][search][value]"].split(" - ")[0], "%d-%m-%Y").date():
            quiry["created_date"] = {"$gte": datetime.strptime(
                request.form["columns[4][search][value]"].split(" - ")[0], "%d-%m-%Y")}
        elif (datetime.now().date() - timedelta(days=1)) == datetime.strptime(request.form["columns[4][search][value]"].split(" - ")[0], "%d-%m-%Y").date():
            quiry["created_date"] = {
                "$gte": datetime.strptime(request.form["columns[4][search][value]"].split(" - ")[0], "%d-%m-%Y"),
                "$lt": (datetime.strptime(request.form["columns[4][search][value]"].split(" - ")[0], "%d-%m-%Y")+timedelta(hours=23, minutes=59, seconds=59))
            }
        else:
            quiry["created_date"] = {
                "$gte": datetime.strptime(request.form["columns[4][search][value]"].split(" - ")[0], "%d-%m-%Y"),
                "$lt": (datetime.strptime(request.form["columns[4][search][value]"].split(" - ")[1], "%d-%m-%Y")+timedelta(hours=23, minutes=59, seconds=59))
            }

    # Sorting
    try:
        if request.form['order[0][column]'] == '4':
            if request.form['order[0][dir]'] == 'asc':
                sort_quiry = {"created_date" : 1}
            else:
                sort_quiry = {"created_date" : -1}
    except:
        pass

    try:
        skp = int(int(request.form['start']) / int(request.form['length'])) - int(request.form['length'])
    except (KeyError, ValueError, ZeroDivisionError) as e:
        skp = 0  # default value if calculation fails
 
        
    if skp < 0:
        skp = 0
    per_page = int(request.form['length'])
    if per_page < 0:
        per_page = None

    finding = User_Authentication_db.aggregate([        
        {"$match": quiry},
        {'$sort': sort_quiry},
        {"$skip": int(request.form['start'])},
        {"$limit": int(request.form['length'])}
    ])

    dictinory = []
    for x in finding:
        
        dictinory.append(
            {
                "Company_Name":x["Company_Name"],
                "Mobile_No":x["Mobile_No"],
                "Email_Id":x["Email_Id"],
                "user_type":x["user_type"],
                "created_date": str((x["created_date"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
                "objid":str(x["_id"]),
            }
        )
        
    try:
        if quiry == {}:
            total_data = User_Authentication_db.estimated_document_count()
        else:
            total_data = User_Authentication_db.count_documents(quiry)
    except Exception as e:
        total_data = 0  # or any other default value or handling you prefer

        
    data = {"iTotalDisplayRecords": total_data,
            'aaData': dictinory,
            "iTotalRecords": total_data/int(request.form['length']),
                }
    
    return jsonify(data) 



# Edit prod User Details 
@Admin_Users_Info_bp.route("/edit-prod-user/<objid>",methods=["GET","POST"])
def edit_prod_user_details(objid):
    # try:

        am_bd_name = session.get('am_bd_name')
        admin_objid = session.get('am_bjde')

        name = ""
        if am_bd_name == "Admin_Authentication" and admin_objid != "":
                
            admin_details = Admin_Authentication_db.find_one({"_id":ObjectId(admin_objid)})
            user_info = User_Authentication_db.find_one({"_id":ObjectId(objid)})

            if user_info != None:
                user_info_details= { "Company_Name":user_info['Company_Name'],
                                                        "Mobile_No":user_info['Mobile_No'],
                                                        "Email_Id":user_info['Email_Id']}

                state_info = pincodes_db.aggregate([{
                    '$group': {
                        '_id': {
                            'STATE': '$STATE'
                        }}}])
                state_list = []
                for x in state_info:
                    state_list.append({"state":x['_id']['STATE']})


                list_of_api = []
                api_list = Api_Informations_db.aggregate([{
                                            '$project': {
                                                'api_name': -1, 
                                                'id_str': {
                                                    '$toString': '$_id'
                                                }}}])
                
                for x in list(api_list):
                    list_of_api.append({"api_name":x['api_name'],"objid":x['id_str']})

                prod_user = Production_User_db.find_one({"production_user":user_info['_id']})
                prod_user_dic = {}

                if prod_user != None:
                    prod_user_dic['bussiness_name'] = prod_user['bussiness_name']
                    prod_user_dic['PAN_number'] = prod_user['PAN_number']
                    prod_user_dic['TAN_number'] = prod_user['TAN_number']
                    prod_user_dic['name_of_contact_person'] = prod_user['name_of_contact_person']
                    prod_user_dic['designation_of_contact_person'] = prod_user['designation_of_contact_person']
                    prod_user_dic['email_id'] = prod_user['email_id']
                    prod_user_dic['contact_number'] = prod_user['contact_number']
                    prod_user_dic['register_address'] = prod_user['register_address']
                    prod_user_dic['correspondence_address'] = prod_user['correspondence_address']
                    prod_user_dic['api_retails'] = prod_user['api_retails']
                    prod_user_dic['same_to_registered_address'] = prod_user['same_to_registered_address']
                    
                    # print(prod_user)
                
                else:
                    pass


                return render_template("Prod_user_edit_details.html",
                                    state_list=state_list , list_of_api=list_of_api ,
                                    user_info_details=user_info_details,
                                    prod_user_dic=prod_user_dic,objid=objid)
            else:
                return jsonify({"status_code": 404,
                                        "status": "Error",
                                        "response": "The requested resource or endpoint doesn’t exist!"}) , 404 
        return redirect("/BBRgt/admin-login-RRtggR")
    # except:
    #     return redirect("/error")



# Edit prod User Details 
@Admin_Users_Info_bp.route("/edit-prod-user/form/<objid>",methods=["GET","POST"])
def edit_prod_user_form_details(objid):
    try:
        if request.method == "POST":
            if objid != "":
                user_details = User_Authentication_db.find_one({"_id":ObjectId(objid)})
                if user_details != None:
                    print(user_details['_id'])
                    prod_user = Production_User_db.find_one({"production_user":ObjectId(user_details['_id'])})
                    
                    # Update Document
                    if prod_user != None:
                        try:
                            request.form['same_to_registered_address']
                            same_to_registered_address = True
                        except:
                            same_to_registered_address = False
                        
                        if same_to_registered_address == True:
                            correspondence_address = [{"correspond_address1":request.form['register_address1'],
                                                "correspond_address2":request.form['register_address2'],
                                                "correspond_address3":request.form['register_address3'],
                                                "correspond_country":request.form['register_country'],
                                                "correspond_pincode":request.form['register_pincode'],
                                                "correspond_state":request.form['register_state'],
                                                "correspond_city":request.form['register_city']}]
                        else:
                            correspondence_address = [{"correspond_address1":request.form['correspond_address1'],
                                                "correspond_address2":request.form['correspond_address2'],
                                                "correspond_address3":request.form['correspond_address3'],
                                                "correspond_country":request.form['correspond_country'],
                                                "correspond_pincode":request.form['correspond_pincode'],
                                                "correspond_state":request.form['correspond_state'],
                                                "correspond_city":request.form['correspond_city']}]
                        
                        # Api Retails
                        api_retails = []
                        for x,y,z in zip(request.form.getlist('name_of_api'),request.form.getlist('api_pricing'),request.form.getlist('api_status')):
                            if x != "" and y != "" and z != "":
                                api_retails.append({"name_of_api":x,
                                                    "api_pricing":y,
                                                    "api_status":z})


                        Production_User_db.update_one({"_id":prod_user['_id']},{"$set":{
                            "bussiness_name" : request.form['bussiness_name'],
                            "PAN_number" : request.form['PAN_number'],
                            "TAN_number" : request.form['TAN_number'],
                            "name_of_contact_person" : request.form['name_of_contact_person'],
                            "designation_of_contact_person" : request.form['designation_of_contact_person'],
                            "email_id" : request.form['email_id'],
                            "contact_number" : request.form['contact_number'],
                            "register_address" : [{
                                                "register_address1":request.form['register_address1'],
                                                "register_address2":request.form['register_address2'],
                                                "register_address3":request.form['register_address3'],
                                                "register_country":request.form['register_country'],
                                                "register_pincode":request.form['register_pincode'],
                                                "register_state":request.form['register_state'],
                                                "register_city":request.form['register_city']}],
                            "correspondence_address" : correspondence_address,
                            "same_to_registered_address":same_to_registered_address,
                            "api_retails":api_retails,
                            "updated_on": datetime.now()
                            
                        }})

                        flash("Production Details Update Successfully!")
                        return redirect("/BBRgt/edit-prod-user/"+str(objid))
                    
                    # Insert Document
                    else:
                        try:
                            request.form['same_to_registered_address']
                            same_to_registered_address = True
                        except:
                            same_to_registered_address = False
                        
                        if same_to_registered_address == True:
                            correspondence_address = [{"correspond_address1":request.form['register_address1'],
                                                "correspond_address2":request.form['register_address2'],
                                                "correspond_address3":request.form['register_address3'],
                                                "correspond_country":request.form['register_country'],
                                                "correspond_pincode":request.form['register_pincode'],
                                                "correspond_state":request.form['register_state'],
                                                "correspond_city":request.form['register_city']}]
                        else:
                            correspondence_address = [{"correspond_address1":request.form['correspond_address1'],
                                                "correspond_address2":request.form['correspond_address2'],
                                                "correspond_address3":request.form['correspond_address3'],
                                                "correspond_country":request.form['correspond_country'],
                                                "correspond_pincode":request.form['correspond_pincode'],
                                                "correspond_state":request.form['correspond_state'],
                                                "correspond_city":request.form['correspond_city']}]
                        
                        # Api Retails
                        api_retails = []
                        for x,y,z in zip(request.form.getlist('name_of_api'),request.form.getlist('api_pricing'),request.form.getlist('api_status')):
                            if x != "" and y != "" and z != "":
                                api_retails.append({"name_of_api":x,
                                                    "api_pricing":y,
                                                    "api_status":z})

                        Production_User_db.insert_one({
                            "production_user": user_details['_id'],
                            "service" : "Enable",
                            "bussiness_name" : request.form['bussiness_name'],
                            "PAN_number" : request.form['PAN_number'],
                            "TAN_number" : request.form['TAN_number'],
                            "name_of_contact_person" : request.form['name_of_contact_person'],
                            "designation_of_contact_person" : request.form['designation_of_contact_person'],
                            "email_id" : request.form['email_id'],
                            "contact_number" : request.form['contact_number'],
                            "register_address" : [{
                                                "register_address1":request.form['register_address1'],
                                                "register_address2":request.form['register_address2'],
                                                "register_address3":request.form['register_address3'],
                                                "register_country":request.form['register_country'],
                                                "register_pincode":request.form['register_pincode'],
                                                "register_state":request.form['register_state'],
                                                "register_city":request.form['register_city']}],
                            "correspondence_address" : correspondence_address,
                            "same_to_registered_address":same_to_registered_address,
                            "api_retails":api_retails,
                            "created_on":datetime.now(),
                            "updated_on": datetime.now()
                        })

                        flash("Production Details Add Successfully!")
                        return redirect("/BBRgt/edit-prod-user/"+str(objid))

                else:
                    return jsonify({"status_code": 404,
                                    "status": "Error",
                                    "response": "The requested resource or endpoint doesn’t exist!"}) , 404 

    except:
        return jsonify({"status_code": 400,
                            "status": "Error",
                            "response": "An issue with the request syntax or parameters!"}) , 400 


# View prod User Details
@Admin_Users_Info_bp.route("/view-prod-user/<objid>",methods=["GET","POST"])
def view_prod_user_details(objid):
    # try:
        am_bd_name = session.get('am_bd_name')
        admin_objid = session.get('am_bjde')

        name = ""
        if am_bd_name == "Admin_Authentication" and admin_objid != "":
                
            admin_details = Admin_Authentication_db.find_one({"_id":ObjectId(admin_objid)})

            usr_details = User_Authentication_db.find_one({"_id":ObjectId(objid)})

            if usr_details['user_flag'] == "0":

                # Total Number of api counts
                total_api_count = Prod_user_api_history_db.aggregate([
                                    {
                                        '$match': {
                                            'user_id': ObjectId(usr_details['_id'])
                                        }
                                    }, {
                                        '$lookup': {
                                            'from': 'Api_Informations', 
                                            'localField': 'api_name', 
                                            'foreignField': '_id', 
                                            'as': 'api_details'
                                        }
                                    }, {
                                        '$group': {
                                            '_id': '$api_details', 
                                            'api_total': {
                                                '$sum': 1
                                            }
                                        }
                                    }, {
                                        '$sort': {
                                            'api_total': -1
                                        }
                                    }
                                ])
                
                api_count_list = []
                total_apis = 0
                for x in list(total_api_count):
                    total_apis += int(x['api_total'])
                    api_count_list.append({
                        "api_name" : x['_id'][0]['api_name'],
                        "count": x['api_total']
                    })

                
                # usr basic details
                usr_basic_details = {"Company_Name":usr_details['Company_Name'],
                                    "Mobile_No":usr_details['Mobile_No'],
                                    "Email_Id":usr_details['Email_Id'],
                                    "used_test_credits":usr_details['used_test_credits'],
                                    "user_type":usr_details['user_type'],
                                    "user_flag":usr_details['user_flag'],
                                    "api_status":usr_details['api_status'],
                                    "user_status":usr_details['user_status'],
                                    "tester_flag":usr_details['tester_flag'],
                                    "unlimited_test_credits":usr_details['unlimited_test_credits']
                                    }
                
                # Advance user details
                advance_user_details = {}
                prod_usr = Production_User_db.find_one({"production_user":ObjectId(usr_details['_id'])})
                if prod_usr != None:
                    api_retails = []
                    for x in prod_usr['api_retails']:
                        api_details = Api_Informations_db.find_one({"_id": ObjectId(x['name_of_api'])})
                        api_retails.append({"name_of_api":api_details['api'],
                                            "api_name" : api_details['api_name'],
                                            "api_objid" : str(api_details['_id']),
                                            "credits_per_use" : api_details['credits_per_use'],
                                            "api_pricing":x['api_pricing'],
                                            "api_status":x['api_status'],
                                            })

                    advance_user_details = {
                        "service" : prod_usr['service'],
                        "bussiness_name" : prod_usr['bussiness_name'],
                        "PAN_number" : prod_usr['PAN_number'],
                        "TAN_number" : prod_usr['TAN_number'],
                        "name_of_contact_person" : prod_usr['name_of_contact_person'],
                        "designation_of_contact_person" : prod_usr['designation_of_contact_person'],
                        "email_id" : prod_usr['email_id'],
                        "contact_number" : prod_usr['contact_number'],
                        "register_address" : prod_usr['register_address'],
                        "correspondence_address" : prod_usr['correspondence_address'],
                        "same_to_registered_address" : prod_usr['same_to_registered_address'],
                        "api_retails":api_retails,
                        "created_on" : prod_usr['created_on'],
                    }

                # Credit Request
                check_credit_req = list(additional_credits_db.find({"user_id":ObjectId(objid)}))

                granted_credit_details = []
                if len(check_credit_req) != 0:
                    for x in check_credit_req:
                        granted_credit_details.append({
                            "created_on": str((x["created_on"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
                            "granted_credits":x['granted_credits'],
                            "granted_date":x['granted_date']
                        })

                # Tester Flag Option
                tester_flag_options = [
                        {"value": True, "label": "True"},
                        {"value": False, "label": "False"},
                    ]

                # Api Flag Option
                api_flag_option = [
                    {"value":"Enable","label":"Enable"},
                    {"value":"Disable","label":"Disable"},
                ]

                # List of Api
                list_of_api = []
                api_list = Api_Informations_db.aggregate([{
                                            '$project': {
                                                'api_name': -1, 
                                                'id_str': {
                                                    '$toString': '$_id'
                                                }}}])
                
                for x in list(api_list):
                    list_of_api.append({"api_name":x['api_name'],
                                        "objid":x['id_str']})
                    
                # prev month
                start_of_prev_month, end_of_prev_month = get_previous_month_dates()
                query = {
                        'user_id': ObjectId(usr_details['_id']),
                        "created_on": {
                            "$gte": start_of_prev_month,
                            "$lt": end_of_prev_month + timedelta(days=1)  # Add one day to include the last day
                        }
                    }
                
                prior_month_results = Prod_user_api_history_db.find(query)

                # Prior Month Apis
                prior_month_count = len(list(prior_month_results))

                # Failed APIs
                fail_apis = Prod_user_api_history_db.aggregate([{
                                        '$match': {
                                            'user_id': ObjectId(objid), 
                                            'http_status': {
                                                '$ne': 200
                                            }}}])
                
                fail_apis_count = len(list(fail_apis))

                # Monthly Billing
                now = datetime.utcnow()
                start_of_month = datetime(now.year, now.month, 1)
                if now.month == 12:  # Handle December edge case
                    end_of_month = datetime(now.year + 1, 1, 1)
                else:
                    end_of_month = datetime(now.year, now.month + 1, 1)
                total_api_call_Count =  Prod_user_api_history_db.aggregate([
                                        {
                                            "$match": {
                                                "created_on": {"$gte": start_of_month, 
                                                               "$lt": end_of_month}
                                            }
                                        },
                                        {
                                            '$match': {
                                                'user_id': ObjectId(objid)
                                            }
                                        }, {
                                            '$group': {
                                                '_id': '$api_name', 
                                                'api_Call': {
                                                    '$sum': 1
                                                }
                                            }
                                        },
                                        { '$lookup': {
                                                'from': 'Api_Informations', 
                                                'localField': '_id', 
                                                'foreignField': '_id', 
                                                'as': 'api_details'
                                            }
                                        }
                                    ])
                
                
                api_and_count = []
                for x in total_api_call_Count:
                    # total_monthly_billing = int(x['api_Call']) * int(x['api_details'][0]['credits_per_use'])
                    api_and_count.append({"api_name": x['api_details'][0]['api_name'],
                                          "api": x['api_details'][0]['api'],
                                          "api_count" : x['api_Call'],
                                          "credit_per_use" : int(x['api_details'][0]['credits_per_use']),
                                          "api_objid" : str(x['_id'])
                                          })

                # Create a mapping of api_objid to api_pricing from list2
                api_pricing_map = {item['api_objid']: item['api_pricing'] for item in api_retails}

                # Add api_pricing to list1 based on matching api_objid
                for item in api_and_count:
                    item['api_pricing'] = api_pricing_map.get(item['api_objid'], 'Not Found')

                # Multiply Monthly Billing
                total_monthly_billing = 0 
                for x in api_and_count:
                    total_monthly_billing += int(x['api_count']) * int(x['credit_per_use']) * int(x['api_pricing'])                                   
                
                return render_template('Prod_user_view_details.html',
                                    usr_basic_details=usr_basic_details, objid =objid,
                                    api_count_list=api_count_list , total_apis = total_apis,
                                    advance_user_details = advance_user_details,
                                    granted_credit_details = granted_credit_details ,
                                    tester_flag_options=tester_flag_options ,
                                    api_flag_option=api_flag_option , list_of_api=list_of_api ,
                                    prior_month_count = prior_month_count , fail_apis_count = fail_apis_count ,
                                    total_monthly_billing = total_monthly_billing , api_and_count = api_and_count
                                    )
            return jsonify({"status": "error",
                            "message": "Invalid input. Please provide valid user data!",
                            "status_code": 400})
        
        return redirect("/BBRgt/admin-login-RRtggR")
    # except:
    #     return redirect("/error")

    


# Edit test User Details
@Admin_Users_Info_bp.route("/edit-test-user/<objid>",methods=["GET","POST"])
def edit_test_user_details(objid):

    try:
        am_bd_name = session.get('am_bd_name')
        admin_objid = session.get('am_bjde')

        name = ""
        if am_bd_name == "Admin_Authentication" and admin_objid != "":
                
            admin_details = Admin_Authentication_db.find_one({"_id":ObjectId(admin_objid)})

            return render_template('Test_user_edit_details.html')
        
        return redirect("/BBRgt/admin-login-RRtggR")
    except:
        return redirect("/error")

# View test User Details
@Admin_Users_Info_bp.route("/view-test-user/<objid>",methods=["GET","POST"])
def view_test_user_details(objid):
    try:
        am_bd_name = session.get('am_bd_name')
        admin_objid = session.get('am_bjde')

        name = ""
        if am_bd_name == "Admin_Authentication" and admin_objid != "":
                
            admin_details = Admin_Authentication_db.find_one({"_id":ObjectId(admin_objid)})

            usr_details = User_Authentication_db.find_one({"_id":ObjectId(objid)})

            if usr_details['user_flag'] == "1":

                # Total Number of api counts
                total_api_count = Test_user_api_history_db.aggregate([
                                    {
                                        '$match': {
                                            'user_id': ObjectId(usr_details['_id'])
                                        }
                                    }, {
                                        '$lookup': {
                                            'from': 'Api_Informations', 
                                            'localField': 'api_name', 
                                            'foreignField': '_id', 
                                            'as': 'api_details'
                                        }
                                    }, {
                                        '$group': {
                                            '_id': '$api_details', 
                                            'api_total': {
                                                '$sum': 1
                                            }
                                        }
                                    }, {
                                        '$sort': {
                                            'api_total': -1
                                        }
                                    }
                                ])
                
                api_count_list = []
                total_apis = 0
                for x in list(total_api_count):
                    total_apis += int(x['api_total'])
                    api_count_list.append({
                        "api_name" : x['_id'][0]['api_name'],
                        "count": x['api_total']
                    })


                # usr basic details
                usr_basic_details = {"Company_Name":usr_details['Company_Name'],
                                    "Mobile_No":usr_details['Mobile_No'],
                                    "Email_Id":usr_details['Email_Id'],
                                    "used_test_credits":usr_details['used_test_credits'],
                                    "user_type":usr_details['user_type'],
                                    "user_flag":usr_details['user_flag'],
                                    "api_status":usr_details['api_status'],
                                    "user_status":usr_details['user_status'],
                                    "tester_flag":usr_details['tester_flag'],
                                    "unlimited_test_credits":usr_details['unlimited_test_credits']
                                    }
                
                
                # Credit Request
                check_credit_req = list(additional_credits_db.find({"user_id":ObjectId(objid)}))

                granted_credit_details = []
                if len(check_credit_req) != 0:
                    for x in check_credit_req:
                        granted_credit_details.append({
                            "created_on": str((x["created_on"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
                            "granted_credits":x['granted_credits'],
                            "granted_date":x['granted_date']
                        })

                # Tester Flag Option
                tester_flag_options = [
                        {"value": True, "label": "True"},
                        {"value": False, "label": "False"},
                    ]

                # Api Flag Option
                api_flag_option = [
                    {"value":"Enable","label":"Enable"},
                    {"value":"Disable","label":"Disable"},
                ]

                # List of Api
                list_of_api = []
                api_list = Api_Informations_db.aggregate([{
                                            '$project': {
                                                'api_name': -1, 
                                                'id_str': {
                                                    '$toString': '$_id'
                                                }}}])
                
                for x in list(api_list):
                    list_of_api.append({"api_name":x['api_name'],
                                        "objid":x['id_str']})


                return render_template('Test_user_view_details.html',
                                    granted_credit_details =granted_credit_details,
                                    usr_basic_details=usr_basic_details, objid =objid,
                                    api_count_list=api_count_list,total_apis=total_apis,
                                    tester_flag_options=tester_flag_options ,
                                    api_flag_option=api_flag_option , list_of_api=list_of_api)
            
                                   
            return jsonify({"status": "error",
                            "message": "Invalid input. Please provide valid user data!",
                            "status_code": 400})
        
        return redirect("/BBRgt/admin-login-RRtggR")
    except:
        return redirect("/error")


# State & City using postal code
@Admin_Users_Info_bp.route("/pincode-details/<pincode>")
def State_city_details(pincode):

    if  pincode != "" and  len(pincode) == 6:

        pincode_details = pincodes_db.aggregate([{'$match': {
                        'POSTAL_CODE': int(pincode)
                    }}, {
                    '$group': {
                        '_id': {
                            'STATE': '$STATE', 
                            'city': '$city'
                        }}}, {
                    '$project': {
                        '_id': 0, 
                        'STATE': '$_id.STATE', 
                        'city': '$_id.city'}}])
        
        pins = list(pincode_details)
        
        if len(pins) != 0:

            return jsonify({"status_code": 200,
                                "status": "Success",
                                "response": {"State":pins[0]['STATE'],
                                             "City":pins[0]['city']
                                            }}) , 200
        else:
            return jsonify({"status_code": 400,
                            "status": "Error",
                            "response": "Please enter a valid pincode."}) , 400

    return jsonify({"status_code": 400,
                            "status": "Error",
                            "response": "Please enter a valid pincode."}) , 400

@Admin_Users_Info_bp.route("/Consumed-as-test_usr-api-details/<objid>",methods=["GET","POST"])
def Consumed_api_details(objid):
    quiry = {"user_id":ObjectId(objid)}
    dictinory = []
    
    sort_quiry = {}

    # Searching
    if request.form['columns[0][search][value]'] != "":
        quiry = {'request_id':{"$regex" : str(request.form['columns[0][search][value]']),"$options": "i"}}

    if request.form['columns[4][search][value]'] != "":
        quiry = {"api_name": ObjectId(request.form['columns[4][search][value]']) ,
                 "user_id":ObjectId(objid)
                 }

    # # Sorting
    try:
        if request.form['order[0][column]'] == '5':
            if request.form['order[0][dir]'] == 'asc':
                sort_quiry = {"created_on" : 1}
            else:
                sort_quiry = {"created_on" : -1}
    except:
        sort_quiry = {"created_on" : 1}

    try:
        skp = int(int(request.form['start']) / int(request.form['length'])) - int(request.form['length'])
    except (KeyError, ValueError, ZeroDivisionError) as e:
        skp = 0  # default value if calculation fails
 
        
    if skp < 0:
        skp = 0
    per_page = int(request.form['length'])
    if per_page < 0:
        per_page = None

    finding = Test_user_api_history_db.aggregate([    
        {"$match" : {"user_id":ObjectId(objid)}} ,   
        {"$match": quiry},
        {
        '$lookup': {
            'from': 'Api_Informations', 
            'localField': 'api_name', 
            'foreignField': '_id', 
            'as': 'api_info'
        }},
        {'$sort': sort_quiry},
        {"$skip": int(request.form['start'])},
        {"$limit": int(request.form['length'])}
    ])

    dictinory = []
    for x in finding:
        
        dictinory.append(
            {
                "request_id":x["request_id"],
                "request_on":str((x["request_on"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
                "response_on":str((x["response_on"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
                "http_status":x["http_status"],
                "api_name" : x['api_info'][0]['api'],
                "created_on":str((x["created_on"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y")),
                "objid":str(x["_id"]),
            }
        )
        
    try:
        if quiry == {}:
            total_data = Test_user_api_history_db.estimated_document_count()
        else:
            total_data = Test_user_api_history_db.count_documents(quiry)
    except Exception as e:
        total_data = 0  # or any other default value or handling you prefer

        
    data = {"iTotalDisplayRecords": total_data,
            'aaData': dictinory,
            "iTotalRecords": total_data/int(request.form['length']),
                }
    
    return jsonify(data) 


