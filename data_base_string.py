
from pymongo import MongoClient

databse = MongoClient(
    "mongodb://regtechdb:JWC4Ky6B2KOcKfhJpaCtRKFa75AuCvTOqOIEBIQ5MDLjJQgsF1wVTjBQfHvcK7IH6AUZgc3xEYBsACDbjXW0Eg%3D%3D@regtechdb.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@regtechdb@")

# Live DB
# Regtch_services_UAT = databse['Regtech_Services_AHM_UAT']

# UAT TESting AHM
Regtch_services_UAT = databse['Blue_Beetle_Regtech']


