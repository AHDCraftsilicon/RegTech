# Live DB
from pymongo import MongoClient


database = MongoClient("mongodb://regtech-live:zwSZCkcoWOCRiN51pBzkBNpxRd2tJGQvEToLAHV2nxjfEDURRVDR4Ink8QKust4TXzSOn5yg2Fj6ACDbiqD4nw%3D%3D@regtech-live.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@regtech-live@")
# Testing My Side
Regtch_services_UAT = database['Regtech']


User_Authentication_db = Regtch_services_UAT["User_Authentication"]


for x in User_Authentication_db.find():
    User_Authentication_db.update_one({"_id":x['_id']},{"$set":{"tester_flag":False}})
    print(x)


# User_Authentication_db.update_many({"creadte_date":{"$exists":True}},{"$rename":{"creadte_date":"created_date"}})