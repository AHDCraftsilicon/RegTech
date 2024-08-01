from flask import Blueprint, render_template,request,redirect,flash,jsonify,send_file,make_response
from data_base_string import *
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt,create_access_token,set_access_cookies
from datetime import timedelta



# Blueprint
login_Admin_bp = Blueprint("login_Admin_bp",
                        __name__,
                        url_prefix="/",
                        template_folder="templates")


# Database
login_db = Regtch_services_UAT['Login_db']



@login_Admin_bp.route("/admin/login",methods=["GET","POST"])
def login_admin_main():

    try:
        verify_jwt_in_request()
        claims = get_jwt()

    except:
        pass

    if request.method == "POST":
        # print(request.form)
        
        if request.form['corporate_name'] != "" and request.form["user_name"] != "" and request.form["password"] != "":
            login_Details = login_db.find_one({"username":request.form["user_name"] , "corporate_name":request.form["corporate_name"] , "password":request.form["password"]})
            if login_Details != None:
            
                duration = timedelta(minutes=30)
                access_token = create_access_token(expires_delta=duration,identity={'data':'Admin Login Successfully','objid':str(login_Details['_id'])}
                                                ,additional_claims={"is_api": False,"is_admin":True})
                
                if login_Details != None:
                    resp = redirect('/poratl-page')
                    set_access_cookies(resp, access_token)
                    # response = make_response(resp)
                    # response.set_cookie('admin_token', access_token)
                    flash(''+login_Details['username']+' Login Successfully!')
                    return resp
            else:
                flash('Please Add Valid Corporate Name & User Name & Password!')
                return redirect("/admin/login")
        
            

        # flash('Please Add All Require Details!')
        return redirect("/admin/login")


    return render_template("login.html")