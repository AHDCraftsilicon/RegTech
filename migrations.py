
from pymongo import MongoClient


# Local Database
# databse = MongoClient(
#     "mongodb://localhost:27017/")

# Live Database
databse_old = MongoClient(
    "mongodb://mongodbregtech:8E6iWPpNAqEM9KD8SYltq0MOu7D0HOVEsfGcP7mbe5lBaZvj3tJrr54j21UGGKLrzh5b1xjiZbQhACDbKJMP9Q==@mongodbregtech.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@mongodbregtech@")

Regtch_services_UAT = databse_old['Regtech_Services_UAT']["Api_request_history_test"]


# New Database
new_database = MongoClient("mongodb://regtechdb:JWC4Ky6B2KOcKfhJpaCtRKFa75AuCvTOqOIEBIQ5MDLjJQgsF1wVTjBQfHvcK7IH6AUZgc3xEYBsACDbjXW0Eg%3D%3D@regtechdb.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@regtechdb@")

Regtch_services_UAT_new = new_database['Regtech_Services_UAT']["Api_request_history_test"]



for x in Regtch_services_UAT.find():

    try:
        print(x['unique_id'])
        Regtch_services_UAT_new.insert_one({
        "unique_id": x['unique_id'],
        "api_name": x['api_name'],
        "api_start_time": x['api_start_time'],
        "api_end_time": x['api_end_time'],
        "status": x['status'],
        "response_duration": x['response_duration'],
        "response_time": x['response_time'],
        "request_data" : x['request_data'], 
        "response_data":x['response_data'],
        "creadte_date": x['creadte_date']
        })
    except:
        pass

    break