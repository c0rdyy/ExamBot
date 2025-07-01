from dotenv import load_dotenv
import os

load_dotenv()

SQLALCHEMY_URL = os.getenv('SQLALCHEMY_URL')
