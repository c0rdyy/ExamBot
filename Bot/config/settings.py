from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_URL = os.getenv('SQLALCHEMY_URL')
ADMIN_IDS=[566938479,1533701707]