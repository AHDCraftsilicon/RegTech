from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file
import os
from data_base_string import *
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import datetime,timedelta
from bson import ObjectId


# Blueprint
comapny_list_table_bp = Blueprint("comapny_list_table_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")


# Database
Login_db = Regtch_services_UAT["Login_db"]


# Company List Route
@comapny_list_table_bp.route("/company-list-view",methods=["GET","POST"])
@jwt_required(locations=['cookies'])
def company_main_routes():

    return render_template("comapny_list_.html")


@comapny_list_table_bp.route("/comapny_list/data_table",methods=["GET","POST"])
@jwt_required(locations=['cookies'])
def company_Datatable():
    lists = []

    finding = Login_db.find()
    
    for x in finding:
        
        lists.append({
            "corporate_id":x["corporate_id"],
            "corporate_name":x['corporate_name'],
            "username":x['username'],
            "created_on": str((x["created_on"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
            "objid":str(x["_id"]),
        })
    

    return jsonify({"data":lists})

