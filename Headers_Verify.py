

from flask import request,jsonify
import bleach
import random
import uuid
import urllib.parse
import re

# DataBase
from data_base_string import *


Test_user_api_history_db = Regtch_services_UAT['Test_user_api_history']


# Expected headers
expected_headers = {
    "Content-Type": "application/json",
    "Cross-Origin-Window-Policy": "deny",
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Content-Security-Policy": "policy",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload"
}

def normalize_header_value(value):
    """Normalize header values by stripping whitespace."""
    return value.strip() if value else None

def check_headers(f):
    def wrapper(*args, **kwargs):
        # Check if all expected headers and values are present
        for header, expected_value in expected_headers.items():
            actual_value = normalize_header_value(request.headers.get(header))
            if actual_value != expected_value:
                # Return error message if headers are missing or values do not match
                error_msg = {
                    "status_code": 400,
                    "status": "InvalidHeader",
                    "response": "Required headers are missing or invalid!"
                }
                # print(f"Header check failed: Expected '{header}: {expected_value}', got '{header}: {actual_value}'")
                return jsonify({"data": error_msg}), 400
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__  # Preserve the original function name
    return wrapper



# HTML Injection and Also Missing Key

def clean(value, strip=False):
    """Sanitize input value by stripping disallowed HTML tags and attributes."""
    return bleach.clean(value, strip=strip)


URL_PATTERN = r"(https?|wss?):\/\/(?:[-\w.]|(?:%[\da-fA-F]{2}))+"

def validate_no_urls(input_string):
    # Check if the input contains any URLs
    if re.search(URL_PATTERN, input_string):
        return None  # Invalid input
    return input_string

def check_html_injection(data, keys_to_check):
    for key in keys_to_check:
        if key in data:
            # Check if the value is empty
            if key == 'binary_img' and not data[key]:
                continue

            if key == 'base64_img' and not data[key]:
                continue

            if key == "env":
                if data[key] not in ["test", "prod"]:
                    return jsonify({
                        "data": {
                            "status_code": 400,
                            "status": "Error",
                            "response": "Invalid value for 'env'. Allowed values are 'test' or 'prod'!"
                        }
                    }), 400
            
            if not data[key]:  # This checks for empty strings or None
                return jsonify({
                    "data": {
                        "status_code": 400,
                        "status": "Error",
                        "response": f"The value for '{key}' cannot be empty! Please provide a valid value!"
                    }
                }), 400
            
            # Sanitize the value
            decoded_name = urllib.parse.unquote(data[key])

            validated_name = validate_no_urls(decoded_name)

            if not validated_name:
                return jsonify({
                    "data": {
                        "status_code": 400,
                        "status": "Error",
                        "response": "The input contains disallowed HTML tags or attributes or URLs! Please remove any unsafe HTML!"
                    }
                }), 400

            sanitized_value = clean(decoded_name, strip=True)
            if data[key] != sanitized_value:
                return jsonify({
                    "data": {
                        "status_code": 400,
                        "status": "Error",
                        "response": "The input contains disallowed HTML tags or attributes or URLs! Please remove any unsafe HTML!"
                    }
                }), 400
        else:
            return jsonify({
                "data": {
                    "status_code": 400,
                    "status": "Error",
                    "response": f"Please verify your key! The provided key is missing or invalid!"
                }
            }), 400
    return None


# Random request id generate
def generate_random_id():
    request_id ='-'.join(''.join(random.choices('0123456789abcdef', k=4)) for _ in range(5))

    # id already exist in system
    check_db =  Test_user_api_history_db.find_one({"request_id":request_id})
    
    if check_db != None:
        generate_random_id()
    
    return request_id


def generate_random_client_id():
    part1 = uuid.uuid4().hex[:12]  # Generates 12 hex characters
    part2 = str(uuid.uuid4())      # Generates a UUID string
    return f"{part1}/{part2}"

def generate_random_client_secret_key():
    return str(uuid.uuid4())


# PDF File Extention
ALLOWED_EXTENSIONSS = {'pdf'}

def allowed_pdf_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONSS