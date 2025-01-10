#!/usr/bin/env python3
from secrets import token_hex

"""
create a secret key to use in SECRET_KEY
"""
print(token_hex(25))

