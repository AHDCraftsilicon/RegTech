from flask import Flask,jsonify,redirect,url_for,request,render_template,render_template_string
from functools import wraps
from apps.addhar_masking import adhar_masking_bp
from apps.image_quality_ckeck import image_quality_check_bp
from apps.name_matching import name_matching_bp
from apps.language_translate import language_translate_bp
from apps.token_request import token_request_bp
from apps.ocr_image_readings import ocr_image_reading_bp
from apps.database_log import database_table_bp
from apps.login_admin import login_Admin_bp
from apps.object_detaction import object_detaction_bp
from apps.bank_statement_pdf_text import bank_statement_bp
from apps.company_list import comapny_list_table_bp
from flask_jwt_extended import JWTManager, create_access_token, jwt_required,unset_jwt_cookies
from datetime import datetime, timedelta

# Testing
from apps.test_zbar_image import test_zbar_image_bp



def crete_app():
    app = Flask(__name__)
    # app = Flask(__name__,template_folder='app/components')
    app.secret_key = "djfljdfljfnkjsfhjfshjkfjfjfhjdhfdjhdfu"
    app.config['UPLOAD_FOLDER'] = "./static/addhar_masksing_img"

    app.config["JWT_SECRET_KEY"] = "craftsiliconniblerectechservice"
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    # app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    # app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=15)

    
    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def my_expired_token_callback(jwt_header, jwt_payload):
        # print(jwt_payload)
        if jwt_payload["is_api"] == True:
            return jsonify({"status": "Failure",
                    "statusCode": "401",
                    "statusMessage": "Invalid token or expired token"
                }), 401
        else:
            return redirect('/admin/login')

    @jwt.invalid_token_loader
    def invalid_token_callback(callback):
        request_path = request.path
        # print(callback , request_path)
        if '/api/v1/' in request_path:
            return jsonify({"status": "Failure",
                    "statusCode": "401",
                    "statusMessage": "Invalid token or expired token"
                }), 401
        else:
            return redirect('/admin/login')
    
    @jwt.unauthorized_loader
    def my_expired_token_callbacks(jwt_payload):
        # print('...........')
        # print("jwt",jwt_payload)        
        # original_request_path = request.path
        # print(original_request_path)
        # if original_request_path == '/database-log' :
        #     return redirect('/database-log')
        # else:
        return redirect('/admin/login')
    
    # ADDED FOR VERSION CHECK IN DEPLOYEMNT

    @app.route('/version-check', methods=["GET"])
    def version():
        return {"version":"0.0.7.7"}
    
    #END VERSIONS CHECK

    @app.route('/admin/logout', methods=["GET"])
    @jwt_required()
    def logout():
        m = redirect('/admin/login')
        unset_jwt_cookies(m)
        return m
    
    # @jwt.unauthorized_loader
    # def my_expired_token_callbacks(jwt_payload):
    #     return jsonify({"status": "Failure",
    #                 "statusCode": "401",
    #                 "statusMessage": "Invalid token or expired token"
    #             }), 401



     # Top Bar
    def load_topbar(username):
            with app.open_resource('components/topbar.html') as f:
                return render_template_string(f.read().decode('utf-8'),username=username)
    
    # # # Navbar Routes  
    def navigation_urls(manage_role):
            with app.open_resource('components/nav_routes.html') as f:
                return render_template_string(f.read().decode('utf-8'))
            

    #   # Footer 
    def load_footer():
            with app.open_resource('components/footer.html') as f:
                return f.read().decode('utf-8')
    
    # Css
    def load_css():
            with app.open_resource('components/css_urls.html') as f:
                return f.read().decode('utf-8')
     
    # Javascript    
    def load_javascript():
            with app.open_resource('components/script_urls.html') as f:
                return f.read().decode('utf-8')
            


    app.register_blueprint(adhar_masking_bp)
    app.register_blueprint(image_quality_check_bp)
    app.register_blueprint(name_matching_bp)
    app.register_blueprint(language_translate_bp)
    app.register_blueprint(token_request_bp)
    app.register_blueprint(ocr_image_reading_bp)
    app.register_blueprint(database_table_bp)
    app.register_blueprint(login_Admin_bp)
    app.register_blueprint(test_zbar_image_bp)
    app.register_blueprint(object_detaction_bp)
    app.register_blueprint(bank_statement_bp)
    app.register_blueprint(comapny_list_table_bp)


    app.jinja_env.globals['load_topbar'] = load_topbar
    app.jinja_env.globals['navigation_urls'] = navigation_urls
    app.jinja_env.globals['load_footer'] = load_footer
    app.jinja_env.globals['load_css'] = load_css
    app.jinja_env.globals['load_javascript'] = load_javascript
    # app.jinja_env.globals['check_password'] = check_password
    # app.jinja_env.globals['party_view_javascript'] = party_view_javascript
    # app.jinja_env.globals['dashboard_url'] = dashboard_url

    
    
    
    return app