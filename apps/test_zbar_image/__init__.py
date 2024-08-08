from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import  jwt_required
import subprocess
from passporteye import read_mrz
import pytesseract , os , time
from werkzeug.utils import secure_filename
import re

# Blueprint
test_zbar_image_bp = Blueprint("test_zbar_image_bp",
                        __name__,
                        url_prefix="/")


# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def date_get(num):
    num_str = str(num)

    # Parse the year, month, and day
    year = int(num_str[:2])
    month = int(num_str[2:4])
    day = int(num_str[4:6])

    # Assume the year is in the 1900s if it's less than a certain threshold (e.g., 50), otherwise 2000s
    if year < 50:
        year += 2000
    else:
        year += 1900

    # Create the date object
    date = datetime(year, month, day)

    return date.strftime('%Y-%m-%d')



@test_zbar_image_bp.route('/passport_testing')
def passport_main():
    mrz = read_mrz("./apps/static/abc.jpg")

# Print the extracted MRZ data
    if mrz is not None:
        data_store = []
        # mrz_data = mrz.to_dict()
        # for key, value in mrz_data.items():
        #     print(key)

        # get_dob = date_get(mrz_data["date_of_birth"])
        # get_expiration = date_get(mrz_data["expiration_date"])

        # data_store.append({
        #     "mrz_type":mrz_data["mrz_type"],
        #     "date_of_birth":get_dob,
        #     "expiration_date":get_expiration,
        #     "nationality":mrz_data["nationality"],
        #     "gender":mrz_data["sex"],
        #     "number":mrz_data["number"],
        #     "personal_number":mrz_data["personal_number"],
        #     "mrz_lines":mrz_data["raw_text"],
        #     })

            
        return jsonify({"Data":mrz.to_dict()})
    else:
        print("MRZ could not be extracted.")
    return jsonify({"data":"ajgdjsg"})



@test_zbar_image_bp.route('/passport_testing_api',methods=['POST'])
def passport_main_api():
    if request.method == 'POST':
        f = request.files["img"]
        filename_img = str(time.time()).replace(".", "")
        if f.filename != "":
            f.save(os.path.join('./apps/static/passport_data', secure_filename(
                filename_img+"."+f.filename.split(".")[-1])))
            img = "apps/static/passport_data/"+filename_img+"."+f.filename.split(".")[-1]

            mrz = read_mrz(img)

            passport_json_data = {}
            if mrz is not None:
                passport_data = mrz.to_dict()

                if passport_data['personal_number'] != "":
                    passport_json_data['personal_number'] = passport_data['personal_number']

                if passport_data['raw_text'] != "":
                    passport_json_data['raw_text'] = passport_data['raw_text']

                if passport_data['names'] != "":
                    passport_json_data['name'] = passport_data['names']

                if passport_data['number'] != "":
                    passport_json_data['number'] = passport_data['number']

                if passport_data['surname'] != "":
                    passport_json_data['surname'] = passport_data['surname']

                if passport_data['country'] != "":
                    passport_json_data['country'] = passport_data['country']
                
                if passport_data['valid_score'] != "":
                    passport_json_data['valid_score'] = passport_data['valid_score']

                if passport_data['sex'] != "":
                    passport_json_data['sex'] = passport_data['sex']

                if passport_data['mrz_type'] != "":
                    passport_json_data['mrz_type'] = passport_data['mrz_type']

               
                if passport_json_data != {}:
                    return {"response": 200,
                            "message": "Success",
                            "responseValue": {
                                "Table1": [
                                    {
                                        "DocumentResponse": passport_json_data
                                    }
                                ]
                            }
                        }
                else:
                    return {"response": 400,
                                        "message": "Error",
                                        "responseValue": "Please upload a high-quality and readable image."
                                    }
            else:
                return {"response": 400,
                                        "message": "Error",
                                        "responseValue": "Please upload a high-quality and readable image."
                                    }


@test_zbar_image_bp.route('/zbar_testing')
def zbar_main():
    Qr_Code_scane = subprocess.run(['zbarimg', '--raw', './apps/static/bar_test.png'], capture_output=True)
    xml_string = Qr_Code_scane.stdout.decode('utf-8')
    return jsonify({"data":xml_string})
