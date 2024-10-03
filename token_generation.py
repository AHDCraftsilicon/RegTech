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
