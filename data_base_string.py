
from pymongo import MongoClient

# Live DB
# database = MongoClient("mongodb://regtech-live:zwSZCkcoWOCRiN51pBzkBNpxRd2tJGQvEToLAHV2nxjfEDURRVDR4Ink8QKust4TXzSOn5yg2Fj6ACDbiqD4nw%3D%3D@regtech-live.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@regtech-live@")
# Regtch_services_UAT = database['Regtech']
# Regtch_services_UAT = database['Regtech_UAT']


# 192.168.10.121:27017
database = MongoClient("mongodb://192.168.10.121:27017/")
Regtch_services_UAT = database['Regtech_UAT']

# 127
# database = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.1")
# Regtch_services_UAT = database['Regtech']





