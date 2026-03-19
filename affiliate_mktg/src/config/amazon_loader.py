from dotenv import load_dotenv
import os

load_dotenv()


def get_amazon_config():
    return {
        "ACCESS_KEY_PAAPI": os.getenv("ACCESS_KEY_PAAPI"),
        "SECRET_KEY_PAAPI": os.getenv("SECRET_KEY_PAAPI"),
        "PARTNER_TAG": os.getenv("PARTNER_TAG"),
        "ENCRYPTION_KEY": os.getenv("ENCRYPTION_KEY"),
        "MARKETPLACE": os.getenv("MARKETPLACE"),
        "THROTTLE_DELAY": os.getenv("THROTTLE_DELAY"),
        "HOST": os.getenv("HOST"),
        "REGION": os.getenv("REGION"),
        "CREDENTIAL_ID_CREATORSAPI": os.getenv("CREDENTIAL_ID_CREATORSAPI"),
        "CREDENTIAL_SECRET_CREATORSAPI": os.getenv("CREDENTIAL_SECRET_CREATORSAPI"),
        "VERSION_CREATORSAPI": os.getenv("VERSION_CREATORSAPI"),
    }