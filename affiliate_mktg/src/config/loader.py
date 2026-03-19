from dotenv import load_dotenv
import os
from itsdangerous import URLSafeSerializer

load_dotenv()


def get_blog_config():
    return {
        "BLOG_ID": os.getenv("BLOG_ID"),
        "SCOPES_STR": os.getenv("SCOPES_STR"),
        "SERVICE_NAME": os.getenv("SERVICE_NAME"),
        "SERVICE_VERSION": os.getenv("SERVICE_VERSION"),
        "BASE_URL": os.getenv("BASE_URL"),
        "LABELS": os.getenv("LABELS"),
        "LIVE_POST": os.getenv("LIVE_POST"),
        "FILE_EXTENSION": os.getenv("FILE_EXTENSION"),
        "LOCATION_JSON": os.getenv("LOCATION_JSON"),
        "CLIENT_SECRETS_JSON": os.getenv("CLIENT_SECRETS_JSON"),
        "FILTER_POST_COUNT": os.getenv("FILTER_POST_COUNT"),
        "FILTER_POST": os.getenv("FILTER_POST"),
        "FILTER_DAYS": os.getenv("FILTER_DAYS"),
        "MODEL_NAME": os.getenv("MODEL_NAME"),
        "MODEL_OPTIONS_JSON": os.getenv("MODEL_OPTIONS_JSON"),
        "TOPIC": os.getenv("TOPIC"),
        "STREAM": os.getenv("STREAM"),
        "SYSTEM_PROMPT_ROLE": os.getenv("SYSTEM_PROMPT_ROLE"),
        "SYSTEM_PROMPT_STYLE": os.getenv("SYSTEM_PROMPT_STYLE"),
        "SYSTEM_PROMPT_TEMPLATE": os.getenv("SYSTEM_PROMPT_TEMPLATE"),
        "USER_PROMPT_TEMPLATE": os.getenv("USER_PROMPT_TEMPLATE"),
    }


def get_starlette_config():
    return {
        "SESSION_SECRET_KEY": os.getenv("SESSION_SECRET_KEY"),
        "HOMEPAGE_PATH": os.getenv("HOMEPAGE_PATH"),
        "SESSION_PATH": os.getenv("SESSION_PATH"),
        "STATS_PATH": os.getenv("STATS_PATH"),
        "RESET_STATS_PATH": os.getenv("RESET_STATS_PATH"),
        "HEALTH_PATH": os.getenv("HEALTH_PATH"),
        "RUN_GENERATE_LINK_POST_BLOG_MANUAL_PATH": os.getenv(
            "RUN_GENERATE_LINK_POST_BLOG_MANUAL_PATH"
        ),
        "GET": os.getenv("GET"),
        "POST": os.getenv("POST"),
        "SERIALLIZER": URLSafeSerializer(os.getenv("SESSION_SECRET_KEY")),
    }
