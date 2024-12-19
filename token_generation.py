import jwt
from datetime import datetime, timedelta
from cryptography.fernet import Fernet, InvalidToken
import base64
from flask import request,jsonify


key = b'jpoqaVOJPJzsBuRvcUSAuhPkbCRTXwGvZ6njt0Wjyng='
cipher_suite = Fernet(key)



def encrypt_token(token):
    return cipher_suite.encrypt(token.encode())

def decrypt_token(encrypted_token):
    return cipher_suite.decrypt(encrypted_token).decode()



# Image Extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg','jfif'}
ALLOWED_MIME_TYPES = {'image/jpeg', 'image/png'}

def allowed_file(file):
    # Check the file extension
    filename = file.filename
    if not '.' in filename:
        return False
    ext = filename.rsplit('.', 1)[1].lower()
    # Check if extension and MIME type are valid
    return ext in ALLOWED_EXTENSIONS and file.mimetype in ALLOWED_MIME_TYPES

