from flask import Blueprint, render_template,request,redirect,flash,jsonify,session
from flask_jwt_extended import jwt_required,get_jwt
from datetime import timedelta,datetime
from cryptography.fernet import Fernet
from bson import ObjectId


# DataBase
from data_base_string import *

# Blueprint
Production_User_bp = Blueprint("Production_User_bp",
                        __name__,
                        url_prefix="/BBRgt",
                        template_folder="templates")


# Database 
Admin_Authentication_db = Regtch_services_UAT["Admin_Authentication"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]
Production_User_db = Regtch_services_UAT["Production_User"]
Api_Informations_db = Regtch_services_UAT["Api_Informations"]



# Production Route
@Production_User_bp.route("/production-user")
def production_user_main():
    try:
        am_bd_name = session.get('am_bd_name')
        admin_objid = session.get('am_bjde')


        name = ""
        if am_bd_name == "Admin_Authentication" and admin_objid != "":
            
            admin_details = Admin_Authentication_db.find_one({"_id":ObjectId(admin_objid)})

            if admin_details != None:
                name = admin_details["name"]

            user_list = []
            user_details = User_Authentication_db.aggregate([{
                                        '$project': {
                                            'Email_Id': -1, 
                                            'id_str': {
                                                '$toString': '$_id'
                                            }}}])
            
            for x in list(user_details):
                user_list.append({"Email_Id":x['Email_Id'],"objid":x['id_str']})

            list_of_api = []
            api_list = Api_Informations_db.aggregate([{
                                        '$project': {
                                            'api_name': -1, 
                                            'id_str': {
                                                '$toString': '$_id'
                                            }}}])
            
            for x in list(api_list):
                list_of_api.append({"api_name":x['api_name'],"objid":x['id_str']})


            return render_template("production_user.html",
                                    name=name,user_list=user_list,
                                    list_of_api=list_of_api)

        return redirect("/BBRgt/admin-login-RRtggR")
    
    except:
        return redirect("/error")




# Api Info Data-Table
@Production_User_bp.route("/production-user/data-table",methods=["GET","POST"])
def Admin_production_user():

    quiry = {}
    dictinory = []
    
    sort_quiry = {"created_on":1}

    # searching
    if request.form['columns[1][search][value]'] != "":
        quiry = {'production_user': ObjectId(request.form['columns[1][search][value]'])}

    if request.form['columns[2][search][value]'] != "":
        quiry = {'service': request.form['columns[2][search][value]']}

    if request.form['columns[3][search][value]'] != "":
        quiry = {'bussiness_name': {"$regex":request.form['columns[3][search][value]'],"$options": "i"}}
    # try:
    #     if request.form['order[0][column]'] == '5':
    #         if request.form['order[0][dir]'] == 'asc':
    #             sort_quiry = {"created_on" : 1}
    #         else:
    #             sort_quiry = {"created_on" : -1}
    # except:
    #     pass

    # try:
    #     if request.form['order[0][column]'] == '6':
    #         if request.form['order[0][dir]'] == 'asc':
    #             sort_quiry = {"updated_on" : 1}
    #         else:
    #             sort_quiry = {"updated_on" : -1}
    # except:
    #     pass

    try:
        skp = int(int(request.form['start']) / int(request.form['length'])) - int(request.form['length'])
    except (KeyError, ValueError, ZeroDivisionError) as e:
        skp = 0  # default value if calculation fails
 
        
    if skp < 0:
        skp = 0
    per_page = int(request.form['length'])
    if per_page < 0:
        per_page = None

    finding = Production_User_db.aggregate([   
        {"$lookup": {
        "from": 'User_Authentication',
        "localField": 'production_user',
        "foreignField": '_id',
        "as": 'production_user_name'}},     
        {"$match": quiry},
        {'$sort': sort_quiry},
        {"$skip": int(request.form['start'])},
        {"$limit": int(request.form['length'])}
    ])

    dictinory = []
    for x in finding:        
        dictinory.append(
            {
                "production_user":x['production_user_name'][0]['Company_Name'],
                "Email_Id":x['production_user_name'][0]['Email_Id'],
                "service":x["service"],
                "bussiness_name":x["bussiness_name"],
                "name_of_contact_person":x["name_of_contact_person"],
                "api_count":"",
                "created_on": str((x["created_on"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
                "updated_on": str((x["updated_on"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
                "objid":str(x["_id"]),
            }
        )
        
    try:
        if quiry == {}:
            total_data = Production_User_db.estimated_document_count()
        else:
            total_data = Production_User_db.count_documents(quiry)
    except Exception as e:
        total_data = 0  # or any other default value or handling you prefer

        
    data = {"iTotalDisplayRecords": total_data,
            'aaData': dictinory,
            "iTotalRecords": total_data/int(request.form['length']),
            }
    
    return jsonify(data)





# Add Production
@Production_User_bp.route("/production-user/add",methods=["GET","POST"])
def new_user_for_production():
    if request.method == "POST":
        claims = get_jwt()

        if request.form['user_objid'] != "":

            user_details = User_Authentication_db.find_one({"_id":ObjectId(request.form['user_objid'])})

            if user_details != None:

                User_Authentication_db.update_one({"_id":user_details['_id']},
                                                  {"$set":{"user_type":"Production User"}})

                
                Production_User_db.insert_one({"production_user":user_details['_id'],
                                               "service" : "Enable",
                                               "bussiness_name":request.form["bussiness_name"],
                                               "name_of_contact_person":request.form["name_of_contact_person"],
                                               "designation_of_contact_person":request.form["designation_of_contact_person"],
                                               "email_id":request.form["email_id"],
                                               "contact_number":request.form["contact_number"],
                                               "PAN_number":request.form["PAN_number"],
                                               "TAN_number":request.form["TAN_number"],
                                               "registered_address":request.form["registered_address"],
                                               "correspondence_address":request.form["correspondence_address"],
                                               "api_retails":[],
                                               "created_on":datetime.now(),
                                               "updated_on":datetime.now(),
                                               })

                flash("Data Add SuccessFully!")
                return redirect("/BBRgt/production-user")
            
            flash("Verify Your User ID")
            return redirect("/BBRgt/production-user")
        
        
        flash("Please Select Production User!")
        return redirect("/BBRgt/production-user")



# Get Production Details
@Production_User_bp.route("/get/production-user/<objid>",methods=["GET"])
def get_production_details(objid):
    try:
        prod_details = Production_User_db.find_one({"_id":ObjectId(objid)})

        prod_list = []
        if prod_details != None:
            prod_list.append({
                "production_user":str(prod_details['production_user']),
                "service":prod_details['service'],
                "bussiness_name":prod_details['bussiness_name'],
                "name_of_contact_person":prod_details['name_of_contact_person'],
                "designation_of_contact_person":prod_details['designation_of_contact_person'],
                "email_id":prod_details['email_id'],
                "contact_number":prod_details['contact_number'],
                "PAN_number":prod_details['PAN_number'],
                "TAN_number":prod_details['TAN_number'],
                "registered_address":prod_details['registered_address'],
                "correspondence_address":prod_details['correspondence_address'],
                "objid":str(prod_details['_id'])
            })
        

            return jsonify({"status_code": 200,
                            "status": "Success",
                            "response": prod_list}) , 200
        else:
            return jsonify({"status_code": 404,
                            "status": "Error",
                            "response": "The requested resource or endpoint doesn’t exist!"}) , 404 


    except:
        return jsonify({"status_code": 400,
                            "status": "Error",
                            "response": "An issue with the request syntax or parameters!"}) , 400  
