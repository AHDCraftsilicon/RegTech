from flask import Blueprint, render_template,request,redirect,flash,jsonify,session
from flask_jwt_extended import jwt_required,get_jwt
from datetime import timedelta,datetime
from cryptography.fernet import Fernet
from bson import ObjectId
from datetime import timedelta


# DataBase
from data_base_string import *

# Blueprint
Admin_Api_informations_bp = Blueprint("Admin_Api_informations_bp",
                        __name__,
                        url_prefix="/BBRgt",
                        template_folder="templates")


# Database 
Admin_Authentication_db = Regtch_services_UAT["Admin_Authentication"]
Api_Informations_db = Regtch_services_UAT["Api_Informations"]


# Admin Api Information
@Admin_Api_informations_bp.route("/api-infos")
def admin_api_informations():
    try:

        am_bd_name = session.get('am_bd_name')
        admin_objid = session.get('am_bjde')

        name = ""
        if am_bd_name == "Admin_Authentication" and admin_objid != "":
                
            admin_details = Admin_Authentication_db.find_one({"_id":ObjectId(admin_objid)})

            if admin_details != None:
                name = admin_details["name"]


            return render_template("api_information.html",
                                    name=name)
        
        return redirect("/BBRgt/admin-login-RRtggR")
    
    except:
        return redirect("/error")


# Api Info Data-Table
@Admin_Api_informations_bp.route("/api-info/data-table",methods=["GET","POST"])
def Admin_api_info_data_table():

    try:

        am_bd_name = session.get('am_bd_name')
        admin_objid = session.get('am_bjde')

        if am_bd_name == "Admin_Authentication":
            if admin_objid != "":
                admin_details = Admin_Authentication_db.find_one({"_id":ObjectId(admin_objid)})

                if admin_details != None:

                    quiry = {}
                    dictinory = []
                    
                    sort_quiry = {"created_on":1}
                    try:
                        if request.form['order[0][column]'] == '5':
                            if request.form['order[0][dir]'] == 'asc':
                                sort_quiry = {"created_on" : 1}
                            else:
                                sort_quiry = {"created_on" : -1}
                    except:
                        pass

                    try:
                        if request.form['order[0][column]'] == '6':
                            if request.form['order[0][dir]'] == 'asc':
                                sort_quiry = {"updated_on" : 1}
                            else:
                                sort_quiry = {"updated_on" : -1}
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

                    finding = Api_Informations_db.aggregate([        
                        {"$match": quiry},
                        {'$sort': sort_quiry},
                        {"$skip": int(request.form['start'])},
                        {"$limit": int(request.form['length'])}
                    ])

                    dictinory = []
                    for x in finding:
                        
                        dictinory.append(
                            {
                                "api":x["api"],
                                "api_name":x["api_name"],
                                "view_permission":x["view_permission"],
                                "credits_per_use":x["credits_per_use"],
                                "status":x["status"],
                                "created_on": str((x["created_on"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
                                "updated_on": str((x["updated_on"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
                                "objid":str(x["_id"]),
                            }
                        )
                        
                    try:
                        if quiry == {}:
                            total_data = Api_Informations_db.estimated_document_count()
                        else:
                            total_data = Api_Informations_db.count_documents(quiry)
                    except Exception as e:
                        total_data = 0  # or any other default value or handling you prefer

                        
                    data = {"iTotalDisplayRecords": total_data,
                            'aaData': dictinory,
                            "iTotalRecords": total_data/int(request.form['length']),
                                }
                    
                    return jsonify(data) 

                else:
                    return jsonify({"data":{
                                    "status_code": 400,
                                    "status": "Error",
                                    "response":"The server couldn't understand the request due to invalid syntax."
                                }})
            else:
                return jsonify({"data":{
                                    "status_code": 502,
                                    "status": "Error",
                                    "response":"The server received an invalid response from an upstream server."
                                }})
            
        else:
            return jsonify({"data":{
                                "status_code": 502,
                                "status": "Error",
                                "response":"The server received an invalid response from an upstream server."
                            }})
        
    except:
        return redirect("/error")
    
    


# Api Info Add
@Admin_Api_informations_bp.route("/api-info/add",methods=["GET","POST"])
def Admin_api_info_add():
    if request.method == "POST":

        admin_objid = session.get('am_bjde')

        if request.form["view_permission"] == "False":
            view_permission = False
        else:
            view_permission = True

        Api_Informations_db.insert_one({
            "api": request.form["api"],
            "api_name": request.form["api_name"],
            "long_api_description": request.form["long_api_description"],
            "sort_api_description": request.form["sort_api_description"],
            "api_logo": request.form["api_logo"],
            "page_url": request.form["page_url"],
            "status": request.form["status"],
            "credits_per_use": request.form["credits_per_use"],
            "view_permission": view_permission,
            "created_on": datetime.now(),
            "updated_on": datetime.now(),
            "created_by":ObjectId(admin_objid)
        })

        flash("Data Add SuccessFully!")
        return redirect("/BBRgt/api-infos")
    
# Get Objid through details
@Admin_Api_informations_bp.route("/get/apinfo/details/<objid>",methods=["GET"])
def Api_info_objid_details(objid):
    if objid != "":
        data_list = []
        try:
           db_details = Api_Informations_db.find_one({"_id":ObjectId(objid)}) 
           data_list.append({
                "api": db_details["api"],
                "api_name" : db_details["api_name"],
                "long_api_description" : db_details["long_api_description"],
                "sort_api_description" : db_details["sort_api_description"],
                "api_logo" : db_details["api_logo"],
                "page_url" : db_details["page_url"],
                "status" : db_details["status"],
                "credits_per_use" : db_details["credits_per_use"],
                "view_permission":db_details["view_permission"],
                "objid":str(db_details['_id'])
           })

        except:
            pass
        
        return jsonify({"status_code": 200,
                            "status": "Success",
                            "response": data_list}) , 200 
    

# Api Info Edit
@Admin_Api_informations_bp.route("/api-info/edit/<objid>",methods=["GET","POST"])
def Admin_api_info_edit(objid):
    if request.method == "POST":

        admin_objid = session.get('am_bjde')
        
        if request.form["view_permission"] == "False":
            view_permission = False
        else:
            view_permission = True

        Api_Informations_db.update_one({"_id": ObjectId(objid)} , {"$set": {
            "api": request.form["api"],
            "api_name": request.form["api_name"],
            "long_api_description": request.form["long_api_description"],
            "sort_api_description": request.form["sort_api_description"],
            "api_logo": request.form["api_logo"],
            "page_url": request.form["page_url"],
            "status": request.form["status"],
            "credits_per_use": request.form["credits_per_use"],
            "view_permission": view_permission,
            "updated_on": datetime.now(),
            "created_by":ObjectId(admin_objid)
        }})

        flash("Data Edit SuccessFully!")
        return redirect("/BBRgt/api-infos")





