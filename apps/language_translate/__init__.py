from flask import Blueprint, request, jsonify
from googletrans import Translator , LANGUAGES
# from flask_jwt_extended import JWTManager, jwt_required,get_jwt_identity


# Blueprint
language_translate_bp = Blueprint("language_translate_bp",
                        __name__,
                        url_prefix="/")

translator = Translator()

@language_translate_bp.route('/api/v1/languagetransalator/getlanguagetranslator',methods=['POST'])
# @jwt_required()
def language_translator_main():
    if request.method == 'POST':
        
        try:
            # abc = get_jwt_identity()
            data = request.get_json()
            if not data or 'SampleText' not in data:
                return jsonify({"response": "999",
                        "message": "Error",
                        "responseValue": "SampleText cannot be null or empty."
                    }), 400
            elif not data or 'ToLanguage' not in data:
                return jsonify({"response": "999",
                        "message": "Error",
                        "responseValue": "ToLanguage cannot be null or empty."
                    }), 400
            elif not data or 'FromLanguage' not in data:
                return jsonify({"response": "999",
                        "message": "Error",
                        "responseValue": "FromLanguage cannot be null or empty."
                    }), 400


            translation = translator.translate(data['SampleText'], src=data['ToLanguage'], dest=data['FromLanguage'])
            if translation.text != "":
                return jsonify({"response": "000",
                                "message": "Success",
                                "responseValue": {
                                    "Table1": [{
                                            "TranslatedText": translation.text}]}}), 200
            else:
                return jsonify({"response": "000",
                                "message": "Success",'responseValue':"Please Choose Correct language!"})
        except:
            if not data or 'SampleText' not in data:
                return jsonify({"response": "999",
                        "message": "Error",
                        "responseValue": "SampleText cannot be null or empty."
                    }), 400
            return jsonify({"response": "000",
                            "message": "Success",
                            "responseValue": {
                                "Table1": [{"TranslatedText": data['SampleText']
                                            }]}}), 200


