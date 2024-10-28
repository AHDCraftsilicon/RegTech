from flask import Flask,render_template_string,g , session,redirect , request , jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
import os
from flask_socketio import SocketIO, emit

# Index Page(Landing Page)
from apps.Index import Index_Page_bp

# User Authentication
from apps.Authentication_User.User_admin_SingUp import User_Admin_SignUp_bp
from apps.Authentication_User.User_admin_SingIn import User_Admin_SignIn_bp
from apps.Authentication_User.User_Token_verify import User_Token_Verify_bp
from apps.Authentication_User.User_Forgot_pass_and_reset import User_Forgot_pass_and_reset_bp

# User Api Dashboard
from apps.User_Routes.User_admin_Api_Dashboard import User_Admin_Api_Dashboard_bp
# Dashboard Inner Routes
from apps.User_Routes.Admin_Api_Uses.Name_Comparison import Admin_Api_Uses_Name_Comparison_bp
from apps.User_Routes.Admin_Api_Uses.Aadhaar_OCR import Aadhaar_OCR_bp
from apps.User_Routes.Admin_Api_Uses.PAN_OCR import PAN_OCR_bp
from apps.User_Routes.Admin_Api_Uses.Aadhaar_Redaction import Aadhaar_Redaction_bp
from apps.User_Routes.Admin_Api_Uses.Passport_OCR import Passport_OCR_bp
from apps.User_Routes.Admin_Api_Uses.KYC_Quality_check import KYC_Quality_check_bp
from apps.User_Routes.Admin_Api_Uses.Langu_Trans import Language_translate_bp
from apps.User_Routes.Admin_Api_Uses.Bank_Statements import Bank_Statments_bp
from apps.User_Routes.Admin_Api_Uses.ITR_Analysis import ITR_analysis_bp
# User Api Credentials
from apps.User_Routes.Api_Credentials import User_Admin_Api_Credentials_bp
# User Api Support
from apps.User_Routes.support import User_Support_bp
# User Api Usage_Insights
from apps.User_Routes.Usage_Insights import User_Api_Usage_bp
# User APi Credits & Pricing
from apps.User_Routes.Credits_pricing import Credits_Pricing_bp
# USer Api Documentation
from apps.User_Routes.Api_Documentation import User_api_Documentation_bp



# Admin Authentication
# from apps.Authentication_Admin.Admin_login import Admin_login_bp
# # Admin ROutes
# from apps.Admin_Routes.Admin_Dashboard import Admin_Dashboard_bp
# from apps.Admin_Routes.Company_Details import Admin_Company_details_bp



# Token For access api
from apps.Every_Apis.Access_Token import Access_Token_api_bp

# Every Apis
from apps.Every_Apis.Name_Matching import Name_Matching_api_bp
from apps.Every_Apis.Language_Translator import Language_Translator_api_bp
from apps.Every_Apis.KYC_Quality_Check import KYC_Quality_Check_api_bp
from apps.Every_Apis.Aadhaar_Redaction import Aadhaar_Redaction_api_bp
from apps.Every_Apis.OCR import OCR_all_api_bp , init_socketio
from apps.Every_Apis.Bank_Statement import Bank_Statement_api_bp
from apps.Every_Apis.ITR_Statement import ITR_Statement_api_bp
from apps.Every_Apis.Voter_Redaction import Voter_Redaction_api_bp
from apps.Every_Apis.Face_Matching import Face_matching_api_bp
from apps.Every_Apis.Multiple_name_match import Multi_name_match_api_bp
from apps.Every_Apis.Pennydrop import Pennydrop_api_bp
from apps.Every_Apis.Aadhaar_mobile_link import Aadhaar_mobile_link_bp
from apps.Every_Apis.Aadhaar_Authentication import Aadhaar_Auth_bp
from apps.Every_Apis.Voter_Authentication import Voter_Auth_bp

# logger=True, engineio_logger=True

socketios = SocketIO()

