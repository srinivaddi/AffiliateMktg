import os
import pickle
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build

from affiliate_mktg.src.config.loader import get_blog_config
from affiliate_mktg.src.utils.logging_setup import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)
configValues = get_blog_config()

class BlogService:
    def __init__(self):
        logger.info("Hello from BlogService!")
        self.SCOPES_STR = configValues["SCOPES_STR"]
        self.SCOPES = [self.SCOPES_STR]
        self.SERVICE_NAME = configValues["SERVICE_NAME"]
        self.SERVICE_VERSION = configValues["SERVICE_VERSION"]
        self.CLIENT_SECRETS_JSON = configValues["CLIENT_SECRETS_JSON"]
        self.CLIENT_SECRETS = json.loads(self.CLIENT_SECRETS_JSON)

    def get_credentials(self):
        creds = None
        try:
            if os.path.exists("token.pickle"):
                with open("token.pickle", "rb") as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                try:
                    if creds and creds.expired and creds.refresh_token:
                        creds.refresh(Request())
                    else:
                        raise RefreshError("No valid refresh token")
                except RefreshError:
                    logger.warning(
                        "Refresh token invalid or expired. Re-authenticating..."
                    )
                    flow = InstalledAppFlow.from_client_config(
                        self.CLIENT_SECRETS, self.SCOPES
                    )
                    creds = flow.run_local_server(
                        port=0, access_type="offline", prompt="consent"
                    )

                with open("token.pickle", "wb") as token:
                    pickle.dump(creds, token)

            return creds

        except Exception as e:
            logger.error(
                f"Error loading or creating credentials: {e}", exc_info=True
            )
            raise ValueError(f"Error loading or creating credentials: {e}")

    def get_blogger_service(self):
        try:
            creds = self.get_credentials()
            service = build(
                self.SERVICE_NAME, self.SERVICE_VERSION, credentials=creds
            )
            return service
        except Exception as e:
            logger.error(
                f"Error generating  blogger service: {e}", exc_info=True
            )
            raise ValueError(f"Error generating  blogger service: {e}")
