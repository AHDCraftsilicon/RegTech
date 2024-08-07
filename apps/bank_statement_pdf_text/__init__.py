from flask import Blueprint, request,jsonify
from werkzeug.utils import secure_filename
import time , os
from data_base_string import *
from datetime import datetime
from flask_jwt_extended import  jwt_required
from apps.bank_statement_pdf_text.uco_bank_pdf_text import *
from apps.bank_statement_pdf_text.hdfc_bank_pdf_text import *
from werkzeug.datastructures import ImmutableMultiDict

# Blueprint
bank_statement_bp = Blueprint("bank_statement_bp",
                        __name__,
                        url_prefix="/")


# Database
Api_request_history_db = Regtch_services_UAT["Api_request_history_test"]


@bank_statement_bp.route("/api/v1/bankstatement/bankstatementanalysis",methods=['POST'])
# @jwt_required()
def bank_statment_get_main():

    if request.method == 'POST':
        api_call_start_time = datetime.now()

        form_data = request.form
        data = list(form_data.items())

        keys_to_check = ["CorporateID", "UniqueID", "BankName"]


        for key in keys_to_check:
            if key not in form_data or not form_data[key]:
                if key == "UniqueID":
                    store_response = {"response": 400,
                            "message": "Error",
                            "responseValue": key +" cannot be null or empty."
                        }
                    return jsonify(store_response), 400
               
                else:
                    check_log_db = Api_request_history_db.find_one({"unique_id":form_data["UniqueID"]})
                    
                    if check_log_db != None:
                        api_call_end_time = datetime.now()
                        duration = api_call_end_time - api_call_start_time
                        duration_seconds = duration.total_seconds()
                        store_response = {"response": 400,
                                        "message": "Error",
                                        "responseValue": "Request with the same unique ID has already been processed!"
                                    }

                        Api_request_history_db.insert_one({
                                        "corporate_id":form_data["CorporateID"],
                                        "unique_id":form_data["UniqueID"],
                                        "api_name":"Bank_statement",
                                        "api_start_time":api_call_start_time,
                                        "api_end_time":datetime.now(),
                                        "status": "Fail",
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "request_data":str(data),
                                        "response_data" :str(store_response),
                                        "creadte_date":datetime.now(),
                                    })
                        
                        return jsonify(store_response),400
                    
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    # CorporateId
                    if key == "CorporateID":
                        store_response = {"response": 400,
                                "message": "Error",
                                "responseValue": key +" cannot be null or empty."
                            }
                        
                        Api_request_history_db.insert_one({
                                        "unique_id":form_data["UniqueID"],
                                        "api_name":"Bank_statement",
                                        "api_start_time":api_call_start_time,
                                        "api_end_time":datetime.now(),
                                        "status": "Fail",
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "request_data":str(data),
                                        "response_data" :str(store_response),
                                        "creadte_date":datetime.now(),
                                    })
                        
                    else:
                        store_response = {"response": 400,
                                "message": "Error",
                                "responseValue": key +" cannot be null or empty."
                            }
                        
                        Api_request_history_db.insert_one({
                                        "unique_id":form_data["UniqueID"],
                                        "corporate_id":form_data["CorporateID"],
                                        "api_name":"Bank_statement",
                                        "api_start_time":api_call_start_time,
                                        "api_end_time":datetime.now(),
                                        "status": "Fail",
                                        "response_duration":str(duration),
                                        "response_time":duration_seconds,
                                        "request_data":str(data),
                                        "response_data" :str(store_response),
                                        "creadte_date":datetime.now(),
                                    })

                    
                    return jsonify(store_response), 400


        
        try:
            pdf_file = request.files["PDF_File"]
            filename_ipdf = str(time.time()).replace(".", "")
        except:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response =  {"response": 400,
                        "message": "Error",
                        "responseValue": "PDF_File cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                                "corporate_id":form_data["CorporateID"],
                                "unique_id":form_data["UniqueID"],
                                "api_name":"Bank_statement",
                                "api_start_time":api_call_start_time,
                                "api_end_time":datetime.now(),
                                "status": "Fail",
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "request_data":str(data),
                                "response_data" :str(store_response),
                                "creadte_date":datetime.now(),
                        })

            return jsonify(store_response), 400
        

        # Check UniqueID
        check_log_db = Api_request_history_db.find_one({"unique_id":form_data["UniqueID"]})
        
        if check_log_db == None:
            if pdf_file.filename != "":
                pdf_file.save(os.path.join('./apps/static/bank_statement_analysing', secure_filename(
                    filename_ipdf+"."+pdf_file.filename.split(".")[-1])))
                pdf_store_file = "apps/static//bank_statement_analysing/"+filename_ipdf+"."+pdf_file.filename.split(".")[-1]
                
                if form_data["BankName"] == "UCOBANK":
                    uco_response =  uco_bank_statmenr_main(pdf_store_file)
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    store_response = {"response": 200,
                                            "message": "Success",
                                            "responseValue": {
                                                "Table1": [uco_response]}}
                    
                    Api_request_history_db.insert_one({
                                     "corporate_id":form_data["CorporateID"],
                                    "unique_id":form_data["UniqueID"],
                                    "api_name":"Bank_statement",
                                    "api_start_time":api_call_start_time,
                                    "api_end_time":datetime.now(),
                                    "status": "Success",
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "request_data":str(data),
                                    "response_data" :str(store_response),
                                    "creadte_date":datetime.now(),
                                })

                    return jsonify(store_response), 200

                elif form_data["BankName"] == "HDFCBANK":
                    hdfc_response = hdfc_bank_statment_main(pdf_store_file)
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    store_response = {"response": 200,
                                            "message": "Success",
                                            "responseValue": {
                                                "Table1": [hdfc_response]}}
                    
                    Api_request_history_db.insert_one({
                                    "corporate_id":form_data["CorporateID"],
                                    "unique_id":form_data["UniqueID"],
                                    "api_name":"Bank_statement",
                                    "api_start_time":api_call_start_time,
                                    "api_end_time":datetime.now(),
                                    "status": "Success",
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "request_data":str(data),
                                    "response_data" :str(store_response),
                                    "creadte_date":datetime.now(),
                                })

                    return jsonify(store_response), 200
                
                else:
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    store_response = {"response": 400,
                            "message": "Error",
                            "responseValue": "Please add Valid BankName!"
                        }
                    
                    Api_request_history_db.insert_one({
                                    "corporate_id":form_data["CorporateID"],
                                    "unique_id":form_data["UniqueID"],
                                    "api_name":"Bank_statement",
                                    "api_start_time":api_call_start_time,
                                    "api_end_time":datetime.now(),
                                    "status": "Fail",
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "request_data":str(data),
                                    "response_data" :str(store_response),
                                    "creadte_date":datetime.now(),
                                })

                    return jsonify(store_response), 400

            else:
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                store_response = {"response": 400,
                            "message": "Error",
                            "responseValue": "Please Upload Bank Statement!"
                        }
                Api_request_history_db.insert_one({
                                "corporate_id":form_data["CorporateID"],
                                "unique_id":form_data["UniqueID"],
                                "api_name":"Bank_statement",
                                "api_start_time":api_call_start_time,
                                "api_end_time":datetime.now(),
                                "status": "Fail",
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "request_data":str(data),
                                "response_data" :str(store_response),
                                "creadte_date":datetime.now(),
                            })
                
                return jsonify(store_response), 400
                

        else:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": 400,
                            "message": "Error",
                            "responseValue": "Request with the same unique ID has already been processed!"
                        }

            Api_request_history_db.insert_one({
                           "corporate_id":form_data["CorporateID"],
                            "unique_id":form_data["UniqueID"],
                            "api_name":"Bank_statement",
                            "api_start_time":api_call_start_time,
                            "api_end_time":datetime.now(),
                            "status": "Fail",
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "request_data":str(data),
                            "response_data" :str(store_response),
                            "creadte_date":datetime.now(),
                        })
            
            return jsonify(store_response),400
        
