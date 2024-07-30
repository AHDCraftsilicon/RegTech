from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file
import os

from flask_jwt_extended import JWTManager, jwt_required,get_jwt
# Blueprint
portal_table_bp = Blueprint("portal_table_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")



@portal_table_bp.route("/poratl-page",methods=["GET","POST"])
@jwt_required(locations=['cookies'])
def portal_main_page():
    print(get_jwt())

    return render_template("portal_page.html")


@portal_table_bp.route("/poratl-data_table",methods=["GET","POST"])
@jwt_required(locations=['cookies'])
def portal_data_table():
    parent_path = os.listdir("./apps/static/NimbleRegTechlog/")
    
    lists = []
    for company_name in parent_path:
        print(company_name)
        for service_name in os.listdir("./apps/static/NimbleRegTechlog/"+company_name):
                for year in os.listdir("./apps/static/NimbleRegTechlog/"+ company_name + "/" +service_name):
                    for month in os.listdir("./apps/static/NimbleRegTechlog/"+ company_name + "/" +service_name + "/" +year):
                        for date in os.listdir("./apps/static/NimbleRegTechlog/"+ company_name + "/" +service_name + "/"+year+"/"+month):
                            # for log_file in os.listdir("./apps/static/NimbleRegTechlog/"+ company_name + "/" +project_name + "/"+api_name+"/"+year+"/"+month+"/"+date):
                            lists.append({
                                "company_name":company_name,
                                "service_name":service_name,
                                "year":year,
                                "month":month,
                                "date":date,
                                # "log_file_download": "./apps/static/NimbleRegTechlog/"+ company_name + "/" +project_name + "/"+api_name+"/"+year+"/"+month+"/"+date+ "/"+ log_file,
                                # "log_file":log_file
                            })
                    
              
    return jsonify({"data":lists})

@portal_table_bp.route("/log_text_file_list/table",methods=["POST"])
def log_text_list_Files():

    if request.method == 'POST': 
        data = []
        for log_file in os.listdir("./apps/static/NimbleRegTechlog/"+ request.form["path_name"]):
            data.append({
                "log_file":log_file,
                "log_file_download": "./static/NimbleRegTechlog/"+ request.form["path_name"] + "/" + log_file
            })


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
