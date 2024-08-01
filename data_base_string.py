
from pymongo import MongoClient


# Local Database
# databse = MongoClient(
#     "mongodb://localhost:27017/")

# Live Database
databse = MongoClient(
    "mongodb://mongodbregtech:8E6iWPpNAqEM9KD8SYltq0MOu7D0HOVEsfGcP7mbe5lBaZvj3tJrr54j21UGGKLrzh5b1xjiZbQhACDbKJMP9Q==@mongodbregtech.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@mongodbregtech@")

Regtch_services_UAT = databse['Regtech_Services_UAT']