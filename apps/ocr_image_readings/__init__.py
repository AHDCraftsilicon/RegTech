from flask import Blueprint, request, jsonify
# from flask_jwt_extended import JWTManager, jwt_required,get_jwt_identity
import time , os
from werkzeug.utils import secure_filename
from ocr_reading_files.pancard_ocr import *
from ocr_reading_files.electoion_card_ocr import *
from ocr_reading_files.passport_id_ocr import *
from ocr_reading_files.addhar_ocr_without_load import *
import base64 , io

# Blueprint
ocr_image_reading_bp = Blueprint("ocr_image_reading_bp",
                        __name__,
                        url_prefix="/")




@ocr_image_reading_bp.route('/api/v1/readdocument/readiamgetext',methods=['POST'])
def ocr_image_read_text_main():
    if request.method == 'POST':  

        # try:

        data = request.get_json() 
        if not data or 'ImageBase64' not in data:
            return jsonify({"response": "999",
                        "message": "Error",
                        "responseValue": "ImageBase64 cannot be null or empty."
                    }), 400
        
        if not data or 'documenttype' not in data:
            return jsonify({"response": "999",
                        "message": "Error",
                        "responseValue": "ImageBase64 cannot be null or empty."
                    }), 400
        
        # return jsonify({"data":""})
    
        if data['ImageBase64'] != "":
            try:
                base64_string = data['ImageBase64'].split(',')[1]
            except:
                base64_string = data['ImageBase64']

            # print(base64_string.split(',')[1])

            if base64_string.startswith('data:image/jpeg;base64,'):
                base64_string = base64_string.replace('data:image/jpeg;base64,', '')

            # Decode the base64 string into bytes
            image_bytes = base64.b64decode(base64_string)

            # Convert bytes data to PIL Image
            image = Image.open(io.BytesIO(image_bytes))

            # Save the image to a file (example: 'output.jpg')
            filename_img = str(time.time()).replace(".", "")
            # print(filename_img+".png")
            static_file_name = filename_img+".png"

            image.save(os.path.join('apps/static/ocr_image', secure_filename(static_file_name)))
            
            image_path = "./apps/static/ocr_image/" +static_file_name

            if data['documenttype'] == "PanCard":
                pancard = pancard_main(image_path)
                return pancard
            elif data['documenttype'] == "AdharCard":
                print(image_path)
                addhar_Card = aadhar_ocr_image_read_main(image_path)
                # os.remove(image_path)
                return addhar_Card
            elif data['documenttype'] == "VoterID":
                election_Card = voter_id_read(image_path)
                return election_Card
            elif data['documenttype'] == "PassportID":
                passport = passport_main(image_path)
                return passport 
            else:
                return jsonify({"response": "999",
                        "message": "Error",
                        "responseValue": "Error Processing your request"
                    })
                
    # except:
    #     return jsonify({"response": "999",
    #                     "message": "Error",
    #                     "responseValue": "Error Processing your request"
    #                 })            


        # f = request.files["ImageBase64"]
        # filename_img = str(time.time()).replace(".", "")
        # if f.filename != "":
        #     f.save(os.path.join('./apps/static/ocr_image', secure_filename(
        #         filename_img+"."+f.filename.split(".")[-1])))
        #     img = "/static/ocr_image/"+filename_img+"."+f.filename.split(".")[-1]

        
                



    

