from flask import Blueprint, request, jsonify
from datetime import datetime
from flask_jwt_extended import  jwt_required
import subprocess
from passporteye import read_mrz
import pytesseract

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
        mrz_data = mrz.to_dict()
        for key, value in mrz_data.items():
            print(key)

        get_dob = date_get(mrz_data["date_of_birth"])
        get_expiration = date_get(mrz_data["expiration_date"])

        data_store.append({
            "mrz_type":mrz_data["mrz_type"],
            "date_of_birth":get_dob,
            "expiration_date":get_expiration,
            "nationality":mrz_data["nationality"],
            "gender":mrz_data["sex"],
            "number":mrz_data["number"],
            "personal_number":mrz_data["personal_number"],
            "mrz_lines":mrz_data["raw_text"],
            })

            
        return jsonify({"Data":mrz.to_dict()})
    else:
        print("MRZ could not be extracted.")
    return jsonify({"data":"ajgdjsg"})


@test_zbar_image_bp.route('/zbar_testing')
def zbar_main():
    Qr_Code_scane = subprocess.run(['zbarimg', '--raw', './apps/static/bar_test.png'], capture_output=True)
    xml_string = Qr_Code_scane.stdout.decode('utf-8')
    return jsonify({"data":xml_string})
