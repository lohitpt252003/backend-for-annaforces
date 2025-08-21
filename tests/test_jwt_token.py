import sys
import os
import time

from utils.jwt_token import generate_token, validate_token

token = generate_token(123)
print(token)
print(validate_token(token))
for i in range(100):
    time.sleep(2)
    print(validate_token(token))