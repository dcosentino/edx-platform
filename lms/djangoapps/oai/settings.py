from django.conf import settings

from datetime import timedelta

# Endpoint settings
REPOSITORY_NAME = settings.PLATFORM_NAME
ADMIN_EMAIL = settings.TECH_SUPPORT_EMAIL
OAI_ENDPOINT_NAME = 'oai'
RESULTS_LIMIT = 100
RESUMPTION_TOKEN_VALIDITY = timedelta(hours=6)
METADATA_FORMAT = 'oai_dc'
OWN_SET_PREFIX = settings.PLATFORM_NAME
RESUMPTION_TOKEN_SALT = 'change_me' # salt used to generate resumption tokens

if hasattr(settings, 'OAI_SETTINGS'):
    OAI_ENDPOINT_NAME = settings.OAI_SETTINGS.get('OAI_ENDPOINT_NAME')
    RESULTS_LIMIT = settings.OAI_SETTINGS.get('RESULTS_LIMIT') or RESULTS_LIMIT
    METADATA_FORMAT = settings.OAI_SETTINGS.get('METADATA_FORMAT') or METADATA_FORMAT
    RESUMPTION_TOKEN_SALT = settings.OAI_SETTINGS.get('RESUMPTION_TOKEN_SALT') or RESUMPTION_TOKEN_SALT


