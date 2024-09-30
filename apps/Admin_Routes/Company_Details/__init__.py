from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from flask_jwt_extended import jwt_required,get_jwt
from datetime import timedelta
from cryptography.fernet import Fernet
from bson import ObjectId


# DataBase
from data_base_string import *

# Blueprint
Admin_Company_details_bp = Blueprint("Admin_Company_details_bp",
                        __name__,
                        url_prefix="/BBRgt",
                        template_folder="templates")


# Database 
Admin_Authentication_db = Regtch_services_UAT["Admin_Authentication"]
User_Authentication_db = Regtch_services_UAT["User_Authentication"]


# Company Route
@Admin_Company_details_bp.route("/Company-details")
@jwt_required(locations=['cookies'])
def admin_company_page():
    claims = get_jwt()

    name = ""
    if claims["sub"]["db_name"] == "Admin_Authentication":
        if claims["sub"]["objid"] != "":
            print(claims["sub"]["objid"])
            admin_details = Admin_Authentication_db.find_one({"_id":ObjectId(claims["sub"]["objid"])})

            if admin_details != None:
                name = admin_details["name"]


    return render_template("company_details_page.html",
                            name=name)


# Company Data-Table

@Admin_Company_details_bp.route("/company-details/data-table",methods=["GET","POST"])
@jwt_required(locations=['cookies'])
def Admin_company_data_table():
    quiry = {}
    dictinory = []
    
    sort_quiry = {}

    if request.form['order[0][column]'] == '4':
        if request.form['order[0][dir]'] == 'asc':
            sort_quiry = {"creadte_date" : 1}
        else:
            sort_quiry = {"creadte_date" : -1}

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
        # {'$sort': sort_quiry},
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
                "creadte_date": str((x["creadte_date"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
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

