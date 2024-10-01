from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from flask_jwt_extended import JWTManager, jwt_required,get_jwt
from datetime import   datetime

# DataBase
from data_base_string import *

# Blueprint
Index_Page_bp = Blueprint("Index_Page_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")

contact_db = Regtch_services_UAT["contact_us"]

@Index_Page_bp.route("/")
def index_main_page():

    return render_template("Index_page.html")


# sub links
@Index_Page_bp.route("/aadhaar-redaction-api")
def aadhaar_redaction():

    return render_template("aadhaar_redaction.html")

@Index_Page_bp.route("/ocr-api")
def ocr_Details():

    return render_template("ocr.html")


@Index_Page_bp.route("/bank-statement-api")
def bank_statments():

    return render_template("bank_statement.html")


@Index_Page_bp.route("/ITR-statement-api")
def ITR_statement():

    return render_template("ITR_statement.html")


@Index_Page_bp.route("/name-match-api")
def Name_Match():

    return render_template("name_match.html")


@Index_Page_bp.route("/lang-translate-api")
def Lang_trans():

    return render_template("lang_translate.html")


@Index_Page_bp.route("/kyc-quality-check-api")
def kyc_quality_check():

    return render_template("kyc_quality_check.html")


# Legal complacency


@Index_Page_bp.route("/privacy-policy")
def privacy_policy():

    return render_template("privacy-policy.html")


@Index_Page_bp.route("/terms-of-use")
def terms_of_use():

    return render_template("terms-of-use.html")


@Index_Page_bp.route("/legal")
def legal():

    return render_template("legal.html")


@Index_Page_bp.route("/license-and-agreement")
def licence_agreement():

    return render_template("license-and-agreement.html")


@Index_Page_bp.route("/contact-us")
def contact_us():

    return render_template("contact_us.html")




@Index_Page_bp.route("/contact-from",methods=["POST","GET"])
def contact_us_form():
    if request.method == 'POST':
        contact_db.insert_one({
            "first_name" : request.form["first_name"],
            "last_name" : request.form["last_name"],
            "mobile_no" : request.form["mobile_no"],
            "email" : request.form["email"],
            "company_name" : request.form["company_name"],
            "message" : request.form["message"],
            "created_on" : datetime.now()
        })

        return redirect('/contact-us')
    
    return redirect('/')


