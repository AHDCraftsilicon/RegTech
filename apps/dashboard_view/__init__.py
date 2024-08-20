from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from data_base_string import *
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta
from datetime import datetime

# Blueprint
dashboard_bp = Blueprint("dashboard_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")

# Database
Api_request_history_db = Regtch_services_UAT["Api_request_history_test"]


@dashboard_bp.route("/admin/dashboard",methods=["GET","POST"])
def dashboard_main():

    # Total Comapny Count
    company_details = []
    company_agg = Api_request_history_db.aggregate([{
                '$group': {
                    '_id': '$corporate_id',
                    'count': {'$sum': 1},
                    'documents': {
                        '$push': {
                            '$slice': ['$documents', 10]  
                        }
                    }
                }
            },
            {
                '$match': {
                    'count': {'$gt': 1}
                }
            }])
    total_Company_count = 0
    for company_count in  company_agg:
        if company_count["_id"] != None and company_count["_id"] != "":
            # print(company_count['_id'])
            total_Company_count += 1
            company_details.append({
                "company_name":company_count["_id"],
                "api_count":company_count["count"]
                })


    # Today Api Count

    now = datetime.now()

    # Define the start and end of the current day
    start_of_day = datetime(now.year, now.month, now.day)
    end_of_day = start_of_day + timedelta(days=1)

    # Today Api Count
    Today_api_count = Api_request_history_db.count_documents({
        'creadte_date': {
            '$gte': start_of_day,
            '$lt': end_of_day
        }
    })

    # Today Success Api Count
    Today_api_success_count = Api_request_history_db.count_documents({
        'creadte_date': {
            '$gte': start_of_day,
            '$lt': end_of_day
        },
        "status":"Success"
    })

    # Today Fail Api Count
    Today_api_fail_count = Api_request_history_db.count_documents({
        'creadte_date': {
            '$gte': start_of_day,
            '$lt': end_of_day
        },
        "status":"Fail"
    })

    return render_template("dashboard.html" , 
                           total_Company_count=total_Company_count,Today_api_fail_count=Today_api_fail_count,
                           Today_api_count=Today_api_count,Today_api_success_count=Today_api_success_count,
                           company_details=company_details)