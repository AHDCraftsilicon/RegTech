
from pymongo import MongoClient


# Local Database
databse = MongoClient(
    "mongodb://localhost:27017/")

Regtch_services_UAT = databse['Regtech_Services_UAT']