def crete_app():
    app = Flask(__name__)
    
    socketios.init_app(app)

    init_socketio(socketios)

    
    
    app.secret_key = "jnClOF0X4pzE2wHFdl0sjwFBR4CDiAcb2B13BDED3E63A69CD7F5F2A89A4FDDDF44"
    app.config['SESSION_PERMANENT'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)
    app.config['SESSION_COOKIE_NAME'] = 'k_'
    CORS(app , resources={r"/*": {"origins": "https://regtech.blubeetle.ai/"}}) 

    # JWT Secret key
    app.config["JWT_SECRET_KEY"] = "Craft_Silicon_Regtech_Makarba_Ahm"
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    # app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    # app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=15)



    

    
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        return jsonify({"status": "Failure",
                    "statusCode": 401,
                    "statusMessage": "Invalid token or expired token"
                }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        return jsonify({"status": "Failure",
                    "statusCode": 401,
                    "statusMessage": "Invalid token or expired token"
                }), 401
    

    @jwt.unauthorized_loader
    def my_expired_token_callbacks(jwt_payload):
        return jsonify({"status": "Failure",
                    "statusCode": 401,
                    "statusMessage": "Invalid token or expired token"
                }), 401
    
    

    
    # Landing Page Css
    def Landing_routes_Urls():
        with app.open_resource('Components/Landing_Page/Landing_page_urls.html') as f:
           return f.read().decode('utf-8')
        
    def Landing_Page_Topbar():
        with app.open_resource('Components/Landing_Page/Landing_page_Topbar.html') as f:
           return f.read().decode('utf-8')
        

    def Landing_Page_Footer():
        with app.open_resource('Components/Landing_Page/Landing_page_Footer.html') as f:
           return f.read().decode('utf-8')


    # Authentication Css
    def Auth_Css_Urls():
        with app.open_resource('Components/Auth_Css_urls.html') as f:
            return f.read().decode('utf-8')
        
    # Auth SideBar
    def Auth_Sidebar():
        with app.open_resource('Components/Auth_SideBar.html') as f:
            return f.read().decode('utf-8')
        
    
    # User Portal Css
    def User_Portal_urls():
        with app.open_resource('Components/User_Portal/User_portal_Css_urls.html') as f:
            return f.read().decode('utf-8')

            
         

    # User Portal Topbar
    def User_portal_topbar(user_name):
        with app.open_resource('Components/User_Portal/User_portal_Topbar.html') as f:
            return render_template_string(f.read().decode('utf-8'),user_name=user_name)
        
    # User Portal SideBar
    def User_portal_sidebar():
        with app.open_resource('Components/User_Portal/User_portal_Sidebar.html') as f:
            return f.read().decode('utf-8')
            

    # Admin Portal Css
    def Admin_Portal_urls():
        with app.open_resource('Components/Admin_Portal/Admin_portal_Css_urls.html') as f:
            return f.read().decode('utf-8')
        
    # Admin Portal SideBar
    def Admin_Portal_sidebar():
        with app.open_resource('Components/Admin_Portal/Admin_portal_Sidebar.html') as f:
            return f.read().decode('utf-8')
        
    # Admin Portal Topbar
    def Admin_Portal_topbar(name):
        with app.open_resource('Components/Admin_Portal/Admin_portal_Topbar.html') as f:
            return render_template_string(f.read().decode('utf-8'),name=name)

    
    
    # User Authentication 
    app.register_blueprint(User_Admin_SignUp_bp)
    app.register_blueprint(User_Admin_SignIn_bp)
    app.register_blueprint(User_Token_Verify_bp)
    app.register_blueprint(User_Forgot_pass_and_reset_bp)

    # User View
    app.register_blueprint(User_Admin_Api_Dashboard_bp)
    # Api Dashboard Pages
    app.register_blueprint(Admin_Api_Uses_Name_Comparison_bp)
    app.register_blueprint(Aadhaar_OCR_bp)
    app.register_blueprint(PAN_OCR_bp)
    app.register_blueprint(Aadhaar_Redaction_bp)
    app.register_blueprint(Passport_OCR_bp)
    app.register_blueprint(KYC_Quality_check_bp)
    app.register_blueprint(Language_translate_bp)
    app.register_blueprint(Bank_Statments_bp)
    app.register_blueprint(ITR_analysis_bp)
    # Api Credentials
    app.register_blueprint(User_Admin_Api_Credentials_bp)
    app.register_blueprint(User_Support_bp)
    app.register_blueprint(User_Api_Usage_bp)
    app.register_blueprint(Credits_Pricing_bp)
    app.register_blueprint(User_api_Documentation_bp)

    # Index Page
    app.register_blueprint(Index_Page_bp)
    

    # # Admin Authentication
    # app.register_blueprint(Admin_login_bp)
    # # Admin Dashboard
    # app.register_blueprint(Admin_Dashboard_bp)
    # app.register_blueprint(Admin_Company_details_bp)
    

    # Every api access token 
    app.register_blueprint(Access_Token_api_bp)
    # Every Apis
    app.register_blueprint(Name_Matching_api_bp)
    app.register_blueprint(Language_Translator_api_bp)
    app.register_blueprint(KYC_Quality_Check_api_bp)
    app.register_blueprint(Aadhaar_Redaction_api_bp)
    app.register_blueprint(OCR_all_api_bp)
    app.register_blueprint(Bank_Statement_api_bp)
    app.register_blueprint(ITR_Statement_api_bp)
    app.register_blueprint(Voter_Redaction_api_bp)
    app.register_blueprint(Face_matching_api_bp)
    app.register_blueprint(Multi_name_match_api_bp)
    app.register_blueprint(Pennydrop_api_bp)
    app.register_blueprint(Aadhaar_mobile_link_bp)
    app.register_blueprint(Aadhaar_Auth_bp)
    app.register_blueprint(Voter_Auth_bp)

    # Initialize the socketio instance for each blueprint
    def register_socketio(blueprint, socketio_instance):
        blueprint.socketios = socketio_instance

    register_socketio(OCR_all_api_bp, socketios)



    # Landing Page URLS
    app.jinja_env.globals['Landing_routes_Urls'] = Landing_routes_Urls
    app.jinja_env.globals['Landing_Page_Topbar'] = Landing_Page_Topbar
    app.jinja_env.globals['Landing_Page_Footer'] = Landing_Page_Footer

    # Templetes Default Modal Call
    app.jinja_env.globals['Auth_Css_Urls'] = Auth_Css_Urls
    app.jinja_env.globals['Auth_Sidebar'] = Auth_Sidebar

    # User Portal URLS
    app.jinja_env.globals['User_Portal_urls'] = User_Portal_urls
    app.jinja_env.globals['User_portal_topbar'] = User_portal_topbar
    app.jinja_env.globals['User_portal_sidebar'] = User_portal_sidebar

    # Admin Portal URLs
    app.jinja_env.globals['Admin_Portal_urls'] = Admin_Portal_urls
    app.jinja_env.globals['Admin_Portal_topbar'] = Admin_Portal_topbar
    app.jinja_env.globals['Admin_Portal_sidebar'] = Admin_Portal_sidebar
    
    @app.route('/logout')
    def logout():
        # Clear all session data
        session.clear()
        # Redirect to the login page or any other desired page
        return redirect("/")

    # Headers Add

    @app.after_request
    def set_x_frame_options(response):
        if request.method == 'POST':
            response.headers['X-Frame-Options'] = 'DENY'  # or 'SAMEORIGIN'
        return response

    @app.before_request
    def generate_nonce():
        g.nonce = os.urandom(16).hex()
        
    @app.after_request
    def apply_security_headers(response):
        response.headers["Cross-Origin-Window-Policy"] = "deny"
        response.headers["Content-Security-Policy"] = ("default-src 'self'; "
                                                        "img-src 'self' data: blob:;" 
                                                        "script-src 'self' 'report-sample' 'unsafe-eval' 'nonce-{nonce}' https://www.gstatic.com https://www.google.com;" 
                                                        "style-src 'self' 'unsafe-hashes';"  
                                                        "frame-ancestors 'self';" 
                                                        "form-action 'self';" 
                                                        "connect-src 'self'; "
                                                        "object-src 'none'; "
                                                        "base-uri 'self'; "
                                                        "frame-src 'self' https://www.google.com/;"
                                                        "font-src 'self' https://fonts.googleapis.com https://fonts.gstatic.com;" ).format(nonce=g.nonce)
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'

         # access-control
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'origin'
        response.headers['Age'] = '3600'
        response.headers['Cache-Control'] = 'public, max-age=3600'
        
        return response
    


    return app