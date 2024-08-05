from flask import Blueprint, request,jsonify
from werkzeug.utils import secure_filename
import time , os
from data_base_string import *
from datetime import datetime
from flask_jwt_extended import  jwt_required
from apps.bank_statement_pdf_text.uco_bank_pdf_text import *
from apps.bank_statement_pdf_text.hdfc_bank_pdf_text import *

# Blueprint
bank_statement_bp = Blueprint("bank_statement_bp",
                        __name__,
                        url_prefix="/")


# Database
Api_request_history_db = Regtch_services_UAT["Api_request_history"]


@bank_statement_bp.route("/api/v1/bankstatement/bankstatementanalysis",methods=['POST'])
@jwt_required()
def bank_statment_get_main():

    if request.method == 'POST':
        api_call_start_time = datetime.now()

        try:
            UniqueID = request.form["UniqueID"]
        except:
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "UniqueID cannot be null or empty."
                    }
            return jsonify(store_response),400

        try:
            CorporateID = request.form["CorporateID"]
        except:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "CorporateID cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                            "api_name":"Bank_statement",
                            "unique_id":request.form["UniqueID"],
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(request.form)
                        })

            return jsonify(store_response), 400
        
       
        
        
        try:
            pdf_file = request.files["PDF_File"]
            filename_ipdf = str(time.time()).replace(".", "")
        except:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response =  {"response": "400",
                        "message": "Error",
                        "responseValue": "PDF_File cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                            "api_name":"Bank_statement",
                            "unique_id":request.form['UniqueID'],
                            "corporate_id":request.form["CorporateID"],
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(request.form)
                        })

            return jsonify(store_response), 400
        

        try:
            BankName = request.form["BankName"]
        except:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response =  {"response": "400",
                        "message": "Error",
                        "responseValue": "BankName cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                            "api_name":"Bank_statement",
                            "unique_id":request.form['UniqueID'],
                            "corporate_id":request.form["CorporateID"],
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(request.form)
                        })

            return jsonify(store_response), 400
        
        
        

        data = {"pdf_file":pdf_file,"BankName":BankName,"CorporateID":CorporateID,"UniqueID":UniqueID}
        if CorporateID == "":
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "CorporateID cannot be null or empty."
                    }
            Api_request_history_db.insert_one({
                            "api_name":"Bank_statement",
                            "corporate_id":request.form["CorporateID"],
                            "unique_id":UniqueID,
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
            
            return jsonify(store_response), 400
        
        if UniqueID == "":
            store_response = {"response": "400",
                        "message": "Error",
                        "responseValue": "UniqueID cannot be null or empty."
                    }

            return jsonify(store_response), 400
        else:
            check_log_db = Api_request_history_db.find_one({"unique_id":UniqueID})
    
        
        if check_log_db == None:
            if pdf_file.filename != "":
                pdf_file.save(os.path.join('./apps/static/bank_statement_analysing', secure_filename(
                    filename_ipdf+"."+pdf_file.filename.split(".")[-1])))
                pdf_store_file = "apps/static//bank_statement_analysing/"+filename_ipdf+"."+pdf_file.filename.split(".")[-1]
                datass = {"pdf_file":pdf_store_file,"BankName":BankName,"CorporateID":CorporateID,"UniqueID":UniqueID}
                
                if BankName == "UCOBANK":
                    uco_response =  uco_bank_statmenr_main(pdf_store_file)
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    store_response = {"response": "200",
                                            "message": "Success",
                                            "responseValue": {
                                                "Table1": [uco_response]}}
                    
                    Api_request_history_db.insert_one({
                                    "api_name":"Bank_statement",
                                    "corporate_id":request.form["CorporateID"],
                                    "unique_id":UniqueID,
                                    "current_date_time":datetime.now(),
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "return_response" :str(store_response),
                                    "request_data":str(datass)
                                })

                    return jsonify(store_response), 200

                elif BankName == "HDFCBANK":
                    hdfc_response = hdfc_bank_statment_main(pdf_store_file)
                    api_call_end_time = datetime.now()
                    duration = api_call_end_time - api_call_start_time
                    duration_seconds = duration.total_seconds()
                    store_response = {"response": "200",
                                            "message": "Success",
                                            "responseValue": {
                                                "Table1": [hdfc_response]}}
                    
                    Api_request_history_db.insert_one({
                                    "api_name":"Bank_statement",
                                    "corporate_id":request.form["CorporateID"],
                                    "unique_id":UniqueID,
                                    "current_date_time":datetime.now(),
                                    "response_duration":str(duration),
                                    "response_time":duration_seconds,
                                    "return_response" :str(store_response),
                                    "request_data":str(datass)
                                })

                    return jsonify(store_response), 200

            else:
                api_call_end_time = datetime.now()
                duration = api_call_end_time - api_call_start_time
                duration_seconds = duration.total_seconds()
                store_response = {"response": "400",
                            "message": "Error",
                            "responseValue": "Please Upload Bank Statement!"
                        }
                Api_request_history_db.insert_one({
                                "api_name":"Bank_statement",
                                "corporate_id":request.form["CorporateID"],
                                "unique_id":UniqueID,
                                "current_date_time":datetime.now(),
                                "response_duration":str(duration),
                                "response_time":duration_seconds,
                                "return_response" :str(store_response),
                                "request_data":str(data)
                            })
                
                return jsonify(store_response), 400
                

        else:
            api_call_end_time = datetime.now()
            duration = api_call_end_time - api_call_start_time
            duration_seconds = duration.total_seconds()
            store_response = {"response": "400",
                            "message": "Error",
                            "responseValue": "Request with the same unique ID has already been processed!"
                        }

            Api_request_history_db.insert_one({
                            "corporate_id":request.form["CorporateID"],
                            "unique_id":request.form["UniqueID"],
                            "api_name":"Bank_statement",
                            "current_date_time":datetime.now(),
                            "response_duration":str(duration),
                            "response_time":duration_seconds,
                            "return_response" :str(store_response),
                            "request_data":str(data)
                        })
            
            return jsonify(store_response),400
        
