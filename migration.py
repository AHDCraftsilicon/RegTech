# Live DB
from pymongo import MongoClient

# database = MongoClient("mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.3.1")

database = MongoClient("mongodb://regtech-live:zwSZCkcoWOCRiN51pBzkBNpxRd2tJGQvEToLAHV2nxjfEDURRVDR4Ink8QKust4TXzSOn5yg2Fj6ACDbiqD4nw%3D%3D@regtech-live.mongo.cosmos.azure.com:10255/?ssl=true&retrywrites=false&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@regtech-live@")
# Testing My Side
Regtch_services_UAT = database['Regtech']



# 1
# Database Indexing 
# Api_Informations_db = Regtch_services_UAT['Api_Informations']

# Api_Informations_db.create_index({"api_name":-1})
# Api_Informations_db.create_index({"long_api_description":-1})
# Api_Informations_db.create_index({"sort_api_description":-1})
# Api_Informations_db.create_index({"api_logo":-1})
# Api_Informations_db.create_index({"page_url":-1})
# Api_Informations_db.create_index({"status":-1})
# Api_Informations_db.create_index({"credits_per_use":-1})
# Api_Informations_db.create_index({"created_by":-1})
# Api_Informations_db.create_index({"created_on":-1})
# Api_Informations_db.create_index({"updated_on":-1})


# 2
# User_Authentication_db = Regtch_services_UAT['User_Authentication']
# User_Authentication_db.update_many({},{"$set": {"user_type": "Test User"}})

# 3
# User_Authentication_db = Regtch_services_UAT['User_Authentication']
# User_Authentication_db.create_index({"Company_Name":-1})
# User_Authentication_db.create_index({"Mobile_No":-1})
# User_Authentication_db.create_index({"Email_Id":-1})
# User_Authentication_db.create_index({"verify_token":-1})
# User_Authentication_db.create_index({"flag":-1})
# User_Authentication_db.create_index({"token_expired_time_duration_min":-1})
# User_Authentication_db.create_index({"verify_token_create_date":-1})
# User_Authentication_db.create_index({"client_id":-1})
# User_Authentication_db.create_index({"client_secret_key":-1})
# User_Authentication_db.create_index({"total_test_credits":-1})
# User_Authentication_db.create_index({"used_test_credits":-1})
# User_Authentication_db.create_index({"unlimited_test_credits":-1})
# User_Authentication_db.create_index({"secret_key_pass":-1})
# User_Authentication_db.create_index({"encrypted_pass":-1})
# User_Authentication_db.create_index({"tester_flag":-1})
# User_Authentication_db.create_index({"created_date":-1})
# User_Authentication_db.create_index({"user_type":-1})


# 4
# Api_Informations_db = Regtch_services_UAT['Api_Informations']
# Api_Informations_db.update_many({},{"$set":{"api":""}})
# Api_Informations_db.update_many({},{"$set":{"view_permission":True}})


# 5
# Production_User_db = Regtch_services_UAT['Production_User']
# Production_User_db.create_index({"production_user":-1})
# Production_User_db.create_index({"service":-1})
# Production_User_db.create_index({"bussiness_name":-1})
# Production_User_db.create_index({"name_of_contact_person":-1})
# Production_User_db.create_index({"designation_of_contact_person":-1})
# Production_User_db.create_index({"email_id":-1})
# Production_User_db.create_index({"contact_number":-1})
# Production_User_db.create_index({"PAN_number":-1})
# Production_User_db.create_index({"TAN_number":-1})
# Production_User_db.create_index({"registered_address":-1})
# Production_User_db.create_index({"correspondence_address":-1})
# Production_User_db.create_index({"api_retails":-1})
# Production_User_db.create_index({"created_on":-1})
# Production_User_db.create_index({"updated_on":-1})

# 6
# pincodes_db = Regtch_services_UAT["pincodes"]
# pincodes_db.create_index({"POSTAL_CODE":-1})
# pincodes_db.create_index({"STATE":-1})
# pincodes_db.create_index({"city":-1})
# pincodes_db.create_index({"sub_city":-1})

# 7
# User_Authentication_db = Regtch_services_UAT['User_Authentication']
# User_Authentication_db.update_many({},{"$set": {"user_flag":2}})


# 8
# User_Authentication_db = Regtch_services_UAT['User_Authentication']
# User_Authentication_db.update_many({},{"$set": {"api_status":'Enable',
#                                                 "user_status":'Enable'}})


# 9
# User_Authentication_db = Regtch_services_UAT['User_Authentication']
# User_Authentication_db.update_many({},{"$set":{'used_test_credits':50}})