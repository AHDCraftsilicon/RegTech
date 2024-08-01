from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file
import os
from data_base_string import *
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import datetime,timedelta


# Blueprint
portal_table_bp = Blueprint("portal_table_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")


# Database
Api_request_history_db = Regtch_services_UAT["Api_request_history"]


@portal_table_bp.route("/poratl-page",methods=["GET","POST"])
@jwt_required(locations=['cookies'])
def portal_main_page():
    print(get_jwt())

    return render_template("portal_page.html")


@portal_table_bp.route("/poratl-data_table",methods=["GET","POST"])
@jwt_required(locations=['cookies'])
def portal_data_table():
    # parent_path = os.listdir("./apps/static/NimbleRegTechlog/")
    
    lists = []

    finding = Api_request_history_db.aggregate([{
        "$group": {
            "_id": {
                "api_name": "$api_name",
                "corporate_id":"$corporate_id",
                "date": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$current_date_time",
                        
                    }}},
            "data": {
                "$push": {
                    "current_date_time": "$current_date_time",
                    "response_duration": "$response_duration",
                    "response_time": "$response_time",
                    "return_response": "$return_response",
                    "request_data": "$request_data",
                  "corporate_id":"$corporate_id"
                }}}},{"$sort": {
                    "_id.api_name": 1,
                    "_id.date": 1}},
                    {"$project": {
                                "_id": 0,
                                "api_name": "$_id.api_name",
                                "date": "$_id.date",
                                "data": 1,
                                "corporate_id":"$_id.corporate_id"
                            }}])
    
    for x in finding:
        lists.append({
            "api_name":x["api_name"],
            "date":x["date"],
            "corporate_id":x["corporate_id"],
        })
        # print(x)
        # break

    # for company_name in parent_path:
    #     print(company_name)
    #     for service_name in os.listdir("./apps/static/NimbleRegTechlog/"+company_name):
    #             for year in os.listdir("./apps/static/NimbleRegTechlog/"+ company_name + "/" +service_name):
    #                 for month in os.listdir("./apps/static/NimbleRegTechlog/"+ company_name + "/" +service_name + "/" +year):
    #                     for date in os.listdir("./apps/static/NimbleRegTechlog/"+ company_name + "/" +service_name + "/"+year+"/"+month):
    #                         # for log_file in os.listdir("./apps/static/NimbleRegTechlog/"+ company_name + "/" +project_name + "/"+api_name+"/"+year+"/"+month+"/"+date):
    #                         lists.append({
    #                             "company_name":company_name,
    #                             "service_name":service_name,
    #                             "year":year,
    #                             "month":month,
    #                             "date":date,
    #                             # "log_file_download": "./apps/static/NimbleRegTechlog/"+ company_name + "/" +project_name + "/"+api_name+"/"+year+"/"+month+"/"+date+ "/"+ log_file,
    #                             # "log_file":log_file
    #                         })
                    
              
    return jsonify({"data":lists})


