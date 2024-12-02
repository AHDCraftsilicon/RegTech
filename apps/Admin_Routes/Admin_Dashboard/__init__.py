from flask import Blueprint, render_template,request,redirect,session
from flask_jwt_extended import jwt_required ,get_jwt
from datetime import timedelta
from cryptography.fernet import Fernet
import base64
from bson import ObjectId


# DataBase
from data_base_string import *

# Blueprint
Admin_Dashboard_bp = Blueprint("Admin_Dashboard_bp",
                        __name__,
                        url_prefix="/BBRgt",
                        template_folder="templates")


# Database 
Admin_Authentication_db = Regtch_services_UAT["Admin_Authentication"]


@Admin_Dashboard_bp.route("/dashboard")
def admin_dashboard_main():

    try:
        am_bd_name = session.get('am_bd_name')
        admin_objid = session.get('am_bjde')
        print("------- ", am_bd_name)

        name = ""
        if am_bd_name == "Admin_Authentication" and admin_objid != "":
                
            admin_details = Admin_Authentication_db.find_one({"_id":ObjectId(admin_objid)})

            if admin_details != None:
                name = admin_details["name"]

            return render_template("admin_dashboard.html" , 
                                name=name)
            
        return redirect("/BBRgt/admin-login-RRtggR")
    except:
        return redirect("/error")