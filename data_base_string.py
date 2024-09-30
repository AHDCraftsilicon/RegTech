
from pymongo import MongoClient

# # UAT Database
# database = MongoClient("mongodb://Regtech:Makarba%40380051*@20.197.47.40:27017/?authSource=Regtech")

# # Testing My Side
# Regtch_services_UAT = database['Regtch_UAT']



database = MongoClient("mongodb://regtechdb:JWC4Ky6B2KOcKfhJpaCtRKFa75AuCvTOqOIEBIQ5MDLjJQgsF1wVTjBQfHvcK7IH6AUZgc3xEYBsACDbjXW0Eg%3D%3D@regtechdb.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@regtechdb@")
# Testing My Side
Regtch_services_UAT = database['Regtech_Services_Testing']


# Live Regtech
# Regtch_services_UAT = databse['Regtech_Services_Testing']

# Unit Testing (Testing Team)
# Regtch_services_UAT = databse['Regtech_Services_Testing']