@portal_table_bp.route("/poratl-data_tabless",methods=["GET","POST"])
@jwt_required(locations=['cookies'])
def portal_data_tabless():
    # parent_path = os.listdir("./apps/static/NimbleRegTechlog/")
    
    lists = []

    finding = Api_request_history_db.find()
    
    for x in finding:
        
        try:
            unique_id  = x["unique_id"]
        except:
            unique_id = ""
        lists.append({
            "corporate_id":x["corporate_id"],
            "api_name":x["api_name"],
            "unique_id":unique_id,
            "current_date_time": str((x["current_date_time"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
            "request_data":x['request_data'],
            "_id":str(x["_id"]),
        })
    
                    
              
    return jsonify({"data":lists})



@portal_table_bp.route("/log_text_file_list/table")
def log_text_list_Files():

    # if request.method == 'POST': 
    data = []
    date_str = "30-07-2024".split(" - ")[0]

    # Parse the date string into a datetime object
    date_obj = datetime.strptime(date_str, "%d-%m-%Y")

    print(type(date_obj))
    
    finding = Api_request_history_db.find({"current_date_time":{"$gte" :date_obj}})
    
    # print("----- ", finding)
    for x in finding:
        print(x)
    return jsonify({"data":data})


# # Plan Table
# @planlist_bp.route('/plan_list/data_table/api',methods=['GET','POST'])
# @admin_required()
# def plan_data_table():
#     quiry = {}
#     sort_quiry = {}
#     if request.form["columns[1][search][value]"] != "":
#         quiry["plan_name"] = {"$regex": request.form["columns[1][search][value]"], "$options": "i"}
    
#     if request.form["columns[2][search][value]"] != "":
#         quiry["plan_type"] = request.form["columns[2][search][value]"]
    
#     if request.form["columns[3][search][value]"] != "":
#         quiry["intrest"] = {"$regex": request.form["columns[3][search][value]"], "$options": "i"}
   
#     if request.form["columns[4][search][value]"] != "":
#         quiry["fix_month"] ={"$regex": request.form["columns[4][search][value]"]}

#     if request.form["columns[6][search][value]"] != "":
#         if datetime.now().date() == datetime.strptime(request.form["columns[6][search][value]"].split(" - ")[0], "%d-%m-%Y").date():
#             quiry["created_date"] = {"$gte": datetime.strptime(
#                 request.form["columns[6][search][value]"].split(" - ")[0], "%d-%m-%Y")}
       
#         elif (datetime.now().date() - timedelta(days=1)) == datetime.strptime(request.form["columns[6][search][value]"].split(" - ")[0], "%d-%m-%Y").date():
#             quiry["created_date"] = {
#                 "$gte": datetime.strptime(request.form["columns[6][search][value]"].split(" - ")[0], "%d-%m-%Y"),
#                 "$lt": (datetime.strptime(request.form["columns[6][search][value]"].split(" - ")[0], "%d-%m-%Y")+timedelta(hours=23, minutes=59, seconds=59))
#             }
        
#         else:
#             quiry["created_date"] = {
#                 "$gte": datetime.strptime(request.form["columns[6][search][value]"].split(" - ")[0], "%d-%m-%Y"),
#                 "$lt": (datetime.strptime(request.form["columns[6][search][value]"].split(" - ")[1], "%d-%m-%Y")+timedelta(hours=23, minutes=59, seconds=59))
#             }
            
#     if request.form["columns[7][search][value]"] != "":
#         if datetime.now().date() == datetime.strptime(request.form["columns[7][search][value]"].split(" - ")[0], "%d-%m-%Y").date():
#             quiry["updated_date"] = {"$gte": datetime.strptime(
#                 request.form["columns[7][search][value]"].split(" - ")[0], "%d-%m-%Y")}
       
#         elif (datetime.now().date() - timedelta(days=1)) == datetime.strptime(request.form["columns[7][search][value]"].split(" - ")[0], "%d-%m-%Y").date():
#             quiry["updated_date"] = {
#                 "$gte": datetime.strptime(request.form["columns[7][search][value]"].split(" - ")[0], "%d-%m-%Y"),
#                 "$lt": (datetime.strptime(request.form["columns[7][search][value]"].split(" - ")[0], "%d-%m-%Y")+timedelta(hours=23, minutes=59, seconds=59))
#             }
       
#         else:
#             quiry["updated_date"] = {
#                 "$gte": datetime.strptime(request.form["columns[7][search][value]"].split(" - ")[0], "%d-%m-%Y"),
#                 "$lt": (datetime.strptime(request.form["columns[7][search][value]"].split(" - ")[1], "%d-%m-%Y")+timedelta(hours=23, minutes=59, seconds=59))
#             }
    
#     if request.form['order[0][column]'] == '1':
#         if request.form['order[0][dir]'] == 'asc':
#             sort_quiry = {'_id':1}
#         else:
#             sort_quiry = {'_id': -1}
    
#     if request.form['order[0][column]'] == '6':
#         if request.form['order[0][dir]'] == 'asc':
#             sort_quiry = {'created_date':1}
#         else:
#             sort_quiry  = {'created_date': -1}
            
#     if request.form['order[0][column]'] == '7':
#         if request.form['order[0][dir]'] == 'asc':
#             sort_quiry = {'updated_date': 1}
#         else:
#             sort_quiry = {'updated_date': -1}
    
    
#     dictinory = []
#     skp = int(int(request.form['start']) /
#               int(request.form['length']))-int(request.form['length'])
#     if skp < 0:
#         skp = 0
#     per_page = int(request.form['length'])
#     if per_page < 0:
#         per_page = None

#     finding = plan_db.aggregate([{'$sort':sort_quiry},
#                                  {"$match":quiry},
#                                  {"$skip":int(request.form['start'])},
#                                  {"$limit":int(request.form['length'])}])
#     for x in finding:
#         dictinory.append({
#             "plan_name": x["plan_name"],
#             "plan_type": x["plan_type"],
#             "intrest": x["intrest"],
#             "fix_month": x["fix_month"],
#             "notes": x["notes"],
#             "created_date": str(x["created_date"].strftime("%d-%m-%Y  %H:%M:%S")),
#             "updated_date": str(x["updated_date"].strftime("%d-%m-%Y  %H:%M:%S")),
#             "_id": str(x["_id"])
#         })
#     if quiry == {}:
#         total_data = plan_db.estimated_document_count()
#     else:
#         total_data = plan_db.count_documents(quiry)
#     data = {
#         "iTotalDisplayRecords": total_data,
#         'aaData': dictinory,
#         "iTotalRecords": total_data/int(request.form['length']),
#     }
#     return jsonify(data)
