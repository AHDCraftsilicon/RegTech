

from flask import request,jsonify
import bleach


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


def check_html_injection(data, keys_to_check):
    for key in keys_to_check:
        if key in data:
            # Check if the value is empty
            if not data[key]:  # This checks for empty strings or None
                return jsonify({
                    "data": {
                        "status_code": 400,
                        "status": "Error",
                        "response": f"The value for '{key}' cannot be empty."
                    }
                }), 400
            
            # Sanitize the value
            sanitized_value = clean(data[key], strip=True)
            if data[key] != sanitized_value:
                return jsonify({
                    "data": {
                        "status_code": 400,
                        "status": "Error",
                        "response": "The input contains disallowed HTML tags or attributes!"
                    }
                }), 400
        else:
            return jsonify({
                "data": {
                    "status_code": 400,
                    "status": "Error",
                    "response": f"Please Verify Your Key!"
                }
            }), 400
    return None