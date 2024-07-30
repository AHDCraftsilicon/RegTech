from flask import Blueprint, request,jsonify
from werkzeug.utils import secure_filename
import time , os
from apps.bank_statement_pdf_text.uco_bank_pdf_text import *


# Blueprint
bank_statement_bp = Blueprint("bank_statement_bp",
                        __name__,
                        url_prefix="/")


@bank_statement_bp.route("/api/v1/bank_statment/analysis",methods=['POST'])
def bank_statment_get_main():

    if request.method == 'POST':
        
        pdf_file = request.files["PDF_File"]
        filename_ipdf = str(time.time()).replace(".", "")
        if pdf_file.filename != "":
            pdf_file.save(os.path.join('./apps/static/bank_statement_analysing', secure_filename(
                filename_ipdf+"."+pdf_file.filename.split(".")[-1])))
            pdf_store_file = "apps/static//bank_statement_analysing/"+filename_ipdf+"."+pdf_file.filename.split(".")[-1]
            
            if request.form["BankName"] == "UCOBANK":
                uco_response =  uco_bank_statmenr_main(pdf_store_file)

                return jsonify({"data":uco_response})
            

        return  jsonify({"data":"yess"})

