from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file
import os
from data_base_string import *
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import datetime,timedelta
from bson import ObjectId


# Blueprint
database_table_bp = Blueprint("database_table_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")


# Database
Api_request_history_db = Regtch_services_UAT["Api_request_history"]


# Database Log Route
@database_table_bp.route("/database-log",methods=["GET","POST"])
@jwt_required(locations=['cookies'])
def portal_main_page():

    return render_template("portal_page.html")


# @database_table_bp.route("/poratl-data_table",methods=["GET","POST"])
# @jwt_required(locations=['cookies'])
# def portal_data_table():
#     # parent_path = os.listdir("./apps/static/NimbleRegTechlog/")
    
#     lists = []

#     finding = Api_request_history_db.aggregate([{
#         "$group": {
#             "_id": {
#                 "api_name": "$api_name",
#                 "corporate_id":"$corporate_id",
#                 "date": {
#                     "$dateToString": {
#                         "format": "%Y-%m-%d",
#                         "date": "$current_date_time",
                        
#                     }}},
#             "data": {
#                 "$push": {
#                     "current_date_time": "$current_date_time",
#                     "response_duration": "$response_duration",
#                     "response_time": "$response_time",
#                     "return_response": "$return_response",
#                     "request_data": "$request_data",
#                   "corporate_id":"$corporate_id"
#                 }}}},{"$sort": {
#                     "_id.api_name": 1,
#                     "_id.date": 1}},
#                     {"$project": {
#                                 "_id": 0,
#                                 "api_name": "$_id.api_name",
#                                 "date": "$_id.date",
#                                 "data": 1,
#                                 "corporate_id":"$_id.corporate_id"
#                             }}])
    
#     for x in finding:
#         lists.append({
#             "api_name":x["api_name"],
#             "date":x["date"],
#             "corporate_id":x["corporate_id"],
#         })
#         # print(x)
#         # break

#     # for company_name in parent_path:
#     #     print(company_name)
#     #     for service_name in os.listdir("./apps/static/NimbleRegTechlog/"+company_name):
#     #             for year in os.listdir("./apps/static/NimbleRegTechlog/"+ company_name + "/" +service_name):
#     #                 for month in os.listdir("./apps/static/NimbleRegTechlog/"+ company_name + "/" +service_name + "/" +year):
#     #                     for date in os.listdir("./apps/static/NimbleRegTechlog/"+ company_name + "/" +service_name + "/"+year+"/"+month):
#     #                         # for log_file in os.listdir("./apps/static/NimbleRegTechlog/"+ company_name + "/" +project_name + "/"+api_name+"/"+year+"/"+month+"/"+date):
#     #                         lists.append({
#     #                             "company_name":company_name,
#     #                             "service_name":service_name,
#     #                             "year":year,
#     #                             "month":month,
#     #                             "date":date,
#     #                             # "log_file_download": "./apps/static/NimbleRegTechlog/"+ company_name + "/" +project_name + "/"+api_name+"/"+year+"/"+month+"/"+date+ "/"+ log_file,
#     #                             # "log_file":log_file
#     #                         })
                    
              
#     return jsonify({"data":lists})


# Database Data-table
@database_table_bp.route("/poratl-data_tabless",methods=["GET","POST"])
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
            "objid":str(x["_id"]),
        })
    
                    
              
    return jsonify({"data":lists})



@database_table_bp.route("/poratl-data_tabless_ajex",methods=["GET","POST"])
@jwt_required(locations=['cookies'])
def portal_data_tabless_ajex():
    # parent_path = os.listdir("./apps/static/NimbleRegTechlog/")
    
    quiry = {}
    dictinory = []
    
    sort_quiry = {}
    
    if request.form["columns[1][search][value]"] != "" :
            quiry['api_name'] = {'$regex' : request.form["columns[1][search][value]"], "$options" :"i"}
    
    if request.form["columns[2][search][value]"] != "" :
        quiry['unique_id'] = {'$regex' : request.form["columns[2][search][value]"], "$options" :"i"}
    
    if request.form["columns[3][search][value]"] != "":
        if datetime.now().date() == datetime.strptime(request.form["columns[3][search][value]"].split(" - ")[0], "%d-%m-%Y").date():
            quiry["current_date_time"] = {"$gte": datetime.strptime(
                request.form["columns[3][search][value]"].split(" - ")[0], "%d-%m-%Y")}
        elif (datetime.now().date() - timedelta(days=1)) == datetime.strptime(request.form["columns[3][search][value]"].split(" - ")[0], "%d-%m-%Y").date():
            quiry["current_date_time"] = {
                "$gte": datetime.strptime(request.form["columns[3][search][value]"].split(" - ")[0], "%d-%m-%Y"),
                "$lt": (datetime.strptime(request.form["columns[3][search][value]"].split(" - ")[0], "%d-%m-%Y")+timedelta(hours=23, minutes=59, seconds=59))
            }
        else:
            quiry["current_date_time"] = {
                "$gte": datetime.strptime(request.form["columns[3][search][value]"].split(" - ")[0], "%d-%m-%Y"),
                "$lt": (datetime.strptime(request.form["columns[3][search][value]"].split(" - ")[1], "%d-%m-%Y")+timedelta(hours=23, minutes=59, seconds=59))
            }
            
 

    if request.form['order[0][column]'] == '3':
        if request.form['order[0][dir]'] == 'asc':
            sort_quiry = {"current_date_time" : 1}
        else:
            sort_quiry = {"current_date_time" : -1}

    
    
    try:
        skp = int(int(request.form['start']) / int(request.form['length'])) - int(request.form['length'])
    except (KeyError, ValueError, ZeroDivisionError) as e:
        skp = 0  # default value if calculation fails
 
        
    if skp < 0:
        skp = 0
    per_page = int(request.form['length'])
    if per_page < 0:
        per_page = None
    

    

    finding = Api_request_history_db.aggregate([        
        {"$match": quiry},
        {'$sort': sort_quiry},
        {"$skip": int(request.form['start'])},
        {"$limit": int(request.form['length'])}
    ])
   
        # Handle the error

    dictinory = []
    for x in finding:
        
        try:
            unique_id  = x["unique_id"]
        except:
            unique_id = ""

        dictinory.append(
            {
                "corporate_id":x["corporate_id"],
                "api_name":x["api_name"],
                "unique_id":unique_id,
                "current_date_time": str((x["current_date_time"]+timedelta(hours=5,minutes=30)).strftime("%d-%m-%Y %H:%M:%S")),
                "request_data":x['request_data'],
                "objid":str(x["_id"]),
            }
        )
        
    try:
        if quiry == {}:
            total_data = Api_request_history_db.estimated_document_count()
        else:
            total_data = Api_request_history_db.count_documents(quiry)
    except Exception as e:
        total_data = 0  # or any other default value or handling you prefer

        
    data = {"iTotalDisplayRecords": total_data,
            'aaData': dictinory,
            "iTotalRecords": total_data/int(request.form['length']),
                }
    
    return jsonify(data) 



# Database-log file download
@database_table_bp.route("/log_file/download/<objid>")
@jwt_required(locations=['cookies'])
def log_download(objid):
    data = Api_request_history_db.find_one({"_id":ObjectId(objid)})
    
    request_list = []

    try:
        unique_id = data["unique_id"]
    except:
        unique_id = ""
    request_list.append({
        "return_response":data["return_response"],
        "request_data":data["request_data"],
        "unique_id":unique_id
    })

    return jsonify({"data":request_list})


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
