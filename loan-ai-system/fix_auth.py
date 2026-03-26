import streamlit_authenticator as stauth
import os
from dotenv import load_dotenv

load_dotenv()

# Streamlit-authenticator 0.4.x expects a specific config structure
# and the Hasher is used differently.
# Let's just generate a fresh hash for 'admin' using bcrypt directly as it's the standard.

import bcrypt
pwd = b"admin"
hashed = bcrypt.hashpw(pwd, bcrypt.gensalt(12)).decode()
print(f"NEW_HASH: {hashed}")
