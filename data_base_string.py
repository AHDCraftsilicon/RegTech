
from pymongo import MongoClient

# # Live DB
# database = MongoClient("mongodb://Regtech:Makarba%40380051*@20.197.47.40:27017/?authSource=Regtech")

# # Testing My Side
# Regtch_services_UAT = database['Regtech']


# # UAT DB
# database = MongoClient("mongodb://regtechdb:JWC4Ky6B2KOcKfhJpaCtRKFa75AuCvTOqOIEBIQ5MDLjJQgsF1wVTjBQfHvcK7IH6AUZgc3xEYBsACDbjXW0Eg%3D%3D@regtechdb.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@regtechdb@")
# # Testing My Side
# Regtch_services_UAT = database['Regtech_UAT']


# Live DB
database = MongoClient("mongodb://regtech-live:zwSZCkcoWOCRiN51pBzkBNpxRd2tJGQvEToLAHV2nxjfEDURRVDR4Ink8QKust4TXzSOn5yg2Fj6ACDbiqD4nw%3D%3D@regtech-live.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@regtech-live@")
# Testing My Side
Regtch_services_UAT = database['Regtech']



