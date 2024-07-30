from pymongo import MongoClient 
from datetime import datetime

mongo_String = MongoClient('mongodb://localhost:27017/') 
  
# Create database named demo if they don't exist already 
regtech_db = mongo_String["Regtech_Services_UAT"]
user_master_db = regtech_db["Login_db"]

# print(regtech_db.command("collstats", user_master_db)["size"])

# Insert Doc

user_master_db.insert_one({
    "Username" : "Test",
    "password" : "abcd",
    "corporate_id" : "Craftsilicon",
    "corporate_name" : "CRAFTS",
    "client_id" : "",
    "secret_key" : "",
    "status" : "",
    "isdelete" : "",
    "created_on" : datetime.now(),
    "created_by" : "test",
    "modify_on" : datetime.now(),
    "modify_by" : "test",
})